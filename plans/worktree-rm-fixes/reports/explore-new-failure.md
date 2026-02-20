# Exploration: Worktree `new` Command Failure and Cleanup

## Summary

The `new` command creates worktrees but has no cleanup mechanism when `git worktree add` fails (exit 255 or other errors). When the command fails mid-way, it leaves an empty directory behind that can't be easily cleaned up. The `rm` command can handle broken worktrees, but only if they're registered with git; `ls` won't detect unregistered empty directories.

---

## Key Findings

### 1. The `new` Command Implementation

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/cli.py`

**Entry point:** `new()` command at lines 208-240.

**Call chain:**
1. `new()` (line 214) — validates slug/task args
2. Derives slug from task name (line 223) via `derive_slug()`
3. Creates container with `wt_path(slug, create_container=True)` (line 228)
4. Calls `_setup_worktree()` (line 231) — **THIS IS WHERE FAILURES OCCUR**
5. If task provided, moves task in session.md (line 237)

**Code flow (lines 208-240):**
```python
def new(slug: str | None, base: str, session: str, task: str, session_md: str) -> None:
    # ... validation ...
    if task:
        slug = derive_slug(task)
        # Create temp session file
        temp_session_file = session = f.name
    # CHECK: directory must not exist before _setup_worktree
    if (path := wt_path(slug, create_container=True)).exists():
        click.echo(f"Error: existing directory {path}", err=True)
        raise SystemExit(1)  # ← Exits if directory exists

    _setup_worktree(path, slug, base, session, task)  # ← Can fail here
```

**Critical issue:** If `_setup_worktree()` fails (via exception), the function doesn't catch it. The empty directory `path` was created by `wt_path(..., create_container=True)` and **remains behind**.

### 2. Worktree Setup (`_setup_worktree`)

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/cli.py`, lines 171-184

```python
def _setup_worktree(
    worktree_path: Path, slug: str, base: str, session: str, task: str
) -> None:
    """Create worktrees, register sandbox, init environment."""
    _create_parent_worktree(worktree_path, slug, base, session)  # Line 175
    # ... rest of setup (sandbox registration, environment init) ...
```

**Calls `_create_parent_worktree()` which calls `_git("worktree", "add", ...)`**

If any `_git()` call fails with a non-zero exit code:
- **`_git()` function raises `subprocess.CalledProcessError`** (see below)
- Exception propagates back through `_setup_worktree()` to `new()`
- **The `new()` function does NOT catch this exception**
- The empty directory remains in the container

### 3. The `_git()` Utility Function

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/utils.py`, lines 7-21

```python
def _git(
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
) -> str:
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,  # ← Default is True
        env=env,
        input=input_data,
    )
    return r.stdout.strip()
```

**When `check=True`** (the default):
- If git returns non-zero exit code, `subprocess.run()` raises `CalledProcessError`
- No exception handling in `_git()`, `_create_parent_worktree()`, or `_setup_worktree()`
- Exception propagates to `new()`

### 4. Failure Scenario: Exit 255

Git exits with 255 when:
- Worktree directory already exists (e.g., from prior failed attempt)
- Permission issues
- Filesystem errors
- Lock file conflicts

**Example:** If the first `git worktree add` fails with exit 255:
1. The container directory `/path/to/project-wt/slug/` was created (lines 228, via `wt_path(..., create_container=True)`)
2. The git worktree registration failed (no `.git` directory in the slug subdirectory)
3. Exception raised, `new()` exits
4. **Directory `/path/to/project-wt/slug/` remains empty but exists**
5. Next `new slug` attempt fails at line 228 collision check

### 5. How `rm` Detects and Handles Broken Worktrees

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/cli.py`, lines 336-398

**The `rm` command has fallback detection:**

