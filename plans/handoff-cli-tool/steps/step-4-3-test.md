# Cycle 4.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Cycle 4.3: Completed section write with committed detection (H-2)

**RED Phase:**

**Test:** `test_write_completed_overwrite`, `test_write_completed_append`, `test_write_completed_auto_strip`
**File:** `tests/test_session_handoff.py`

Tests use real git repos via `tmp_path` — committed detection requires `git diff HEAD`. Fixture must have a committed `agents/session.md` with an existing `## Completed This Session` section so that diff modes can be distinguished.

**Assertions — overwrite mode (no prior diff):**
- First handoff or prior content already committed → `write_completed(session_path, new_lines)` overwrites `## Completed This Session` section entirely with `new_lines`; section contains exactly `new_lines` and no prior content

**Assertions — append mode (old removed by agent):**
- Agent cleared old completed content from working tree, new additions provided → `write_completed()` writes only `new_lines` to section (prior committed lines NOT restored); resulting section contains exactly `new_lines`

**Assertions — auto-strip mode (old preserved with additions):**
- Prior committed content still present + new additions → `write_completed()` strips content that matches HEAD version, keeps only new additions

**Detection mechanism:**
- `git diff HEAD -- agents/session.md` extracts completed section from both sides
- If no diff in completed section region → overwrite
- If diff shows old lines removed → append
- If diff shows old lines preserved + new lines → auto-strip committed

**Expected failure:** Function doesn't exist

**Why it fails:** No committed detection logic

**Verify RED:** `pytest tests/test_session_handoff.py::test_write_completed_overwrite -v`

---
