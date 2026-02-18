# Vet Review: Phase 3 Checkpoint — Conflict Preservation + Untracked File Recovery

**Scope**: Phase 3 implementation in `merge.py`, updated tests for conflict/untracked scenarios, module extraction to `merge_state.py`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix

## Summary

Phase 3 correctly implements D-3 (conflict preservation — no abort/clean) and D-4 (untracked file recovery via git add + retry). The core behavioral logic is sound. Three lint violations blocked `just dev` on entry (C901 complexity, two B904 missing exception chaining). The module extraction was not yet done. All four issues were fixed: `merge_state.py` created, `merge.py` reduced from 441 to 312 lines, complexity reduced from 11 to 6, B904 compliant.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`just dev` failing — lint violations and line limit exceeded**
   - Location: `src/claudeutils/worktree/merge.py`
   - Problem: Three ruff failures blocked precommit: C901 (`_recover_untracked_file_collision` complexity 11 > 10), B904 x2 (missing `from err` / `from None` in except clauses at original lines 237, 250). Additionally file at 441 lines exceeds 400-line limit. Module extraction was specified in task prompt but not yet done.
   - Fix: Extracted `_detect_merge_state` and `_recover_untracked_file_collision` into `merge_state.py`. Split `_recover_untracked_file_collision` into `_parse_untracked_files` + `_add_and_commit_files` helpers to reduce McCabe complexity from 11 to 6. Added `from err` to both except clauses. Updated imports in `merge.py` and two test files.
   - **Status**: FIXED

### Minor Issues

1. **`test_merge_aborts_cleanly_when_untracked_file_blocks` located in errors test file**
   - Location: `tests/test_worktree_merge_errors.py:93`
   - Note: This test exercises recovery behavior (untracked file auto-resolution), not an error condition. Its natural home is `test_worktree_merge_validation.py`, where `test_merge_untracked_file_same_content_auto_resolved` already lives. The misplacement doesn't affect correctness but reduces discoverability.
   - **Status**: DEFERRED — test is in scope (changed file) but relocation is cosmetic and would require updating test module imports; acceptable to address in a future cleanup pass.

2. **`test_merge_conflict_surfaces_git_error` located in errors test file but tests conflict exit code**
   - Location: `tests/test_worktree_merge_errors.py:230`
   - Note: Tests exit code 3 + MERGE_HEAD preserved — this is conflict-preservation behavior (D-3), not an error-handling concern. Minor categorization issue only.
   - **Status**: DEFERRED — same rationale as above; no correctness impact.

## Fixes Applied

- `src/claudeutils/worktree/merge_state.py` — created: `_detect_merge_state`, `_parse_untracked_files`, `_add_and_commit_files`, `_recover_untracked_file_collision`. Extracted from `merge.py`. B904-compliant exception chaining throughout. `_recover_untracked_file_collision` complexity reduced from 11 to 6 by factoring out parse and add steps.
- `src/claudeutils/worktree/merge.py` — removed `_detect_merge_state` and `_recover_untracked_file_collision` (was 441 lines, now 312). Added imports from `merge_state.py`.
- `tests/test_worktree_merge_merge_head.py:8` — updated import: `_detect_merge_state` now from `claudeutils.worktree.merge_state`.
- `tests/test_worktree_merge_routing.py:10` — updated import: `_detect_merge_state` now from `claudeutils.worktree.merge_state`.

All changes committed. `just dev` passes: 1057/1058 (1 xfail known pre-existing), precommit OK.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-3: No abort/clean -fd, preserve MERGE_HEAD on conflict | Satisfied | `_phase3_merge_parent` exits 3 on conflict, no abort call; `test_merge_conflict_surfaces_git_error` asserts MERGE_HEAD.returncode == 0 |
| D-4: Untracked files — git add then retry | Satisfied | `_recover_untracked_file_collision` parses stderr, adds files, commits, retries; `test_merge_aborts_cleanly_when_untracked_file_blocks` asserts exit 0 |
| D-7: No data loss invariant | Satisfied | No `git merge --abort` or `git clean -fd` in any code path; conflict handler preserves staged content |
| Module extraction (session.md blocker) | Satisfied | `merge_state.py` created; `merge.py` at 312 lines (well below 400 limit) |

---

## Positive Observations

- `_parse_untracked_files` handles both git error message variants ("untracked working tree file" and "your local changes...would be overwritten") — covers git version differences.
- Recovery path checks MERGE_HEAD after retry rather than trusting return code alone — handles the case where merge started but produced conflicts.
- `test_merge_untracked_file_same_content_auto_resolved` verifies the key D-4 invariant: same-content untracked file results in exit 0 AND branch fully merged (ancestor check).
- `test_merge_conflict_surfaces_git_error` asserts "aborted" not in output — explicitly validates D-3 preservation.
- Tests use real git repos (`tmp_path`), not mocked subprocess — behavior tested end-to-end.
