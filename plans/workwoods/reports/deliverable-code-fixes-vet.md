# Vet Review: Workwoods Planstate Deliverable Code Fixes (M-4/M-5/M-6/M-7)

**Scope**: M-4 gate priority chain, M-5 dynamic phase discovery, M-6 TreeInfo enrichment + display.py rewrite, M-7 tests
**Date**: 2026-02-18
**Mode**: review + fix

## Summary

All four deliverables (M-4 through M-7) are implemented and functional. 36 tests pass. The gate priority chain correctly implements the D-7 four-type priority order. Dynamic phase discovery uses glob instead of a hardcoded map. TreeInfo carries all design-specified fields. display.py has no subprocess calls. Minor deslop issues found and fixed: redundant branch strip, trivial docstrings, duplicate comment.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Redundant branch strip in display.py**
   - Location: `src/claudeutils/worktree/display.py:10`
   - Note: `tree.branch.replace("refs/heads/", "")` is dead code — `aggregation.py` already strips `refs/heads/` when building `TreeInfo.branch` (line 44). The else-branch default `"main"` is also unreachable since `TreeInfo.branch` is always set from git output.
   - **Status**: FIXED

2. **Narration comment duplicates docstring in inference.py**
   - Location: `src/claudeutils/planstate/inference.py:63`
   - Note: `# Phase-level gates inserted dynamically between runbook-outline and outline` restates the priority ordering already documented in `_first_stale_gate`'s docstring on line 68.
   - **Status**: FIXED

3. **Trivial private-function docstrings in inference.py**
   - Location: `src/claudeutils/planstate/inference.py:11,33,44`
   - Note: `_collect_artifacts`, `_determine_status`, `_derive_next_action` docstrings restate the function names without adding non-obvious behavior information.
   - **Status**: FIXED

4. **Trivial docstring in display.py**
   - Location: `src/claudeutils/worktree/display.py:9`
   - Note: `"""Format a single tree header line from aggregated TreeInfo."""` — "from aggregated TreeInfo" names the parameter type, adding no behavioral information.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/display.py:9` — Simplified docstring to remove redundant parameter type description
- `src/claudeutils/worktree/display.py:10` — Replaced redundant branch strip with direct field access; removed unreachable else-branch
- `src/claudeutils/planstate/inference.py:63` — Removed narration comment that duplicated the docstring
- `src/claudeutils/planstate/inference.py:11,33,44` — Removed trivial single-line docstrings from private helper functions

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-7: Gate priority chain (design > runbook outline > phase-level > outline) | Satisfied | `inference.py:58-92` — `_GATE_PRIORITY` covers first two; phase loop covers third; outline check covers fourth |
| Dynamic phase discovery (plans with 7+ phases covered) | Satisfied | `vet.py:18-23` — `_build_source_report_map` globs `runbook-phase-*.md` dynamically |
| TreeInfo fields: path, slug, branch, is_main, commits_since_handoff, latest_commit_subject, latest_commit_timestamp, is_dirty, task_summary | Satisfied | `aggregation.py:16-28` — all 9 fields present |
| display.py uses aggregated TreeInfo data, no subprocess calls | Satisfied | `display.py` — no subprocess import; calls `aggregate_trees()` once |

---

## Positive Observations

- Gate priority chain test coverage is thorough: 8 parametrized cases covering all priority levels, combinations, and empty input.
- `_find_best_report` correctly separates numbered iterations from named variants (e.g., `-opus`) and applies the right selection rule per category.
- `_commits_since_handoff` uses a two-step git query (anchor hash → rev-list count), handling missing anchor gracefully by returning 0.
- Integration tests in `test_worktree_ls_upgrade.py` use real git repos via `tmp_path`, not mocked subprocess. Correct approach for this layer.
- `aggregate_trees` correctly handles main-tree-wins conflict resolution (main overrides worktree on name collision).
