"""Contract tests for ``plugin/bin/triage-feedback.sh``.

The script measures the set the review gate reviewed (D-90): it runs
``changed-files.sh <job>``, so the base comes from report history (D-88) and
the call takes the job name alone. Fixtures and the subprocess wrappers live in
``tests/triage_feedback_helpers.py``.

This module holds the files-changed, reports and classification tests. It was
split to keep each module under its line cap, and three sibling modules hold
the rest. ``tests/test_triage_feedback_behavioral.py`` holds the
behavioural-code tests. ``tests/test_triage_feedback_log.py`` holds the log
tests: the one-row-per-evidence append and its idempotence.
``tests/test_triage_feedback_failures.py`` holds the failure arms of the
entry, the reports count and the classification parse.
"""

from pathlib import Path

import pytest

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _commit_reports_fixture,
    _init_repo,
    _run_git,
    _run_triage,
    _run_triage_relative,
    _triage_lines,
    _verdict,
)


def test_files_changed_is_the_review_gates_list(tmp_path: Path) -> None:
    """Files changed counts what ``changed-files.sh`` lists, not the raw diff.

    The pre-run commit adds an outline review, outside the run. Run commit 1
    adds the item report, ``a.txt`` and two exempt paths, ``inbox/x.md`` and
    ``.claude/handoff-task.md``; run commit 2 adds ``item-1-2.md`` and
    ``b.txt``. The raw ``<base> HEAD`` diff lists 6 paths; the gate's list
    holds ``a.txt`` and ``b.txt``: 2. The stdout assertion precedes the
    exit-code one so a usage exit fails on the missing evidence.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(repo, "outline review", {f"plans/{JOB}/reports/outline-review.md": "ok\n"})
    _commit_item_report(
        repo,
        {
            "a.txt": "a\n",
            "inbox/x.md": "note\n",
            ".claude/handoff-task.md": "task\n",
        },
    )
    _commit(
        repo,
        "run: item 1.2",
        {f"plans/{JOB}/reports/item-1-2.md": "item report\n", "b.txt": "b\n"},
    )

    result = _run_triage(JOB, repo)
    assert "- Files changed: 2" in result.stdout.splitlines(), (
        result.stdout + result.stderr
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_reports_exclude_the_per_item_report(tmp_path: Path) -> None:
    """Reports counts what the run committed beyond the item report (D-90).

    Planning reports, ``runbook-review.md`` and ``explore-x.md``, are
    committed before the base and fall outside the ``<base> HEAD`` range; an
    on-disk count reads them. One run commit adds ``item-1-1.md`` and a plain
    ``notes.txt``. Another adds ``item-1-12.md``, which a single-digit
    ``item-[0-9]-[0-9].md`` would count, revises ``runbook-review.md``, which
    a count of every touched path would read, and adds
    ``explore/notes.md``, below the reports directory, which a pathspec
    without ``:(glob)`` would match. A third adds the review-gate report
    ``review-code.md``. None counts, so a Simple run reads ``match`` (0
    reports, no definitions) and a Complex one, at one changed file,
    ``overclassified``. A later commit adds the slice report
    ``item-1-1-s1-code-review.md``, which is not the per-item
    ``item-<N>-<M>.md`` and counts: 1 report, so Simple reads
    ``underclassified``.

    ``classification.md`` is committed with the planning reports, as a plan
    leaves it, and the Complex and Simple relabels are on-disk edits only:
    triage reads the file from disk, and an uncommitted edit leaves the
    ``<base> HEAD`` range alone.
    """
    repo = tmp_path / "repo"
    _commit_reports_fixture(repo)
    classification = repo / "plans" / JOB / "classification.md"

    lines = _triage_lines(JOB, repo)
    assert "- Reports: 0" in lines, "\n".join(lines)
    assert "- Behavioral code: no" in lines, "\n".join(lines)
    assert _verdict(lines) == "match", "\n".join(lines)

    classification.write_text("- **Classification:** Complex\n", encoding="utf-8")
    lines = _triage_lines(JOB, repo)
    assert _verdict(lines) == "overclassified", "\n".join(lines)

    classification.write_text("- **Classification:** Simple\n", encoding="utf-8")
    _commit(
        repo,
        "run: slice review",
        {f"plans/{JOB}/reports/item-1-1-s1-code-review.md": "ok\n"},
    )
    lines = _triage_lines(JOB, repo)
    assert "- Reports: 1" in lines, "\n".join(lines)
    assert _verdict(lines) == "underclassified", "\n".join(lines)


def test_reports_exclude_the_tdd_audit_report(tmp_path: Path) -> None:
    """The audit's ``tdd-audit.md`` is review record, not a counted report.

    D-90: a finished TDD job's closing commit adds ``tdd-audit.md`` beside the
    review reports, so a re-invoked job would count it and measure different
    evidence. The run adds ``item-1-1.md``, a plain ``notes.txt`` and
    ``tdd-audit.md``: 0 reports, so a Simple run reads ``match``. An
    implementation excluding only ``review.md``, ``review-*.md`` and
    ``final-review.md`` counts it and reads ``underclassified``.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "planning",
        {f"plans/{JOB}/classification.md": "- **Classification:** Simple\n"},
    )
    _commit_item_report(
        repo,
        {"notes.txt": "plain text\n", f"plans/{JOB}/reports/tdd-audit.md": "ok\n"},
    )

    lines = _triage_lines(JOB, repo)
    assert "- Reports: 0" in lines, "\n".join(lines)
    assert _verdict(lines) == "match", "\n".join(lines)


