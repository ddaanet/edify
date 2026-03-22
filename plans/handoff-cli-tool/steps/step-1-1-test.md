# Cycle 1.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.1: git commit returncode propagation

**Finding:** C#2 + MN-1

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:62-84, 110-148, 215-291`

---

**RED Phase:**

**Test:** `test_commit_pipeline_git_failure`
**Assertions:**
- When git commit subprocess returns non-zero exit, `commit_pipeline()` returns `CommitResult(success=False)` with output containing git's stderr
- When `_stage_files` raises `CalledProcessError`, `commit_pipeline()` returns `CommitResult(success=False)` with structured error message, not unhandled traceback
- Same for `_commit_submodule`'s internal `git add` — failure returns structured error

**Expected failure:** `AssertionError` — pipeline currently ignores returncode, unconditionally returns `success=True`

**Why it fails:** `_git_commit` discards `result.returncode`, returns only `result.stdout.strip()`. `commit_pipeline` wraps it in `CommitResult(success=True)` unconditionally.

**Verify RED:** `pytest tests/test_session_commit_pipeline_ext.py::test_commit_pipeline_git_failure -v`

---
