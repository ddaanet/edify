# Cycle 3.3

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.3: Output format alignment

**Finding:** M#9

**Prerequisite:** Read `src/claudeutils/session/status/render.py:8-57` — current rendering

---

**RED Phase:**

**Test:** `test_status_format_merged_next`
**Assertions:**
- First eligible pending task in In-tree list is prefixed with `▶`
- No separate `Next:` section in output when first in-tree is next task
- First task line includes command in backticks, model, and restart metadata
- Non-first tasks show model (if non-default) but not command/restart

**Expected failure:** `AssertionError` — separate `Next:` section always rendered, `render_pending` uses `- name` without `▶`

**Why it fails:** `render_next` always generates separate section; `render_pending` doesn't distinguish first task.

**Verify RED:** `pytest tests/test_session_status.py::test_status_format_merged_next -v`

---
