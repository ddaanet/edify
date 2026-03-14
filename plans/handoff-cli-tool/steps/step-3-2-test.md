# Cycle 3.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

## Cycle 3.2: Render list sections with parametrized tests

**RED Phase:**

**Test:** `test_render_section[pending]`, `test_render_section[worktree]`, `test_render_section[unscheduled]`, `test_render_empty_section[pending]`, `test_render_empty_section[worktree]`, `test_render_empty_section[unscheduled]`
**File:** `tests/test_session_status.py`

**Assertions — In-tree section:**
- `render_pending(tasks, plan_states)` with two tasks returns:
  ```
  In-tree:
  ▶ Build parser (sonnet)
    `/runbook plans/parser/design.md`
    Plan: parser | Status: outlined
  - Fix bug (haiku)
  ```
- First pending task gets `▶` marker with command when Next is suppressed (single-task or first-in-tree case)
- Task with non-default model shows `(model)`. Default (sonnet) omitted
- Task with associated plan directory shows nested plan/status line
- Completed tasks (`checkbox == "x"`) excluded

**Assertions — Worktree section:**
- `render_worktree(tasks)` with branched task returns:
  ```
  Worktree:
  - Parallel work → my-slug
  - Future work → wt
  ```
- `→ slug` for branched tasks, `→ wt` for destined-but-not-yet-branched

**Assertions — Unscheduled Plans section:**
- `render_unscheduled(all_plans, task_plan_dirs)` with plans not associated to any task returns:
  ```
  Unscheduled Plans:
  - orphan-plan — designed
  ```
- Plans with status `delivered` excluded
- Sorted alphabetically
- Plans associated to any pending task excluded

**Empty section assertions (all three):**
- Each render function returns `""` when input list is empty

**Additional test:** `test_render_session_continuation`
**Assertions:**
- `render_session_continuation(is_dirty=True, review_pending_plans=[])` returns `Session: uncommitted changes — \`/handoff\`, \`/commit\``
- `render_session_continuation(is_dirty=True, review_pending_plans=["foo"])` returns `Session: uncommitted changes — \`/handoff\`, \`/commit\`, \`/deliverable-review plans/foo\``
- `render_session_continuation(is_dirty=False, review_pending_plans=[])` returns `""` (omit entirely when clean)

**Expected failure:** `ImportError` — render functions don't exist

**Why it fails:** No rendering functions for these sections

**Verify RED:** `pytest tests/test_session_status.py -k "render_section or render_empty or render_session" -v`

---
