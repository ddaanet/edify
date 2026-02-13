# Cycle 4.1: Task extraction by name with metadata and formatting

**Timestamp:** 2026-02-12T17:15:00Z

## Status: GREEN_VERIFIED

## Execution Summary

### RED Phase
- **Test command:** `just test tests/test_worktree_cli.py::test_focus_session_task_extraction`
- **Result:** FAIL as expected
- **Failure message:** `ImportError: cannot import name 'focus_session'`
- **Verification:** Test correctly identifies missing function

### GREEN Phase
- **Test command:** `just test tests/test_worktree_cli.py::test_focus_session_task_extraction`
- **Result:** PASS after implementation
- **Implementation:** Added `focus_session()` function to parse session.md and extract task by name

### Regression Check
- **Test command:** `just test tests/test_worktree_cli.py`
- **Result:** 16/16 passed ✓
- **Regressions:** None

### Refactoring
- **Lint:** `just lint` → PASS
- **Precommit:** Line limit warnings (src/claudeutils/worktree/cli.py: 421 lines, tests/test_worktree_cli.py: 411 lines)
- **Complexity:** No violations
- **Changes:** Fixed import placement (moved inline import to module top-level per PLC0415)

## Files Modified

- `src/claudeutils/worktree/cli.py` — Added `focus_session()` function
- `tests/test_worktree_cli.py` — Added `test_focus_session_task_extraction()` test

## Implementation Details

**Function: `focus_session(task_name: str, session_md_path: str | Path) -> str`**

Extracts a task from session.md file by matching task name pattern and generates a focused session document.

**Behavior:**
- Reads session.md file
- Searches for task line matching pattern: `- [ ] **<task-name>** <metadata>`
- Extracts full task line with metadata (command, model, restart flag)
- Generates focused session with:
  - H1 header: `# Session: Worktree — <task-name>`
  - Status line: `**Status:** Focused worktree for parallel execution.`
  - Pending Tasks section containing only extracted task
- Returns formatted string (not written to file)

**Technical approach:**
- Uses regex `re.search()` with pattern preserving metadata
- Handles task lines with trailing metadata (command, model flags)
- Raises `ValueError` if task not found

## Notes

Line limit warnings present but expected for this phase. Files exceed 400-line limit:
- `src/claudeutils/worktree/cli.py`: 421 lines
- `tests/test_worktree_cli.py`: 411 lines

These will be addressed in architecture refactoring (Phase 4 refactor checkpoint).

## Stop Condition

None — cycle complete and verified.

## Decisions Made

- Regex pattern includes space after `**` to properly capture metadata with correct spacing
- Used `rstrip()` on captured metadata to handle trailing newlines
- Pattern uses non-greedy matching with lookahead to stop at next task or section
