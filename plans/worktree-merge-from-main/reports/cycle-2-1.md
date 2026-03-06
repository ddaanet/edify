### Cycle 2.1: resolve_session_md from-main policy 2026-03-02
- Status: GREEN_VERIFIED
- Test command: `just test tests/test_worktree_merge_from_main.py::test_resolve_session_md_from_main_keeps_ours_exactly tests/test_worktree_merge_from_main.py::test_resolve_session_md_default_direction_still_merges`
- RED result: FAIL as expected — `TypeError: resolve_session_md() got an unexpected keyword argument 'from_main'`
- GREEN result: PASS — both tests pass after adding `from_main: bool = False` (keyword-only) to `resolve_session_md`
- Regression check: 1599/1600 passed (1 xfail pre-existing)
- Refactoring: Fixed FBT001/FBT002 lint errors by making `from_main` keyword-only (`*` separator); moved local imports in test to top-level to fix PLC0415
- Files modified: `src/claudeutils/worktree/resolve.py`, `tests/test_worktree_merge_from_main.py`
- Stop condition: none
- Decision made: Added two tests — primary (`test_resolve_session_md_from_main_keeps_ours_exactly`) which fails as expected, and regression (`test_resolve_session_md_default_direction_still_merges`) which passes confirming existing behaviour is preserved. Regression test uses default call (no `from_main` kwarg) so it passes today and guards against regressions in GREEN.