def test_reports_read_names_byte_exact(tmp_path: Path) -> None:
    """Report names are read NUL-delimited, never as git's quoted form.

    Without ``-z``, git C-quotes a name holding ``"`` whatever
    ``core.quotePath`` says, so the review-gate report ``review-"x".md``
    reads as a quoted name ending ``.md"``, escapes the ``review-*.md``
    exclusion and counts. ``explore-é.md`` counts either way: it is there so
    the expected 1 comes from a counted report, not from an empty read.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit_item_report(
        repo,
        {
            f'plans/{JOB}/reports/review-"x".md': "ok\n",
            f"plans/{JOB}/reports/explore-é.md": "notes\n",
        },
    )

    lines = _triage_lines(JOB, repo)
    assert "- Reports: 1" in lines, "\n".join(lines)


def test_files_changed_counts_committed_changes_only(tmp_path: Path) -> None:
    """Files changed counts the committed diff from the base to HEAD only.

    Every file is tracked before the run, so each later edit is a diff:
    ``git diff`` never lists an untracked path, which would drop the
    uncommitted files for the wrong reason. Two run commits follow --
    ``a.txt`` with the item report, then ``d.txt`` and ``e.txt`` -- and
    ``b.txt`` is left modified unstaged and ``c.txt`` modified and staged
    (D-90). The answer, 3, differs from every neighbouring range: the last
    commit alone reads 2, the index against HEAD 1, the working tree against
    HEAD 2, the base against the index 4 and against the working tree 5, and
    the unfiltered committed diff, item report included, 4.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    names = ("a.txt", "b.txt", "c.txt", "d.txt", "e.txt")
    _commit(repo, "track files", dict.fromkeys(names, "original\n"))

    _commit_item_report(repo, {"a.txt": "changed\n"})
    _commit(repo, "change d and e", {"d.txt": "changed\n", "e.txt": "changed\n"})

    (repo / "b.txt").write_text("modified, uncommitted\n", encoding="utf-8")
    (repo / "c.txt").write_text("staged, uncommitted\n", encoding="utf-8")
    _run_git(repo, "add", "c.txt")

    lines = _triage_lines(JOB, repo)
    assert "- Files changed: 3" in lines, "\n".join(lines)


