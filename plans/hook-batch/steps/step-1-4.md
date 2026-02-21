# Cycle 1.4

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.4: New Directives with Dual Output (p:, b:, q:, learn:)

**Objective:** Add four directive entries with dual output pattern. p: gets dual output (was identical systemMessage+additionalContext). b:, q:, learn: are new directives not yet in DIRECTIVES dict.

---

**RED Phase:**

**Prerequisite:** Read current Tier 2 dual-output logic in main() (post-1.3 additive structure) — understand which directives currently get short systemMessage vs full expansion.

**Test:** `test_p_directive_dual_output`
**File:** `tests/test_userpromptsubmit_shortcuts.py` — add to new class `TestNewDirectives`

**Assertions:**
- `result = call_hook("p: some task")`
- `result["systemMessage"]` equals `"[PENDING] Capture task, do not execute."` (concise, NOT full expansion)
- `result["hookSpecificOutput"]["additionalContext"]` contains `"Do NOT execute"` (full expansion present)
- `len(result["systemMessage"]) < 60` (concise — not the full expansion text)

**Test:** `test_b_brainstorm_directive`

**Assertions:**
- `result = call_hook("b: ideas for this problem")`
- `result["systemMessage"]` contains `"[BRAINSTORM]"`
- `result["hookSpecificOutput"]["additionalContext"]` contains `"diverge"` or `"without evaluating"` or `"no ranking"` (D-5: diverge only)
- `result["hookSpecificOutput"]["additionalContext"]` does NOT contain `"recommend"` or `"converge"` (D-5: no convergence)

**Test:** `test_q_quick_directive`

**Assertions:**
- `result = call_hook("q: what is the difference between X and Y")`
- `result["systemMessage"]` contains `"[QUICK]"`
- `result["hookSpecificOutput"]["additionalContext"]` contains `"terse"` or `"no ceremony"` or `"directly"`

**Test:** `test_learn_directive`

**Assertions:**
- `result = call_hook("learn: discovered that X causes Y")`
- `result["systemMessage"]` contains `"[LEARN]"`
- `result["hookSpecificOutput"]["additionalContext"]` contains `"learnings.md"` (target file)
- `result["hookSpecificOutput"]["additionalContext"]` contains `"Anti-pattern"` or `"Correct pattern"` (format guidance)

**Test:** `test_directive_long_form_aliases`

**Assertions:**
- `call_hook("brainstorm: ideas")["systemMessage"]` contains `"[BRAINSTORM]"` (long-form alias)
- `call_hook("question: how does X work")["systemMessage"]` contains `"[QUICK]"` (long-form alias)
- `call_hook("pending: new task name")["systemMessage"]` contains `"[PENDING]"` (pre-existing alias, verify still works)

**Expected failure:** `AssertionError`
- p: currently sends full expansion as systemMessage (not concise `"[PENDING] Capture task, do not execute."`)
- b:, q:, learn: — `call_hook` returns `{}` (keys not in DIRECTIVES)

**Why it fails:** DIRECTIVES dict has no entries for 'b', 'brainstorm', 'q', 'question', 'learn'. p: uses the else branch in Tier 2 which sends full expansion to both systemMessage and additionalContext.

**Verify RED:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestNewDirectives -v`

---

**GREEN Phase:**

**Implementation:** Add expansion constants for 4 directives; update DIRECTIVES dict; update p: output logic to dual output.

**Behavior — p:/pending: (update to dual output):**
- systemMessage: `'[PENDING] Capture task, do not execute.'` (concise)
- additionalContext: full `_PENDING_EXPANSION` text
- Mirrors d:/discuss: dual-output pattern

**Behavior — b:/brainstorm: (new):**
- `_BRAINSTORM_EXPANSION`: diverge without converging; generate options/alternatives; no evaluation, no ranking; defer convergence — D-5
- systemMessage: `'[BRAINSTORM] Generate options, do not converge.'` (concise)
- additionalContext: full expansion

**Behavior — q:/question: (new):**
- `_QUICK_EXPANSION`: terse response; no preamble; no follow-up suggestions; answer directly
- systemMessage: `'[QUICK] Terse response, no ceremony.'` (concise)
- additionalContext: full expansion

**Behavior — learn: (new, no short alias — 'learn' IS the canonical form):**
- `_LEARN_EXPANSION`: append to agents/learnings.md; H2 format; anti-pattern → correct pattern → rationale; check line count after
- systemMessage: `'[LEARN] Append to learnings.'` (concise)
- additionalContext: full expansion

**Approach:** Add 4 constants near _DISCUSS_EXPANSION and _PENDING_EXPANSION. Update DIRECTIVES dict to map all keys. Add p:/pending: to the dual-output dispatch set (currently only `('d', 'discuss')`).

**Changes:**
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add `_BRAINSTORM_EXPANSION`, `_QUICK_EXPANSION`, `_LEARN_EXPANSION` constants in constants section
  Location hint: near `_DISCUSS_EXPANSION` and `_PENDING_EXPANSION` (~line 38-85)
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Update DIRECTIVES dict to add `'b'`, `'brainstorm'`, `'q'`, `'question'`, `'learn'` keys
  Location hint: DIRECTIVES dict definition (~line 88-92)
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Update dual-output dispatch set in Tier 2 per-directive output logic to include `'p'`/`'pending'`
  Location hint: Tier 2 output construction in main() — the set that currently only contains `'d'`/`'discuss'`

**Verify GREEN:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestNewDirectives -v`
**Verify existing alias tests:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestLongFormAliases -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---
