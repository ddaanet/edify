# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

**GREEN Phase:**

**Implementation:** Add metadata validation after parsing

**Behavior:**
- After `parse_session`, validate in_tree_tasks have required metadata
- Tasks without command metadata → `_fail("**Error:** Old-format tasks ...")` with exit 2
- Detection: compare raw block count to parsed task count, or check metadata
- Alternative: validate task.command is not None for each parsed task

**Changes:**
- File: `status/cli.py`
  Action: Add validation comparing raw block count to parsed task count, or check metadata
  Location: After `parse_session` call, before rendering

**Verify GREEN:** `just green`
