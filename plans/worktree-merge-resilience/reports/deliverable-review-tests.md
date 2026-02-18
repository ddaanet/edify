# Deliverable Review: Test Artifacts

**Scope**: Test suite for worktree-merge-resilience implementation (7 test files, ~2000 lines)
**Date**: 2026-02-18
**Design ref**: `plans/worktree-merge-resilience/outline.md`, `plans/worktree-merge-resilience/requirements.md`

## Summary

The test suite provides solid coverage of the state machine routing, conflict handling, and exit code semantics. All 5 D-5 states are tested through `merge()` integration tests. FR-1 through FR-5 and NFR-1/NFR-2 all have corresponding test assertions. The main gaps are: (1) `_detect_merge_state()` lacks direct unit tests for 3 of 5 states, and (2) several tests accept overly broad exit code ranges (`0 or 3`) where the scenario should deterministically produce one or the other.

**Overall Assessment**: Needs Minor Changes

---

## test_worktree_merge_routing.py

### Minor: _detect_merge_state unit coverage limited to 2 of 5 states
**Location:** test_worktree_merge_merge_head.py:12-84 (where unit tests live)
**Axis:** Coverage
**Design ref:** D-5
**Finding:** `_detect_merge_state()` is directly unit-tested for `merged` and `clean` states only (in `test_detect_state_merged`). The `parent_resolved`, `parent_conflicts`, and `submodule_conflicts` states are only tested indirectly through `merge()` routing in test_worktree_merge_routing.py. If `merge()` routing changes, these indirect tests could pass despite a broken `_detect_merge_state()`. Direct unit tests for each state would strengthen the contract.

### Minor: Broad exit code assertion in submodule_conflicts routing test
**Location:** test_worktree_merge_routing.py:190
**Axis:** Specificity
**Design ref:** D-5, NFR-1
**Finding:** `test_merge_continues_to_phase3_when_submodule_conflicts` asserts `exit_code in (0, 3)`. The test sets up a scenario where the parent branch has a non-conflicting `branch.txt` added, so after Phase 3 auto-resolves agent-core (--ours), no source conflicts should remain. The expected exit code should be deterministically `0`. Accepting `3` here weakens the assertion — a regression that incorrectly reports conflicts would pass.

### Minor: Merged state test calls merge() but doesn't verify Phase 1+2 execution
**Location:** test_worktree_merge_routing.py:59-86
**Axis:** Specificity
**Design ref:** D-5 (merged → Phase 1+2+4)
**Finding:** `test_merge_merged_state_routes_through_phase1_2_4` calls `merge("test-branch")` and checks the branch is still merged, but doesn't verify that Phase 1 (validation) or Phase 2 (submodule) actually executed. The test name claims routing through phases 1, 2, and 4, but only asserts the end state. A mock or spy on `_phase1_validate_clean_trees` / `_phase2_resolve_submodule` would confirm routing correctness.

### Minor: parent_resolved test doesn't assert state detection
**Location:** test_worktree_merge_routing.py:89-135
**Axis:** Specificity
**Design ref:** D-5
**Finding:** `test_merge_resumes_from_parent_resolved` sets up MERGE_HEAD with no conflicts and calls `merge()`, but never asserts `_detect_merge_state() == "parent_resolved"`. The state detection is assumed but not verified. If state detection returned `"clean"` instead, the test might still pass (clean state also runs Phase 4 after Phase 3 succeeds as no-op).

## test_worktree_merge_conflicts.py

### Major: test_conflict_output_contains_all_fields doesn't check status code type
**Location:** test_worktree_merge_conflicts.py:344
**Axis:** Specificity
**Design ref:** FR-4
**Finding:** The assertion `any(code in output for code in ["UU", "AU", "DU", "AA", "UD", "DD"])` checks that some status code exists in output but doesn't verify the correct code for the scenario. A both-modified conflict (same file edited on both sides) should produce `UU`. Asserting specifically `"UU" in output` would catch regressions where the status code formatting is wrong.

### Minor: No test for delete/modify conflict type in output
**Location:** test_worktree_merge_conflicts.py (missing)
**Axis:** Coverage
**Design ref:** FR-4 (conflicted file list with conflict type)
**Finding:** FR-4 requires "conflict type (both-modified, delete/modify, etc.)". Only both-modified (`UU`) scenarios are tested. No test creates a delete/modify conflict (one side deletes a file, other modifies) to verify the status code output shows e.g. `DU` or `UD`.

## test_worktree_merge_errors.py

