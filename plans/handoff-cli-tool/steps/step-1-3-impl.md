# Cycle 1.3

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

**GREEN Phase:**

**Implementation:** Let CleanFileError propagate to CLI for exit code routing

**Behavior:**
- Remove `try/except CleanFileError` from `commit_pipeline` — let it propagate
- CLI catches `CleanFileError` specifically, displays message, exits 2
- Per "context at failure, display at top" — validate_files provides context, CLI routes exit code
- Other failures continue through `CommitResult(success=False)` → exit 1

**Changes:**
- File: `commit_pipeline.py`
  Action: Remove lines 229-236 (try/except CleanFileError), let it propagate
  Location: `commit_pipeline` function

- File: `cli.py`
  Action: Add `except CleanFileError as e` before the pipeline call result check, echo and exit 2
  Location: `commit_cmd` function

**Verify GREEN:** `just green`
