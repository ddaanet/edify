"""Failure-arm tests for ``plugin/bin/triage-feedback.sh``.

This module is for the script's failure arms: the usage error (exit 1, no
stdout, no log row), an entry that stops triage with ``ERROR:`` and exit 2
and appends no log row (including a run outside any work tree, which prints
one ``ERROR:`` line, and a ``changed-files.sh`` failure whose own output is
printed first), a failing git call behind the reports count, and a
classification parse that fails rather than returning a result (an
unreadable ``classification.md`` or a failing label ``sed``). A run that
reaches a verdict, including ``no-classification``, is a result and stays in
the hub. The behavioural-code and log failures stay in their own modules
(D-90).

Split from ``tests/test_triage_feedback.py``, which keeps the files-changed,
reports and classification tests, to keep each module under its line cap.
See ``tests/triage_feedback_helpers.py`` for the shared fixtures.
"""

import os
import shlex
import shutil
from pathlib import Path

import pytest

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _init_repo,
    _run_git,
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


@pytest.mark.parametrize(
    ("job", "extra_args"),
    [
        pytest.param(None, (), id="no-args"),
        pytest.param(JOB, ("HEAD",), id="stale-base"),
    ],
)
def test_usage_error_exits_1(
    tmp_path: Path, job: str | None, extra_args: tuple[str, ...]
) -> None:
    """Zero or two or more arguments exit 1 with the usage line on stderr.

    The fixture commits a ``def`` under a ``Simple`` classification, so
    ``triage-feedback.sh j`` alone would reach ``underclassified`` and log a
    row. ``no-args`` runs the script with no argument; ``stale-base`` passes
    ``j HEAD``, the retired two-argument form. Both leave stdout empty and
    log nothing.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit_item_report(
        repo,
        {
            f"plans/{JOB}/classification.md": "- **Classification:** Simple\n",
            "module.py": "def foo():\n    pass\n",
        },
    )
    result = _run_triage(job, repo, extra_args=extra_args)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stderr.strip() == "Usage: triage-feedback.sh <job>", result.stderr
    assert result.stdout == "", result.stdout
    assert not (repo / "plans" / "reports" / "triage-feedback-log.md").exists()


def test_changed_files_error_is_printed_then_exit_2(tmp_path: Path) -> None:
    """A ``changed-files.sh`` exit 2 prints its output, then triage's cause.

    An unborn repository, with ``classification.md`` on disk, fails
    ``changed-files.sh``'s ``git log`` and exits 2. Triage prints that
    ``ERROR:`` line, then ``ERROR: changed-files.sh exited 2``, and exits 2
    with nothing else on stdout and no log row. A guard that tests for status
    1 only lets the run go on with the error text as its base, and a guard
    that prints both lines but does not exit goes on the same way: either
    adds ``ERROR: git diff failed`` from the reports count, still exit 2.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "-q", "-b", "main")
    classification = repo / "plans" / JOB / "classification.md"
    classification.parent.mkdir(parents=True)
    classification.write_text("- **Classification:** Simple\n", encoding="utf-8")

    result = _run_triage(JOB, repo)
    lines = result.stdout.splitlines()
    output = result.stdout + result.stderr
    assert lines == [
        "ERROR: git log failed",
        "ERROR: changed-files.sh exited 2",
    ], output
    assert result.returncode == 2, output
    assert not (repo / "plans" / "reports" / "triage-feedback-log.md").exists()


def _underclassified_repo(repo: Path) -> Path:
    """Build an ``underclassified`` run; return its ``classification.md``.

    The run commit holds a ``def`` under a ``Simple`` classification, so a
    run that is not stopped logs a row.
    """
    _init_repo(repo)
    _commit_item_report(
        repo,
        {
            f"plans/{JOB}/classification.md": "- **Classification:** Simple\n",
            "module.py": "def foo():\n    pass\n",
        },
    )
    return repo / "plans" / JOB / "classification.md"


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode-000 file")
def test_unreadable_classification_is_an_error(tmp_path: Path) -> None:
    """An unreadable ``classification.md`` exits 2 with ``grep failed``.

    The file exists, so the ``-f`` test passes, and ``grep`` exits 2 on it.
    Read as "no Classification line" the run would end at
    ``no-classification`` with an evidence report and exit 0; the fixture
    otherwise reaches ``underclassified`` and logs a row. The behavioural
    grep prints the same ``ERROR:`` line, so grep's own diagnostic, naming
    the file, ties the failure to the classification grep. The mode is
    restored before cleanup.
    """
    repo = tmp_path / "repo"
    classification = _underclassified_repo(repo)
    classification.chmod(0o000)
    try:
        result = _run_triage(JOB, repo)
    finally:
        classification.chmod(0o644)

    output = result.stdout + result.stderr
    assert result.stdout.splitlines() == ["ERROR: grep failed"], output
    assert "classification.md" in result.stderr, output
    assert result.returncode == 2, output
    assert not (repo / "plans" / "reports" / "triage-feedback-log.md").exists()


def test_failing_label_sed_is_an_error(tmp_path: Path) -> None:
    """A failing label ``sed`` exits 2 with ``sed failed``, never a verdict.

    The script runs ``sed`` once, on the label. A ``sed`` shim, on a call
    whose arguments name ``Classification``, runs the real tool and then
    exits 4, so the label is printed and only the status reports the
    failure; it passes any other call through. Without the guard, ``set -e``
    ends the run at exit 4 with no ``ERROR:`` line. A guard that drops the
    status, or tests the captured label for emptiness instead, reads
    ``Simple``, reaches ``underclassified`` and logs a row.
    """
    real_sed = shutil.which("sed")
    assert real_sed is not None, "sed not found on PATH"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "sed"
    quoted_sed = shlex.quote(real_sed)
    shim.write_text(
        "#!/bin/sh\n"
        'for arg in "$@"; do\n'
        '    case "$arg" in\n'
        "        *Classification*)\n"
        f'            {quoted_sed} "$@"\n'
        '            echo "shim: fail" >&2\n'
        "            exit 4\n"
        "            ;;\n"
        "    esac\n"
        "done\n"
        f'exec {quoted_sed} "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    repo = tmp_path / "repo"
    _underclassified_repo(repo)

    result = _run_triage(JOB, repo, path_prepend=bin_dir)
    output = result.stdout + result.stderr
    assert result.stdout.splitlines() == ["ERROR: sed failed"], output
    assert result.returncode == 2, output
    assert not (repo / "plans" / "reports" / "triage-feedback-log.md").exists()
