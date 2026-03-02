### Cycle 1.2: Batch from_main adaptation of merge.py phase functions 2026-03-02
- Status: RED_VERIFIED
- Test command: `just test tests/test_worktree_merge_from_main.py`
- RED result: FAIL as expected — 5 new tests fail with `TypeError: got an unexpected keyword argument 'from_main'` (functions not yet accept `from_main` parameter)
- GREEN result: N/A (RED phase only)
- Regression check: 1/1 existing test passed (test_merge_accepts_from_main_keyword)
- Refactoring: none
- Files modified: tests/test_worktree_merge_from_main.py
- Stop condition: none
- Decision made: none

**Tests written:**
- `test_phase1_rejects_main_branch_when_from_main` — `_phase1_validate_clean_trees("main", from_main=True)` on main → TypeError (no param yet)
- `test_phase1_passes_on_non_main_branch_when_from_main` — same call on feature branch → TypeError (no param yet)
- `test_phase4_skips_lifecycle_when_from_main` — `_phase4_merge_commit_and_precommit(..., from_main=True)` → TypeError
- `test_format_conflict_report_hints_from_main` — `_format_conflict_report([...], "main", from_main=True)` → TypeError
- `test_phase3_passes_from_main_to_auto_resolve` — `_phase3_merge_parent("feature", from_main=True)` → TypeError

All 5 fail as expected. RED phase verified.
