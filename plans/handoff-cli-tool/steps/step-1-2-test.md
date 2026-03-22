# Cycle 1.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.2: Validation before submodule commit

**Finding:** C#3

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:215-291` — current pipeline ordering

---

**RED Phase:**

**Test:** `test_pipeline_validates_before_submodule_commit`
**Assertions:**
- When `_validate` returns failure result, `_commit_submodule` has not been called
- Mock `_commit_submodule` and `_validate` (failing) — assert `_commit_submodule` call count is 0
- When validation passes, submodule commits proceed normally

**Expected failure:** `AssertionError` — submodule commit at line 256-264 runs before `_validate` at line 271

**Why it fails:** Pipeline order is: commit submodules → stage parent → validate. Submodules committed before validation gate.

**Verify RED:** `pytest tests/test_session_commit_pipeline_ext.py::test_pipeline_validates_before_submodule_commit -v`

---
