# Phase 1: Path Computation and CLI Registration

**Complexity:** Medium (4 cycles)
**Files:**
- `src/claudeutils/cli.py`
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Register CLI group and extract path computation logic into testable function.

**Dependencies:** None (foundation phase)

---

## Cycle 1.1: `wt_path()` basic path construction with CLI group registration

**Objective:** Register worktree CLI group and extract path computation into testable function for the simplest case (repository not in worktree container).

**Prerequisite:** Read `src/claudeutils/cli.py` lines 1-50 — understand Click group registration pattern and existing command structure. Read `src/claudeutils/worktree/cli.py` lines 1-100 — understand existing worktree creation logic and path handling patterns.

**RED Phase:**

**Test:** `test_wt_path_not_in_container`
**Assertions:**
- Import succeeds: `from claudeutils.worktree.cli import worktree` does not raise ImportError
- Group is callable: `isinstance(worktree, click.Group)` is True
- `wt_path("feature-a")` returns Path ending with `claudeutils-wt/feature-a`
- Returned path parent directory name ends with `-wt`
- Returned path is absolute (not relative)
- Container directory does not exist yet (creation happens later)

**Expected failure:** ImportError (group not registered in main CLI) or NameError (function `wt_path` not defined)

**Why it fails:** `cli.add_command(worktree)` not yet added to main CLI, and `wt_path()` function doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`

---

**GREEN Phase:**

**Implementation:** Register worktree CLI group and extract path computation into standalone `wt_path(slug)` function

**Behavior:**
- Import statement added to main CLI imports section
- Command registered via `cli.add_command(worktree)` call
- Underscore prefix automatically hides from help (Click convention)
- New `wt_path(slug)` function takes slug as string input, returns Path object
- Detects current directory is NOT in `-wt` container (parent name doesn't end with `-wt`)
- Constructs container name: `<current-repo-name>-wt`
- Returns: `<parent-of-repo>/<repo-name>-wt/<slug>`

**Approach:** Follow existing command registration pattern in `src/claudeutils/cli.py`, then port bash `wt-path()` function logic from justfile (lines 100-120)

**Changes:**
- File: `src/claudeutils/cli.py`
  Action: Add import `from claudeutils.worktree.cli import worktree` at top
  Location hint: With other command imports
- File: `src/claudeutils/cli.py`
  Action: Add `cli.add_command(worktree)` registration call
  Location hint: After other command registrations
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `wt_path(slug: str) -> Path` before `new` command definition
  Location hint: At module level, before command functions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement logic — detect parent directory, check for `-wt` suffix, construct container path if not in container
  Location hint: Function body uses `Path.cwd()`, `.parent.name`, string operations

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_cli_*.py -v`
- All existing CLI tests pass

---

## Cycle 1.2: Container detection and sibling paths

**Objective:** Detect when repository is already inside a worktree container directory and verify sibling path logic for multiple worktrees.

**RED Phase:**

**Test:** `test_wt_path_in_container`
**Assertions:**
- When `Path.cwd().parent.name` ends with `-wt`, `wt_path("feature-b")` returns sibling path (not nested container)
- Returned path is `<parent-container>/<slug>` (parent already is the container)
- Path does NOT contain nested `-wt/-wt` structure
- Container name matches parent directory name exactly
- Multiple slugs produce different paths: `wt_path("wt-a")` and `wt_path("wt-b")` return different paths
- Both paths share same parent directory (the container)
- Paths differ only in final slug component
- Neither path creates nested containers

**Expected failure:** AssertionError: path contains nested `-wt/-wt` or doesn't recognize existing container

**Why it fails:** Container detection logic not yet implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_in_container -v`

---

**GREEN Phase:**

**Implementation:** Add container detection branch to `wt_path()` function

**Behavior:**
- Check if `Path.cwd().parent.name.endswith('-wt')`
- If true: current directory is already in a container, return `parent/<slug>`
- If false: use existing logic from 1.1 (create new container path)
- Function is stateless (pure function of slug input) — each call with different slug returns different path with same parent

**Approach:** Conditional branch at function start — container check determines path construction strategy

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add container detection conditional at start of `wt_path()` function
  Location hint: Before existing path construction logic from 1.1

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_in_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`
- Cycle 1.1 test still passes (existing behavior preserved)

---

## Cycle 1.3: Container creation — directory materialization

**Objective:** Create container directory when it doesn't exist (filesystem side effect).

**RED Phase:**

**Test:** `test_wt_path_creates_container`
**Assertions:**
- Before calling `wt_path()`, container directory doesn't exist
- After calling `wt_path("slug", create_container=True)`, container directory exists on filesystem
- Created directory has correct name (`<repo-name>-wt`)
- Created directory is empty (no files inside)
- Directory permissions are default (0o755 on Unix)

**Expected failure:** AssertionError: container directory doesn't exist after function call, or NameError: `create_container` parameter doesn't exist

**Why it fails:** `wt_path()` currently only computes paths, doesn't create directories

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_creates_container -v`

---

**GREEN Phase:**

**Implementation:** Add optional container creation to `wt_path()` function

**Behavior:**
- Add `create_container: bool = False` parameter to function signature
- When `create_container=True` and not in container, create the container directory
- Use `Path.mkdir(parents=True, exist_ok=True)` for idempotent creation
- Only create when NOT already in container (no-op if in container)

**Approach:** Conditional directory creation after path computation, only when flag is True and container doesn't exist

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `create_container` parameter to `wt_path()` signature
  Location hint: After `slug` parameter, with default `False`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add directory creation logic after path computation (when not in existing container)
  Location hint: At end of function, conditional on parameter

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_creates_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous tests still pass (default `create_container=False` preserves existing behavior)

---

## Cycle 1.4: Edge cases — special characters, root directory, deep nesting

**Objective:** Handle edge cases in path computation (unusual but valid scenarios).

**RED Phase:**

**Test:** `test_wt_path_edge_cases`
**Assertions:**
- Slug with special characters preserved in path: `wt_path("fix-bug#123")` includes `#123` in path
- From root directory: `wt_path("test")` doesn't crash, constructs valid path
- From deeply nested directory (5+ levels): path construction still works correctly
- Empty container case: if manually in empty `-wt` directory, sibling path still computed

**Expected failure:** Various: ValueError on special chars, error on root directory, incorrect path from deep nesting

**Why it fails:** Edge cases not yet handled in path computation logic

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_edge_cases -v`

---

**GREEN Phase:**

**Implementation:** Add edge case handling to `wt_path()` function

**Behavior:**
- Special characters in slug: preserve as-is (filesystem will handle)
- Root directory: detect via `Path.cwd() == Path("/")`, construct reasonable container path
- Deep nesting: existing logic already handles (uses `.parent` which works at any depth)
- Error on truly invalid slug (e.g., empty string, only whitespace): raise ValueError

**Approach:** Add validation at function start, handle root directory special case, rely on pathlib for deep nesting

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add slug validation at function start (check for empty/whitespace)
  Location hint: First lines of function
- File: `src/claudeutils/worktree/cli.py`
  Action: Add root directory detection and handling
  Location hint: Before container detection logic

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_edge_cases -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous tests still pass

---
