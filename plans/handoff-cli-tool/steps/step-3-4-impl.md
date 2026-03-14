# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Wire the `status_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `status_cmd` Click command implementation
- Read `agents/session.md` (cwd-relative) → `parse_session()`
- Call `claudeutils _worktree ls` via subprocess for plan states
- Parse `_worktree ls` output for plan status: lines matching `  Plan: {name} [{status}] → ...` — extract name and status into a dict `{name: status}` passed to `render_pending()`
- Check git tree dirty state for session continuation header
- Check plan states for any `review-pending` plans
- Call render functions (session continuation, Next/merged, Pending, Worktree, Unscheduled, Parallel)
- Concatenate non-empty sections with blank line separators, ANSI-colored output
- Output to stdout, exit 0
- Missing session.md → `_fail("**Error:** Session file not found: agents/session.md", code=2)`
- Old format (missing metadata) → exit 2 (fatal, propagated from parser)

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `status_cmd` with full pipeline
  Location hint: Status command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

**Phase 3 Checkpoint:** `just precommit` — status subcommand fully functional.