### Minor: test_merge_aborts_cleanly_when_untracked_file_blocks name is misleading
**Location:** test_worktree_merge_errors.py:93
**Axis:** Specificity
**Design ref:** FR-3, NFR-2
**Finding:** The test name says "aborts cleanly" but the docstring says "adds untracked file and retries, resulting in conflict markers" and asserts `exit_code == 0`. The name contradicts D-3/NFR-2 (no abort). The test correctly validates FR-3 behavior (git add + retry), but the name should reflect recovery, not abort.

### Minor: test_merge_conflict_surfaces_git_error assertion is loose
**Location:** test_worktree_merge_errors.py:286
**Axis:** Specificity
**Design ref:** NFR-1
**Finding:** `assert "conflict" in result.output.lower() or "file.txt" in result.output` — the `or` makes this assertion always pass if either condition holds. A stronger assertion would check both: that the conflict file name appears AND that the output contains the conflict report structure (status code, hint line).

## test_worktree_merge_merge_head.py

### Minor: test_phase4_merge_head_empty_diff creates MERGE_HEAD manually
**Location:** test_worktree_merge_merge_head.py:119
**Axis:** Independence
**Design ref:** FR-5
**Finding:** Writing MERGE_HEAD directly to `.git/MERGE_HEAD` bypasses git's merge machinery. While this is valid for unit-testing Phase 4 in isolation, git's internal state (MERGE_MSG, MERGE_MODE files) is not set up. If `_phase4_merge_commit_and_precommit` ever relies on these auxiliary files, this test would give false confidence. The test is acceptable as-is but worth noting.

## test_worktree_merge_submodule.py

### Major: Submodule conflict tests accept exit 0 or 3 non-deterministically
**Location:** test_worktree_merge_submodule.py:310, :349
**Axis:** Specificity
**Design ref:** FR-1, D-2
**Finding:** Both `test_submodule_conflict_does_not_abort_pipeline` and `test_merge_resume_after_submodule_resolution` (first merge) assert `exit_code in (0, 3)`. Per D-2, submodule conflict leaves MERGE_HEAD in agent-core, continues to Phase 3. Phase 3 auto-resolves agent-core (--ours). If no other source conflicts exist, exit should be `0`. If source conflicts exist, exit should be `3`. The test setup creates only a submodule conflict (no parent source file conflicts), so exit `0` is the expected deterministic result. Accepting `3` masks regressions.

However: `test_submodule_conflict_does_not_abort_pipeline` then asserts agent-core MERGE_HEAD exists (line 319), which conflicts with exit 0 — if the merge completed successfully through Phase 4, agent-core MERGE_HEAD should have been consumed by the submodule merge resolution in Phase 3 → commit in Phase 4. This assertion may be checking the wrong thing, or the test may be detecting that the submodule conflict was *not* auto-resolved (which would mean exit 3). The non-deterministic exit code makes it hard to know which invariant the test is actually verifying.

### Minor: test_merge_submodule_fetch uses partial mock that's fragile
**Location:** test_worktree_merge_submodule.py:76-132
**Axis:** Independence
**Design ref:** D-6
**Finding:** The test patches `claudeutils.worktree.merge.subprocess.run` but only intercepts specific commands, passing others through. This creates coupling to the exact command sequence. If the implementation changes the order of `merge-base`, `cat-file`, and `fetch` calls, or changes which module's `subprocess.run` is called (e.g., `merge_state.subprocess.run`), the mock won't intercept. The test currently works but is fragile.

## test_worktree_merge_correctness.py

No issues found. This file provides solid coverage of Phase 4 edge cases (MERGE_HEAD loss, already-merged branch, single-parent warning) with precise exit code assertions.

## test_worktree_merge_validation.py

### Minor: test_merge_idempotency accepts exit code 2 as valid
**Location:** test_worktree_merge_validation.py:171
**Axis:** Specificity
**Design ref:** FR-5
**Finding:** `assert result.exit_code in (0, 2)` after a `git reset --hard HEAD~1` + re-merge. Exit code 2 means fatal/safety error, which is not a valid idempotency outcome. FR-5 requires idempotent resume — re-running should detect state and succeed. If exit 2 occurs, the branch was deleted or state is broken, which should be a test failure, not an accepted outcome.

---

## Positive Observations

- **Real git repos throughout**: Tests use `tmp_path` with real git operations, avoiding mock-heavy tests that miss integration issues. This catches real git behavior (MERGE_HEAD lifecycle, conflict markers, submodule mechanics).
- **NFR-2 compliance verified**: No test calls `git merge --abort` or `git clean -fd`. Tests assert "aborted" not in output and "Traceback" not in output — the no-data-loss invariant is actively verified.
- **Exit code 3 precisely tested**: `test_merge_reports_and_exits_3_when_parent_conflicts` and `test_merge_conflict_source_files` correctly assert `exit_code == 3` (not just non-zero), directly verifying NFR-1.
- **Conflict report structure tested**: `test_conflict_output_contains_all_fields` checks all FR-4 acceptance criteria (filename, status code, diff stats, divergence info, hint line with merge command and slug).
- **Resume flow tested end-to-end**: `test_merge_resume_after_submodule_resolution` exercises the full resolve-and-retry flow, verifying the wt_commit becomes ancestor of agent-core HEAD after resolution.
- **Phase 4 edge cases thorough**: `test_worktree_merge_correctness.py` covers 4 Phase 4 scenarios (MERGE_HEAD loss, already-merged, no-staged-unmerged, no-staged-merged) with precise exit codes and commit message checks.

