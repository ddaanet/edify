# Cycle 1.5

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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
