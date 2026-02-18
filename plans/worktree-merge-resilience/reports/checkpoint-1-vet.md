# Vet Review: Phase 1 Checkpoint — State Machine Routing

**Scope**: `_detect_merge_state`, `merge()` routing, tests in `test_worktree_merge_merge_head.py` and `test_worktree_merge_routing.py`
**Date**: 2026-02-18
**Mode**: review + fix

## Summary

State machine implementation correctly follows D-5 detection ordering and handles all 5 states. The "merged" state routing deviation (Phase 1+2+4 instead of D-5's Phase 4 only) is correct — branches at HEAD are their own ancestors, and Phase 2 is no-op when submodule already resolved. Tests cover all routing paths except the "merged" state integration path through `merge()`. D-7 no-data-loss invariant is satisfied in new code (parent_conflicts exits 3, preserves MERGE_HEAD).

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing integration test for "merged" state routing**
   - Location: `tests/test_worktree_merge_routing.py`
   - Problem: `test_detect_state_merged` in merge_head.py tests detection only. No test verifies that `merge()` with a merged branch routes through Phase 1+2+4 and succeeds. The diagnostic fix (Cycle 1.2) that changed "merged" from Phase 4 only to Phase 1+2+4 has no integration coverage.
   - Suggestion: Add test that calls `merge()` with an already-merged branch and verifies exit 0 + branch still merged.
   - **Status**: FIXED

2. **Phase 3 still calls `git merge --abort` + `git clean -fd` (D-7 violation)**
   - Location: `src/claudeutils/worktree/merge.py:213-218`
   - Problem: Data loss on conflict paths — violates D-7 no-data-loss invariant.
   - **Status**: DEFERRED — Phase 3 Cycles 3.1-3.2 will remove abort+clean. Scope OUT explicitly lists this.

3. **`err=True` on `click.echo` calls (D-8 violation)**
   - Location: `src/claudeutils/worktree/merge.py:199, 232, 246, 274-276, 280`
   - Problem: D-8 requires all output to stdout. Several error/warning paths still use `err=True`.
   - **Status**: DEFERRED — Phase 5 (Step 5.1/5.2) handles `err=True` migration to stdout. Scope OUT.

### Minor Issues

1. **`_format_git_error` is dead code**
   - Location: `src/claudeutils/worktree/merge.py:15-24`
   - Note: Defined but never called anywhere in the codebase. Pre-existing (before Phase 1).
   - **Status**: OUT-OF-SCOPE — pre-existing, not introduced by current changes.

2. **`_detect_merge_state` uses raw subprocess for MERGE_HEAD checks instead of `_git` helper**
   - Location: `src/claudeutils/worktree/merge.py:43-56`
   - Note: `_git` returns stdout string, not CompletedProcess. Checking returncode requires raw subprocess. This is a deliberate pattern used consistently throughout merge.py for return-code-dependent checks.
   - **Status**: OUT-OF-SCOPE — deliberate pattern, not a defect.

## Fixes Applied

- `tests/test_worktree_merge_routing.py` — Added `test_merge_merged_state_routes_through_phase1_2_4` integration test: creates already-merged branch, calls `merge()`, verifies exit 0, branch still merged, and no extra parents added (fast-forward-like behavior for already-merged state).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-5: State detection ordering | Satisfied | `_detect_merge_state` checks merged→submodule→parent→clean (merge.py:40-67) |
| D-5: 5-state coverage | Satisfied | `merge()` handles all 5 states with routing dispatch (merge.py:302-325) |
| D-7: No data loss in new code | Satisfied | `parent_conflicts` branch echoes conflicts + exit 3, preserves MERGE_HEAD (merge.py:310-317). No abort/clean in new routing code. |
| FR-5: Idempotent resume | Satisfied | parent_resolved→Phase 4, submodule_conflicts→Phase 3+4, merged→Phase 1+2+4 |

## Positive Observations

- Detection order matches D-5 spec exactly (merged first, clean last as fallback)
- parent_conflicts handler correctly preserves merge state (no abort, exit 3)
- "merged" routing deviation well-justified: Phase 2 is no-op when submodule resolved, Phase 1 validates preconditions
- Tests verify behavioral outcomes (parent count, merge message, exit codes) not implementation details
- Test refactoring (466→268 lines) preserved all behavioral assertions while extracting reusable helpers
