# Cycle 4.4

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

**GREEN Phase:**

**Implementation:** Add state caching to `src/claudeutils/session/handoff.py`

**Behavior:**
- `HandoffState` dataclass: `input_markdown: str`, `timestamp: str`, `step_reached: str`
- `save_state(input_md: str, step: str) -> None` — write JSON to `tmp/.handoff-state.json`. Create `tmp/` if needed
- `load_state() -> HandoffState | None` — read and parse JSON, return None if file missing
- `clear_state() -> None` — delete state file if exists

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `HandoffState`, `save_state()`, `load_state()`, `clear_state()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Mid-phase checkpoint:** `just precommit` — mutations + recovery established before diagnostics integration.

---
