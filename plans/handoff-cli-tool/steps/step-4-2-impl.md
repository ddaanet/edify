# Cycle 4.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

**GREEN Phase:**

**Implementation:** Add `overwrite_status()` to `src/claudeutils/session/handoff.py`

**Behavior:**
- Read session.md, find line after `# Session Handoff:` and before first `## ` heading
- Replace that region with `**Status:** {new_text}\n`
- Preserve blank line between status and first `##`
- Write back to file

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `overwrite_status(session_path: Path, status_text: str) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
