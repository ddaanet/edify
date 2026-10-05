"""Exemption-pattern tests for ``plugin/skills/build/scripts/verify-step.sh``.

KD-7 in ``plans/build-defects/outline.md``: any change is dirt except three
paths dirty by convention, under a status taken with
``--untracked-files=all``. D-91 exempts ``memory``, ``.claude/handoff-*.md``
and ``inbox/*.md`` (each ``*`` one path component) in any porcelain state but
a rename or copy, which fails closed as dirt.

Split from ``tests/test_verify_step.py``, which keeps the fail-closed tests,
to keep each module under its line cap. See ``tests/verify_step_helpers.py``
for the shared fixtures.
"""

from pathlib import Path

from .verify_step_helpers import (
    _assert_dirty,
    _init_repo,
    _run_git,
    _run_script,
    _status,
    _stub_just,
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
    repo = _init_repo(tmp_path)

    bin_dir, marker = _stub_just(tmp_path)

    (repo / "inbox").mkdir()
    (repo / "inbox" / "brief.md").write_text("brief\n", encoding="utf-8")
    handoff = repo / ".claude" / "handoff-task.md"
    handoff.write_text("staged\n", encoding="utf-8")
    _run_git(repo, "add", ".claude/handoff-task.md")
    handoff.write_text("staged then edited\n", encoding="utf-8")
    assert _status(repo) == "MM .claude/handoff-task.md\n?? inbox/brief.md\n"

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.exists(), "just precommit was not invoked: " + result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "stray.txt").write_text("stray\n", encoding="utf-8")
    (repo / ".claude" / "notes.md").write_text("notes\n", encoding="utf-8")
    (repo / ".claude" / "handoff-notes.txt").write_text("x\n", encoding="utf-8")

    _assert_dirty(
        _run_script(repo, bin_dir),
        "?? .claude/handoff-notes.txt",
        "?? .claude/notes.md",
        "?? stray.txt",
    )

    (repo / "stray.txt").unlink()
    (repo / ".claude" / "notes.md").unlink()
    (repo / ".claude" / "handoff-notes.txt").unlink()
    (repo / "inbox" / "notes.txt").write_text("notes\n", encoding="utf-8")

    _assert_dirty(_run_script(repo, bin_dir), "?? inbox/notes.txt")


def test_memory_gitlink_is_clean_and_a_sibling_name_is_not(tmp_path: Path) -> None:
    """The ``memory`` gitlink is exempt in any porcelain state.

    ``MM memory`` — a staged gitlink bump with a newer submodule commit on top —
    sets both columns, so an exemption keyed on the pre-KD-7 `` M memory`` line
    alone, or one dropping ``memory`` from the pattern, fails the clean phase.

    Decoy phase: an untracked ``memory.md`` beside it is dirt listed alone,
    which catches an unanchored ``memory`` prefix.
    """
    repo = _init_repo(tmp_path)
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
    assert _status(repo) == "MM memory\n"

    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "memory.md").write_text("not the gitlink\n", encoding="utf-8")

    _assert_dirty(_run_script(repo, bin_dir), "?? memory.md")


def test_rename_out_of_exempt_path_is_dirty(tmp_path: Path) -> None:
    r"""A staged rename out of an exempt path is listed as dirt.

    The pre-F-1 pattern matched ``inbox/[^/]+\.md`` against the ``old ->
    new`` tail of an ``R`` line, so ``inbox/a.md -> notes.md`` passed as one
    exempt path even though ``notes.md`` is not exempt.
    """
    repo = _init_repo(tmp_path)
    (repo / "inbox").mkdir()
    (repo / "inbox" / "a.md").write_text("a\n", encoding="utf-8")
    _run_git(repo, "add", "inbox/a.md")
    _run_git(repo, "commit", "-q", "-m", "add inbox/a.md")
    _run_git(repo, "mv", "inbox/a.md", "notes.md")
    assert _status(repo) == "R  inbox/a.md -> notes.md\n"

    bin_dir, _marker = _stub_just(tmp_path)

    _assert_dirty(_run_script(repo, bin_dir), "R  inbox/a.md -> notes.md")


