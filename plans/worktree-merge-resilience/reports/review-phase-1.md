# Runbook Review: Phase 1 — State detection + idempotent resume

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-1.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (5 cycles)

## Summary

Phase 1 implements `_detect_merge_state(slug)` and rewrites `merge()` to route based on detected state. The phase structure is sound and file references are valid. Two structural issues were found: (1) Cycle 1.1 GREEN described the full detection function including all states, which would make Cycles 1.4 and 1.5 RED phases non-failing; (2) Cycle 1.5 explicitly acknowledged its RED test may already pass — a direct TDD violation. Both were fixed by decomposing implementation incrementally across cycles.

**Overall Assessment**: Ready

## Findings

### Critical Issues

**Issue 1: Cycle 1.5 RED explicitly non-failing**
- Location: Cycle 1.5, RED Phase
- Problem: The RED phase stated "This test should already pass IF the state machine routes `clean` to the full pipeline" — directly acknowledging the test may not fail before GREEN. A RED that may already pass provides no TDD discipline guarantee.
- Fix: Rewrote the RED to specify a sabotage-then-revert protocol: apply a 1-line change to `_detect_merge_state` (return `"merged"` always) to force failure of the 2-parent assertion, then confirm RED fails, then proceed to GREEN. Added STOP condition if test passes without sabotage.
- **Status**: FIXED

### Major Issues

**Issue 2: Cycle 1.1 GREEN implemented full `_detect_merge_state` (all states)**
- Location: Cycle 1.1, GREEN Phase — `_detect_merge_state` behavior description
- Problem: Cycle 1.1 GREEN described the complete detection function including submodule MERGE_HEAD and parent MERGE_HEAD checks. If fully implemented in Cycle 1.1, Cycle 1.4's RED would not fail (submodule detection already exists) and Cycle 1.5 would pass immediately. RED/GREEN sequencing broken for Cycles 1.4 and 1.5.
- Fix: Scoped Cycle 1.1 GREEN to minimal implementation — `_is_branch_merged` check only, returning `"merged"` or `"clean"`. Added note that parent and submodule checks are added in Cycles 1.2 and 1.4 respectively. Moved parent MERGE_HEAD detection to Cycle 1.2 GREEN (which needed it for the `parent_resolved` routing test). Submodule check stays in Cycle 1.4 GREEN.
- **Status**: FIXED

**Issue 3: Cycle 1.2 GREEN did not document `_detect_merge_state` extension**
- Location: Cycle 1.2, GREEN Phase
- Problem: With Cycle 1.1 GREEN scoped to minimal, Cycle 1.2 GREEN needed to explicitly document the extension of `_detect_merge_state` to add parent MERGE_HEAD detection (required for `parent_resolved` routing to work). The original omitted this — it only documented the `merge()` routing rewrite.
- Fix: Added explicit "Behavior for `_detect_merge_state` extension" section to Cycle 1.2 GREEN, and added corresponding Changes entry for the extension alongside the `merge()` rewrite entry.
- **Status**: FIXED

**Issue 4: Cycle 1.4 RED assertions too weak — negative-only condition**
- Location: Cycle 1.4, RED Phase, Assertions
- Problem: "exit code is NOT 1" is a negative assertion that accepts any other exit code. More critically, with Cycle 1.1 GREEN implementing the full detection function, Cycle 1.4's RED would not fail at all. Even after fixing Issue 2, the expected failure reason was wrong — the correct failure is that `_detect_merge_state` (as of Cycle 1.2) does not check agent-core MERGE_HEAD, causing `"clean"` misclassification.
- Fix: Added a direct `_detect_merge_state` return value assertion (`"submodule_conflicts"` when agent-core is mid-merge), updated the expected failure reason to reflect the actual failure mode (misclassification as `"clean"`), and clarified that positive exit code (0 or 3) confirms correct routing.
- **Status**: FIXED

### Minor Issues

**Issue 5: Cycle 1.4 test setup — redundant `monkeypatch.chdir`**
- Location: Cycle 1.4, Test setup step 4
- Problem: `repo_with_submodule` fixture already calls `monkeypatch.chdir(repo_path)` internally. Instructing the executor to also call `monkeypatch.chdir` is confusing and would cause a double-chdir.
- Fix: Changed step 4 to note "chdir already handled by fixture" and removed the explicit monkeypatch instruction.
- **Status**: FIXED

**Issue 6: Cycle 1.2 test setup missing `mock_precommit` mention**
- Location: Cycle 1.2, Test setup
- Problem: Common context states "Use `mock_precommit` fixture for all cycles." Cycle 1.2 test setup steps did not mention it explicitly — the executor must know to include it when invoking `merge()` which can reach Phase 4.
- Fix: Added explicit `mock_precommit` to step 4 of Cycle 1.2 test setup.
- **Status**: FIXED

## Fixes Applied

- Cycle 1.1 GREEN: Scoped `_detect_merge_state` implementation to `merged`/`clean` only; added note that remaining states added in Cycles 1.2 and 1.4
- Cycle 1.2 GREEN: Added `_detect_merge_state` extension behavior (parent MERGE_HEAD detection); added corresponding Changes entry
- Cycle 1.2 test setup step 4: Added explicit `mock_precommit` fixture mention
- Cycle 1.4 RED assertions: Added `_detect_merge_state` direct return value assertion; updated expected failure reason to correct misclassification cause
- Cycle 1.4 GREEN: Rewrote from "verify existing behavior" to "add submodule MERGE_HEAD check" — now clearly additive with specific implementation behavior
- Cycle 1.4 test setup step 4: Removed redundant `monkeypatch.chdir` (fixture handles it)
- Cycle 1.5 RED: Replaced "may already pass" acknowledgment with sabotage-then-revert protocol; added STOP condition for weak assertions; updated test setup to remove redundant chdir note

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
