---
name: hook-batch-phase-1
model: sonnet
---

# Phase 1: UserPromptSubmit Improvements

**Type:** TDD
**Target:** `agent-core/hooks/userpromptsubmit-shortcuts.py` (839 lines)
**Test file:** `tests/test_userpromptsubmit_shortcuts.py` (282 lines)
**Design refs:** `plans/hook-batch/outline.md` (Phase 1), `plans/hook-batch/userpromptsubmit-plan.md`

**Prerequisites:**
- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 765-839 — understand current `main()` structure (Tier 1 at 772, Tier 2 at 784-812, Tier 3 at 814-832)
- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 156-206 — understand current `scan_for_directive()` implementation
- Read `tests/test_userpromptsubmit_shortcuts.py` — understand existing test classes and helper `call_hook()`
- Note: `scan_for_directive` already scans all lines (not first-line-only). Cycle 1.1 targets only Tier 1 COMMANDS (line 772 `if prompt in COMMANDS`), not directives.
- Note: existing `TestAnyLineMatching.test_any_line_matching` (line 222) asserts first-directive-only behavior. Cycle 1.3 GREEN must update this test to expect additive behavior.

**Key decisions:**
- D-7: Directives are additive (all fire), section-scoped. First-match-return is eliminated.
- Tier 1 (COMMANDS) still first-match-wins — only one shortcut per prompt makes sense.
- Pattern guards (Tier 2.5) are additionalContext-only — no systemMessage. Additive.
- Tier 3 continuation runs even when directives fire (no early return from Tier 2 after D-7).

---

## Cycle 1.1: Line-Based Shortcut Matching

**Objective:** Tier 1 COMMANDS trigger when shortcut appears as sole content of any prompt line, not only when entire prompt equals the shortcut.

---

**RED Phase:**

**Prerequisite:** Read `main()` at line 772 — understand `if prompt in COMMANDS` exact-match check.

**Test:** `test_tier1_shortcut_on_own_line_in_multiline_prompt`
**File:** `tests/test_userpromptsubmit_shortcuts.py` — add to class `TestTier1Commands` (create class if not present)

**Assertions:**
- `call_hook("s\nsome additional context")` → result dict is non-empty (not `{}`)
- `call_hook("s\nsome additional context")["hookSpecificOutput"]["additionalContext"]` contains `"[#status]"`
- `call_hook("x\ndo the next thing")["hookSpecificOutput"]["additionalContext"]` contains `"[#execute]"`
- `call_hook("s\nsome additional context")` does NOT have a `"systemMessage"` key (multi-line: additionalContext only, systemMessage suppressed to avoid noisy expansion in status bar)

**Test:** `test_tier1_shortcut_exact_match_unchanged`

**Assertions:**
- `call_hook("s")["systemMessage"]` contains `"[#status]"` (single-line still gets systemMessage)
- `call_hook("x")["systemMessage"]` contains `"[#execute]"`
- `call_hook("s")["hookSpecificOutput"]["additionalContext"]` contains `"[#status]"`

**Test:** `test_tier1_no_false_positive_embedded`

**Assertions:**
- `call_hook("this is about status")` returns `{}` (empty — `s` embedded in word, not own-line)
- `call_hook("fix something")` returns `{}` (no shortcut on own line)
- `call_hook("  s  trailing space")` — behavior: stripped `"s trailing space"` is NOT in COMMANDS (line has text after shortcut), returns `{}`

**Expected failure:** `AssertionError` — `call_hook("s\nsome additional context")` currently returns `{}` because `"s\nsome additional context" not in COMMANDS`

**Why it fails:** `if prompt in COMMANDS` at line 772 performs exact string match against entire prompt. Multi-line prompts never match.

