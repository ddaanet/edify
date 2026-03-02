# Review: Phase 1 Checkpoint — Direction-aware merge pipeline

**Scope**: `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_from_main.py`
**Date**: 2026-03-02T00:00:00Z
**Mode**: review + fix

## Summary

Phase 1 implements `from_main: bool = False` parameter threading through `merge()` and all 4 phase functions, with correct behavioral branching in each. All 6 tests pass, `just dev` passes clean. Two issues identified: a suppressed `ARG001` in `merge()` that masks incomplete threading, and a weak assertion in `test_phase3_passes_from_main_to_auto_resolve` that allows the test to pass vacuously when the mock is never called.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`merge()` has `# noqa: ARG001` suppressing unused `from_main` — parameter not threaded**
   - Location: `src/claudeutils/worktree/merge.py:368`
   - Problem: `merge(slug: str, *, from_main: bool = False) -> None:  # noqa: ARG001` — the `from_main` parameter is declared but never passed to any phase call inside `merge()`. The noqa silences the linter warning rather than wiring it up. This means `merge("main", from_main=True)` never propagates direction to `_phase1_validate_clean_trees`, `_phase3_merge_parent`, or `_phase4_merge_commit_and_precommit`. The design spec (Cycle 1.1 GREEN) requires: "Thread to `_phase1_validate_clean_trees`, `_phase2_resolve_submodule`, `_phase3_merge_parent`, `_phase4_merge_commit_and_precommit`."
   - Fix: Pass `from_main=from_main` to all phase calls in `merge()`, remove the noqa.
   - **Status**: FIXED

### Minor Issues

1. **`_auto_resolve_known_conflicts` has `# noqa: ARG001` for `from_main` — stub annotation**
   - Location: `src/claudeutils/worktree/merge.py:211`
   - Note: `from_main: bool = False,  # noqa: ARG001` — this is intentional per the Cycle 1.2 GREEN spec ("pass-through for now — policies in Phase 2/3"). However the noqa should be removed once Phase 2 adds real use. Since Phase 2 is out of scope for this checkpoint, this is a known placeholder.
   - **Status**: DEFERRED — Cycle 1.2 GREEN explicitly documents this as a pass-through until Phase 2/3 implement resolution policies. Will be removed when `_auto_resolve_known_conflicts` branches on `from_main` in Phase 2.

2. **`test_phase3_passes_from_main_to_auto_resolve` assertion is vacuously true when mock not called**
   - Location: `tests/test_worktree_merge_from_main.py:229-235`
   - Note: The test body has `if mock_resolve.called: ...` — if `_auto_resolve_known_conflicts` is never called (e.g. because the merge completes without conflicts), the assertion block is skipped entirely and the test passes vacuously. The test does not verify that the mock was called at all. A conflict-free merge (no-conflict scenario) will never exercise the assertion. The docstring says "forwards from_main to _auto_resolve" but there's no `assert mock_resolve.called` before the conditional.
   - Fix: Add `assert mock_resolve.called` before the `if` block to ensure the forwarding path is actually exercised.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/merge.py:375,383,390,392,393,395` — Added `from_main=from_main` to all phase calls in `merge()`, removed `# noqa: ARG001` from `merge()` signature.
- `tests/test_worktree_merge_from_main.py:229` — Added `assert mock_resolve.called` to enforce that `_auto_resolve_known_conflicts` is actually invoked.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 (session.md preservation) | Partial — Phase 2 | `from_main` now threads to `_auto_resolve_known_conflicts`; `resolve_session_md` policy not yet implemented (Phase 2) |
| FR-2 (learnings merge inversion) | Partial — Phase 3 | `from_main` threads; `resolve_learnings_md` inversion not yet implemented (Phase 3) |
| FR-3 (delete/modify accept theirs) | Partial — Phase 2 | `from_main` threads to `_auto_resolve_known_conflicts`; DU/UD resolution not yet implemented (Cycle 2.3) |
| FR-4 (sandbox bypass) | Out of Scope | CLI flag (Phase 3) not yet implemented |
| FR-5 (idempotent resume) | Satisfied | Existing `_detect_merge_state` path unchanged; `from_main` threading does not break resume paths |
| C-1 (unify with existing infrastructure) | Satisfied | `from_main` added as parameter to existing pipeline, no duplication |
| C-2 (clean tree) | Satisfied | `_phase1_validate_clean_trees` continues to call `_check_clean_for_merge` |
| C-3 (worktree skill integration) | Out of Scope | Phase 3/4 |

**Gaps**: FR-1, FR-2, FR-3 partially implemented — resolution policies deferred to Phases 2/3 as designed.

---

## Positive Observations

- `_phase1_validate_clean_trees` correctly gates on `current_branch == "main"` using `symbolic-ref --short HEAD` rather than parsing branch names — correct detection approach.
- `_format_conflict_report` hint correctly omits the slug when `from_main=True` (the hint `--from-main` replaces the slug positional arg, matching the CLI contract from Q-1).
- `_phase4_merge_commit_and_precommit` correctly skips `_append_lifecycle_delivered` when `from_main=True` — main→worktree syncs should not advance worktree lifecycle.
- Test `test_phase4_skips_lifecycle_when_from_main` uses `patch` on `_parse_lifecycle_status` to isolate the test from lifecycle file parsing — correct isolation approach.
- `_run_git` import from `tests.fixtures_worktree` avoids duplication — proper reuse of shared test helpers.
- `contextlib.suppress(SystemExit)` in `test_phase3_passes_from_main_to_auto_resolve` correctly handles the case where phase 3 exits after resolution — test correctly tolerates both success and exit paths.

## Recommendations

- Phase 2 work: when `from_main` branching is added to `_auto_resolve_known_conflicts`, the `# noqa: ARG001` on that parameter can be removed as a natural part of implementing the policy.
