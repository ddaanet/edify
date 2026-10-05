"""Contract tests for ``plugin/bin/triage-feedback.sh``.

The script measures the set the review gate reviewed (D-90): it runs
``changed-files.sh <job>``, so the base comes from report history (D-88) and
the call takes the job name alone. Fixtures and the subprocess wrappers live in
``tests/triage_feedback_helpers.py``.
"""

import shutil
from pathlib import Path

from tests.triage_feedback_helpers import (
    JOB,
    _commit,
    _commit_item_report,
    _def_edits_pending,
    _init_repo,
    _run_git,
    _run_triage,
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
    _init_repo(repo)
    classification = repo / "plans" / JOB / "classification.md"
    _commit(
        repo,
        "planning",
        {
            f"plans/{JOB}/reports/runbook-review.md": "ok\n",
            f"plans/{JOB}/reports/explore-x.md": "notes\n",
            f"plans/{JOB}/classification.md": "- **Classification:** Simple\n",
        },
    )
    _commit_item_report(repo, {"notes.txt": "plain text\n"})
    _commit(
        repo,
        "run: item 1.12",
        {
            f"plans/{JOB}/reports/item-1-12.md": "item report\n",
            f"plans/{JOB}/reports/runbook-review.md": "ok, revisited\n",
            f"plans/{JOB}/reports/explore/notes.md": "notes\n",
        },
    )
    _commit(repo, "run: review", {f"plans/{JOB}/reports/review-code.md": "ok\n"})

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


def test_uncommitted_definition_is_not_behavioral(tmp_path: Path) -> None:
    """Behavioral code reads the committed diff from the base to HEAD only.

    Both repos come from ``_def_edits_pending``: the run commit tracks
    ``module.py`` and ``other.py`` holding no definition, then each file
    picks up a ``def`` line, ``module.py`` unstaged and ``other.py`` staged
    (D-90). The negative leaves both edits uncommitted, so it reads ``no``
    only once neither the working tree nor the index reaches the diff.

    The positive differs only in committing those same edits, then a
    plain-text commit on top, and must read ``yes``: an implementation whose
    regex misses the ``def`` lines, that diffs only the uncommitted state, or
    that diffs only the last commit reads ``no`` there. It runs second so the
    negative's result stays its own.
    """
    repo = tmp_path / "repo"
    _def_edits_pending(repo)

    lines = _triage_lines(JOB, repo)
    assert "- Behavioral code: no" in lines, "\n".join(lines)

    positive_repo = tmp_path / "positive"
    _def_edits_pending(positive_repo)
    _run_git(positive_repo, "commit", "-q", "-a", "-m", "commit defs")
    _commit(positive_repo, "add notes", {"notes.txt": "plain text\n"})

    lines = _triage_lines(JOB, positive_repo)
    assert "- Behavioral code: yes" in lines, "\n".join(lines)


def test_forced_color_does_not_hide_definitions(tmp_path: Path) -> None:
    r"""A repo-local ``color.ui always`` still finds a committed ``def``.

    Forced colour wraps each added line in escape codes, so the patterns'
    ``^\+`` anchor matches nothing and the committed definition reads
    ``no``. The script's ``--no-color`` keeps the patch plain: ``yes``.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _run_git(repo, "config", "color.ui", "always")
    _commit_item_report(repo, {"module.py": "def foo():\n    pass\n"})

    lines = _triage_lines(JOB, repo)
    assert "- Behavioral code: yes" in lines, "\n".join(lines)


def test_failing_diff_is_an_error_not_no(tmp_path: Path) -> None:
    """A committed diff git cannot produce fails the script, never reads ``no``.

    The committed ``module.py`` blob is deleted from the object store. The
    list of changed paths reads trees only and still succeeds; the patch
    needs the blob and fails. A match fed from that failure inside an
    ``if`` would report ``Behavioral code: no`` and exit 0. The failure exits
    2 with an ``ERROR:`` line on stdout, the interface for a git failure.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit_item_report(repo, {"module.py": "def foo():\n    pass\n"})
    blob = _run_git(repo, "rev-parse", "HEAD:module.py").strip()
    (repo / ".git" / "objects" / blob[:2] / blob[2:]).unlink()

    result = _run_triage(JOB, repo)
    assert result.returncode == 2, result.stdout + result.stderr
    assert f"unable to read {blob}" in result.stderr, result.stderr
    assert any(line.startswith("ERROR: ") for line in result.stdout.splitlines()), (
        result.stdout
    )
    assert "- Behavioral code:" not in result.stdout, result.stdout


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


def test_behavioral_code_reads_the_lists_paths_only(tmp_path: Path) -> None:
    """Behavioral code diffs only the paths in the gate's list (D-90).

    The first run commits ``item-1-1.md``, whose prose has a line starting
    ``class with an explicit whitelist``, and ``inbox/x.md`` holding a
    ``def``. Both fall outside the list, which is empty: ``no``, and a diff
    over the whole ``<base> HEAD`` range would read ``yes`` from either file.
    A further commit adds ``a.py`` holding a ``def``, and the same repo reads
    ``yes``.

    An empty list runs no diff, because an empty pathspec diffs everything. A
    second repo keeps the list non-empty, ``notes.txt`` alone, beside the same
    exempt ``def`` and ``class`` report line: an implementation that
    special-cases only the empty list and then diffs the range, or the list
    plus the job's reports, reads ``yes`` there, and must read ``no``.

    The pathspecs are literal. A third repo's list is a file named ``*.md``,
    holding no definition; as a glob pathspec it matches ``inbox/x.md`` and
    reads its ``def``.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit(
        repo,
        "run: item 1.1",
        {
            f"plans/{JOB}/reports/item-1-1.md": (
                "item report\nclass with an explicit whitelist\n"
            ),
            "inbox/x.md": "def foo():\n",
        },
    )

    lines = _triage_lines(JOB, repo)
    assert "- Files changed: 0" in lines, "\n".join(lines)
    assert "- Behavioral code: no" in lines, "\n".join(lines)

    _commit(repo, "add a", {"a.py": "def foo():\n    pass\n"})
    lines = _triage_lines(JOB, repo)
    assert "- Behavioral code: yes" in lines, "\n".join(lines)

    non_empty = tmp_path / "non-empty"
    _init_repo(non_empty)
    _commit_item_report(
        non_empty,
        {
            f"plans/{JOB}/reports/item-1-1.md": (
                "item report\nclass with an explicit whitelist\n"
            ),
            "notes.txt": "plain\n",
            "inbox/x.md": "def foo():\n",
        },
    )
    lines = _triage_lines(JOB, non_empty)
    assert "- Files changed: 1" in lines, "\n".join(lines)
    assert "- Behavioral code: no" in lines, "\n".join(lines)

    glob_name = tmp_path / "glob-name"
    _init_repo(glob_name)
    _commit_item_report(glob_name, {"*.md": "plain\n", "inbox/x.md": "def foo():\n"})
    lines = _triage_lines(JOB, glob_name)
    assert "- Files changed: 1" in lines, "\n".join(lines)
    assert "- Behavioral code: no" in lines, "\n".join(lines)
