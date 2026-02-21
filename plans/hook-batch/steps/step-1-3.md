# Cycle 1.3

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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
- Update `TestAnyLineMatching.test_any_line_matching` line 222-228: multi-directive prompt now returns BOTH expansions; assert both `"[DISCUSS]"` AND `"[PENDING]"` appear in `output_multi["systemMessage"]` (two separate `assert ... in output_multi["systemMessage"]` statements)

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
