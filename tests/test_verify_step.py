"""Contract tests for ``plugin/skills/build/scripts/verify-step.sh``.

KD-7 in ``plans/build-defects/outline.md``: any change is dirt except three
paths dirty by convention — `` M memory``, ``.claude/handoff-*.md`` and
``inbox/*.md`` — under a status taken with ``--untracked-files=all``.

Each test builds a throwaway git repo under ``tmp_path`` and runs the script
by absolute path with CWD at the repo root, following the subprocess-run
pattern in ``tests/test_triage_feedback.py``.
"""

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "plugin" / "skills" / "build" / "scripts" / "verify-step.sh"


def _run_git(repo: Path, *args: str, returncode: int = 0) -> str:
    """Run git in ``repo`` insulated from user and system config; return stdout.

    Failures assert with stderr attached rather than raising a bare
    ``CalledProcessError`` (docs/references/testing.md D-21). ``returncode``
    is the exit expected, for a call that fails on purpose.
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
    assert result.returncode == returncode, (
        f"git {args}: {result.stdout}{result.stderr}"
    )
    return result.stdout


def _init_repo(repo: Path) -> None:
    """Init a git repo at ``repo`` with one commit including a handoff file."""
    repo.mkdir(parents=True, exist_ok=True)
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "config", "user.email", "test@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    claude_dir = repo / ".claude"
    claude_dir.mkdir()
    (claude_dir / "handoff-task.md").write_text("original\n", encoding="utf-8")
    _run_git(repo, "add", "README.md", ".claude/handoff-task.md")
    _run_git(repo, "commit", "-q", "-m", "seed")


def _stub_just(bin_dir: Path, marker: Path) -> None:
    """Write a ``just`` stub in ``bin_dir`` appending its args to ``marker``."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "just"
    stub.write_text(f'#!/bin/sh\necho "$*" >> "{marker}"\nexit 0\n', encoding="utf-8")
    stub.chmod(0o755)


