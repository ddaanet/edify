"""Exit-code tests for ``plugin/skills/build/scripts/changed-files.sh``.

These tests hold the script's failure exits: ``ERROR:`` with exit 2 for a git
failure, an unsafe job name or an unloadable ``exempt-paths.sh``, and
``NO-BASE:`` with exit 1 when no item report is committed (D-88, D-90).

A late diff failure also lives here: ``ERROR:`` stands alone, with no
``BASE:`` line and no path above it (D-90).

Split from ``tests/test_changed_files.py``, which keeps the base and list
tests, to keep each module under its line cap. The ``--phase`` tests (D-89)
are in ``tests/test_changed_files_phase.py``. See
``tests/changed_files_helpers.py`` for the shared fixtures.
"""

import shlex
import shutil
from pathlib import Path

import pytest

from .changed_files_helpers import SCRIPT, _commit, _init_repo, _run_git, _run_script


def test_git_failure_is_error_not_no_base(tmp_path: Path) -> None:
    """A git failure exits 2 with ``ERROR:``, never ``NO-BASE:``'s exit 1.

    Exit 1 is ``NO-BASE:``'s code, not every failure's. A repo whose root
    commit adds the item report has a report but no parent to take as the
    base: a git failure, exit 2 with ``ERROR:``. A repo with no commit at
    all fails one step earlier, in the ``git log`` query itself, and must
    give exit 2 too, never the empty result that ``NO-BASE:`` reads. An
    implementation answering ``NO-BASE:`` from either failure branch reds
    here.
    """
    unborn = tmp_path / "unborn"
    unborn.mkdir()
    _run_git(unborn, "init", "-q", "-b", "main")
    unborn_result = _run_script(unborn, "j")
    assert unborn_result.returncode == 2, unborn_result.stdout + unborn_result.stderr
    assert "ERROR: git log failed" in unborn_result.stdout.splitlines(), (
        unborn_result.stdout
    )
    assert "NO-BASE:" not in unborn_result.stdout, unborn_result.stdout

    root_repo = _init_repo(tmp_path / "root-item")
    root_report = root_repo / "plans" / "j" / "reports" / "item-1-1.md"
    root_report.parent.mkdir(parents=True)
    root_report.write_text("1\n", encoding="utf-8")
    _run_git(root_repo, "add", "--", "plans/j/reports/item-1-1.md")
    _run_git(root_repo, "commit", "-q", "--amend", "--no-edit")
    root_result = _run_script(root_repo, "j")
    assert (root_result.returncode, root_result.stdout[: len("ERROR:")]) == (
        2,
        "ERROR:",
    ), root_result.stdout + root_result.stderr


def test_no_item_report_exits_1(tmp_path: Path) -> None:
    """No committed ``item-*`` report gives ``NO-BASE:``, never ``BASE:``.

    The repo holds job ``j``'s own planning reports (``explore-x.md``,
    ``outline-review.md``, neither matching ``item-*``), a committed
    ``item-*`` report for job ``jj`` (``plans/jj/reports/item-1-1.md``), and
    an **uncommitted** ``plans/j/reports/item-1-1.md`` sitting on disk. D-88
    keys on committed history scoped to this job: a derivation that ignores
    the job or prefix-matches it (``plans/j*``) finds ``jj``'s report, and
    one matching any committed report regardless of the ``item-*`` name
    finds ``explore-x.md``, so each prints a ``BASE:``; one that takes the
    on-disk file as a run in progress has no history to derive from and does
    not print ``NO-BASE:``.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "other job item", {"plans/jj/reports/item-1-1.md": "o\n"})
    _commit(
        repo,
        "j planning",
        {
            "plans/j/reports/explore-x.md": "x\n",
            "plans/j/reports/outline-review.md": "r\n",
        },
    )
    uncommitted = repo / "plans" / "j" / "reports" / "item-1-1.md"
    uncommitted.parent.mkdir(parents=True, exist_ok=True)
    uncommitted.write_text("uncommitted\n", encoding="utf-8")

    result = _run_script(repo, "j")
    assert (result.returncode, result.stdout[: len("NO-BASE:")]) == (
        1,
        "NO-BASE:",
    ), result.stdout + result.stderr
    assert not any(line.startswith("BASE: ") for line in result.stdout.splitlines()), (
        result.stdout
    )


def test_unsafe_job_name_is_a_usage_error(tmp_path: Path) -> None:
    r"""A job name that is not one plain directory under ``plans/`` exits 2.

    The job lands in a ``:(glob)`` pathspec, where ``*``, ``?``, ``[`` and
    ``\`` are glob syntax, so ``j*`` or ``[j]j`` would match job ``jj``'s
    committed item report and print that job's base. ``/``, ``.`` and
    ``..`` would leave ``plans/``. The repo holds ``jj``'s report, so a
    script that passes a glob name through prints a ``BASE:`` from another
    job rather than failing. Every name must exit 2 with ``ERROR:``.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "jj item", {"plans/jj/reports/item-1-1.md": "o\n", "a.txt": "a\n"})
    for job in ("j*", "j?", "[j]j", "j\\", "", ".", "..", "jj/sub"):
        result = _run_script(repo, job)
        assert (result.returncode, result.stdout[: len("ERROR:")]) == (
            2,
            "ERROR:",
        ), f"{job!r}: {result.stdout}{result.stderr}"


