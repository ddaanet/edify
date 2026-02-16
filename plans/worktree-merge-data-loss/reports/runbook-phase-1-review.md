# Runbook Review: Phase 1 (Core Implementation)

**Artifact**: plans/worktree-merge-data-loss/runbook-phase-1.md
**Design**: plans/worktree-merge-data-loss/design.md
**Outline**: plans/worktree-merge-data-loss/runbook-outline.md
**Date**: 2026-02-16
**Mode**: review + fix-all
**Phase types**: TDD (13 cycles)

## Summary

Phase 1 is well-structured with strong RED/GREEN discipline across 13 TDD cycles spanning two independent tracks. No prescriptive Python code found in GREEN phases. All RED phases use prose descriptions with specific assertions. Five issues identified: one major (vacuous cycle with incorrect RED failure claim), three major-minor boundary issues (weak expected failure, integration gap, stale line references), and one minor (missing existing test compatibility note). All fixed.

**Overall Assessment**: Ready

## Findings

### Major Issues

1. **Cycle 1.10: Vacuous RED phase — claims failure that cannot occur**
   - Location: Cycle 1.10 RED Phase
   - Problem: The cycle claims RED will fail with "Exit code 2 from Cycle 1.9 checkpoint (incorrectly blocking already-merged)." This is incorrect. Cycle 1.9 implements `if not _is_branch_merged(slug): exit 2`. For an already-merged branch, `_is_branch_merged` returns True, so the check passes and commit proceeds. The RED test would PASS, not fail. The GREEN phase also states "No additional code needed," confirming no code change drives this cycle.
   - Fix: Converted to `[REGRESSION]` cycle. Updated description to explicitly note RED is expected to PASS. Clarified the cycle's value as a regression guard that locks the idempotent behavior, not as a behavior-driving TDD cycle.
   - **Status**: FIXED

2. **Cycle 1.12: Missing integration wiring**
   - Location: Cycle 1.12 GREEN Phase
   - Problem: The cycle creates `_validate_merge_result` as a standalone function and tests it in isolation, but does not specify WHERE it gets called in `_phase4_merge_commit_and_precommit`. The design (line 155) specifies it runs after commit but before precommit. Without this wiring, Cycle 1.13's end-to-end test would not exercise the validation. The opus review (Finding 3) flagged the same gap.
   - Fix: Added "Integration wiring" section to GREEN phase specifying the call site: after the commit block, before `just precommit`. Added Scenario C to RED assertions for diagnostic logging (parent count warning). Added `Verify existing tests` line for `test_worktree_merge_merge_head.py` compatibility.
   - **Status**: FIXED

3. **Cycle 1.5: Weak expected failure description**
   - Location: Cycle 1.5 RED Phase
   - Problem: Expected failure was "Wrong success message format or branch deletion method" — vague. The actual RED delta is that current code outputs `"Removed worktree {slug}"` (line 382) while the test asserts `"Removed {slug}"` (without "worktree"). This is a specific, detectable difference.
   - Fix: Replaced vague expected failure with specific current-vs-expected comparison. Added detail about message differentiation being the behavioral change.
   - **Status**: FIXED

4. **Cycle 1.7: Unclear separation from Cycle 1.4**
   - Location: Cycle 1.7 RED/GREEN boundary
   - Problem: Cycle 1.4 GREEN already says "Before ANY destructive operations (before `_probe_registrations`)" which implies guard placement. Cycle 1.7 then says "Reorder rm() to execute guard FIRST" — overlapping concern. The expected failure "Some operations execute before guard" is ambiguous about what's different from Cycle 1.4's implementation.
   - Fix: Clarified that Cycle 1.7 tests integration ordering (side effects prevented) vs Cycle 1.4's guard logic (decision to refuse). Updated expected failure to focus on negative assertions (side effects observed despite guard refusal). The RED/GREEN delta is: guard may exist but rm() structure still allows downstream operations to execute.
   - **Status**: FIXED

### Minor Issues

5. **Cycle 1.8: Stale line number references after restructuring**
   - Location: Cycle 1.8 throughout
   - Problem: References "line 373", "lines 369-373" which will be stale after Cycles 1.4-1.7 restructure rm(). Executor would search for non-existent code at those line numbers.
   - Fix: Replaced all hard line number references with semantic descriptions (the `subprocess.run(["git", "branch", "-d", slug])` block with its error message). Added note that line numbers may have shifted.
   - **Status**: FIXED

6. **Cycle 1.8: Regression framing not explicit**
   - Location: Cycle 1.8 Note section
   - Problem: The cycle was described as testing "presentation" without explicitly framing it as a regression guard. The opus review (Finding 2) recommended this framing for clarity.
   - Fix: Updated Note to frame as regression guard for FR-5. Clarified that old fallback code is obsolete after Cycles 1.4-1.7 and this cycle removes it.
   - **Status**: FIXED

## Positive Observations

- No prescriptive Python code in any GREEN phase (all use behavior descriptions + hints)
- All RED phases use prose assertions with specific expected values, error messages, and failure explanations
- Prerequisite validation present for all creation cycles (1.1, 1.2, 1.4, 1.9)
- File references validated: all source files exist (`utils.py`, `cli.py`, `merge.py`, test files). New test files (`test_worktree_rm_guard.py`, `test_worktree_merge_correctness.py`) are to-be-created, which is correct for TDD.
- Checkpoint present after Cycle 1.13 with appropriate scope (Fix + Functional)
- Track independence maintained: Track 1 (1.1-1.8) and Track 2 (1.9-1.13) share only Cycle 1.1 as prerequisite
- Dependency ordering correct: foundation (`_is_branch_merged`) before consumers (guard, Phase 4 checkpoint)
- Density acceptable: no adjacent cycles with <1 branch point difference (Cycle 1.3 orphan edge case is genuine branch point in `_classify_branch`)
- Outline review was completed (both automated and opus interactive): `plans/worktree-merge-data-loss/reports/runbook-outline-review.md`, `runbook-outline-review-opus.md`

## Fixes Applied

- Cycle 1.5: Replaced vague expected failure with specific message comparison
- Cycle 1.7: Clarified RED/GREEN separation from Cycle 1.4 (integration ordering vs guard logic)
- Cycle 1.8: Replaced stale line numbers with semantic code references; added regression guard framing
- Cycle 1.10: Converted to `[REGRESSION]` cycle with correct RED expectation (PASS, not fail)
- Cycle 1.12: Added integration wiring to GREEN phase; added Scenario C for diagnostic logging; added existing test compatibility verification

## Unfixable Issues (Escalation Required)

None -- all issues fixed.

---

**Ready for next step**: Yes
