# Cycle 3.3

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

**GREEN Phase:**

**Implementation:** Merge next-task metadata into In-tree list

**Behavior:**
- `render_pending` marks first eligible pending task with `▶` prefix
- First task includes command, model, restart on its line
- Remove `render_next` call from CLI (Next section eliminated)
- Non-first tasks: name + model (if non-default) only

**Changes:**
- File: `status/render.py`
  Action: Modify `render_pending` — first eligible task gets `▶` + full metadata
  Location: `render_pending` function

- File: `status/cli.py`
  Action: Remove `render_next` call and its section append
  Location: Lines 38-41

**Verify GREEN:** `just green`
