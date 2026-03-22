# Cycle 3.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

**GREEN Phase:**

**Implementation:** Add continuation header rendering

**Behavior:**
- New `render_continuation(is_dirty: bool, plan_states: dict) -> str` function
- Checks dirty state (import `_is_dirty` from `git.py`)
- If dirty, builds "Session: uncommitted changes — `/handoff`, `/commit`"
- Scans plan_states for `review-pending`, appends deliverable-review command
- Continuation header is first section in output

**Changes:**
- File: `status/render.py`
  Action: Add `render_continuation` function
  Location: New function at module level

- File: `status/cli.py`
  Action: Call `_is_dirty()`, call `render_continuation`, prepend to sections
  Location: Before In-tree sections

**Verify GREEN:** `just green`
