# Phase 6: Update `rm` Command

**Complexity:** Medium (5 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Refactor `rm` command with improved removal logic — submodule-first ordering, container cleanup, safe branch deletion.

**Dependencies:** Phase 1 (needs `wt_path()` for path resolution)

---

## Cycle 6.1: Refactor `rm` to use `wt_path()` and add uncommitted changes warning

**Objective:** Update `rm` command to use `wt_path()` for consistent path resolution and warn about dirty trees.

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` — understand current `rm` command implementation.

**RED Phase:**

**Test:** `test_rm_command_path_resolution`
**Assertions:**
- `claudeutils _worktree rm test-slug` resolves to sibling container path `<repo>-wt/test-slug`
- Path resolution consistent with `new` command (uses same `wt_path()` function)
- When worktree has uncommitted changes: warning printed before removal
- Warning contains count of uncommitted files: "Warning: worktree has N uncommitted files"
- Removal proceeds after warning (not blocked)

**Expected failure:** AssertionError: wrong path used, or no warning on dirty tree

**Why it fails:** Command uses hardcoded path logic, doesn't check for uncommitted changes

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`

---

**GREEN Phase:**

**Implementation:** Refactor to use `wt_path()` and add dirty tree check

**Behavior:**
- Replace path construction with `wt_path(slug)` call (no create_container flag for removal)
- Check if worktree path exists on filesystem
- If exists: run `git -C <wt-path> status --porcelain` to check for uncommitted changes
- If output non-empty: count lines, print warning (don't block removal)
- Proceed with removal logic

**Approach:** Replace path logic, add subprocess status check, conditional warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace path construction in `rm` command with `wt_path(slug)` call
  Location hint: Near start of function
- File: `src/claudeutils/worktree/cli.py`
  Action: Add dirty tree check using git status
  Location hint: After path resolution, before removal steps
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning if uncommitted changes found
  Location hint: Conditional on status --porcelain output

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All existing `rm` command tests still pass

---

## Cycle 6.2: Worktree registration probing — parent and submodule

**Objective:** Detect whether parent and/or submodule worktrees are registered (handle partial states).

**RED Phase:**

**Test:** `test_rm_worktree_registration_probing`
**Assertions:**
- Given registered parent worktree at `<wt-path>`: `git worktree list` contains path
- Given registered submodule worktree at `<wt-path>/agent-core`: `git -C agent-core worktree list` contains path
- Probe detects: both registered, only parent, only submodule, neither registered
- Function handles all four states without error
- Registration info used to decide removal commands (probed state determines which `git worktree remove` calls to make)

**Expected failure:** Error when worktree not registered, or wrong removal commands attempted

**Why it fails:** No registration probing, assumes both always registered

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_worktree_registration_probing -v`

---

**GREEN Phase:**

**Implementation:** Add registration detection for parent and submodule worktrees

**Behavior:**
- Parse `git worktree list --porcelain` output to check if `<wt-path>` is registered
- Parse `git -C agent-core worktree list --porcelain` to check if `<wt-path>/agent-core` is registered
- Use path matching (not grep) for reliable detection
- Store boolean flags: `parent_registered`, `submodule_registered`
- Use flags to conditionally execute removal commands (only remove what's registered)

**Approach:** Two subprocess calls with output parsing, path-based matching, boolean flags

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent registration check in `rm` command
  Location hint: Run `git worktree list --porcelain`, parse output for `<wt-path>`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule registration check
  Location hint: Run `git -C agent-core worktree list --porcelain`, parse for `<wt-path>/agent-core`
- File: `src/claudeutils/worktree/cli.py`
  Action: Store registration state as boolean flags
  Location hint: Two variables tracking parent and submodule registration

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_worktree_registration_probing -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`
- Cycle 6.1 test still passes

---

## Cycle 6.3: Submodule-first removal ordering

**Objective:** Remove submodule worktree BEFORE parent worktree (git enforces this order).

**Prerequisite:** Read design lines 109-112 — understand submodule-first removal ordering requirement and git error message.

**RED Phase:**

**Test:** `test_rm_submodule_first_ordering`
**Assertions:**
- Removal order: submodule worktree removed first, parent worktree second
- When both registered: `git -C agent-core worktree remove --force <path>/agent-core` runs before `git worktree remove --force <path>`
- If order violated (parent first): git refuses with error "fatal: 'remove' refusing to remove..."
- Test verifies correct order by checking command sequence (mock subprocess to track order)
- When only parent registered: only parent removal attempted (no submodule command)

**Expected failure:** AssertionError: wrong removal order, or error from git when order violated

**Why it fails:** Removal order not enforced, or both commands attempted regardless of registration state

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_submodule_first_ordering -v`

---

**GREEN Phase:**

**Implementation:** Enforce submodule-first removal order using registration flags

**Behavior:**
- If `submodule_registered == True`: run `git -C agent-core worktree remove --force <wt-path>/agent-core`
- Then, if `parent_registered == True`: run `git worktree remove --force <wt-path>`
- Order guaranteed by sequential execution (submodule first, then parent)
- Use `--force` flag to bypass uncommitted changes warnings (already warned in 6.1)

**Approach:** Sequential subprocess calls conditional on registration flags, explicit ordering

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule removal in `rm` command
  Location hint: First removal step, conditional on `submodule_registered`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent removal after submodule removal
  Location hint: Second removal step, conditional on `parent_registered`
- File: `src/claudeutils/worktree/cli.py`
  Action: Use `--force` flag for both removals
  Location hint: In git worktree remove commands

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_submodule_first_ordering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Cycle 6.1 and 6.2 tests still pass

---

## Cycle 6.4: Post-removal cleanup — orphaned directories and empty container

**Objective:** Clean up orphaned worktree directories and empty containers after git removal.

**RED Phase:**

**Test:** `test_rm_post_removal_cleanup`
**Assertions:**
- After git worktree removal, if `<wt-path>` still exists (orphaned): directory removed with `shutil.rmtree()`
- After directory removal, if container is empty: container directory removed with `os.rmdir()`
- Empty check uses `os.listdir()` returning empty list
- Non-empty container NOT removed (other worktrees present)
- Cleanup idempotent (running twice has same effect as once)

**Expected failure:** AssertionError: orphaned directories remain, or non-empty container removed, or FileNotFoundError

**Why it fails:** No filesystem cleanup after git commands

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_post_removal_cleanup -v`

---

**GREEN Phase:**

**Implementation:** Add filesystem cleanup logic after git removal

**Behavior:**
- After git worktree remove commands: check if `<wt-path>` still exists
- If exists (orphaned): use `shutil.rmtree()` to remove directory tree
- After path cleanup: get container directory (parent of `<wt-path>`)
- Check if container empty: `not os.listdir(container_path)`
- If empty: remove container with `os.rmdir()`
- If not empty or doesn't exist: skip container removal

**Approach:** Filesystem checks with conditional cleanup, use pathlib for path operations

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add orphaned directory cleanup in `rm` command
  Location hint: After git worktree remove commands
- File: `src/claudeutils/worktree/cli.py`
  Action: Check if `<wt-path>` exists, remove with `shutil.rmtree()` if present
  Location hint: Use `Path.exists()` and `shutil.rmtree()`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add container cleanup logic
  Location hint: After path cleanup
- File: `src/claudeutils/worktree/cli.py`
  Action: Check if container empty, remove with `os.rmdir()` if empty
  Location hint: Use `os.listdir()` for empty check, `os.rmdir()` for removal

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_post_removal_cleanup -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous Cycle 6 tests still pass

---

## Cycle 6.5: Safe branch deletion — `-d` with fallback warning

**Objective:** Use safe branch deletion (`-d`) that checks merge status, warn on unmerged instead of force-deleting.

**RED Phase:**

**Test:** `test_rm_safe_branch_deletion`
**Assertions:**
- Branch deletion uses `git branch -d <slug>` (NOT `-D`)
- When branch fully merged: deletion succeeds, no warning
- When branch has unmerged changes: deletion fails, warning printed
- Warning message: "Branch <slug> has unmerged changes. Use: git branch -D <slug>"
- Warning includes manual command for user (no automatic force-delete)
- Exit code 0 even when branch deletion fails (warning, not error)

**Expected failure:** AssertionError: `-D` used instead of `-d`, or error raised on unmerged branch, or no warning printed

**Why it fails:** Command uses `-D` (force delete) or doesn't handle unmerged branch case

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_safe_branch_deletion -v`

---

**GREEN Phase:**

**Implementation:** Add safe branch deletion with graceful failure handling

**Behavior:**
- Run `git branch -d <slug>` with `check=False` (capture exit code)
- If exit code 0 (success): deletion complete
- If exit code ≠ 0 (unmerged): print warning message with manual `-D` command
- Do NOT run `git branch -D` automatically (user decision required)
- Continue execution (don't raise exception on unmerged)

**Approach:** Subprocess with error handling, conditional warning, no automatic force-delete

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch deletion in `rm` command
  Location hint: After directory cleanup
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `git branch -d <slug>` with `check=False`
  Location hint: Use subprocess.run, capture exit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Check exit code, print warning if non-zero
  Location hint: Conditional on exit code, include manual `-D` command in message

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_safe_branch_deletion -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 6 tests still pass

---

**Checkpoint: Post-Phase 6**

**Type:** Light checkpoint (Fix + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Functional:** Review removal ordering against design.
   - Check: Is submodule-first ordering enforced (FR-5 critical correctness constraint)?
   - Check: Does registration probing handle all four states (both, parent-only, sub-only, neither)?
   - Check: Does container cleanup handle non-empty containers correctly?
   - If ordering wrong: STOP, report
   - If all correct: Proceed to Phase 7

**Rationale:** Phase 6 has complex data manipulation (subprocess output parsing) and a critical correctness constraint (submodule-first removal ordering). 17 cycles between Phase 5 and Phase 7 checkpoints exceeds >10 cycle threshold without this gate.
