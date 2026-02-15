# Cycle 2.4

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.4: Any-line directive matching

[DEPENDS: Cycle 2.3]

**RED Phase:**

**Test**: `test_any_line_matching`

**Assertions**:
- Directive on line 2 (not line 1) is found and returned
- Directive on line 3 is found
- Directive inside fenced block returns None (excluded by fence detection)
- First non-fenced directive match is returned (not all matches)

**Expected failure**: AssertionError (current `re.match` at line 653 only matches line 1, or None returned for non-first-line directives)

**Why it fails**: Current implementation uses `re.match(r'^(\w+):\s+(.+)', prompt)` which matches full prompt string start, not per-line

**Verify RED**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_any_line_matching -v`

---

**GREEN Phase:**

**Implementation**: Replace inline `re.match` with any-line scanner

**Behavior**:
- Split prompt into lines
- Iterate lines in order
- Skip lines inside fenced blocks (use Cycle 2.3 fence detection)
- Match directive pattern (`<word>: <text>`) on non-fenced lines
- Return first match where key is in DIRECTIVES
- Return None if no match found

**Approach**: Create scanner function that takes prompt string, returns (key, value) tuple or None. Use fence detection from Cycle 2.3 to skip fenced lines. Apply existing DIRECTIVES lookup logic.

**Changes**:
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add any-line scanner function, replace inline `re.match` at line 653 with scanner call
  Location hint: Function definition near fence tracking, call site at Tier 2 logic (line 653 region)

**Verify GREEN**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_any_line_matching -v`

**Verify no regression**: `pytest tests/test_userpromptsubmit_shortcuts.py -v`

**Note**: Tier 1 exact-match behavior (lines 641-651 region) remains unchanged. Only Tier 2 directive matching updated.

---
