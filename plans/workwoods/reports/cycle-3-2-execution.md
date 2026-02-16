# Cycle 3.2: Detect main tree (is_main=True, slug=None)

**Timestamp:** 2026-02-17

## Execution Summary

- **Status:** GREEN_VERIFIED
- **Test command:** `pytest tests/test_planstate_aggregation.py::test_main_tree_detection -v`
- **RED result:** FAIL as expected (AttributeError: 'TreeInfo' object has no attribute 'is_main')
- **GREEN result:** PASS
- **Regression check:** 949/950 tests passed (1 known xfail)
- **Refactoring:** Code style fixes (added blank lines)
- **Files modified:**
  - `src/claudeutils/planstate/aggregation.py` — Added is_main and slug fields to TreeInfo, updated _parse_worktree_list() to compute them
  - `tests/test_planstate_aggregation.py` — Added test_main_tree_detection and updated test_parse_worktree_list_porcelain to include new fields
- **Stop condition:** None
- **Decision made:** Used Path.name to extract slug from worktree path (basename only, as specified)

## Implementation Details

Extended `aggregation.py` module with:
- **TreeInfo**: Updated NamedTuple to include is_main (bool) and slug (str | None) fields
- **_parse_worktree_list()**: Refactored to enumerate worktrees and assign:
  - First tree (index 0): is_main=True, slug=None (main repository)
  - Other trees: is_main=False, slug=Path(path).name (worktree directory basename)

Test cases:
- Main tree detection: Verifies first tree has is_main=True and slug=None
- Worktree slug extraction: Verifies other trees have is_main=False and correct slug from path basename
- Both tests work with 3-tree scenario (main + 2 worktrees)
