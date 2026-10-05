"""Behavioural-code tests for ``plugin/bin/triage-feedback.sh``.

Behavioral code runs the definition patterns over the committed
``<base> HEAD`` diff, limited to the paths of the review gate's list (D-90).

Split from ``tests/test_triage_feedback.py``, which keeps the files-changed,
reports and failure tests, to keep each module under its line cap. See
``tests/triage_feedback_helpers.py`` for the shared fixtures.
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


def test_early_match_in_a_large_diff_is_not_an_error(tmp_path: Path) -> None:
    """A ``def`` atop a diff past the pipe buffer reads ``yes``, not an error.

    The captured diff is piped into a ``grep -q`` that exits at its first
    match, here the opening ``def``, with over a megabyte still unwritten, so
    the writer dies of SIGPIPE. Under ``pipefail`` the pipeline's status is
    that 141, which a form reading it rather than grep's own exit reports as
    ``ERROR: grep failed`` and exit 2. The stdout assertion precedes the
    exit-code one so the ``ERROR:`` line shows on failure.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    _commit_item_report(repo, {"a.py": "def foo():\n" + "x = 1\n" * 200_000})

    result = _run_triage(JOB, repo)
    assert "- Behavioral code: yes" in result.stdout.splitlines(), (
        result.stdout + result.stderr
    )
    assert result.returncode == 0, result.stdout + result.stderr