**Verify RED:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands -v`

---

**GREEN Phase:**

**Implementation:** Replace exact-match check at line 772 with line-scanning loop. Preserve all downstream output logic.

**Behavior:**
- Split prompt on `'\n'`, strip each line
- If stripped line matches a COMMANDS key exactly (no extra words): trigger that expansion
- First matching line wins (Tier 1 is still first-match)
- Single-line exact match: systemMessage + additionalContext (current behavior preserved)
- Match within multi-line prompt: additionalContext only (no systemMessage — avoid noisy status bar display)

**Approach:** Loop replaces the single `if prompt in COMMANDS` check. The output construction block (currently lines 774-781) needs conditional systemMessage based on whether it was a single-line match.

**Changes:**
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Replace lines 771-782 (`if prompt in COMMANDS:` block) with line-scanning loop
  Location hint: `main()` function, before Tier 2 directive scan

**Verify GREEN:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestTier1Commands -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

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

## Cycle 1.3: Additive Directive Scanning (D-7)

**Objective:** Refactor `scan_for_directive` → `scan_for_directives` to collect ALL directives in a prompt (not first-match-return). Each directive is section-scoped. Tier 2 no longer returns early.

---

**RED Phase:**

**Prerequisite:** Read `scan_for_directive()` at lines 156-206 — understand current single-pass return-on-first-match implementation. Read `main()` Tier 2 block at lines 784-812 — note `if directive_match:` early return.

**Test:** `test_multiple_directives_both_fire`
**File:** `tests/test_userpromptsubmit_shortcuts.py` — add new class `TestAdditiveDirectives`

**Assertions:**
- `result = call_hook("d: discuss this\np: new task")` → result is non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"DISCUSS"` or `"Evaluate critically"` (from DISCUSS expansion)
- `result["hookSpecificOutput"]["additionalContext"]` contains `"PENDING"` or `"Do NOT execute"` (from PENDING expansion)
- Both directive expansions appear in a single additionalContext string

**Test:** `test_directive_section_scoping`

**Assertions:**
- `result = call_hook("d: discuss this topic\nsome discussion content\np: new task name")` → additionalContext contains both DISCUSS and PENDING expansions
- (Section scoping: d: section is "discuss this topic\nsome discussion content", p: section is "new task name")

**Test:** `test_single_directive_still_works`

**Assertions:**
- `call_hook("d: some topic")["hookSpecificOutput"]["additionalContext"]` contains `"Evaluate critically"` (single directive unchanged)
- `call_hook("d: some topic")["systemMessage"]` contains `"[DISCUSS]"` (dual output still works)

**Expected failure:** `AssertionError` — `call_hook("d: discuss this\np: new task")` currently returns only DISCUSS expansion (first match), PENDING expansion is absent

**Why it fails:** `scan_for_directive()` returns on first match (line 204: `return (directive_key, match.group(2))`). The `if directive_match:` block at line 784 processes one result and returns.

**Update required in GREEN:** Existing `TestAnyLineMatching.test_any_line_matching` lines 222-228 assert first-directive-only behavior with `"assert "[DISCUSS]" in output_multi["systemMessage"]"`. This test must be updated to expect additive behavior (both DISCUSS and PENDING fire).

**Verify RED:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestAdditiveDirectives -v`

---

**GREEN Phase:**

**Implementation:** New `scan_for_directives()` function (returns list), refactored main() Tier 2 block.

**Behavior:**
- `scan_for_directives(prompt)` → `List[Tuple[str, str]]` where each tuple is `(directive_key, section_content)`
- Section content: all lines from the directive line to the next directive line (exclusive) or end of prompt
- Fence exclusion preserved (directive lines inside fenced blocks are skipped)
- Returns empty list if no directives found
- `main()` Tier 2 block: iterate over all returned directives; build combined additionalContext (all expansions joined with double newline); build combined systemMessage (all concise messages joined with `' | '`)
- Tier 2 does NOT return early — falls through to Tier 2.5 and Tier 3 after collecting all directives
- Existing `scan_for_directive` (singular) can be removed OR kept as alias returning first item (removing is cleaner)
- Update `TestAnyLineMatching.test_any_line_matching` line 222-228: multi-directive prompt now returns BOTH expansions; assert `"[DISCUSS]"` AND `"[PENDING]"` in systemMessage (or change assertion to verify both directives fired)

**Approach:** New function iterates lines building sections; main() collects into lists and combines. The dual-output logic (d:/discuss: special-case) moves into per-directive output building.

**Changes:**
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add `scan_for_directives()` function after line 206; refactor main() Tier 2 block at lines 784-812
  Location hint: after existing `scan_for_directive()` definition
- File: `tests/test_userpromptsubmit_shortcuts.py`
  Action: Update `TestAnyLineMatching.test_any_line_matching` multi-directive assertion at line 222-228

**Verify GREEN:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestAdditiveDirectives -v`
**Verify updated test:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestAnyLineMatching -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---

