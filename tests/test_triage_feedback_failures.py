"""Failure-arm tests for ``plugin/bin/triage-feedback.sh``.

This module is for the script's failure arms: an entry that stops triage
with ``ERROR:`` and exit 2 and appends no log row (including a run outside
any work tree, which prints one ``ERROR:`` line), a failing git call behind
the reports count, and a classification parse that fails rather than
returning a result. A run that reaches a verdict, including
``no-classification``, is a result and stays in the hub. The behavioural-code
and log failures stay in their own modules (D-90).

Split from ``tests/test_triage_feedback.py``, which keeps the files-changed,
reports and classification tests, to keep each module under its line cap.
See ``tests/triage_feedback_helpers.py`` for the shared fixtures.
"""

import shutil
from pathlib import Path

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _init_repo,
    _run_triage,
)


def test_failing_reports_diff_is_an_error_not_none(tmp_path: Path) -> None:
    """A failing reports diff exits 2, never reads as ``Reports: 0``.

    No repo state fails the ``--diff-filter=A`` name-only diff without
    failing ``changed-files.sh``'s diff first, so a ``git`` shim fails that
    one call. The count is a pipeline into ``wc -c``; a form that loses the
    diff's status prints ``Reports: 0`` and exits 0.
    """
    real_git = shutil.which("git")
    assert real_git is not None, "git not found on PATH"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = diff ]; then\n'
        '    for arg in "$@"; do\n'
        '        [ "$arg" = --diff-filter=A ] && { echo "shim: fail" >&2; exit 128; }\n'
        "    done\n"
        "fi\n"
        f'exec "{real_git}" "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit_item_report(repo, {"a.txt": "a\n"})

    result = _run_triage(JOB, repo, path_prepend=bin_dir)
    assert "ERROR: git diff failed" in result.stdout.splitlines(), result.stdout
    assert "- Reports:" not in result.stdout, result.stdout
    assert result.returncode == 2, result.stdout + result.stderr


def test_no_base_is_an_error_with_no_log_row(tmp_path: Path) -> None:
    """``changed-files.sh``'s ``NO-BASE:`` stops triage: exit 2, no row.

    The repo holds no committed item report, so ``changed-files.sh j`` exits
    1 with ``NO-BASE:``. Triage prints that line, then its own ``ERROR:``,
    and exits 2 (D-90). The classification is ``Simple`` and the commit
    holds a ``def``, so a run reaching a verdict would log an
    ``underclassified`` row. An unguarded capture under ``set -e`` exits 1
    with empty stdout instead, and one that drops the printed output loses
    the ``NO-BASE:`` cause.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "no item report",
        {
            f"plans/{JOB}/classification.md": "- **Classification:** Simple\n",
            "module.py": "def foo():\n    pass\n",
        },
    )

    result = _run_triage(JOB, repo)
    lines = result.stdout.splitlines()
    assert any(line.startswith("NO-BASE: ") for line in lines), result.stdout
    assert any(line.startswith("ERROR: ") for line in lines), result.stdout
    assert "## Evidence" not in lines, result.stdout
    assert result.returncode == 2, result.stdout + result.stderr
    assert not (repo / "plans" / "reports" / "triage-feedback-log.md").exists()


def test_outside_a_work_tree_is_one_error_line(tmp_path: Path) -> None:
    """Outside any work tree triage prints one ``ERROR:`` line and exits 2.

    The CWD is a directory in no work tree, with ``GIT_CEILING_DIRECTORIES``
    set to its parent so no enclosing repository is found. The only stdout
    line is the script's own cause: no ``changed-files.sh exited`` text, which
    would name a second failure behind the first. Nothing is created under the
    CWD, so no log directory is made.
    """
    outside = tmp_path / "outside"
    outside.mkdir()

    result = _run_triage(
        JOB, outside, env_extra={"GIT_CEILING_DIRECTORIES": str(tmp_path)}
    )
    lines = result.stdout.splitlines()
    output = result.stdout + result.stderr
    assert len(lines) == 1, output
    assert lines[0].startswith("ERROR: "), output
    assert lines[0].removeprefix("ERROR: ").strip(), output
    assert "changed-files.sh exited" not in result.stdout, output
    assert result.returncode == 2, output
    assert list(outside.iterdir()) == [], output
