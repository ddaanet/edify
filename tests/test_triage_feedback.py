"""Contract tests for ``plugin/bin/triage-feedback.sh``.

The script measures the set the review gate reviewed (D-90): it runs
``changed-files.sh <job>``, so the base comes from report history (D-88) and
the call takes the job name alone. Fixtures and the subprocess wrappers live in
``tests/triage_feedback_helpers.py``.
"""

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
