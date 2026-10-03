"""Contract tests for ``plugin/skills/build/scripts/changed-files.sh``.

KD-1 and KD-6 in ``plans/build-fixes/outline.md``: the base is the parent of
the earliest commit adding a ``plans/<job>/reports/item-*`` report, and the
changed-files list is the committed diff since that base, minus the job's own
``plans/<job>/`` record and the exempt paths ``exempt-paths.sh`` names.

Each test builds a throwaway git repo under ``tmp_path`` and runs the script
by absolute path with CWD at the repo root, following the ``_init_repo``
pattern in ``tests/test_verify_step.py``.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "skills" / "build" / "scripts" / "changed-files.sh"


def _run_git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` insulated from user and system config; return stdout.

    Failures assert with stderr attached rather than raising a bare
    ``CalledProcessError`` (docs/references/testing.md D-21).
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"
    return result.stdout


def _init_repo(tmp_path: Path) -> Path:
    """Init a repo under ``tmp_path``, seeded with ``README.md`` and ``b.txt``.

    ``b.txt`` is seeded here, before the run's first commit, so a later
    run commit can change (not add) it.
    """
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    (repo / "b.txt").write_text("base\n", encoding="utf-8")
    _run_git(repo, "add", "README.md", "b.txt")
    _run_git(repo, "commit", "-q", "-m", "seed")
    return repo


def _run_script(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run ``changed-files.sh`` by absolute path with CWD at ``repo``."""
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        [str(SCRIPT), *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _commit(repo: Path, message: str, files: dict[str, str]) -> str:
    """Write and commit ``files``; return the new commit's sha.

    ``files`` maps a repo-relative path to its content.
    """
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _run_git(repo, "add", "--", *files)
    _run_git(repo, "commit", "-q", "-m", message)
    return _run_git(repo, "rev-parse", "HEAD").strip()


def test_base_is_parent_of_first_item_report_commit(tmp_path: Path) -> None:
    """``BASE:`` names the parent of the first committed ``item-*`` report.

    History: seed (root) -> another job's item report -> ``j``'s
    ``explore-x.md`` and ``runbook.md`` -> P adds ``outline-review.md`` ->
    item 1.1 (report, new ``a.txt``) -> item 1.2 (report, changed ``b.txt``,
    revised ``runbook.md``) -> a report-less code-review fix to ``a.txt``.
    Only the parent of item 1.1's commit, P, is right. Each decoy commit
    rules out a wrong derivation that the bare spec history collapses onto P:
    the other job's report catches an unscoped ``plans/*/reports/item-*``;
    ``explore-x.md`` catches "first commit touching ``plans/j/reports/``"
    taken without its parent; the trailing fix catches ``HEAD~<item count>``.
    The root and P's parent are both distinct from P.

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
    base: a git failure, exit 2 with ``ERROR:``. That check runs first, so
    an implementation answering ``NO-BASE:`` from the parent lookup's failure
    branch — which both cases reach — reds there.
    """
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


def test_phase_without_boundary_gives_run_base(tmp_path: Path) -> None:
    """``--phase`` with no boundary landed in the run falls back to the run base.

    KD-2 and KD-8: the phase base is the latest commit in ``<run base>..HEAD``
    touching ``plans/j/reports/phase-*-corrector.md``, and the run base (KD-1)
    when none matches. History: seed -> a ``phase-1-corrector.md`` report for
    ``j`` -> ``j``'s ``runbook.md``, the run base -> item 1.1 (report, new
    ``a.txt``) -> another job's ``plans/jj/reports/phase-1-corrector.md``
    inside the run -> item 1.2 (report, changed ``b.txt``).

    The pre-run report sits one commit before the run base, so a search over
    the whole history names it, not the base; the in-run ``jj`` report
    catches a search ignoring the job, which would name it as the base. Only
    the run base, the commit before item 1.1, is right. ``--phase`` must also
    print exactly what the bare call prints; only ``plans/j/`` is filtered
    out, so the list is ``a.txt``, ``b.txt`` and the other job's report.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "pre-run phase", {"plans/j/reports/phase-1-corrector.md": "p\n"})
    base_sha = _commit(repo, "j planning", {"plans/j/runbook.md": "v1\n"})
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    _commit(repo, "jj boundary", {"plans/jj/reports/phase-1-corrector.md": "o\n"})
    _commit(repo, "item 1.2", {"plans/j/reports/item-1-2.md": "2\n", "b.txt": "x\n"})

    plain = _run_script(repo, "j")
    assert plain.returncode == 0, plain.stdout + plain.stderr
    assert plain.stdout.splitlines() == [
        f"BASE: {base_sha}",
        "a.txt",
        "b.txt",
        "plans/jj/reports/phase-1-corrector.md",
    ], plain.stdout

    result = _run_script(repo, "j", "--phase")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == plain.stdout
