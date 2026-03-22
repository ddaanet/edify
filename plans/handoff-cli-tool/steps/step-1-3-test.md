# Cycle 1.3

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.3: Exit code 2 for CleanFileError

**Finding:** C#4

**Prerequisite:** Read `src/claudeutils/session/cli.py:16-32` and `commit_pipeline.py:227-236`

---

**RED Phase:**

**Test:** `test_commit_cli_clean_file_exits_2`
**Assertions:**
- CLI returns exit code 2 when `commit_pipeline` raises `CleanFileError`
- CLI returns exit code 1 for other pipeline failures (validation fail, git error)
- Output contains the CleanFileError message

**Expected failure:** `AssertionError` — CLI exits 1 for all `success=False` results

**Why it fails:** `cli.py:31-32` exits 1 unconditionally for all failures. CleanFileError caught inside pipeline, never reaches CLI.

**Verify RED:** `pytest tests/test_session_commit_cli.py::test_commit_cli_clean_file_exits_2 -v`

---