def _run_script(
    repo: Path,
    bin_dir: Path,
    *,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run verify-step.sh by absolute path with CWD at ``repo``.

    ``bin_dir`` is prepended to ``PATH`` so the stub ``just`` is found first;
    git config is insulated the same way as ``_run_git``. ``extra_env`` is
    applied last, so a ``PATH`` entry there replaces the prepended one
    outright instead of merely prefixing it.
    """
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(SCRIPT)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_conventional_dirt_is_clean_and_other_dirt_is_not(tmp_path: Path) -> None:
    """KD-7's exemptions clear the tree; any other change is dirt.

    Clean phase: an untracked ``inbox/brief.md`` (the only file under
    ``inbox/``) and a ``.claude/handoff-task.md`` modified in both index and
    worktree (``MM``, so an exemption keyed on one porcelain column fails) are
    dirty by convention: exit 0, ``CLEAN:``, and the stub ``just`` records
    exactly one ``precommit`` call.

    Dirty phase: an untracked ``stray.txt`` plus decoys ``.claude/notes.md``
    and ``.claude/handoff-notes.txt`` (inside ``.claude/`` but not
    ``handoff-*.md``) give exit 1 and a DIRTY listing of exactly those three
    lines, so neither exempt path is echoed and an exemption of all of
    ``.claude/``, of ``.claude/*.md`` or of ``.claude/handoff-*`` is caught.

    Inbox phase: with those removed, an untracked ``inbox/notes.txt`` (inside
    ``inbox/`` but not ``*.md``) is dirt listed by its own path. That catches
    an exemption of all of ``inbox/``, and a status without
    ``--untracked-files=all`` whose collapsed ``?? inbox/`` line is exempted.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)

    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    _stub_just(bin_dir, marker)

    (repo / "inbox").mkdir()
    (repo / "inbox" / "brief.md").write_text("brief\n", encoding="utf-8")
    handoff = repo / ".claude" / "handoff-task.md"
    handoff.write_text("staged\n", encoding="utf-8")
    _run_git(repo, "add", ".claude/handoff-task.md")
    handoff.write_text("staged then edited\n", encoding="utf-8")
    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        "MM .claude/handoff-task.md\n?? inbox/brief.md\n"
    )

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.exists(), "just precommit was not invoked: " + result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "stray.txt").write_text("stray\n", encoding="utf-8")
    (repo / ".claude" / "notes.md").write_text("notes\n", encoding="utf-8")
    (repo / ".claude" / "handoff-notes.txt").write_text("x\n", encoding="utf-8")

    result = _run_script(repo, bin_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "DIRTY: uncommitted changes",
        "?? .claude/handoff-notes.txt",
        "?? .claude/notes.md",
        "?? stray.txt",
    ], result.stdout

    (repo / "stray.txt").unlink()
    (repo / ".claude" / "notes.md").unlink()
    (repo / ".claude" / "handoff-notes.txt").unlink()
    (repo / "inbox" / "notes.txt").write_text("notes\n", encoding="utf-8")

    result = _run_script(repo, bin_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "DIRTY: uncommitted changes",
        "?? inbox/notes.txt",
    ], result.stdout


def test_memory_gitlink_is_clean_and_a_sibling_name_is_not(tmp_path: Path) -> None:
    """The ``memory`` gitlink is exempt in any porcelain state.

    ``MM memory`` — a staged gitlink bump with a newer submodule commit on top —
    sets both columns, so an exemption keyed on the pre-KD-7 `` M memory`` line
    alone, or one dropping ``memory`` from the pattern, fails the clean phase.

    Decoy phase: an untracked ``memory.md`` beside it is dirt listed alone,
    which catches an unanchored ``memory`` prefix.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    submodule = repo / "memory"
    submodule.mkdir()
    _run_git(submodule, "init", "-q", "-b", "main")
    _run_git(submodule, "config", "user.name", "Test User")
    _run_git(submodule, "config", "user.email", "test@example.com")
    _run_git(submodule, "commit", "-q", "--allow-empty", "-m", "fact 1")
    _run_git(repo, "add", "memory")
    _run_git(repo, "commit", "-q", "-m", "add memory gitlink")
    _run_git(submodule, "commit", "-q", "--allow-empty", "-m", "fact 2")
    _run_git(repo, "add", "memory")
    _run_git(submodule, "commit", "-q", "--allow-empty", "-m", "fact 3")
    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        "MM memory\n"
    )

    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    _stub_just(bin_dir, marker)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "memory.md").write_text("not the gitlink\n", encoding="utf-8")

    result = _run_script(repo, bin_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "DIRTY: uncommitted changes",
        "?? memory.md",
    ], result.stdout


def test_rename_out_of_exempt_path_is_dirty(tmp_path: Path) -> None:
    r"""A staged rename out of an exempt path is listed as dirt.

    The pre-F-1 pattern matched ``inbox/[^/]+\.md`` against the ``old ->
    new`` tail of an ``R`` line, so ``inbox/a.md -> notes.md`` passed as one
    exempt path even though ``notes.md`` is not exempt.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "inbox").mkdir()
    (repo / "inbox" / "a.md").write_text("a\n", encoding="utf-8")
    _run_git(repo, "add", "inbox/a.md")
    _run_git(repo, "commit", "-q", "-m", "add inbox/a.md")
    _run_git(repo, "mv", "inbox/a.md", "notes.md")
    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        "R  inbox/a.md -> notes.md\n"
    )

    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    _stub_just(bin_dir, marker)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "DIRTY: uncommitted changes",
        "R  inbox/a.md -> notes.md",
    ], result.stdout


def test_quoted_exempt_path_is_clean(tmp_path: Path) -> None:
    """A quoted exempt path (a space in the name) still clears the tree.

    Git quotes a porcelain path containing a space; the pre-F-1 pattern
    anchored directly on ``inbox/`` with no allowance for the quotes.

    Decoy phase: a quoted ``inbox/my notes.txt``, differing from the brief
    only in not being ``*.md``, is dirt listed alone. That catches an
    allowance exempting every quoted path rather than quoted exempt paths.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "inbox").mkdir()
    (repo / "inbox" / "my brief.md").write_text("brief\n", encoding="utf-8")
    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        '?? "inbox/my brief.md"\n'
    )

    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    _stub_just(bin_dir, marker)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "inbox" / "my notes.txt").write_text("notes\n", encoding="utf-8")
    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        '?? "inbox/my brief.md"\n?? "inbox/my notes.txt"\n'
    )

    result = _run_script(repo, bin_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "DIRTY: uncommitted changes",
        '?? "inbox/my notes.txt"',
    ], result.stdout


def test_exempt_paths_clean_in_any_porcelain_state(tmp_path: Path) -> None:
    """Exempt paths clear the tree in XY states beyond `` M``, ``MM``, ``??``.

    One tree holds a staged add, a staged delete, a worktree-only delete and an
    unmerged conflict from a real two-branch merge on a tracked file. KD-7
    frees both columns of anything but a rename or copy. Every line must be
    filtered for ``CLEAN:``, so a pattern losing any one of ``A``, ``D`` or
    ``U`` in either column lists that line as dirt — as does the narrower
    ``[ M?]`` in both columns, which none of the four pairs is drawn from.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "inbox").mkdir()
    (repo / "inbox" / "old.md").write_text("base\n", encoding="utf-8")
    (repo / "inbox" / "conflict.md").write_text("base\n", encoding="utf-8")
    _run_git(repo, "add", "inbox/old.md", "inbox/conflict.md")
    _run_git(repo, "commit", "-q", "-m", "add inbox files")

    _run_git(repo, "checkout", "-q", "-b", "feature")
    (repo / "inbox" / "conflict.md").write_text("feature\n", encoding="utf-8")
    _run_git(repo, "commit", "-q", "-am", "feature change")
    _run_git(repo, "checkout", "-q", "main")
    (repo / "inbox" / "conflict.md").write_text("main\n", encoding="utf-8")
    _run_git(repo, "commit", "-q", "-am", "main change")

    # Both branches rewrote the same line: the merge stops at exit 1, leaving UU.
    _run_git(repo, "merge", "feature", "-m", "merge", returncode=1)

    _run_git(repo, "rm", "-q", "inbox/old.md")
    (repo / ".claude" / "handoff-new.md").write_text("new\n", encoding="utf-8")
    _run_git(repo, "add", ".claude/handoff-new.md")
    (repo / ".claude" / "handoff-task.md").unlink()

    assert _run_git(repo, "status", "--porcelain", "--untracked-files=all") == (
        "A  .claude/handoff-new.md\n"
        " D .claude/handoff-task.md\n"
        "UU inbox/conflict.md\n"
        "D  inbox/old.md\n"
    )

    bin_dir = tmp_path / "bin"
    marker = tmp_path / "just-invocations"
    _stub_just(bin_dir, marker)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"


def test_git_status_failure_exits_2(tmp_path: Path) -> None:
    """A CWD outside any repo fails closed with exit 2, not a raw fatal.

    ``GIT_CEILING_DIRECTORIES`` blocks git from discovering an enclosing
    repository, so the failure is deterministic regardless of checkout.
    """
    outside = tmp_path / "outside"
    outside.mkdir()
    bin_dir = tmp_path / "bin"

    result = _run_script(
        outside,
        bin_dir,
        extra_env={"GIT_CEILING_DIRECTORIES": str(tmp_path)},
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR: git status failed" in result.stdout.splitlines(), result.stdout
    assert not any(
        line.startswith(("CLEAN:", "DIRTY:")) for line in result.stdout.splitlines()
    ), result.stdout


def test_missing_just_exits_2(tmp_path: Path) -> None:
    """A clean repo with no ``just`` on ``PATH`` fails closed, not silently.

    Pre-F-2 code ran ``just precommit`` unconditionally, so a missing tool
    was reported as a precommit failure rather than an environment fault.
    """
    repo = tmp_path / "repo"
    _init_repo(repo)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("bash", "git", "grep"):
        resolved = shutil.which(tool)
        assert resolved is not None, f"{tool} not found on the outer PATH"
        (bin_dir / tool).symlink_to(resolved)
    assert shutil.which("just", path=str(bin_dir)) is None

    result = _run_script(repo, bin_dir, extra_env={"PATH": str(bin_dir)})
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR: just not found on PATH" in result.stdout.splitlines(), result.stdout
    assert "PRECOMMIT:" not in result.stdout, result.stdout