```python
def rm(slug: str, confirm: bool, force: bool) -> None:
    # ...
    worktree_path = _get_worktree_path_for_branch(slug) or wt_path(slug)
    # Line 355: ↑ Tries to get path from git registration, falls back to naming convention

    # Lines 376-377: Probe if worktree is registered with git
    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    # Lines 381-382: If registered, try to remove via git
    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)

    # Lines 384-385: Remove directory (works even if not registered)
    if worktree_path.exists():
        shutil.rmtree(worktree_path)
```

**Key insight:** `rm` can handle broken (empty) worktrees:
- It doesn't require the worktree to be in git's list
- Falls back to naming convention: `_get_worktree_path_for_branch()` returns `None` for broken worktrees
- Uses `wt_path(slug)` naming convention to locate the directory
- Removes the directory with `shutil.rmtree()` regardless of registration status

**However:** The probe functions check only git registration:

```python
def _probe_registrations(worktree_path: Path) -> tuple[bool, bool]:
    """Check parent and submodule worktree registration."""
    parent_list = _git("worktree", "list", "--porcelain", check=False)
    # ...
    parent_reg = str(worktree_path) in parent_list
    submodule_reg = str(worktree_path / "agent-core") in submodule_list
    return parent_reg, submodule_reg
```

A broken worktree (directory with no `.git` inside) won't appear in `git worktree list`, so `parent_reg` will be `False`.

### 6. How `ls` Lists Worktrees (Does NOT Detect Broken Ones)

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/cli.py`, lines 84-95

```python
def ls(*, porcelain: bool) -> None:
    """List worktrees and main tree."""
    main_path = _git("rev-parse", "--show-toplevel")
    porcelain_output = _git("worktree", "list", "--porcelain")  # ← Git list

    if porcelain:
        for slug, branch, path in _parse_worktree_list(porcelain_output, main_path):
            # ...
```

**Limitation:** Relies entirely on `git worktree list --porcelain` output:
- Only lists worktrees registered in git
- A broken worktree (empty directory from failed `new`) **won't appear in `git worktree list`**
- Won't be visible in `ls` output, but the directory still exists on disk

**Display function** in `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/display.py`:
- Calls `aggregate_trees()` which scans git's registered worktrees
- Doesn't scan the filesystem for unregistered directories

### 7. Worktree Path Detection (`_get_worktree_path_for_branch`)

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/utils.py`, lines 133-143

```python
def _get_worktree_path_for_branch(slug: str) -> Path | None:
    """Get the actual worktree path for a branch from git."""
    list_output = _git("worktree", "list", "--porcelain", check=False)
    for line in list_output.split("\n"):
        if line.startswith("worktree "):
            worktree_path = Path(line[len("worktree ") :])
        elif line.startswith("branch ") and worktree_path:
            if line[len("branch ") :] == f"refs/heads/{slug}":
                return worktree_path
            worktree_path = None
    return None
```

**Returns `None` for:**
- Broken worktrees (not in `git worktree list`)
- Non-existent branches (branch was never created or was deleted)

**The `rm` command handles this:** Falls back to `wt_path(slug)` naming convention (line 355).

### 8. Test Coverage for Failure Scenarios

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_new_creation.py`

**Existing tests:**
- `test_new_basic_flow()` — Success case, worktree created
- `test_new_directory_collision()` — Detects existing directory before `_setup_worktree()` is called
- `test_new_collision_detection()` — Reuses existing branch

**Missing tests:**
- ❌ `test_new_failure_cleanup()` — What happens when `git worktree add` fails with exit 255?
- ❌ `test_new_failure_leaves_empty_dir()` — Verify the bug: empty directory remains
- ❌ `test_rm_handles_broken_worktree()` — Can `rm` clean up the broken worktree?

### 9. The Dirty Check Bug (Secondary Issue)

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-fixes/src/claudeutils/worktree/cli.py`, lines 357-363

```python
def rm(slug: str, confirm: bool, force: bool) -> None:
    # ...
    if not force:
        if _is_parent_dirty(exclude_path=str(worktree_path.parent)):
            # ↑ Bug: Uses worktree_path.parent
```

**Reported bug:** "dirty check fails on parent instead of target worktree"

