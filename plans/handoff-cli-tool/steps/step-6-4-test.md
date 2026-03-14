# Cycle 6.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.4: Validation levels (C-4)

**RED Phase:**

**Test:** `test_commit_just_lint`, `test_commit_no_vet`, `test_commit_combined_options`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `just-lint` option → pipeline runs `just lint` instead of `just precommit`
- `no-vet` option → vet check skipped entirely
- `just-lint` + `no-vet` → lint only, no vet
- `amend` + `no-vet` → full precommit, amend, no vet
- `amend` + `just-lint` → lint only, amend
- Options are orthogonal — any combination valid

**Expected failure:** Options not affecting validation behavior

**Why it fails:** No option dispatch for validation levels

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_just_lint -v`

---
