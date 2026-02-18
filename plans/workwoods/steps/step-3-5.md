# Cycle 3.5

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.5: Task summary from session.md (first pending task)

**RED Phase:**

**Test:** `test_task_summary_extraction`
**Assertions:**
- Setup: Create git repo with agents/session.md containing "## Pending Tasks\n- [ ] **Fix bug** — description"
- Call _task_summary(repo_path) → returns string "Fix bug" (task name only, not markdown formatting)
- Edge case: session.md exists but no Pending Tasks section → returns None (not exception)
- Edge case: Pending Tasks section empty (no task lines) → returns None
- Edge case: session.md file doesn't exist → returns None (not FileNotFoundError)
- Verification: Uses extract_task_blocks(content, section="Pending Tasks") and returns blocks[0].name

**Expected failure:** NameError: name '_task_summary' is not defined, or returns None when pending task exists

**Why it fails:** Session.md reading and task extraction not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_task_summary_extraction -v`

**GREEN Phase:**

**Implementation:** Read session.md, call extract_task_blocks(), return first task name

**Behavior:**
- Check if <tree>/agents/session.md exists
- If not exists: return None
- Read file content
- Call extract_task_blocks(content, section="Pending Tasks")
- If blocks empty: return None
- Otherwise: return blocks[0].name

**Approach:** Import extract_task_blocks from worktree.session module

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _task_summary(tree_path: Path) -> str | None
  Location hint: New helper function, imports extract_task_blocks

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo, write session.md with pending task
  Location hint: New test function, verify correct task name extracted

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_task_summary_extraction -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
