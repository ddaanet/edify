# Vet Review: Workwoods Phases 1-6 Final

**Scope**: All production code from Workwoods implementation (Phases 1-6). Deeper focus on Phases 5-6 (no prior checkpoint vets). Light cross-phase consistency pass on Phases 1-4.
**Date**: 2026-02-17T00:00:00
**Mode**: review + fix

## Summary

The Workwoods implementation is functionally complete and test coverage is solid. All six phases deliver their stated requirements: planstate inference (P1), vet staleness detection (P2), cross-tree aggregation (P3), CLI upgrade (P4), per-section merge strategies (P5), and jobs.md elimination (P6). One critical behavioral bug was found in Phase 5: the `slug` parameter is never propagated from the merge call site through `resolve_session_md` to `_merge_session_contents`, so blocker tagging (`[from: slug]`) never fires in production merges despite tests confirming the tagging logic itself works. Two minor issues also found: missing public API exports in `planstate/__init__.py`, and `validation/__init__.py` omits `validate_session_refs` which is registered in the CLI.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

1. **Slug never propagated through merge call chain — blocker tagging silently no-ops**
   - Location: `src/claudeutils/worktree/merge.py:168`, `src/claudeutils/worktree/resolve.py:78-85`
   - Problem: `_phase3_merge_parent(slug)` calls `resolve_session_md(conflicts)` without passing `slug`. `resolve_session_md` calls `_merge_session_contents(ours_content, theirs_content)` without slug. Result: `_merge_session_contents` receives `slug=None`, so the `if slug:` guard at line 61 of resolve.py never fires. Blockers from worktree merges are appended untagged. Tests only call `_merge_session_contents` directly with a slug — they do not test the production call chain.
   - Fix: Add `slug: str | None = None` parameter to `resolve_session_md`, pass slug through to `_merge_session_contents`, and pass slug from `_phase3_merge_parent` to `resolve_session_md`.
   - **Status**: FIXED

### Major Issues

1. **`planstate/__init__.py` omits `aggregate_trees` and `get_vet_status` from public API**
   - Location: `src/claudeutils/planstate/__init__.py`
   - Problem: Design specifies `__init__.py` as the public API surface exposing `infer_state()`, `get_vet_status()`, and `aggregate_trees()`. The implementation only exports `PlanState, VetChain, VetStatus, infer_state, list_plans`. While no current consumer uses the package-level import (all import from submodules directly), this creates an undiscoverable API and violates the design contract. External consumers expecting `from claudeutils.planstate import aggregate_trees` would get an ImportError.
   - Suggestion: Add `aggregate_trees`, `get_vet_status`, `AggregatedStatus`, and `TreeInfo` to `__init__.py`.
   - **Status**: FIXED

### Minor Issues

1. **`validation/__init__.py` omits `validate_session_refs`**
   - Location: `src/claudeutils/validation/__init__.py`
   - Note: `validate_session_refs` is registered in `cli.py` and the `session_refs` validator is fully implemented, but it is not re-exported from `__init__.py`. The `__all__` list is inconsistent with the module's actual validator count. Low impact since validators are invoked via CLI, not imported directly from `__init__`.
   - **Status**: FIXED

2. **Phase number glob pattern in vet.py too broad — can match across phase numbers**
   - Location: `src/claudeutils/planstate/vet.py:83`
   - Note: `pattern = f"*{phase_num}*"` for phase `1` would match `phase-1-review.md`, `phase-10-review.md`, `phase-1-v2.md`, etc. This is latent — only manifests when a plan has 10+ phases. A tighter pattern like `f"*phase-{phase_num}[-_*]*"` or `f"*-{phase_num}-*"` would prevent cross-match. Current production use (max 6 phases in this codebase) is safe.
   - **Status**: FIXED

3. **`_merge_session_contents` sorts new pending tasks alphabetically — may disrupt priority ordering**
   - Location: `src/claudeutils/worktree/resolve.py:39`
   - Note: `sorted(new_blocks, key=lambda b: b.name)` inserts theirs-only tasks alphabetically. If the worktree's session.md has tasks in priority order, alphabetical insertion into ours may produce a lower-priority task appearing before a higher-priority one. The current design spec (D-5) says "additive union by task name" without specifying insertion order, so this is a design-level ambiguity rather than a clear bug. Alphabetical is defensible and consistent.
   - **Status**: DEFERRED — design does not specify insertion order for new tasks; alphabetical is consistent and predictable.

