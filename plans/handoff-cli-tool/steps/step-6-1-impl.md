# Cycle 6.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Add commit pipeline to `src/claudeutils/session/commit.py`

**Behavior:**
- `CommitResult` dataclass: `success: bool`, `output: str`
- `commit_pipeline(input: CommitInput) -> CommitResult`
- Stage files via `git add`
- Run `just precommit` (validation level dispatch added in Cycle 6.4)
- Run vet check via `vet_check(input.files)` (option-gating added in Cycle 6.4)
- Commit with message from `CommitInput.message`
- Return raw git commit output on success

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add `CommitResult`, `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
