# Cycle 6.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.1: Parent-only commit pipeline

**RED Phase:**

**Test:** `test_commit_parent_only`, `test_commit_precommit_failure`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(commit_input)` with files in parent repo only (no submodule files), precommit passing:
  - Stages listed files via `git add`
  - Runs `just precommit`
  - Commits with message from `CommitInput.message`
  - Returns `CommitResult(success=True, output="[branch hash] message\n N files changed...")` — raw git output
  - Exit code 0
- `commit_pipeline(commit_input)` with precommit failure:
  - Returns `CommitResult(success=False, output="**Precommit:** failed\n\n<error output>")`
  - Files staged but NOT committed
  - Exit code 1

**Expected failure:** `ImportError` — no commit pipeline

**Why it fails:** No commit pipeline in `session/commit.py`

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_parent_only -v`

---
