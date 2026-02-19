# Exploration: Worktree `rm` Implementation

## Summary

Found the `rm` command implementation in `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`. The code handles worktree removal with three main issues:
1. **Dirty check on parent instead of target worktree** — The `_is_parent_dirty()` check at line 357 uses the current working directory (parent repo) instead of checking the target worktree.
2. **Broken worktree handling** — No cleanup for worktrees created by failed `new` command (empty directory, exit 255).
3. **Submodule branch cleanup missing with `--confirm`** — The `--confirm` flag bypasses branch validation but still tries submodule cleanup; however, there's no explicit cleanup of submodule branches in the rm code path.

## Key Findings

### 1. The `rm` Command Entry Point

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`
**Function:** `rm()` at lines 336–399

```python
@worktree.command()
@click.argument("slug")
@click.option("--confirm", is_flag=True, default=False, help="...")
@click.option("--force", is_flag=True, default=False, help="...")
def rm(slug: str, confirm: bool, force: bool) -> None:
    """Remove worktree and its branch."""
    if not force:
        _check_confirm(slug, confirm)  # Line 353

    worktree_path = _get_worktree_path_for_branch(slug) or wt_path(slug)
    if not force:
        if _is_parent_dirty(exclude_path=str(worktree_path.parent)):  # BUG 1: Line 357
            click.echo("Parent repo has uncommitted changes...", err=True)
            raise SystemExit(2)
        if _is_submodule_dirty():  # Line 364
            click.echo("Submodule (agent-core) has uncommitted changes...", err=True)
            raise SystemExit(2)

        branch_exists, removal_type = _guard_branch_removal(slug)  # Line 372
    else:
        branch_exists = True
        removal_type = "focused"
    parent_reg, submodule_reg = _probe_registrations(worktree_path)  # Line 376

    _warn_if_dirty(worktree_path)  # Line 378
    amended = _update_session_and_amend(slug)  # Line 379

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)  # Line 382

    if worktree_path.exists():
        shutil.rmtree(worktree_path)  # Line 385

    _git("worktree", "prune")  # Line 387

    container = worktree_path.parent
    if container.exists() and not list(container.iterdir()):
        container.rmdir()  # Line 391

    if branch_exists:
        _delete_branch(slug, removal_type)  # Line 394
    amend_note = " Merge commit amended." if amended else ""
    detail = " (focused session only)" if removal_type == "focused" else ""
    prefix = "Removed worktree" if removal_type is None else "Removed"
    click.echo(f"{prefix} {slug}{detail}{amend_note}")
```

### 2. Bug 1: Dirty Check on Parent Instead of Target Worktree

**Location:** `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`, line 357

**Problem:**
```python
if _is_parent_dirty(exclude_path=str(worktree_path.parent)):
    click.echo("Parent repo has uncommitted changes. ...")
    raise SystemExit(2)
```

The check calls `_is_parent_dirty()` which always checks the current working directory (the parent repo), not the target worktree. When running `rm` from the parent repo, this is checking the wrong repository.

**Root Cause:**
`_is_parent_dirty()` in `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py` (lines 76–95) runs `git status --porcelain` without changing directories:

```python
def _is_parent_dirty(exclude_path: str | None = None) -> bool:
    """Return True if parent repo has staged/unstaged/untracked changes.

    exclude_path: if given, skip status lines whose path starts with
    Path(exclude_path).name + "/" (used to ignore the worktree container dir
    when it appears as an untracked entry inside the repo).
    """
    output = _git("status", "--porcelain", check=False)  # Runs in CWD
    # ... excludes worktree container from output
    return False
