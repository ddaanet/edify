# Cycle 3.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.4: Dirty state detection (git status --porcelain)

**RED Phase:**

**Test:** `test_dirty_state_detection`
**Assertions:**
- Setup: Create git repo, commit tracked file, create clean state
- Clean state: Call _is_dirty(repo_path) → returns False (boolean False, not falsy value)
- Dirty state: Modify tracked file without staging, call _is_dirty(repo_path) → returns True
- Untracked ignored: Create new untracked file, call _is_dirty(repo_path) → returns False (untracked files don't trigger dirty)
- Verification: Uses git status --porcelain --untracked-files=no (exact command, not --short or other variants)

**Expected failure:** NameError: name '_is_dirty' is not defined, or always returns False even when tracked file modified

**Why it fails:** Dirty state detection not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_dirty_state_detection -v`

**GREEN Phase:**

**Implementation:** Run git status --porcelain, check if output is empty

**Behavior:**
- Run: `git -C <tree> status --porcelain --untracked-files=no`
- If output.strip() is empty → is_dirty=False
- Otherwise → is_dirty=True

**Approach:** String emptiness check after strip()

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _is_dirty(tree_path: Path) -> bool
  Location hint: New helper function

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo, modify tracked file without staging
  Location hint: New test function, create dirty tree and verify detection

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_dirty_state_detection -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
