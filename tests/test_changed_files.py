"""Contract tests for ``plugin/skills/build/scripts/changed-files.sh``.

KD-1 and KD-6 in ``plans/build-fixes/outline.md``: the base is the parent of
the earliest commit adding a ``plans/<job>/reports/item-*`` report, and the
changed-files list is the committed diff since that base, minus the job's own
``plans/<job>/`` record and the exempt paths ``exempt-paths.sh`` names.

The ``--phase`` tests (KD-2) are in ``tests/test_changed_files_phase.py``.
See ``tests/changed_files_helpers.py`` for the shared fixtures.
"""

from pathlib import Path

from .changed_files_helpers import _commit, _init_repo, _run_git, _run_script


def test_base_is_parent_of_first_item_report_commit(tmp_path: Path) -> None:
    """``BASE:`` names the parent of the first committed ``item-*`` report.

    History: seed (root) -> another job's item report -> ``j``'s
    ``explore-x.md`` and ``runbook.md`` -> ``item-x/notes.md`` with
    ``notes.txt`` -> P adds ``outline-review.md`` -> item 1.1 (report, new
    ``a.txt``) -> item 1.2 (report, changed ``b.txt``, revised
    ``runbook.md``) -> a report-less code-review fix to ``a.txt``. Only the
    parent of item 1.1's commit, P, is right. Each decoy commit rules out a
    wrong derivation that the bare spec history collapses onto P: the other
    job's report catches an unscoped ``plans/*/reports/item-*``;
    ``explore-x.md`` catches "first commit touching ``plans/j/reports/``"
    taken without its parent; ``item-x/notes.md`` catches a pathspec
    without ``:(glob)`` magic, whose ``*`` crosses ``/``, which would take
    that commit's parent as the base and list ``notes.txt``; the trailing
    fix catches ``HEAD~<item count>``. The root and P's parent are both
    distinct from P.

    The list drops all of ``plans/j/`` (KD-6), so the item reports and the
    ``runbook.md`` revision in the range must vanish, not just ``reports/``.
    The uncommitted ``README.md`` edit stays out because the diff is
    ``<base> HEAD``, not the working tree. ``git diff`` emits paths in
    sorted order, so the expected order is fixed.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "other job item", {"plans/other/reports/item-1-1.md": "o\n"})
    _commit(
        repo,
        "j planning",
        {"plans/j/reports/explore-x.md": "x\n", "plans/j/runbook.md": "v1\n"},
    )
    _commit(
        repo,
        "j notes",
        {"plans/j/reports/item-x/notes.md": "n\n", "notes.txt": "n\n"},
    )
    base_sha = _commit(
        repo, "outline review", {"plans/j/reports/outline-review.md": "r\n"}
    )
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    _commit(
        repo,
        "item 1.2",
        {
            "plans/j/reports/item-1-2.md": "2\n",
            "b.txt": "changed\n",
            "plans/j/runbook.md": "v2\n",
        },
    )
    _commit(repo, "item 1.2 code-review fixes", {"a.txt": "a fixed\n"})
    (repo / "README.md").write_text("uncommitted\n", encoding="utf-8")

    result = _run_script(repo, "j")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {base_sha}",
        "a.txt",
        "b.txt",
    ], result.stdout


def test_exempt_paths_committed_in_the_run_are_dropped(tmp_path: Path) -> None:
    r"""The run's own commit of exempt paths does not appear in the list.

    The item 1.1 commit — the run's first, so its parent is the base — also
    touches the three exempt paths of KD-6 (``inbox/x.md``,
    ``.claude/handoff-task.md``, a file named ``memory``) and one near-miss
    per boundary of the exempt alternation, each of which must stay listed:

        memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md

    ``inbox/sub/y.md`` (single level; a shell ``case`` glob ``inbox/*.md``
    matches ``/``), ``inbox/x.txt`` and ``.claude/handoff-task.json`` (the
    ``.md`` suffix), ``.claude/other.md`` (the ``handoff-`` prefix),
    ``memoryx.txt`` (the exact name, not a prefix) and ``docs/inbox/x.md``
    (anchored at the path start, which an ungrouped ``^a|b|c$`` loses). The
    exact-list assertion fails an implementation that drops nothing and one
    that drops any near-miss.
    """
    repo = _init_repo(tmp_path)
    base_sha = _run_git(repo, "rev-parse", "HEAD").strip()
    _commit(
        repo,
        "item 1.1",
        {
            "plans/j/reports/item-1-1.md": "1\n",
            "inbox/x.md": "exempt\n",
            ".claude/handoff-task.md": "exempt\n",
            "memory": "exempt\n",
            "inbox/sub/y.md": "keep\n",
            "inbox/x.txt": "keep\n",
            ".claude/handoff-task.json": "keep\n",
            ".claude/other.md": "keep\n",
            "memoryx.txt": "keep\n",
            "docs/inbox/x.md": "keep\n",
        },
    )

    result = _run_script(repo, "j")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {base_sha}",
        ".claude/handoff-task.json",
        ".claude/other.md",
        "docs/inbox/x.md",
        "inbox/sub/y.md",
        "inbox/x.txt",
        "memoryx.txt",
    ], result.stdout


def test_no_item_report_exits_1(tmp_path: Path) -> None:
    """No committed ``item-*`` report gives ``NO-BASE:``, never ``BASE:``.

    The repo holds job ``j``'s own planning reports (``explore-x.md``,
    ``outline-review.md``, neither matching ``item-*``), a committed
    ``item-*`` report for job ``jj`` (``plans/jj/reports/item-1-1.md``), and
    an **uncommitted** ``plans/j/reports/item-1-1.md`` sitting on disk. KD-1
    keys on committed history scoped to this job: a derivation that ignores
    the job or prefix-matches it (``plans/j*``) finds ``jj``'s report, and
    one matching any committed report regardless of the ``item-*`` name
    finds ``explore-x.md``, so each prints a ``BASE:``; one that takes the
    on-disk file as a run in progress has no history to derive from and does
    not print ``NO-BASE:``.

    Exit 1 is ``NO-BASE:``'s code, not every failure's. A repo whose root
    commit adds the item report has a report but no parent to take as the
    base: a git failure, exit 2 with ``ERROR:``. A repo with no commit at
    all fails one step earlier, in the ``git log`` query itself, and must
    give exit 2 too, never the empty result that ``NO-BASE:`` reads. Those
    checks run first, so an implementation answering ``NO-BASE:`` from
    either failure branch reds there.
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


def test_renamed_file_lists_both_paths(tmp_path: Path) -> None:
    """A rename in the run lists its old and its new path.

    Item 1.1's commit renames the pre-run ``b.txt`` to ``c.txt``. The test
    env nulls user config, so git's default ``diff.renames`` is on, and a
    diff with rename detection prints only ``c.txt``. ``--no-renames`` makes
    the rename a deletion plus an addition, so the list carries ``b.txt`` as
    it carries any deleted path, whatever the user's config says.
    """
    repo = _init_repo(tmp_path)
    base_sha = _run_git(repo, "rev-parse", "HEAD").strip()
    _run_git(repo, "mv", "b.txt", "c.txt")
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n"})

    result = _run_script(repo, "j")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {base_sha}",
        "b.txt",
        "c.txt",
    ], result.stdout


def test_paths_with_space_and_non_ascii_bytes_are_listed_whole(
    tmp_path: Path,
) -> None:
    r"""A path with a space or non-ASCII bytes is listed whole and unquoted.

    Item 1.2 reads the diff NUL-delimited. The run commit adds ``my file.txt``
    and ``café.txt`` beside the exempt ``inbox/é.md``. A word-split read
    (``for path in $(git diff --name-only ...)``) lists ``my`` and ``file.txt``
    apart. A newline-delimited read, with ``-z`` dropped from the diff, gets
    git's ``core.quotePath`` form for ``café.txt``, ``"caf\303\251.txt"``, and
    would not match the exempt path either, so ``inbox/é.md`` would leak in
    quoted. The exact-list assertion fails both.
    """
    repo = _init_repo(tmp_path)
    base_sha = _run_git(repo, "rev-parse", "HEAD").strip()
    _commit(
        repo,
        "item 1.1",
        {
            "plans/j/reports/item-1-1.md": "1\n",
            "my file.txt": "keep\n",
            "café.txt": "keep\n",
            "inbox/é.md": "exempt\n",
        },
    )

    result = _run_script(repo, "j")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {base_sha}",
        "café.txt",
        "my file.txt",
    ], result.stdout