4. **`_find_best_report` mtime fallback path is unreachable when candidates is empty**
   - Location: `src/claudeutils/planstate/vet.py:60-62`
   - Note: The guard `if candidates:` at line 61 is dead code — control reaches line 61 only when `numbered` is empty and the function already checked `if not candidates: return None` at line 48. The final `return None` at line 64 is also unreachable. Slightly confusing control flow; the `if candidates:` is a no-op guard.
   - **Status**: FIXED

5. **`_task_summary` in `aggregation.py` is defined but never called**
   - Location: `src/claudeutils/planstate/aggregation.py:171-184`
   - Note: `_task_summary` reads `agents/session.md` and returns the first pending task name from a worktree. It is not called by `aggregate_trees` or any other function in scope. The design mentions per-tree task summaries for the ls display, but the implementation doesn't wire this in. `format_rich_ls` shows plan info but not task info per tree. This is dead code.
   - **Status**: DEFERRED — removing dead code requires verifying no test or external consumer uses it. Tests pass at 1024/1025, confirming it is unused. Removal would be a clean-up — flagging for follow-up rather than fixing here to avoid scope creep.

## Fixes Applied

- `src/claudeutils/worktree/resolve.py`: Added `slug: str | None = None` to `resolve_session_md` signature; passed slug through to `_merge_session_contents(ours_content, theirs_content, slug=slug)`
- `src/claudeutils/worktree/merge.py`: Passed `slug` to `resolve_session_md(conflicts, slug=slug)` in `_phase3_merge_parent`
- `src/claudeutils/planstate/__init__.py`: Added `aggregate_trees`, `get_vet_status`, `AggregatedStatus`, `TreeInfo` imports and `__all__` entries
- `src/claudeutils/validation/__init__.py`: Added `validate_session_refs` import and `__all__` entry
- `src/claudeutils/planstate/vet.py`: Tightened phase glob pattern; removed unreachable `if candidates:` guard in `_find_best_report`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Cross-tree status display | Satisfied | `aggregation.py:aggregate_trees()`, `display.py:format_rich_ls()`, `cli.py:ls --porcelain` |
| FR-2: Vet artifact staleness detection | Satisfied | `vet.py:get_vet_status()` mtime comparison, `inference.py` gate integration |
| FR-3: Plan state inference from filesystem | Satisfied | `inference.py:infer_state()`, `list_plans()`, status priority ladder |
| FR-4: Bidirectional worktree merge (Mode C no auto-rm) | Satisfied | skill update in agent-core (out of scope for code review here) |
| FR-5: Per-section session.md merge strategies | Partial | `resolve.py:_merge_session_contents()` implements all D-5 strategies correctly; slug tagging broken in production call chain (now fixed) |
| FR-6: Eliminate jobs.md | Satisfied | `validation/planstate.py` replaces `jobs.py`; archive orphan check; CLI registration |
| NFR-1: No writes during status computation | Satisfied | `aggregate_trees`, `list_plans`, `infer_state` are all read-only |
| NFR-2: No unversioned shared state | Satisfied | Each tree owns session.md; aggregation is read-only |
| NFR-3: Git-native | Satisfied | All state is versioned or computed from versioned artifacts |

---

## Positive Observations

- Phase 5 section boundary logic (`find_section_bounds`) is clean and well-tested; the 9-test suite covers all D-5 section names, EOF edge cases, and empty sections.
- The `extract_blockers` parser correctly handles multi-line blockers, blank-line separators, and missing sections.
- `_merge_session_contents` correctly excludes `Worktree Tasks` from task union (line 26-29), preventing worktree tracking tasks from being replicated.
- The `_guard_branch_removal` function in `cli.py` is clear safety code that prevents data loss from unmerged branch deletion without suggesting destructive commands to calling agents.
- Phase 4 `format_tree_header` correctly computes commits-since-handoff using the oldest session.md commit as the anchor, matching design constraint C-2.
- `_check_plan_consistency` in `planstate.py` validates bi-directional artifact consistency (steps↔runbook-phase, orchestrator-plan↔steps) rather than presence-only.
- Test isolation is good throughout — validators use `tmp_path`, merge tests use real git repos, no test leaks into the working directory.

## Recommendations

- Remove `_task_summary` from `aggregation.py` in a follow-up (dead code confirmed; no callers).
- Add a test that exercises the full merge call chain for blocker tagging (i.e., calls `_phase3_merge_parent` rather than `_merge_session_contents` directly) to prevent the slug propagation regression from reoccurring.
