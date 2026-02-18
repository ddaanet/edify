# Cycle 3.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.2: Detect main tree (is_main=True, slug=None)

**RED Phase:**

**Test:** `test_main_tree_detection`
**Assertions:**
- Input: list with 3 TreeInfo objects representing main + 2 worktrees
- First TreeInfo: is_main field equals True (boolean True, not truthy value)
- First TreeInfo: slug field equals None (not empty string)
- Second TreeInfo: is_main equals False, slug equals "worktree-1" (extracted from path "/path/wt/worktree-1")
- Third TreeInfo: is_main equals False, slug equals "worktree-2" (extracted from path "/path/wt/worktree-2")
- Slug extraction verifies basename only (path.name, not parent directories)

**Expected failure:** AssertionError: TreeInfo object missing is_main or slug attributes, or is_main=False for first tree

**Why it fails:** Main tree detection logic not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_main_tree_detection -v`

**GREEN Phase:**

**Implementation:** Mark first worktree as main, extract slug from path for others

**Behavior:**
- First TreeInfo in list → is_main=True, slug=None
- Other TreeInfo → is_main=False, slug=path.name (basename)
- Use Path(tree_path).name to extract slug

**Approach:** Enumerate over parsed worktrees, check index == 0 for main

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add is_main and slug fields to TreeInfo, compute based on position
  Location hint: In _parse_worktree_list() or separate post-processing

- File: `src/claudeutils/planstate/models.py`
  Action: Add is_main and slug fields to TreeStatus dataclass
  Location hint: TreeStatus definition

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with porcelain output containing main + 2 worktrees
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_main_tree_detection -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
