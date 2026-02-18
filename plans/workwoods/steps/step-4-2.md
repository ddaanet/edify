# Cycle 4.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.2: Porcelain mode preserves existing behavior

**RED Phase:**

**Test:** `test_porcelain_mode_backward_compatible`
**Assertions:**
- Output format matches existing ls output: `<slug>\t<branch>\t<path>`
- Tab-separated fields preserved
- Main tree excluded (existing behavior)
- Uses existing _parse_worktree_list() logic

**Expected failure:** Output format changed or incompatible with existing consumers

**Why it fails:** Porcelain mode not wired to existing logic

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`

**GREEN Phase:**

**Implementation:** When porcelain=True, execute existing ls logic unchanged

**Behavior:**
- if porcelain: run existing code path (_parse_worktree_list + tab output)
- else: run new rich output path (to be implemented)
- Preserve exact output format for porcelain mode

**Approach:** Conditional branch on porcelain flag

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add if/else branch in ls() based on porcelain parameter
  Location hint: Inside ls function body

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real worktree, verify tab-separated output matches expected format
  Location hint: New test function, use tmp_path with git worktree

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---