@pytest.mark.parametrize(
    ("exempt_paths", "inherited"),
    [
        pytest.param(None, None, id="absent"),
        pytest.param("# defines nothing\n", None, id="defines-nothing"),
        pytest.param("# defines nothing\n", ".*", id="defines-nothing-inherited"),
    ],
)
def test_unloadable_exempt_paths_is_an_error_not_no_base(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    exempt_paths: str | None,
    inherited: str | None,
) -> None:
    """An ``exempt-paths.sh`` that cannot supply the alternation exits 2.

    The script under test is copied into ``tmp_path/scripts`` beside a
    doctored ``exempt-paths.sh``: absent, or present and defining nothing.
    Each repo holds a committed item report, so a script that carried on
    would find a base. The load guard must turn either case into
    ``ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh`` with
    exit 2. A bare ``source`` fails differently: the missing file, or the
    unbound variable under ``set -u``, exits 1, which is ``NO-BASE:``'s
    code, and no ``NO-BASE:`` line is printed either.

    ``defines-nothing-inherited`` runs the script with
    ``EXEMPT_PATHS_ALTERNATION=.*`` in its environment. A guard that tests
    the variable without clearing it first passes on the inherited value,
    drops every path as exempt, and exits 0 with ``BASE:`` alone.
    """
    if inherited is None:
        monkeypatch.delenv("EXEMPT_PATHS_ALTERNATION", raising=False)
    else:
        monkeypatch.setenv("EXEMPT_PATHS_ALTERNATION", inherited)
    repo = _init_repo(tmp_path)
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(SCRIPT, scripts / SCRIPT.name)
    if exempt_paths is not None:
        (scripts / "exempt-paths.sh").write_text(exempt_paths, encoding="utf-8")

    result = _run_script(repo, "j", script=scripts / SCRIPT.name)
    assert result.returncode == 2, result.stdout + result.stderr
    assert (
        "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
        in result.stdout.splitlines()
    ), result.stdout
    assert "NO-BASE:" not in result.stdout, result.stdout


def test_late_diff_failure_prints_error_alone(tmp_path: Path) -> None:
    """A diff failing once the base is known prints ``ERROR:`` alone.

    The run commit adds ``item-1-1.md`` and ``a.txt`` and changes ``b.txt``.
    A ``git`` shim runs the real git and, when its first argument is
    ``diff``, exits 128 after the real command's output, so the failure
    comes after the base is known and the diff has produced paths. D-90
    keeps stdout to ``ERROR:`` alone on exit 2: a script that has printed
    ``BASE:`` or a path by then leaves them above the error.
    """
    real_git = shutil.which("git")
    assert real_git is not None, "git not found on PATH"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = bin_dir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        f'{shlex.quote(real_git)} "$@"\n'
        "status=$?\n"
        '[ "$1" = diff ] && exit 128\n'
        "exit $status\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)
    repo = _init_repo(tmp_path)
    _commit(
        repo,
        "item 1.1",
        {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n", "b.txt": "changed\n"},
    )

    result = _run_script(repo, "j", path_prepend=bin_dir)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stdout.splitlines() == ["ERROR: git diff failed"], result.stdout
