# Cycle 2.2

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.2: Enhanced d: directive injection

**RED Phase:**

**Test**: `test_enhanced_d_injection`

**Assertions**:
- `additionalContext` includes all counterfactual structure elements:
  - "identify assumptions"
  - "articulate failure conditions"
  - "name alternatives"
  - "state confidence level"
- `additionalContext` preserves "do not execute" instruction
- `systemMessage` stays concise: "[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically, do not execute." (no full evaluation framework in user-visible message)

**Expected failure**: AssertionError (existing d: expansion doesn't include counterfactual structure)

**Why it fails**: Current DIRECTIVES['d'] is generic "do not execute" without evaluation structure

**Verify RED**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_enhanced_d_injection -v`

---

**GREEN Phase:**

**Implementation**: Enhance DIRECTIVES['d'] expansion value

**Behavior**:
- Inject counterfactual evaluation structure from research grounding
- Preserve existing "do not execute" behavior
- Dual output: enhanced content to `additionalContext` (Claude sees), concise indicator to `systemMessage` (user sees)

**Approach**: Modify the expansion value in DIRECTIVES dict. Use multi-line string with all evaluation elements. Split output: full structure to additionalContext, short mode indicator to systemMessage.

**Changes**:
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Replace DIRECTIVES['d'] value with enhanced multi-line instruction including counterfactual structure
  Location hint: DIRECTIVES dict, 'd' key value (currently lines 61-65 region)

**Content to include** (from design lines 124-129):
1. Evaluate critically, do not execute
2. Before agreeing: identify assumptions, articulate failure conditions, name alternatives
3. If idea is good: state specifically WHY
4. State confidence level

**Verify GREEN**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_enhanced_d_injection -v`

**Verify no regression**: `pytest tests/test_userpromptsubmit_shortcuts.py -v`

**Note**: This cycle is independent of matching mechanism changes (2.3/2.4). Modifies DIRECTIVES dict value only.

---
