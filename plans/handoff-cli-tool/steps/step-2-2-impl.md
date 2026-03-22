# Cycle 2.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 2

---

**GREEN Phase:**

**Implementation:** Extract git changes logic into shared function

**Behavior:**
- New `git_changes() -> str` function in `git_cli.py` containing `changes_cmd`'s output logic
- `changes_cmd` delegates to `git_changes()`
- Handoff CLI imports `git_changes()` and uses it instead of inline subprocess
- Submodule changes now visible in handoff diagnostics

**Changes:**
- File: `git_cli.py`
  Action: Extract function `git_changes() -> str` from `changes_cmd` body
  Location: Before `changes_cmd`

- File: `git_cli.py`
  Action: `changes_cmd` calls `git_changes()` and echoes result
  Location: `changes_cmd` body

- File: `handoff/cli.py`
  Action: Replace lines 57-72 with `from claudeutils.git_cli import git_changes` and call
  Location: After `write_completed` / before `clear_state`

**Verify GREEN:** `just green`
