"""Contract tests for the log ``plugin/bin/triage-feedback.sh`` appends to.

The log, ``plans/reports/triage-feedback-log.md``, holds one row per
evidence: a run is skipped when the log already holds a row equal to the new
one in every column but the date, and a re-run on new evidence still appends.

Split from ``tests/test_triage_feedback.py``, which keeps the evidence and
verdict tests, to keep each module under its line cap. See
``tests/triage_feedback_helpers.py`` for the shared fixtures.
"""

from pathlib import Path

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_reports_fixture,
    _triage_lines,
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


def _undated(row: str) -> str:
    """Return ``row`` from its second column on, the date column dropped."""
    return row[2:].partition(" | ")[2]
