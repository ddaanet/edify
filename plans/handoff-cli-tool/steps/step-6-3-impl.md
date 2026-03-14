# Cycle 6.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Add amend support to `commit_pipeline()`

**Behavior:**
- If `amend` in `input.options`: add `--amend` to `git commit` args
- If `no-edit` in `input.options`: add `--no-edit` to `git commit` args, `## Message` section not used
- Pass `amend=True` to `validate_files()` — enables HEAD file acceptance
- Submodule amend: `_git("-C", path, "commit", "--amend", "-m", message)` then re-stage pointer
- Submodule amend + `no-edit`: `_git("-C", path, "commit", "--amend", "--no-edit")` then re-stage pointer

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add amend and no-edit flag handling throughout pipeline

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
