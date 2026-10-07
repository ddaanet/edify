"""Contract tests for the log ``plugin/bin/triage-feedback.sh`` appends to.

The log, ``plans/reports/triage-feedback-log.md``, holds one row per
evidence: the append is skipped when the log already holds a row equal to the
new one in every column but the date, and a re-run on new evidence still
appends. The run itself is not skipped: it still prints its evidence and
verdict.

Split from ``tests/test_triage_feedback.py``, which keeps the evidence and
verdict tests, to keep each module under its line cap. See
``tests/triage_feedback_helpers.py`` for the shared fixtures.
"""

import os
from pathlib import Path

import pytest

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _commit_reports_fixture,
    _init_repo,
    _run_triage,
    _triage_lines,
    _verdict,
)

SEEDED_DATE = "2000-01-01"


def test_rerun_appends_no_duplicate_row(tmp_path: Path) -> None:
    """A re-run on the same evidence appends no row; new evidence appends one.

    The run is the reports fixture: ``match``, one changed file, so it logs
    one row under the header. The same run again leaves exactly one row.

    A decoy row for job ``other-j``, equal in every other column, holds the
    new row's text from the job name on, so a log holding only the decoy
    still gains a row: the job column is compared whole. The log re-seeded
    with the run's row under another date, not today's UTC date, and the
    decoy after it gains none and keeps its header and rows unchanged, so
    the comparison ignores the date column, does not match a row only by its
    date, and reads every row rather than the last.

    A further run commit adds ``item-1-2.md`` and ``c.txt``, which moves
    Files changed to 2: the next run appends a row.
    """
    repo = tmp_path / "repo"
    _commit_reports_fixture(repo)
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    undated = f"{JOB} | Simple | 1 | 0 | no | match |"

    _triage_lines(JOB, repo)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3, "\n".join(lines)
    header, first_row = lines[:2], lines[2]
    assert _undated(first_row) == undated, first_row

    _triage_lines(JOB, repo)
    rows = log.read_text(encoding="utf-8").splitlines()[2:]
    assert rows == [first_row], "\n".join(rows)

    decoy_row = f"| {SEEDED_DATE} | other-{undated}"
    log.write_text("\n".join([*header, decoy_row]) + "\n", encoding="utf-8")
    _triage_lines(JOB, repo)
    rows = log.read_text(encoding="utf-8").splitlines()[2:]
    assert len(rows) == 2, "\n".join(rows)
    assert rows[0] == decoy_row, "\n".join(rows)
    assert _undated(rows[1]) == undated, "\n".join(rows)

    seeded_row = f"| {SEEDED_DATE} | {undated}"
    seeded = [*header, seeded_row, decoy_row]
    log.write_text("\n".join(seeded) + "\n", encoding="utf-8")
    _triage_lines(JOB, repo)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert lines == seeded, "\n".join(lines)

    _commit(
        repo,
        "run: item 1.2",
        {f"plans/{JOB}/reports/item-1-2.md": "item report\n", "c.txt": "c\n"},
    )
    _triage_lines(JOB, repo)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5, "\n".join(lines)
    assert lines[:4] == seeded, "\n".join(lines)
    assert _undated(lines[4]) == f"{JOB} | Simple | 2 | 0 | no | match |", lines[4]


