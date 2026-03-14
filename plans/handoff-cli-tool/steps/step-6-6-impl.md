# Cycle 6.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Wire the `commit_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `commit_cmd` Click command implementation
- Read all stdin → `parse_commit_input()`
- Call `commit_pipeline(input)` → `CommitResult`
- Output `result.output` to stdout
- Exit 0 on success, 1 on pipeline error, 2 on input validation error

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `commit_cmd` with full pipeline
  Location hint: Commit command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

**Phase 6 Checkpoint:** `just precommit` — commit subcommand fully functional.