```

The intent appears to be "check if parent is dirty, but exclude the worktree container from the list of untracked files." However, the comment in the `rm()` function suggests it's also supposed to check if the *target worktree* is dirty. The dirty check at line 364 calls `_is_submodule_dirty()` separately, which properly uses `-C agent-core`.

**Test Evidence:**
- `test_rm_blocks_on_dirty_parent()` in `/Users/david/code/claudeutils/tests/test_worktree_rm_dirty.py` (lines 71–89) creates a dirty file in the parent repo and expects `rm --confirm` to block.
- The test description says "Blocks removal if parent repo has uncommitted changes," but the session description says "dirty check fails on parent *instead of* target worktree," implying the function should check the *target* worktree is clean, not the parent.

**Expected Behavior:**
Should verify the target worktree (`worktree_path`) is clean, not the parent repo. Or needs to check both separately.

---

### 3. Bug 2: Broken Worktree from Failed `new` Command

**Location:** Implicit — no cleanup code exists

**Problem:**
The `new` command can fail partway through `_setup_worktree()` (line 171–183 in cli.py), leaving an empty worktree directory with `git worktree` unaware of it. When `rm` is called:

1. `_get_worktree_path_for_branch()` returns `None` (worktree not in git registry)
2. Fallback to `wt_path(slug)` finds the empty directory
3. `_probe_registrations()` returns `(False, False)` — neither worktree is registered
4. Line 381-382 skips `_remove_worktrees()` because no registrations exist
5. Line 385 tries `shutil.rmtree(worktree_path)` — succeeds
6. Branch cleanup still happens (line 394)

**Test Evidence:**
No test explicitly covers this scenario. The test `test_rm_branch_only()` (line 57–81 in test_worktree_rm.py) removes the worktree directory externally and then calls `rm`, which works because it falls through to branch cleanup.

However, a worktree created by a failed `new` command (e.g., `new` fails after creating the directory but before registering with git worktree) would be left in an inconsistent state.

---

### 4. Bug 3: Submodule Branch Cleanup Missing with `--confirm`

**Location:** `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`, lines 336–399

**Problem:**
The `--confirm` flag at line 353 skips the normal confirmation prompt but doesn't affect the branch removal logic. However, there's an asymmetry:

**Branch cleanup in `rm()`:**
- Lines 372–375: When `--force` is NOT set, `_guard_branch_removal()` is called to verify the branch can be safely deleted.
- Lines 373–375: When `--force` IS set, `branch_exists` and `removal_type` are hardcoded to `True` and `"focused"` respectively, skipping the guard.
- Lines 393–394: If `branch_exists` is True, `_delete_branch()` deletes the parent branch.

**Submodule branch cleanup:**
There is **no code** to delete the submodule (`agent-core`) branch. The `_delete_branch()` function (line 293–300) only deletes the parent branch:

```python
def _delete_branch(slug: str, removal_type: str | None) -> None:
    flag = "-D" if removal_type == "focused" else "-d"
    r = subprocess.run(
        ["git", "branch", flag, slug], capture_output=True, text=True, check=False
    )
    # ... error handling
```

**Root Cause:**
The submodule branch is created during `new` command (line 147–168 in `_create_submodule_worktree()`):

```python
def _create_submodule_worktree(...) -> None:
    """Create agent-core submodule worktree if exists."""
    agent_core = Path(project_root) / "agent-core"
    if not agent_core.exists() or not (agent_core / ".git").exists():
        return
    try:
        _git("-C", str(agent_core), "rev-parse", "--verify", slug)
        flag = []  # Branch exists, reuse
    except subprocess.CalledProcessError:
        flag = ["-b"]  # Branch doesn't exist, create it
    _git(
        "-C", str(agent_core), "worktree", "add",
        str(worktree_path / "agent-core"), *flag, slug,
    )
```

But the `rm` command never cleans up the corresponding `agent-core` branch. It only removes the worktree registrations via `_remove_worktrees()` (which calls `git worktree remove --force`), but the branch itself persists.

**Test Evidence:**
The test `test_new_submodule()` in `/Users/david/code/claudeutils/tests/test_worktree_submodule.py` (lines 13–61) verifies that `new` creates a branch in `agent-core`, but there is no test verifying `rm` cleans it up.

**Expected Behavior:**
After `rm`, the submodule branch should be deleted (or at least, the merge logic in the `merge` command assumes it will be).

---

## Dirty Check Logic Detail

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py`

