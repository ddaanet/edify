# Cycle 1.2: Branch classification — _classify_branch(slug) returns count and focused flag

**Timestamp:** 2025-02-16 17:00 UTC
**Status:** GREEN_VERIFIED

## Test Execution

**Test command:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`

### RED Phase

**Expected failure:** ImportError — `_classify_branch` function doesn't exist
**Actual failure:** ImportError — function import failed as expected
**Result:** RED verified ✓

### GREEN Phase

**Implementation:** Added `_classify_branch(slug: str) -> tuple[int, bool]` to `src/claudeutils/worktree/cli.py`

**Behavior:**
- Gets merge-base between HEAD and slug
- Counts commits between merge-base and slug tip using `git rev-list --count`
- If count == 1, checks if commit message matches exactly `f"Focused session for {slug}"`
- Returns (count, is_focused)
- Handles orphan branches (no merge-base) by returning (0, False)

**Test cases verified:**
1. Focused-session-only branch (1 commit with marker): returns (1, True) ✓
2. Real-history branch (1 user commit): returns (1, False) ✓
3. Multi-commit branch (3 commits): returns (3, False) ✓
4. Wrong marker format (similar but incorrect message): returns (1, False) ✓

**Test result:** PASS ✓
**Regression check:** All 888 tests pass (887 passed, 1 xfail — expected) ✓

## Refactoring

### Formatting

- Fixed line length issue in test docstring (split to 88-char limit)
- No additional reformatting needed

### Code Quality Checks

- **Lint status:** All checks passed for modified files
- **File size warning:** cli.py now 407 lines (under 420 threshold, monitoring for extraction)
- **Complexity warnings:** None from modified code

## Files Modified

- `src/claudeutils/worktree/cli.py` — Added `_classify_branch` helper function (28 LOC)
- `tests/test_worktree_rm_guard.py` — Added `test_classify_branch` with 4 test cases (145 LOC)

## Commit Status

- **WIP commit created:** d5bf5cf "WIP: Cycle 1.2 Branch classification..."
- **Ready for amendment:** Yes

## Decision Made

None — implementation follows design specification exactly.

## Notes

The test required careful setup to ensure git checkout commands were placed correctly:
- Must switch back to main (git checkout -) BEFORE calling _classify_branch
- Each test case needs independent setup and cleanup
- This ensures merge-base calculations work correctly from the main branch context