def test_quoted_exempt_path_is_clean(tmp_path: Path) -> None:
    """A quoted exempt path (a space in the name) still clears the tree.

    Git quotes a porcelain path containing a space; the pre-F-1 pattern
    anchored directly on ``inbox/`` with no allowance for the quotes.

    Decoy phase: a quoted ``inbox/my notes.txt``, differing from the brief
    only in not being ``*.md``, is dirt listed alone. That catches an
    allowance exempting every quoted path rather than quoted exempt paths.
    """
    repo = _init_repo(tmp_path)
    (repo / "inbox").mkdir()
    (repo / "inbox" / "my brief.md").write_text("brief\n", encoding="utf-8")
    assert _status(repo) == '?? "inbox/my brief.md"\n'

    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"

    (repo / "inbox" / "my notes.txt").write_text("notes\n", encoding="utf-8")
    assert _status(repo) == '?? "inbox/my brief.md"\n?? "inbox/my notes.txt"\n'

    _assert_dirty(_run_script(repo, bin_dir), '?? "inbox/my notes.txt"')


def test_exempt_paths_clean_in_any_porcelain_state(tmp_path: Path) -> None:
    """Exempt paths clear the tree in XY states beyond `` M``, ``MM``, ``??``.

    One tree holds a staged add, a staged delete, a worktree-only delete and an
    unmerged conflict from a real two-branch merge on a tracked file. KD-7
    frees both columns of anything but a rename or copy. Every line must be
    filtered for ``CLEAN:``, so a pattern losing any one of ``A``, ``D`` or
    ``U`` in either column lists that line as dirt — as does the narrower
    ``[ M?]`` in both columns, which none of the four pairs is drawn from.
    """
    repo = _init_repo(tmp_path)
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

    assert _status(repo) == (
        "A  .claude/handoff-new.md\n"
        " D .claude/handoff-task.md\n"
        "UU inbox/conflict.md\n"
        "D  inbox/old.md\n"
    )

    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("CLEAN:"), result.stdout
    assert marker.read_text(encoding="utf-8") == "precommit\n"


def test_nested_path_under_exempt_dir_is_dirty(tmp_path: Path) -> None:
    r"""The exempt globs are single-level; a path one level deeper is dirt.

    ``inbox/[^/]+\.md`` and ``\.claude/handoff-[^/]+\.md`` each stop at the
    first ``/`` past their directory prefix, so ``inbox/sub/x.md`` and
    ``.claude/handoff-dir/x.md`` are dirt, listed by their own ``??`` lines —
    as they would not be if either glob were widened to span directories.

    Single-level siblings ``inbox/x.md`` and ``.claude/handoff-x.md`` share
    the tree and are absent from the listing, so a pattern that exempts
    neither directory at all, rather than only its nested paths, fails too.
    """
    repo = _init_repo(tmp_path)
    (repo / "inbox" / "sub").mkdir(parents=True)
    (repo / "inbox" / "sub" / "x.md").write_text("x\n", encoding="utf-8")
    (repo / "inbox" / "x.md").write_text("x\n", encoding="utf-8")
    (repo / ".claude" / "handoff-dir").mkdir()
    (repo / ".claude" / "handoff-dir" / "x.md").write_text("x\n", encoding="utf-8")
    (repo / ".claude" / "handoff-x.md").write_text("x\n", encoding="utf-8")

    assert _status(repo) == (
        "?? .claude/handoff-dir/x.md\n"
        "?? .claude/handoff-x.md\n"
        "?? inbox/sub/x.md\n"
        "?? inbox/x.md\n"
    )

    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir)
    _assert_dirty(result, "?? .claude/handoff-dir/x.md", "?? inbox/sub/x.md")
    assert not marker.exists(), "just was invoked: " + result.stdout
