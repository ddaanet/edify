"""Run-location tests for ``plugin/bin/triage-feedback.sh``.

This module holds the run-location tests: a run from a subdirectory and a
run under an exported ``CDPATH`` both measure from the repository root (D-90).
It was split from ``tests/test_triage_feedback.py`` to keep each module under
its line cap. Fixtures and the subprocess wrappers live in
``tests/triage_feedback_helpers.py``.
"""

from pathlib import Path

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _init_repo,
    _run_triage_relative,
    _verdict,
)


def test_subdirectory_run_measures_the_repository_root(tmp_path: Path) -> None:
    """A run from a subdirectory measures the repository root (D-90).

    A committed ``sub/keep.txt`` gives the subdirectory a place in the tree.
    ``classification.md`` reads ``Simple``; the run commit adds the item
    report, the slice report ``item-1-1-s1-red.md`` and ``a.py`` holding a
    ``def``. The script is run by its path relative to ``repo/sub`` with that
    as CWD, through a ``plugin`` symlink beside ``repo``, so it sees a
    ``BASH_SOURCE`` of ``../../plugin/bin/...``: resolved after a change to
    the root it names a missing file and the run exits 2. Measured from the
    root it reads 1 file, 1 report and behavioural code: ``underclassified``,
    one log row at the root, none under ``sub``. Measured from ``sub`` every
    root-relative path misses: 0 reports, no behavioural code and
    ``no-classification``. The evidence assertions come first so a
    measurement from the wrong directory fails on what it read.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "planning",
        {
            "sub/keep.txt": "kept\n",
            f"plans/{JOB}/classification.md": "- **Classification:** Simple\n",
        },
    )
    _commit_item_report(
        repo,
        {
            f"plans/{JOB}/reports/item-1-1-s1-red.md": "ok\n",
            "a.py": "def foo():\n    pass\n",
        },
    )

    result = _run_triage_relative(JOB, repo / "sub", tmp_path)
    lines = result.stdout.splitlines()
    output = result.stdout + result.stderr
    assert "- Files changed: 1" in lines, output
    assert "- Reports: 1" in lines, output
    assert "- Behavioral code: yes" in lines, output
    assert _verdict(lines) == "underclassified", output
    assert result.returncode == 0, output
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    assert log.is_file(), output
    rows = log.read_text(encoding="utf-8").splitlines()[2:]
    assert len(rows) == 1, "\n".join(rows)
    assert not (repo / "sub" / "plans").exists()


def test_cdpath_does_not_move_the_script_dir(tmp_path: Path) -> None:
    """An exported ``CDPATH`` leaves the script directory where it is.

    ``CDPATH`` applies to a ``cd`` operand not starting with ``/``, ``.`` or
    ``..``. The script is run as ``plugin/bin/triage-feedback.sh`` through a
    ``plugin`` symlink at the repo root, with CWD the root and ``CDPATH``
    naming a decoy outside the repo that holds an empty ``plugin/bin``.
    Honoured, ``CDPATH`` sends ``cd plugin/bin`` to the decoy and prints the
    destination into the capture; either sends ``changed-files.sh`` to a path
    that does not exist and exits 2. A decoy rather than ``.``, which names
    the same directory, so a ``cd`` that only silences the print still fails.
    The run reads what the subdirectory run does: 1 file, 1 report,
    behavioural code, ``underclassified`` and one log row.
    """
    decoy = tmp_path / "decoy"
    (decoy / "plugin" / "bin").mkdir(parents=True)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "planning",
        {f"plans/{JOB}/classification.md": "- **Classification:** Simple\n"},
    )
    _commit_item_report(
        repo,
        {
            f"plans/{JOB}/reports/item-1-1-s1-red.md": "ok\n",
            "a.py": "def foo():\n    pass\n",
        },
    )

    result = _run_triage_relative(JOB, repo, repo, env_extra={"CDPATH": str(decoy)})
    lines = result.stdout.splitlines()
    output = result.stdout + result.stderr
    assert "- Files changed: 1" in lines, output
    assert "- Reports: 1" in lines, output
    assert "- Behavioral code: yes" in lines, output
    assert _verdict(lines) == "underclassified", output
    assert result.returncode == 0, output
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    assert len(log.read_text(encoding="utf-8").splitlines()[2:]) == 1, output
