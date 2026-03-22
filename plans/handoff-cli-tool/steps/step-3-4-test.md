# Cycle 3.4

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.4: Old format enforcement

**Finding:** M#12

**Prerequisite:** Read `src/claudeutils/session/parse.py:84-109` and `src/claudeutils/validation/task_parsing.py` — understand what `parse_task_line` returns for old-format lines

---

**RED Phase:**

**Test:** `test_status_rejects_old_format`
**Assertions:**
- Session.md with old-format task lines (e.g., `- [ ] Task name` without `—` command/model metadata) → CLI exits with code 2
- Error output contains message about mandatory metadata
- Well-formed sessions (with metadata) parse and render successfully

**Expected failure:** `AssertionError` — parser returns `None` for unparseable lines (silently filtered), CLI exits 0

**Why it fails:** `parse_task_line` returns `None` for old-format, `parse_tasks` filters None, CLI renders whatever parsed successfully.

**Verify RED:** `pytest tests/test_session_status.py::test_status_rejects_old_format -v`

---
