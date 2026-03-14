# Cycle 3.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

## Cycle 3.1: Render Next task

**RED Phase:**

**Test:** `test_render_next_task`, `test_render_next_skips_worktree_markers`, `test_render_next_no_pending`
**File:** `tests/test_session_status.py`

**Assertions:**
- `render_next(tasks)` where first task is pending (checkbox `" "`) with no `→` marker returns:
  ```
  Next: Build parser
    `/runbook plans/parser/design.md`
    Model: sonnet | Restart: no
  ```
- `render_next(tasks)` where first task has `worktree_marker="my-slug"` and second has `worktree_marker="wt"` and third is plain pending → returns third task's info
- `render_next([])` returns `""` (empty string, no Next section)
- Tasks with checkbox `"x"`, `"!"`, `"†"`, `"-"` are all skipped (only `" "` without marker is eligible)

**Expected failure:** `ImportError` — `render_next` doesn't exist

**Why it fails:** No `session/status.py` module

**Verify RED:** `pytest tests/test_session_status.py::test_render_next_task -v`

---