---

## FR → Test Traceability

| Requirement | Test File | Test Function(s) | Status |
|-------------|-----------|-------------------|--------|
| FR-1: Submodule conflict doesn't abort parent merge | test_worktree_merge_submodule.py | `test_submodule_conflict_does_not_abort_pipeline` | Satisfied — asserts no Traceback, exit 0 or 3, continues pipeline |
| FR-2: Parent merge preserved on source conflicts | test_worktree_merge_routing.py, test_worktree_merge_errors.py | `test_merge_reports_and_exits_3_when_parent_conflicts`, `test_merge_conflict_surfaces_git_error` | Satisfied — asserts MERGE_HEAD exists after conflict, no abort |
| FR-3: Untracked file collision → git add + retry | test_worktree_merge_errors.py | `test_merge_aborts_cleanly_when_untracked_file_blocks`, `test_merge_untracked_file_same_content_auto_resolved` | Satisfied — tests both differing and same-content scenarios |
| FR-4: Conflict report contents | test_worktree_merge_conflicts.py | `test_conflict_output_contains_all_fields` | Satisfied — checks filename, status code, diff stat, divergence, hint |
| FR-5: Idempotent resume | test_worktree_merge_routing.py, test_worktree_merge_merge_head.py, test_worktree_merge_validation.py, test_worktree_merge_submodule.py | `test_merge_merged_state_routes_through_phase1_2_4`, `test_merge_resumes_from_parent_resolved`, `test_merge_continues_to_phase3_when_submodule_conflicts`, `test_merge_reports_and_exits_3_when_parent_conflicts`, `test_merge_clean_state_runs_full_pipeline`, `test_detect_state_merged`, `test_merge_resume_after_submodule_resolution` | Satisfied — all 5 states tested through merge() |
| NFR-1: Exit code 3 | test_worktree_merge_routing.py, test_worktree_merge_errors.py, test_worktree_merge_conflicts.py, test_worktree_merge_validation.py | `test_merge_reports_and_exits_3_when_parent_conflicts`, `test_merge_conflict_surfaces_git_error`, `test_conflict_output_contains_all_fields`, `test_merge_conflict_source_files` | Satisfied — multiple tests assert exact exit code 3 |
| NFR-2: No data loss | test_worktree_merge_routing.py, test_worktree_merge_errors.py | `test_merge_reports_and_exits_3_when_parent_conflicts` (MERGE_HEAD preserved), `test_merge_conflict_surfaces_git_error` (no abort in output, MERGE_HEAD preserved) | Satisfied — no abort/clean in source code, tests verify MERGE_HEAD preservation |

## D-5 State Machine Coverage

| State | Expected Route | Test Function | Status |
|-------|---------------|---------------|--------|
| merged | Phase 1+2+4 | `test_merge_merged_state_routes_through_phase1_2_4` | Tested (end state only, not phase execution) |
| parent_resolved | Phase 4 | `test_merge_resumes_from_parent_resolved` | Tested (MERGE_HEAD set up, merge completes with 2+ parents) |
| parent_conflicts | report + exit 3 | `test_merge_reports_and_exits_3_when_parent_conflicts` | Tested (exit 3, MERGE_HEAD preserved, conflict file in output) |
| submodule_conflicts | Phase 3+4 | `test_merge_continues_to_phase3_when_submodule_conflicts` | Tested (state detection verified, exit 0 or 3) |
| clean | Full pipeline | `test_merge_clean_state_runs_full_pipeline` | Tested (2 parents, merge commit message, branch merged) |

---

## Recommendations

- Tighten the `exit_code in (0, 3)` assertions to single expected values where the scenario is deterministic. The non-determinism suggests either the test setup is underspecified or the assertion is avoiding a flaky test.
- Add direct unit tests for `_detect_merge_state()` returning `parent_resolved`, `parent_conflicts`, and `submodule_conflicts` by constructing the git state and calling the function directly (same pattern as `test_detect_state_merged`).
- Rename `test_merge_aborts_cleanly_when_untracked_file_blocks` to reflect recovery semantics (e.g., `test_merge_recovers_from_untracked_file_collision`).
