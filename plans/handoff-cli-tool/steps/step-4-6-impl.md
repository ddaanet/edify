# Cycle 4.6

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

**GREEN Phase:**

**Implementation:** Add `format_diagnostics()` to `session/handoff.py`

**Behavior:**
- `format_diagnostics(git_output: str) -> str`
- If git output non-empty: return it as structured markdown
- If empty: return empty string
- No precommit result (precommit is pre-handoff gate, not CLI responsibility)
- No learnings age/weight (SessionStart hook concern, not actionable mid-session)

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `format_diagnostics()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