The `_is_parent_dirty()` function (lines 76–95) checks the parent repo's status but uses `exclude_path` to filter out the worktree container directory when it appears as an untracked entry:

```python
def _is_parent_dirty(exclude_path: str | None = None) -> bool:
    output = _git("status", "--porcelain", check=False)
    if not output:
        return False

    exclude_prefix = (Path(exclude_path).name + "/") if exclude_path else None
    for line in output.strip().split("\n"):
        if not line:
            continue
        path = line[3:]  # Skip status codes (first 3 chars)
        if exclude_prefix and path.startswith(exclude_prefix):
            continue  # Ignore worktree container
        return True
    return False
```

The function works correctly for its stated purpose: detect if the parent repo is dirty while ignoring the worktree container itself appearing as an untracked directory.

---

## Submodule-Related Cleanup Paths

### Worktree Removal (in `_remove_worktrees()`)

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py`, lines 157–173

```python
def _remove_worktrees(
    worktree_path: Path,
    parent_registered: bool,
    submodule_registered: bool,
) -> None:
    """Remove worktrees (submodule first, force flag)."""
    if submodule_registered:
        _git(
            "-C", "agent-core", "worktree", "remove", "--force",
            str(worktree_path / "agent-core"),
        )
    if parent_registered:
        _git("worktree", "remove", "--force", str(worktree_path))
```

This removes the worktree registrations but **NOT** the branches.

### Branch Registration Probe

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py`, lines 146–154

```python
def _probe_registrations(worktree_path: Path) -> tuple[bool, bool]:
    """Check parent and submodule worktree registration."""
    parent_list = _git("worktree", "list", "--porcelain", check=False)
    submodule_list = _git(
        "-C", "agent-core", "worktree", "list", "--porcelain", check=False
    )
    parent_reg = str(worktree_path) in parent_list
    submodule_reg = str(worktree_path / "agent-core") in submodule_list
    return parent_reg, submodule_reg
```

This checks if worktrees are registered in git but doesn't check branch state or cleanup branches.

---

## Summary of Code Paths

| Aspect | File | Lines | Details |
|--------|------|-------|---------|
| **rm command entry** | cli.py | 336–399 | Main orchestrator: checks confirm, verifies dirty state, removes worktrees, deletes branch |
| **Dirty check (parent)** | cli.py | 357 | Calls `_is_parent_dirty()` — checks parent repo, not worktree |
| **Dirty check (submodule)** | cli.py | 364 | Calls `_is_submodule_dirty()` — checks agent-core properly |
| **Branch guard** | cli.py | 266–290 | `_guard_branch_removal()` — validates branch can be deleted (merged or focused) |
| **Branch deletion** | cli.py | 293–300 | `_delete_branch()` — deletes parent branch only, no submodule branch deletion |
| **Worktree registration probe** | utils.py | 146–154 | `_probe_registrations()` — checks git worktree registry |
| **Worktree removal** | utils.py | 157–173 | `_remove_worktrees()` — removes worktree registrations via `git worktree remove` |
| **Submodule worktree creation** | cli.py | 147–168 | `_create_submodule_worktree()` — creates branch and worktree in agent-core |
| **Parent dirty check func** | utils.py | 76–95 | `_is_parent_dirty()` — checks parent repo status, filters worktree container |
| **Submodule dirty check func** | utils.py | 98–110 | `_is_submodule_dirty()` — checks agent-core via `-C agent-core` |

---

## Identified Issues Summary

| Bug | Location | Issue | Impact |
|-----|----------|-------|--------|
| **1: Dirty check on wrong repo** | cli.py:357 | `_is_parent_dirty()` checks parent repo, not worktree directory | Verification of correct repo state is inverted |
| **2: Broken worktree cleanup** | cli.py:350–399 | No handling for empty worktree dirs (failed `new`) with no git registration | Orphaned directories left behind |
| **3: Submodule branch not deleted** | cli.py:293–300 | `_delete_branch()` only deletes parent branch, not submodule branch | Stale branches accumulate in agent-core |