def test_unterminated_last_row_is_compared_and_kept_whole(tmp_path: Path) -> None:
    """An unterminated last row is compared, and an append leaves it whole.

    The log seeded with the run's row under another date and no trailing
    newline is left byte for byte unchanged: a ``read`` loop that drops an
    unterminated last line appends a duplicate glued onto it. Seeded instead
    with a decoy row for job ``other-j`` and no trailing newline, the run
    appends its row on a line of its own and the decoy keeps its text.
    """
    repo = tmp_path / "repo"
    _commit_reports_fixture(repo)
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    header = [
        "| Date | Job | Predicted | Files Changed | Reports | Behavioral Code"
        " | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    undated = f"{JOB} | Simple | 1 | 0 | no | match |"
    log.parent.mkdir(parents=True)

    seeded = "\n".join([*header, f"| {SEEDED_DATE} | {undated}"])
    log.write_text(seeded, encoding="utf-8")
    _triage_lines(JOB, repo)
    assert log.read_text(encoding="utf-8") == seeded

    decoy_row = f"| {SEEDED_DATE} | other-{undated}"
    log.write_text("\n".join([*header, decoy_row]), encoding="utf-8")
    _triage_lines(JOB, repo)
    lines = log.read_text(encoding="utf-8").splitlines()
    assert lines[:3] == [*header, decoy_row], "\n".join(lines)
    assert len(lines) == 4, "\n".join(lines)
    assert _undated(lines[3]) == undated, lines[3]


def test_unreadable_log_is_an_error_and_appends_nothing(tmp_path: Path) -> None:
    """A log the script cannot read stops it with exit 2, never a blind append.

    The log is write-only, so an append would succeed where the duplicate
    check cannot run: the script must report ``ERROR:`` rather than append.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores file permissions; chmod 0200 has no effect")

    repo = tmp_path / "repo"
    _commit_reports_fixture(repo)
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    _triage_lines(JOB, repo)
    logged = log.read_text(encoding="utf-8")

    log.chmod(0o200)
    try:
        result = _run_triage(JOB, repo)
    finally:
        log.chmod(0o644)

    assert result.returncode == 2, result.stdout + result.stderr
    assert f"ERROR: cannot read {log.relative_to(repo)}" in result.stdout, result.stdout
    assert log.read_text(encoding="utf-8") == logged


@pytest.mark.parametrize("unwritable", ["header", "row", "directory"])
def test_unwritable_log_is_an_error_not_a_usage_exit(
    tmp_path: Path, unwritable: str
) -> None:
    """A log the script cannot write exits 2 with ``ERROR:``, never exit 1.

    Exit 1 is the usage error's code. Under ``set -e`` a failed redirection
    exits 1, so an unguarded write reads as a usage error. ``header``: the
    log is absent and ``plans/reports/`` is read-only, so the header write
    fails. ``row``: the log holds the header alone and is read-only, so the
    duplicate check reads it and the row append fails. ``directory``:
    ``plans/`` is read-only and holds no ``reports/``, so ``mkdir -p`` fails.
    The error follows the verdict once, as the run's last stdout line. Past
    an unguarded ``mkdir`` the header write fails on the same path with the
    same line, so stderr is pinned too: ``mkdir``'s diagnostic, naming
    ``plans/reports``, and no shell error naming the log, shows the run
    stopped at the directory. Only the path is asserted: the wording is
    localised, and BSD ``mkdir -p`` naming the whole operand is unverified on
    macOS.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores file permissions; chmod has no effect")

    repo = tmp_path / "repo"
    _commit_reports_fixture(repo)
    log_dir = repo / "plans" / "reports"
    log = log_dir / "triage-feedback-log.md"
    if unwritable == "directory":
        log_dir.parent.chmod(0o555)
    elif unwritable == "row":
        log_dir.mkdir(parents=True)
        log.write_text(
            "| Date | Job | Predicted | Files Changed | Reports | Behavioral Code"
            " | Verdict |\n|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
        log.chmod(0o400)
    else:
        log_dir.mkdir(parents=True)
        log_dir.chmod(0o500)
    try:
        result = _run_triage(JOB, repo)
    finally:
        log_dir.parent.chmod(0o755)
        if log_dir.exists():
            log_dir.chmod(0o755)
        if log.exists():
            log.chmod(0o644)

    error = f"ERROR: cannot write {log.relative_to(repo)}"
    assert error in result.stdout, result.stdout + result.stderr
    if unwritable == "directory":
        tail = result.stdout.splitlines()[-3:]
        assert tail == ["## Verdict", "match", error], result.stdout
        assert str(log_dir.relative_to(repo)) in result.stderr, result.stderr
        assert log.name not in result.stderr, result.stderr
    assert result.returncode == 2, result.stdout + result.stderr


def test_rerun_after_the_closing_commit_appends_no_row(tmp_path: Path) -> None:
    """A re-invoked finished job measures the same evidence and logs no row.

    D-90: the ``<job> Finish`` closing commit commits the triage log and, on a
    TDD run, ``tdd-audit.md``, and a re-invocation runs triage again. The run
    is Complex: one run commit (``item-1-1.md`` and ``a.txt``) and a
    review-gate commit (``review-code.md``) read 1 file and 0 reports,
    ``overclassified``, and log one row. The closing commit then adds the log
    as triage wrote it and ``tdd-audit.md``. The second run must read the
    same ``## Evidence`` and ``## Verdict`` and leave the one row. A list that
    carries ``plans/reports/triage-feedback-log.md`` reads 2 files and a
    count that includes ``tdd-audit.md`` reads 1 report: the evidence differs,
    the verdict flips to ``match`` and a second row lands.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "planning",
        {f"plans/{JOB}/classification.md": "- **Classification:** Complex\n"},
    )
    _commit_item_report(repo, {"a.txt": "a\n"})
    _commit(repo, "run: review", {f"plans/{JOB}/reports/review-code.md": "ok\n"})
    log = repo / "plans" / "reports" / "triage-feedback-log.md"

    first = _triage_lines(JOB, repo)
    assert "- Files changed: 1" in first, "\n".join(first)
    assert "- Reports: 0" in first, "\n".join(first)
    assert _verdict(first) == "overclassified", "\n".join(first)
    first_lines = log.read_text(encoding="utf-8").splitlines()
    assert len(first_lines) == 3, "\n".join(first_lines)

    _commit(
        repo,
        f"{JOB} Finish",
        {
            "plans/reports/triage-feedback-log.md": log.read_text(encoding="utf-8"),
            f"plans/{JOB}/reports/tdd-audit.md": "audited\n",
        },
    )
    second = _triage_lines(JOB, repo)

    assert (
        second[: second.index("## Verdict") + 2]
        == first[: first.index("## Verdict") + 2]
    ), "\n".join(second)
    rows = log.read_text(encoding="utf-8").splitlines()
    assert rows == first_lines, "\n".join(rows)


def _undated(row: str) -> str:
    """Return ``row`` from its second column on, the date column dropped."""
    return row[2:].partition(" | ")[2]
