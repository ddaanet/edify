# Cycle 6.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.3: Amend semantics (C-5)

**RED Phase:**

**Test:** `test_commit_amend_parent`, `test_commit_amend_submodule`, `test_commit_amend_validation`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(input)` with `amend` in options:
  - Passes `--amend` to `git commit`
  - Output shows amend format with `Date:` line
  - Message is the full provided message (no `--no-edit`)
- Amend with submodule files:
  - Submodule amended first → pointer re-staged → parent amended
  - Output labeled correctly
- Amend validation:
  - File present in HEAD commit but not in working tree changes → valid for amend (no error)
  - File in neither HEAD nor working tree → `CleanFileError` (same as non-amend)

**Expected failure:** Pipeline doesn't pass `--amend` flag

**Why it fails:** No amend support in pipeline

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_amend_parent -v`

---
