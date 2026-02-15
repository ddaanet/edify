# Cycle 2.5

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.5: Integration test

[DEPENDS: Cycles 2.1, 2.2, 2.3, 2.4]

**RED Phase:**

**Test**: `test_integration_e2e`

**Assertions**:
- Long-form alias (`discuss`) on line 3 inside fenced block is excluded (returns None or doesn't trigger)
- Long-form alias (`discuss`) on line 5 after closing fence is matched and returns enhanced d: injection
- Enhanced content includes counterfactual structure
- Tier 1 exact-match commands unchanged (test `#status`, `#execute` still work exactly as before)

**Expected failure**: AssertionError (integration not verified, or one feature broke another)

**Why it fails**: Integration test not implemented, or feature interaction bugs exist

**Verify RED**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_integration_e2e -v`

---

**GREEN Phase:**

**Implementation**: E2E test via JSON stdin→stdout

**Behavior**:
- Test hook's actual execution model (JSON input via stdin, JSON output via stdout)
- Verify all enhancements work together without interference
- Confirm Tier 1 unchanged (regression protection)

**Approach**: Use subprocess or direct hook invocation. Pipe JSON with `{"user_prompt": "..."}`, assert JSON output contains expected `additionalContext` and `systemMessage`. Test combined scenarios: alias + any-line + fence exclusion.

**Changes**:
- File: `tests/test_userpromptsubmit_shortcuts.py`
  Action: Add E2E test function that exercises full hook with realistic multi-line prompts
  Location hint: After unit tests, before end of file

**Test scenarios**:
1. Multi-line prompt with `discuss:` on line 3 inside triple-backtick fence → no match (excluded)
2. Same prompt structure but `discuss:` on line 5 after fence closes → match with enhanced injection
3. Tier 1 command `#status` → exact match output unchanged from baseline

**Verify GREEN**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_integration_e2e -v`

**Verify no regression**: `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---

### Phase 3: Wiring (type: general)
