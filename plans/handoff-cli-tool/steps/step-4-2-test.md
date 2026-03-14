# Cycle 4.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Cycle 4.2: Status line overwrite in session.md

**RED Phase:**

**Test:** `test_overwrite_status_line`, `test_overwrite_status_line_multiline`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `overwrite_status(session_path, "New status text.")` modifies file: line after `# Session Handoff:` heading becomes `**Status:** New status text.`
- Subsequent call with different text overwrites again (not append)
- Other sections of session.md unchanged
- When status text has multiple lines, each line preserved between heading and first `##`

**Expected failure:** `AttributeError` — `overwrite_status` doesn't exist

**Why it fails:** No status overwrite function

**Verify RED:** `pytest tests/test_session_handoff.py::test_overwrite_status_line -v`

---
