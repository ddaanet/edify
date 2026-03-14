# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

## Cycle 3.4: CLI wiring — `claudeutils _status`

**RED Phase:**

**Test:** `test_status_cli`, `test_status_missing_session`, `test_status_old_format_fatal`
**File:** `tests/test_session_status.py`

**Assertions:**
- CliRunner invoking `_status` with a real session.md file in cwd produces output containing:
  - In-tree section with first pending task (with `▶` marker if single-task)
  - Output exits with code 0
- CliRunner invoking `_status` without session.md file → exit code 2, output contains `**Error:**`
- CliRunner invoking `_status` with session.md containing tasks without pipe-separated metadata → exit code 2 (old format = fatal, mandatory metadata)

**Expected failure:** Command `_status` not registered — Click returns non-zero with "No such command"

**Why it fails:** No `_status` command registered in main CLI

**Verify RED:** `pytest tests/test_session_status.py::test_status_cli -v`

---
