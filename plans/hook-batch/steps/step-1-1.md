# Cycle 1.1

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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
