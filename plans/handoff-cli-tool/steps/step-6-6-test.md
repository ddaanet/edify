# Cycle 6.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.6: CLI wiring — `claudeutils _commit`

**RED Phase:**

**Test:** `test_commit_cli_success`, `test_commit_cli_validation_error`, `test_commit_cli_vet_failure`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- CliRunner invoking `_commit` with valid commit markdown on stdin (real git repo via `tmp_path`, file staged) → exit 0, stdout contains `[branch hash] message` format line
- CliRunner invoking `_commit` with files that have no changes → exit 2, stdout contains `**Error:**` and `STOP:`
- CliRunner invoking `_commit` with empty stdin → exit 2, stdout contains `**Error:**` and references missing required section
- CliRunner invoking `_commit` with files matching `require-review` patterns in pyproject.toml, no vet report present → exit 1, stdout contains `**Vet check:**` and `unreviewed`

**Expected failure:** Command not registered

**Why it fails:** No `_commit` command implementation

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_cli_success -v`

---