## CHECKPOINT: After Cycle 1.3

Run full test suite before proceeding to Cycles 1.4-1.5:

```bash
pytest tests/test_userpromptsubmit_shortcuts.py -v
```

**Gate criteria:**
- All tests pass (0 failures)
- Verify: `call_hook("d: discuss\np: task")` → additionalContext contains both DISCUSS and PENDING
- Verify: `call_hook("s")` → systemMessage contains `"[#status]"` (Tier 1 regression)
- Verify: `call_hook("s\nsome text")` → additionalContext contains `"[#status]"`, no systemMessage
- Verify: continuation prompt (e.g., `/handoff --commit`) still parses via Tier 3 (Tier 2 no longer early-returns)

If any gate fails: STOP. Fix before proceeding to Cycle 1.4.

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

## Cycle 1.5: Pattern Guards (Skill-Editing + CCG)

**Objective:** Add Tier 2.5 pattern guards — two regex detection blocks that inject additionalContext when editing verbs + skill/agent references or platform capability keywords are detected. Additive with directive and continuation outputs.

---

**RED Phase:**

**Prerequisite:** Read main() Tier 2.5 comment area and Tier 3 continuation block (lines 814-832) — understand where Tier 2.5 detection should be inserted (after Tier 2 additive collection, before Tier 3 result combination). Note that after Cycle 1.3, Tier 2 no longer early-returns — Tier 2.5 always runs.

**Test:** `test_skill_editing_guard_verb_noun`
**File:** `tests/test_userpromptsubmit_shortcuts.py` — add new class `TestPatternGuards`

**Assertions:**
- `result = call_hook("fix the commit skill")` → result non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"plugin-dev:skill-development"`
- `result` does NOT have `"systemMessage"` key (guard is additionalContext-only)

**Test:** `test_skill_editing_guard_slash_pattern`

**Assertions:**
- `result = call_hook("update /design description")` → additionalContext contains `"plugin-dev:skill-development"`
- `result = call_hook("improve /commit skill")` → additionalContext contains `"plugin-dev:skill-development"`

**Test:** `test_ccg_guard_hooks_keyword`

**Assertions:**
- `result = call_hook("how do hooks work")` → result non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"claude-code-guide"`
- `result` does NOT have `"systemMessage"` key

**Test:** `test_ccg_guard_platform_keywords`

**Assertions:**
- `call_hook("configure a PreToolUse hook")["hookSpecificOutput"]["additionalContext"]` contains `"claude-code-guide"`
- `call_hook("set up MCP server")["hookSpecificOutput"]["additionalContext"]` contains `"claude-code-guide"`
- `call_hook("add a slash command")["hookSpecificOutput"]["additionalContext"]` contains `"claude-code-guide"`

**Test:** `test_pattern_guard_no_false_positives`

**Assertions:**
- `call_hook("fix the bug in parsing")` returns `{}` (no skill/agent noun, no platform keyword)
- `call_hook("the skill level is high")` returns `{}` (no editing verb, no platform keyword)

**Test:** `test_guard_additive_with_directive`

**Assertions:**
- `result = call_hook("d: how do hooks work")` → result has both DISCUSS expansion AND claude-code-guide content in additionalContext
- (CCG guard fires on "hooks" keyword even when d: directive also fires)

**Expected failure:** `NameError` or `AssertionError` — `EDIT_SKILL_PATTERN`, `EDIT_SLASH_PATTERN`, `CCG_PATTERN` constants don't exist; `call_hook("fix the commit skill")` returns `{}`

**Why it fails:** No Tier 2.5 pattern detection logic in main(); no regex constants defined.

