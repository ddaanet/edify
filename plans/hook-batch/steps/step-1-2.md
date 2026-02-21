# Cycle 1.2

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.2: COMMANDS Dict String Updates (r, xc, hc)

**Objective:** Update three COMMANDS expansion strings — r gets graduated lookup, xc/hc get bracket compression.

---

**RED Phase:**

**Test:** `test_r_expansion_graduated_lookup`
**File:** `tests/test_userpromptsubmit_shortcuts.py` — add to `TestTier1Commands`

**Assertions:**
- `call_hook("r")["hookSpecificOutput"]["additionalContext"]` contains `"conversation context"` (graduated lookup first step)
- `call_hook("r")["hookSpecificOutput"]["additionalContext"]` contains `"session.md"` (second step)
- `call_hook("r")["hookSpecificOutput"]["additionalContext"]` does NOT contain `"Error if no in-progress"` (old text removed)

**Test:** `test_xc_hc_bracket_compression`

**Assertions:**
- `call_hook("xc")["systemMessage"]` starts with `"[execute, commit]"` (bracket style)
- `call_hook("hc")["systemMessage"]` starts with `"[handoff, commit]"` (bracket style)
- `call_hook("xc")["systemMessage"]` does NOT contain `"[#execute --commit]"` (old text removed)
- `call_hook("hc")["systemMessage"]` does NOT contain `"[/handoff --commit]"` (old text removed)

**Expected failure:** `AssertionError` — current r expansion is `'[#resume] Continue in-progress task only. Error if no in-progress task exists.'` (no "conversation context"); current xc starts with `'[#execute --commit]'`

**Why it fails:** Expansion strings in COMMANDS dict use old text.

**Verify RED:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands::test_r_expansion_graduated_lookup tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands::test_xc_hc_bracket_compression -v`

---

**GREEN Phase:**

**Implementation:** Replace three string values in COMMANDS dict.

**Behavior — r expansion (graduated lookup):**
- Step 1: Check conversation context — if in-progress task visible, resume directly
- Step 2: Read session.md — look for `[>]` or in-progress task
- Step 3: Check git status/diff — look for uncommitted work indicating active task
- Report only if genuinely nothing to resume

**Behavior — xc/hc (bracket compression):**
- xc: `[execute, commit]` style + note that this is shorthand for execute then `/handoff` and `/commit` continuation chain
- hc: `[handoff, commit]` style + note that this is shorthand for `/handoff` then `/commit` continuation chain

**Changes:**
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Replace COMMANDS dict values for keys `'r'`, `'xc'`, `'hc'`
  Location hint: `COMMANDS` dict near top of file (~line 40-65)

**Verify GREEN:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---
