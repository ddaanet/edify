# Cycle 4.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Cycle 4.1: Parse handoff stdin

**RED Phase:**

**Test:** `test_parse_handoff_input`, `test_parse_handoff_missing_status`, `test_parse_handoff_missing_completed`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `parse_handoff_input(text)` with valid input returns `HandoffInput` with:
  - `status_line == "Design Phase A complete — outline reviewed."`
  - `completed_lines` is list of strings under `## Completed This Session`
- `parse_handoff_input(text)` without `**Status:**` line raises `HandoffInputError` with message containing "Status"
- `parse_handoff_input(text)` without `## Completed This Session` heading raises `HandoffInputError` with message containing "Completed"

**Input fixture:**
```
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

### Handoff CLI tool design (Phase A)
- Produced outline
- Review by outline-review-agent
```

**Expected failure:** `ImportError` — no `parse_handoff_input` function

**Why it fails:** No `session/handoff.py` module with parsing

**Verify RED:** `pytest tests/test_session_handoff.py::test_parse_handoff_input -v`

---
