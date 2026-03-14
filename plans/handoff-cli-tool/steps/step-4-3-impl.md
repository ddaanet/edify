# Cycle 4.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

**GREEN Phase:**

**Implementation:** Add `write_completed()` to `session/handoff.py`

**Behavior:**
- Compare completed section in working tree vs HEAD via `git diff HEAD -- agents/session.md`
- Parse diff to determine which mode applies
- Execute appropriate write (overwrite, append, or strip-committed-then-keep-new)

**Approach:** Use `_git("diff", "HEAD", "--", str(session_path))` to get diff. Parse for completed section hunk. Absence of hunk → overwrite mode. Hunk with only additions → append mode. Hunk with preserved old + new → auto-strip mode.

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `write_completed(session_path: Path, new_lines: list[str]) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---
