# Cycle 2.1

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.1: Long-form directive aliases

**RED Phase:**

**Test**: `test_long_form_aliases`

**Assertions**:
- `discuss: <text>` produces same `additionalContext` output as `d: <text>`
- `pending: <text>` produces same `additionalContext` output as `p: <text>`
- Both short and long forms produce identical `systemMessage` output

**Expected failure**: KeyError or None return (long-form keys not in DIRECTIVES dict)

**Why it fails**: DIRECTIVES dict only has 'd' and 'p' keys, not 'discuss' and 'pending'

**Verify RED**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_long_form_aliases -v`

**Prerequisite**: Establish test infrastructure. Test file must import hook using `importlib.util.spec_from_file_location` pattern because filename contains hyphen (not importable via standard import).

---

**GREEN Phase:**

**Implementation**: Add long-form aliases to DIRECTIVES dict

**Behavior**:
- Both 'discuss' and 'd' keys map to same expansion value
- Both 'pending' and 'p' keys map to same expansion value
- Lookup logic unchanged (key in DIRECTIVES check works for both)

**Approach**: Modify DIRECTIVES dict initialization to include additional keys with identical values. No changes to directive matching logic.

**Changes**:
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add 'discuss' and 'pending' entries to DIRECTIVES dict (lines 60-71 region)
  Location hint: Inside DIRECTIVES dict definition after 'd' and 'p' entries

**Verify GREEN**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_long_form_aliases -v`

**Verify no regression**: `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---
