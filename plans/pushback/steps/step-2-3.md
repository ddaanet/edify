# Cycle 2.3

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.3: Fenced block exclusion

**RED Phase:**

**Test**: `test_fenced_block_exclusion`

**Assertions**:
- Lines between opening fence (3+ backticks: ` ``` `) and closing fence marked as fenced
- Lines between opening fence (3+ tildes: `~~~`) and closing fence marked as fenced
- Opening and closing must use same character
- Closing fence must have at least same count as opening
- Lines outside fences are not marked as fenced

**Expected failure**: AttributeError or NameError (fence detection function doesn't exist)

**Why it fails**: No fence tracking implementation yet

**Verify RED**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_fenced_block_exclusion -v`

---

**GREEN Phase:**

**Implementation**: Implement fence detection for directive scanning

**Behavior**:
- Track fence depth while scanning lines
- Opening fence: 3+ consecutive backticks or tildes at line start
- Closing fence: same character, same or greater count
- Lines between fences are "inside", others are "outside"

**Approach**: Add fence tracking function. Two options:
1. Reuse existing code from `src/claudeutils/markdown_parsing.py` (_extract_fence_info, _track_fence_depth)
2. Implement simpler standalone version (hook needs are simpler than full parser)

Either approach is valid. Simpler standalone reduces dependencies; code reuse leverages proven logic.

**Changes**:
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add fence tracking function (standalone or imported helper)
  Location hint: Before directive scanning logic, or import at top if reusing

**Verify GREEN**: `pytest tests/test_userpromptsubmit_shortcuts.py::test_fenced_block_exclusion -v`

**Verify no regression**: `pytest tests/test_userpromptsubmit_shortcuts.py -v`

**Note**: This cycle establishes foundation for Cycle 2.4 (any-line matching needs fence exclusion).

---