**Verify RED:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestPatternGuards -v`

---

**GREEN Phase:**

**Implementation:** Three regex constants + two detection blocks in main() as Tier 2.5.

**Behavior:**
- `EDIT_SKILL_PATTERN`: matches editing verbs (fix, edit, update, improve, change, modify, rewrite, refactor) followed by skill/agent noun OR skill/agent noun followed by editing verb
- `EDIT_SLASH_PATTERN`: matches editing verbs followed by `/word` pattern (slash-prefixed skill name)
- `CCG_PATTERN`: matches platform capability keywords (hook, hooks, PreToolUse, PostToolUse, SessionStart, UserPromptSubmit, mcp server, slash command, settings.json, .claude/, plugin.json, keybinding, IDE integration, agent sdk) — case-insensitive

**Injection behavior:**
- EDIT_SKILL_PATTERN or EDIT_SLASH_PATTERN match → inject skill-editing reminder to additionalContext collector:
  `"Load /plugin-dev:skill-development before editing skill files. Load /plugin-dev:agent-development before editing agent files. Skill descriptions require 'This skill should be used when...' format."`
- CCG_PATTERN match → inject CCG reminder to additionalContext collector:
  `"Platform question detected. Use claude-code-guide agent (subagent_type='claude-code-guide') for authoritative Claude Code documentation."`
- Both checks against full prompt text (not line-by-line)
- No systemMessage for either guard (additionalContext only)
- Both are additive: multiple guards can fire simultaneously, and they combine with Tier 2 directive and Tier 3 continuation outputs

**Output combination:** After Tier 2.5 detection, combine all collected additionalContext (directives + guards) before Tier 3 result. If Tier 3 also produces additionalContext (continuation parsing), combine all three. Final output is a single dict with combined additionalContext.

**Approach:** Insert Tier 2.5 block after Tier 2 directive collection, before Tier 3 continuation. Uses `re.search()` against full prompt. Accumulates into a `guard_contexts` list; appended to directive contexts during final combination.

**Changes:**
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add `EDIT_SKILL_PATTERN`, `EDIT_SLASH_PATTERN`, `CCG_PATTERN` constants in constants section
  Location hint: after DIRECTIVES dict, before BUILTIN_SKILLS (~line 93-95)
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add Tier 2.5 pattern guard detection block in main()
  Location hint: between Tier 2 directive collection and Tier 3 continuation block (~line 813)

**Verify GREEN:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestPatternGuards -v`
**Verify additive with directives:** `pytest tests/test_userpromptsubmit_shortcuts.py::TestAdditiveDirectives -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---

## Phase 1 Completion Validation

After all 5 cycles pass:

```bash
pytest tests/test_userpromptsubmit_shortcuts.py -v
```

**Success criteria:**
- All tests pass (0 failures)
- `test_tier1_shortcut_on_own_line_in_multiline_prompt` passes (Cycle 1.1)
- `test_r_expansion_graduated_lookup` and `test_xc_hc_bracket_compression` pass (Cycle 1.2)
- `test_multiple_directives_both_fire` passes (Cycle 1.3)
- `test_p_directive_dual_output`, `test_b_brainstorm_directive`, `test_q_quick_directive`, `test_learn_directive` pass (Cycle 1.4)
- `test_skill_editing_guard_verb_noun`, `test_ccg_guard_hooks_keyword`, `test_guard_additive_with_directive` pass (Cycle 1.5)
- Existing test classes (`TestLongFormAliases`, `TestEnhancedDDirective`, `TestFencedBlockExclusion`, `TestIntegration`) all still pass

**Line count check:** `wc -l agent-core/hooks/userpromptsubmit-shortcuts.py` — expect ~950-980 lines (was 839).

**Stop conditions:**
- RED fails to fail → STOP: test is too weak or already-passing behavior, diagnose before proceeding
- GREEN passes without implementation → STOP: test too weak, strengthen before committing
- Cycle 1.3 GREEN: if `TestAnyLineMatching.test_any_line_matching` fails unexpectedly → review the multi-directive assertion update
- Implementation needs architectural decision → STOP, escalate
