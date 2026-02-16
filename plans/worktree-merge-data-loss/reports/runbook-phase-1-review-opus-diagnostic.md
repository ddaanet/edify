# Runbook Review: Phase 1 (Opus Diagnostic — Second Pass)

**Artifact**: plans/worktree-merge-data-loss/runbook-phase-1.md
**Design**: plans/worktree-merge-data-loss/design.md
**Outline**: plans/worktree-merge-data-loss/runbook-outline.md
**Prior review**: plans/worktree-merge-data-loss/reports/runbook-phase-1-review.md (5 fixes applied)
**Date**: 2026-02-16
**Mode**: review + fix-all (diagnostic second pass)
**Phase types**: TDD (13 cycles)

## Summary

Second-pass diagnostic review focusing on design alignment, source code verification, and issues the first review may have missed. Five issues found: one major (orphan guard message untested), two minor (unverifiable flag assertions, ambiguous skip semantics), two minor (mock reference in integration test, conditional RED failure). All fixed. Design decisions D-1 through D-7 verified aligned. No UNFIXABLE issues.

**Overall Assessment**: Ready

## Findings

### Major Issues

1. **Cycle 1.4: Orphan guard refusal message untested**
   - Location: Cycle 1.4 RED Phase assertions
   - Problem: Cycle 1.4 GREEN implements two guard messages — one for real history (`"has {count} unmerged commit(s)"`) and one for orphan branches (`"is orphaned (no common ancestor)"`). The RED phase only tested real history (Scenario A). The orphan-specific message from design line 55 had no RED coverage. Cycle 1.3 tests classification `(0, False)` but not the guard's refusal message for orphans.
   - Fix: Added Scenario B to Cycle 1.4 RED — orphan branch creation + guard refusal with orphan-specific message assertion.
   - **Status**: FIXED

### Minor Issues

2. **Cycles 1.5/1.6: Unverifiable `-d`/`-D` flag assertions**
   - Location: Cycle 1.5 and 1.6 RED Phase assertions
   - Problem: Assertions said "Verify `git branch -d` was used" and "Verify `git branch -D` was used." Design specifies real git repos (no mocked subprocess), so the flag itself cannot be directly observed. An executor might waste time trying to intercept subprocess calls.
   - Fix: Reframed as behavioral verification. Cycle 1.5: "Branch was merged before deletion (safe delete with `-d` succeeds for merged branches; no force required)." Cycle 1.6: "Branch deleted despite being unmerged (force delete required — `-d` alone would fail for unmerged branch)."
   - **Status**: FIXED

3. **Cycle 1.8: RED failure conditional on Cycles 1.5-1.6 implementation**
   - Location: Cycle 1.8 RED Phase expected failure
   - Problem: If Cycles 1.5-1.6 replace the old branch deletion code at cli.py:369-373 entirely, Cycle 1.8's RED may pass for all scenarios (no old fallback code remains to emit `"git branch -D"`). The expected failure assumed the old code would persist through Cycles 1.4-1.7.
   - Fix: Added note: "If Cycles 1.5-1.6 already replaced this code path, RED may pass for all scenarios — in that case, the GREEN phase is a no-op cleanup verification and the test remains as a regression guard."
   - **Status**: FIXED

4. **Cycle 1.11: "skip silently" ambiguity**
   - Location: Cycle 1.11 GREEN Phase behavior description
   - Problem: "skip silently (nothing to do — already merged)" could be read as "return from function early" vs "skip commit only." Design flow (line 155) specifies "validate ancestry after any successful commit or skip, then precommit" — the skip is commit-only, function continues.
   - Fix: Changed to "skip commit (nothing to commit — already merged). Function continues to validation/precommit."
   - **Status**: FIXED

5. **Cycle 1.7: Mock reference inconsistent with testing strategy**
   - Location: Cycle 1.7 RED Phase assertion on `_probe_registrations`
   - Problem: Assertion said "verify via mock or side effect absence." Design specifies real git repos (no mocked subprocess for git operations). Offering "mock" as an option contradicts the testing strategy.
   - Fix: Changed to "verify via side effect absence: no worktree prune or removal occurred."
   - **Status**: FIXED

