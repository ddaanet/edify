# Cycle 6.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Add option-based validation dispatch to `commit_pipeline()`

**Behavior:**
- Inspect `input.options` set before dispatching validation:
  - `just-lint` present → run `just lint` instead of `just precommit`
  - `no-vet` present → skip vet check entirely
  - Both absent → default: `just precommit` + vet check
  - Orthogonal: each option controls one aspect independently

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add option dispatch logic before validation calls

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