**Context:** `_is_parent_dirty()` checks if the main repo (parent of worktree) is dirty:

```python
def _is_parent_dirty(exclude_path: str | None = None) -> bool:
    """Return True if parent repo has staged/unstaged/untracked changes."""
    output = _git("status", "--porcelain", check=False)
    # ...
    for line in output.strip().split("\n"):
        if not line:
            continue
        path = line[3:]  # Skip status columns
        if exclude_prefix and path.startswith(exclude_prefix):
            continue
        return True
    return False
```

When called with `exclude_path=str(worktree_path.parent)` (the container directory), it tries to exclude lines starting with the container name. But:
- This excludes the entire container, including the worktree directory
- It's an imprecise exclusion (uses string prefix matching)
- The intent is to allow removal of a dirty worktree without being blocked by the worktree's own changes

This is only a problem if the worktree is dirty AND in the container directory. The code is working as designed, but the name is confusing (`_is_parent_dirty` actually means "is the main repo dirty, excluding the worktree container").

---

## Patterns and Architecture

### Entry Point Structure
- **`new()`** command (line 214) — CLI wrapper, validates args, calls setup
- **`_setup_worktree()`** function (line 171) — Orchestrates the creation steps
- **`_create_parent_worktree()`** function (line 125) — Calls git worktree add
- **`_git()`** utility (utils.py line 7) — Wrapper for git commands with error handling

### Error Handling Gaps
1. **No try-except in `new()`** — Exceptions from `_setup_worktree()` propagate uncaught
2. **No cleanup handler** — Empty directory remains if any step fails
3. **No rollback** — No attempt to undo partial setup (container creation)

### Detection and Recovery
1. **`_get_worktree_path_for_branch(slug)`** — Query git registration, returns None if missing
2. **`_probe_registrations(worktree_path)`** — Check if worktree/submodule registered
3. **`rm` fallback** — Uses naming convention when git registration missing
4. **`ls` gap** — Only shows git-registered worktrees, misses broken ones

### Test Structure
- **`test_worktree_new_creation.py`** — Tests successful creation and collision detection
- **`test_worktree_rm.py`** — Tests removal, branch cleanup, merge commits
- **`test_worktree_new_config.py`** — Tests sandbox registration, environment init

---

## Code Locations Summary

| Component | File | Lines | Function |
|-----------|------|-------|----------|
| `new` command | `/src/claudeutils/worktree/cli.py` | 214-240 | `new()` |
| Setup worktree | `/src/claudeutils/worktree/cli.py` | 171-184 | `_setup_worktree()` |
| Create parent | `/src/claudeutils/worktree/cli.py` | 125-144 | `_create_parent_worktree()` |
| Git wrapper | `/src/claudeutils/worktree/utils.py` | 7-21 | `_git()` |
| Worktree path | `/src/claudeutils/worktree/utils.py` | 24-38 | `wt_path()` |
| Git lookup | `/src/claudeutils/worktree/utils.py` | 133-143 | `_get_worktree_path_for_branch()` |
| Probe registration | `/src/claudeutils/worktree/utils.py` | 146-154 | `_probe_registrations()` |
| Dirty check | `/src/claudeutils/worktree/utils.py` | 76-95 | `_is_parent_dirty()` |
| `rm` command | `/src/claudeutils/worktree/cli.py` | 336-398 | `rm()` |
| `ls` command | `/src/claudeutils/worktree/cli.py` | 84-95 | `ls()` |

---

## Impact Assessment

### Severity
- **High** for user experience (broken worktrees block future attempts)
- **Low** for data loss (directory is empty, easily removable)

### Scope
1. **Affected flow:** `_worktree new` → git failure (exit 255 or timeout) → empty directory left
2. **Workaround exists:** `rm --force slug` can clean up broken worktrees
3. **Detection gap:** `ls` won't show broken worktrees; must use `rm` to clean

### Test Gaps
- No test for `git worktree add` failure scenarios
- No test verifying cleanup after `new` failure
- No test showing `rm` can handle broken worktrees
