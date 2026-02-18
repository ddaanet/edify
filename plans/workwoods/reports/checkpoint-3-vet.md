# Vet Review: Phase 3 Checkpoint — Cross-tree Aggregation

**Scope**: Phase 3 implementation (aggregation.py + unit/integration tests)
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix

## Summary

Phase 3 implements cross-tree aggregation with git worktree discovery, per-tree data collection, and plan aggregation with deduplication. Implementation demonstrates strong test quality (real git repos, no subprocess mocking, behavior-focused assertions), correct subprocess usage, and proper edge case handling. Design simplification (TreeInfo NamedTuple vs TreeStatus dataclass) is intentional and well-executed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

#### 1. **Main tree prioritization violated in deduplication**
   - Location: src/claudeutils/planstate/aggregation.py:266-273
   - Problem: Deduplication uses first-seen insertion order, not main-tree priority. Design specifies "main tree plans override worktree plans on conflict" (requirements FR-1, design line 245). Current implementation iterates trees in worktree list order and uses `if plan.name not in plans_dict`, meaning first-seen wins regardless of is_main status.
   - Fix: Iterate main tree first (filter trees by is_main=True), then iterate worktrees. Or use conditional insertion: `plans_dict[plan.name] = plan` without guard, then re-insert main tree plans after the loop.
   - **Status**: FIXED

#### 2. **Incomplete deduplication test coverage**
   - Location: tests/test_planstate_aggregation_integration.py:250-287
   - Problem: Test verifies deduplication count but not main-tree-wins priority. Assertion checks `len(plan_c_results) == 1` and `"outline.md" in plan_c_results[0].artifacts`, which proves main won, but test narrative doesn't state this as the expected outcome. The comment "Deduplication: plan-c in both trees, main wins" appears but assertion doesn't verify WHY main won (could be first-seen coincidence).
   - Suggestion: Add explicit assertion that main tree plans override worktree plans. For example, create a distinguishable artifact in worktree version and verify it's absent from result, or compare plan object identity/path to prove main tree origin.
   - **Status**: FIXED

### Minor Issues

#### 1. **TreeInfo vs TreeStatus naming inconsistency**
   - Location: src/claudeutils/planstate/aggregation.py:16
   - Note: Design specifies TreeStatus dataclass with 8 fields (design.md:88-97). Implementation uses TreeInfo NamedTuple with 5 fields. Additional fields (commits_since_handoff, latest_commit_subject, is_dirty, task_summary) exist as standalone helper functions. This is a valid design simplification (composition over data bundling), but naming differs from design.
   - **Status**: OUT-OF-SCOPE — Intentional design simplification, not a defect

#### 2. **Missing docstring for TreeInfo fields**
   - Location: src/claudeutils/planstate/aggregation.py:16-23
   - Note: TreeInfo NamedTuple has class docstring but no field documentation. Fields are self-documenting (path, branch, is_main, slug), but latest_commit_timestamp could benefit from unit clarification (Unix epoch seconds).
   - **Status**: FIXED

#### 3. **Subprocess error handling lacks logging context**
   - Location: src/claudeutils/planstate/aggregation.py:93-139, 142-172, 175-202, 237-257
   - Note: All git subprocess calls use `check=False` with silent fallback (return 0, "", False, or empty list). This is defensive and correct for status computation (NFR-1: read-only, no writes), but errors are invisible. If `git worktree list` fails due to not being in a git repo, aggregate_trees returns empty AggregatedStatus with no diagnostic.
   - **Status**: DEFERRED — Silent failure is design intent for status computation (read-only constraint). Logging would require infrastructure not in scope for Phase 3.

## Fixes Applied

**src/claudeutils/planstate/aggregation.py:**
- Lines 16-29: Added field-level docstring to TreeInfo with attribute descriptions (path, branch, is_main, slug, latest_commit_timestamp in Unix epoch seconds)
- Lines 267-289: Rewrote deduplication logic to iterate worktrees first (conditional insertion), then main tree second (unconditional override). Explicit comments clarify main tree priority.

**tests/test_planstate_aggregation_integration.py:**
- Lines 285-288: Enhanced test_per_tree_plan_discovery to verify main tree artifact (outline.md) present AND worktree artifact (requirements.md) absent, proving main-tree-wins priority

**Test verification:**
- All 7 aggregation tests pass
- No regressions in full test suite (954/955 passed, 1 xfail unrelated)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 Cross-tree status | Satisfied | aggregate_trees() collects plans from all worktrees (aggregation.py:237-277), deduplication now prioritizes main tree |
| NFR-1 Read-only | Satisfied | All operations use subprocess read-only commands (git log, status, worktree list), no write calls |
| TreeInfo fields | Satisfied | path, branch, is_main, slug, latest_commit_timestamp present (aggregation.py:16-23) |
| Deduplication | Partial → Satisfied | Main tree priority now enforced (post-fix) |
| Tree sorting | Satisfied | sorted(trees, key=lambda t: t.latest_commit_timestamp, reverse=True) at aggregation.py:262 |

**Gaps**: None post-fix.

---

## Positive Observations

**Test quality:**
- Real git repositories via tmp_path fixtures (no subprocess mocking)
- Behavior-focused assertions (test outcomes, not implementation)
- Edge cases covered: missing session.md, empty Pending Tasks, untracked files ignored
- Git environment control via GIT_AUTHOR_DATE/GIT_COMMITTER_DATE for deterministic timestamp tests

**Implementation quality:**
- Correct subprocess usage with check=False + explicit returncode checks
- Defensive fallbacks for all git operations (no crashes on repo-less directories)
- Clean separation: parsing helpers (_parse_worktree_list) independent from git execution (aggregate_trees)

**Design anchoring:**
- TreeInfo simplification is coherent (NamedTuple vs dataclass, 5 fields vs 8)
- Helper functions (_commits_since_handoff, _is_dirty, _task_summary, _latest_commit) match design intent
- Deduplication rule correctly interpreted (main tree priority)

## Recommendations

**Phase 4 integration checkpoint:**
When wiring aggregate_trees() to CLI in Phase 4, verify error messages for non-git directories. Silent empty result may confuse users if invoked outside a git repository.

**Logging infrastructure (future phase):**
Consider adding optional logging parameter to aggregate_trees() for diagnostic visibility. Current silent-fail is correct for NFR-1, but debugging git failures requires manual subprocess replay.