def test_unrecognised_label_is_no_classification(tmp_path: Path) -> None:
    """An unrecognised first ``Classification:`` value is no classification.

    Only an exact ``Simple``, ``Moderate``, ``Complex`` or ``Defect`` is a
    class. The label ``Simple / Moderate agentic-prose (one route)`` starts
    with ``Simple``, and the run commits a ``def``, so a Simple reading would
    give ``underclassified``. The run reads ``no-classification`` instead,
    names the label once, verbatim, on stdout, exits 0 and appends no row. A
    label that fell through to ``match`` would log one. A later, exact
    ``Simple`` line pins the first value: reading the last or any recognised
    one gives ``underclassified``.

    The same fixture relabelled, on disk, to an exact ``Moderate`` and then
    ``Defect`` reaches a verdict, prints no unrecognised line and logs one row
    each, so recognising only ``Simple`` and ``Complex`` reds too.
    """
    label = "Simple / Moderate agentic-prose (one route)"
    repo = tmp_path / "repo"
    _init_repo(repo)
    classification = repo / "plans" / JOB / "classification.md"
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    _commit(
        repo,
        "planning",
        {
            f"plans/{JOB}/classification.md": (
                f"- **Classification:** {label}\n- **Classification:** Simple\n"
            )
        },
    )
    _commit_item_report(repo, {"a.py": "def foo():\n    pass\n"})

    result = _run_triage(JOB, repo)
    lines = result.stdout.splitlines()
    assert _verdict(lines) == "no-classification", result.stdout + result.stderr
    assert lines.count(f"unrecognised classification: {label}") == 1, result.stdout
    assert result.returncode == 0, result.stdout + result.stderr
    assert not log.exists()

    for logged, recognised in enumerate(("Moderate", "Defect"), start=1):
        classification.write_text(
            f"- **Classification:** {recognised}\n", encoding="utf-8"
        )
        lines = _triage_lines(JOB, repo)
        assert _verdict(lines) not in ("", "no-classification"), "\n".join(lines)
        assert not any(
            line.startswith("unrecognised classification:") for line in lines
        ), "\n".join(lines)
        rows = log.read_text(encoding="utf-8").splitlines()[2:]
        assert len(rows) == logged, "\n".join(rows)
        assert f"| {JOB} | {recognised} |" in rows[-1], rows[-1]


@pytest.mark.parametrize(
    "case", ["head-file", "apostrophe-label", "colon-label", "no-label-line"]
)
def test_odd_names_and_labels_do_not_derail_triage(tmp_path: Path, case: str) -> None:
    """A file named ``HEAD`` and odd classification lines leave triage running.

    ``head-file``: the run commits a tracked file named ``HEAD``, which git
    refuses as ambiguous with the revision unless ``--`` precedes the
    pathspecs: exit 0, counted in Files changed.

    ``apostrophe-label``: ``Moderate (my human partner's call)`` is not a
    class. ``xargs`` reads the apostrophe as an unmatched quote; the parse
    must read the value literally: exit 0, no ``xargs`` complaint on stderr,
    and the unrecognised-label line carrying the label verbatim. Whitespace
    on both sides of the value pins the trim at each end, so a parse that
    trims one side only, or ``xargs -0``, which trims neither, reds too.

    ``colon-label``: ``Moderate (note: see *KD-3*)``, on a bare
    ``Classification:`` line, carries a colon and asterisks of its own. Only
    the prefix is stripped, so the unrecognised-label line carries the label
    verbatim; a parse cutting at the last colon, or deleting every ``*``,
    reds.

    ``no-label-line``: a ``classification.md`` with no ``Classification:``
    line is a result, not a failure: verdict ``no-classification``, exit 0, no
    unrecognised-label line and no log row.
    """
    label = {
        "apostrophe-label": "Moderate (my human partner's call)",
        "colon-label": "Moderate (note: see *KD-3*)",
    }.get(case, "")
    text = {
        "head-file": "- **Classification:** Simple\n",
        "apostrophe-label": f"- **Classification:** {label} \t\n",
        "colon-label": f"Classification: {label}\n",
        "no-label-line": "no label here\n",
    }[case]
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(repo, "planning", {f"plans/{JOB}/classification.md": text})
    name = "HEAD" if case == "head-file" else "a.txt"
    _commit_item_report(repo, {name: "a file, not a revision\n"})

    result = _run_triage(JOB, repo)
    lines = result.stdout.splitlines()
    output = result.stdout + result.stderr
    log = repo / "plans" / "reports" / "triage-feedback-log.md"
    if case == "head-file":
        assert "- Files changed: 1" in lines, output
    elif case in ("apostrophe-label", "colon-label"):
        assert f"unrecognised classification: {label}" in lines, output
        assert "xargs" not in result.stderr, result.stderr
        assert not log.exists()
    else:
        assert _verdict(lines) == "no-classification", output
        assert not any(
            line.startswith("unrecognised classification:") for line in lines
        ), output
        assert not log.exists()
    assert result.returncode == 0, output


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
