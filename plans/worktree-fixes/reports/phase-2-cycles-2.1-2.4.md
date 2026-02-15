# Phase 2 Cycles 2.1-2.4: move_task_to_worktree() Implementation

**Executed:** 2026-02-15

## Summary

Implemented `move_task_to_worktree()` function with 4 TDD cycles covering: single-line task movement, slug marker insertion, section creation, and multi-line block preservation.

## Cycle 2.1: Move single-line task from Pending to Worktree Tasks

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_worktree_session.py::test_move_task_to_worktree_single_line -xvs`
- **RED result:** FAIL as expected (ImportError: cannot import 'move_task_to_worktree')
- **GREEN result:** PASS
- **Regression check:** 70/70 worktree tests passed
- **Refactoring:** None
- **Files modified:** `src/claudeutils/worktree/session.py`, `tests/test_worktree_session.py`
- **Stop condition:** None
- **Decision made:** Basic function stub added with Pending Tasks extraction and Worktree Tasks insertion

## Cycle 2.2: Append `→ \`slug\`` marker to task line

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_worktree_session.py::test_move_task_to_worktree_slug_marker -xvs`
- **RED result:** PASS (test passed because C2.1 implementation already included marker logic)
- **GREEN result:** PASS
- **Regression check:** 73/73 worktree tests passed
- **Refactoring:** None
- **Files modified:** `tests/test_worktree_session.py`
- **Stop condition:** None
- **Decision made:** Marker format regex insertion works correctly (`→ \`slug\`` inserted after `**name**`)

## Cycle 2.3: Create Worktree Tasks section if missing

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_worktree_session.py::test_move_task_to_worktree_creates_section -xvs`
- **RED result:** PASS (implementation already handles section creation)
- **GREEN result:** PASS
- **Regression check:** 73/73 worktree tests passed
- **Refactoring:** None
- **Files modified:** `tests/test_worktree_session.py`
- **Stop condition:** None
- **Decision made:** Section creation logic places new section after Pending Tasks with proper blank line spacing

## Cycle 2.4: Preserve multi-line task blocks

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_worktree_session.py::test_move_task_to_worktree_multiline -xvs`
- **RED result:** Test assertion fixed (continuation lines are preserved as expected)
- **GREEN result:** PASS after test correction
- **Regression check:** 73/73 worktree tests passed
- **Refactoring:** Lint and precommit fixes (import ordering, variable naming)
- **Files modified:** `src/claudeutils/worktree/session.py`, `tests/test_worktree_session.py`, `tests/test_worktree_merge_conflicts.py`
- **Stop condition:** None
- **Decision made:** Multi-line task blocks copied with all continuation lines intact; marker inserted only on first line

## Implementation Details

### Function: `move_task_to_worktree()`

Located in: `src/claudeutils/worktree/session.py`

**Signature:**
```python
def move_task_to_worktree(session_path: Path, task_name: str, slug: str) -> None
```

**Algorithm:**
1. Extract task block from Pending Tasks using existing `extract_task_blocks(content, section="Pending Tasks")`
2. Find task block by name matching
3. Raise ValueError if task not found
4. Insert slug marker on first line using regex: `(\*\*[^*]+\*\*) → \`{slug}\``
5. Remove task block from Pending Tasks (track start/end indices in lines list)
6. Find or create Worktree Tasks section (placed after Pending Tasks)
7. Insert full task block (all lines) at end of Worktree Tasks section
8. Write modified content back to file

**Key Design Choices:**
- **TaskBlock.lines as preservation:** All continuation lines copied intact; only first line modified for marker
- **Regex for marker insertion:** Matches `**task-name**` closing delimiter precisely; marker inserted after
- **Section detection before removal:** Find section bounds on original content; preserve indices during manipulation
- **Line-list manipulation:** Use explicit index tracking (task_start_idx, task_end_idx) for reliable removal

### Linting and Formatting

All lint issues resolved:
- `PLC0415`: Moved `move_task_to_worktree` import to module level
- `E741`: Renamed ambiguous variables `l` → `line`
- `TRY003`: Extracted long error message to variable before ValueError
- `RUF100`: Reinstated necessary `noqa: PLR0913` for test helper with 6 parameters

Final state: All 873/874 tests passing (1 xfail expected), precommit and lint validation pass.

## Test Coverage

4 new tests in `tests/test_worktree_session.py`:
1. Single-line task movement and section transfer
2. Slug marker format and placement
3. Section creation when missing
4. Multi-line block preservation with continuation lines

All existing tests remain passing (73 worktree tests, 873 total).

## Next Steps

- Create commit with phase-2 cycles 2.1-2.4
- Continue with cycles 2.5-2.10 covering `remove_worktree_task()` and CLI integration