## Design Alignment Verification

| Decision | Runbook Coverage | Status |
|----------|-----------------|--------|
| D-1: Focused session via marker text | Cycle 1.2 RED: exact marker `"Focused session for {slug}"` verified against cli.py:175 | Aligned |
| D-2: rm exit codes (0/1/2) | Cycles 1.4 (exit 1), 1.5-1.6 (exit 0) | Aligned |
| D-3: No destructive CLI output | Cycle 1.8: tests `"git branch -D"` absence in all output | Aligned |
| D-4: MERGE_HEAD checkpoint | Cycle 1.9: exit 2 when MERGE_HEAD absent + branch unmerged | Aligned |
| D-5: Post-merge ancestry | Cycle 1.12: `_validate_merge_result` with diagnostic logging | Aligned |
| D-6: Guard before destruction | Cycle 1.7: negative assertions verify no side effects before guard | Aligned |
| D-7: `_is_branch_merged` in utils.py | Cycle 1.1: function placed in utils.py, used by both tracks | Aligned |

## Source Code Verification

- cli.py:175 — `f"Focused session for {slug}"` confirmed (Cycle 1.2 marker text)
- cli.py:347-382 — `rm()` function boundaries confirmed (Cycle 1.4 prerequisite)
- cli.py:373 — `f"Branch {slug} has unmerged changes — use: git branch -D {slug}"` confirmed (Cycle 1.8 target)
- cli.py:382 — `f"Removed worktree {slug}"` confirmed (Cycle 1.5 expected failure)
- merge.py:261-299 — `_phase4_merge_commit_and_precommit` confirmed (Cycle 1.9 prerequisite)
- merge.py:282-285 — `if merge_in_progress` / `elif staged_check` confirmed (Cycle 1.9-1.11 target)
- utils.py:1-38 — module structure confirmed (Cycle 1.1 prerequisite)
- test_worktree_rm.py — exists, 3 tests (Cycles 1.4-1.8 regression target)
- test_worktree_merge_merge_head.py — exists, 1 test (Cycle 1.12 compatibility)

## Cross-Track Dependency Verification

- Cycle 1.1 (`_is_branch_merged`): shared prerequisite correctly stated in Cycle 1.9 dependencies and Cycle 1.4 GREEN behavior
- Track 1 (1.1-1.8) and Track 2 (1.9-1.13) share only Cycle 1.1; no other cross-track dependencies
- Cycle 1.13 integration test correctly depends on Cycles 1.9-1.12

## Checkpoint Spacing

13 cycles in single phase with checkpoint after Cycle 1.13. At threshold (guideline flags >10) but acceptable because:
- Two independent tracks reduce coupling (effective 8 + 5, not 13 sequential)
- Light checkpoint (Fix + Functional) matches implementation-only phase
- No architectural changes requiring heavy review

## File Growth Projection

cli.py: 382 current + ~35 LOC delta = ~417 projected. Session.md monitoring directive at 420 noted. Under enforcement threshold (400) by design estimate, approaching monitoring threshold. No action needed — session.md already tracks.

## Fixes Applied

- Cycle 1.4: Added orphan guard refusal scenario (Scenario B) to RED assertions
- Cycle 1.5: Reframed `-d` flag verification as behavioral (merged branch deletion succeeds)
- Cycle 1.6: Reframed `-D` flag verification as behavioral (unmerged branch deletion requires force)
- Cycle 1.7: Replaced "mock or side effect absence" with concrete side-effect-absence check
- Cycle 1.8: Added conditional RED failure note for when prior cycles remove old code path
- Cycle 1.11: Clarified "skip silently" to "skip commit, function continues to validation/precommit"

## Unfixable Issues (Escalation Required)

None -- all issues fixed.

---

**Ready for next step**: Yes
