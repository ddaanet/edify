# Runbook Review: Phase 6 (jobs.md Elimination + Archive)

**Artifact**: plans/workwoods/runbook-phase-6.md
**Date**: 2026-02-16T18:45:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (5 TDD cycles, 9 general steps)

## Summary

Phase 6 implements jobs.md elimination through planstate validator (TDD, cycles 6.1-6.5) and plan-archive migration (general, steps 6.7-6.15). Review identified 1 major issue (vacuous cycle) and 2 minor issues (missing checkpoint, conditional step clarity). All issues fixed.

**Overall Assessment**: Ready

## Critical Issues

None identified.

## Major Issues

### Issue 1: Cycle 6.5 Vacuity

**Location**: Cycle 6.5 (lines 200-236, now removed)
**Problem**: Cycle 6.5 explicitly stated "This cycle merges with 6.4 (registration IS the integration). Keeping as separate cycle for clarity." This is vacuous — the cycle doesn't add behavioral coverage beyond 6.4. Test assertions duplicated 6.4's registration verification.

**Fix**: Removed Cycle 6.5 entirely. Renumbered Cycle 6.6 → 6.5 (jobs validator test removal). Updated all cross-references (TDD Checkpoint, test references in 6.5 GREEN phase).

**Status**: FIXED

## Minor Issues

### Issue 1: Missing General Steps Checkpoint

**Location**: Steps 6.7-6.15 (9 consecutive general steps)
**Problem**: Gap >10 items (total phase has 14 items: 5 TDD + 9 general) without checkpoint in general portion violates LLM failure mode criterion (checkpoint spacing).

**Fix**: Added checkpoint after Step 6.13 titled "Checkpoint: jobs.md Removal Progress". Checkpoint verifies code reference removal, CLAUDE.md cleanup, and skill consistency before file deletion steps.

**Status**: FIXED

### Issue 2: Conditional Step Clarity

**Location**: Step 6.13 (focus_session update)
**Problem**: Step had "If no reference: skip this step" without verification-first pattern. Executors might skip without checking.

**Fix**: Added prerequisite validation ("Grep codebase for focus_session()") and restructured implementation with explicit search-then-decide flow. Updated validation command to use grep pattern matching.

**Status**: FIXED

## Fixes Applied

- Removed vacuous Cycle 6.5 (registration verification that duplicated 6.4)
- Renumbered Cycle 6.6 → Cycle 6.5
- Updated TDD Checkpoint reference from "After Cycle 6.6" → "After Cycle 6.5"
- Updated test count reference in Cycle 6.5 from "6.1-6.5" → "6.1-6.4"
- Added checkpoint after Step 6.13 for general steps verification
- Added prerequisite validation to Step 6.13 (grep for focus_session before conditional logic)
- Restructured Step 6.13 implementation with explicit search-then-decide flow
- Updated Step 6.13 validation command to use pattern matching

## Additional Observations

**TDD Quality (Cycles 6.1-6.5):**
- All GREEN phases use behavior descriptions + hints (no prescriptive code) ✓
- All RED phases have specific test names, assertions, expected failures ✓
- Sequencing follows foundation → consistency → integration pattern ✓
- Cycle 6.4 properly handles CLI integration (both all-validators and subcommand) ✓

**General Steps Quality (6.7-6.15):**
- All steps have clear objectives, implementation, expected outcomes ✓
- Step 6.7 correctly uses git log for plan history extraction ✓
- Steps 6.8-6.9, 6.15 (skill edits) assigned to Opus per design directive ✓
- Step 6.11-6.12 (code cleanup) properly sequenced: validator removal before code removal ✓
- Step 6.14 has dependency verification (6.7 and 6.8-6.13 complete) before deletion ✓

**File References:**
- All referenced files exist in current worktree ✓
- validation/jobs.py exists (to be deleted in 6.11) ✓
- Skills exist at referenced paths (agent-core/skills/*) ✓

**Checkpoint Spacing:**
- TDD Checkpoint after Cycle 6.5 (after 5 cycles) ✓
- General Checkpoint after Step 6.13 (after 7 general steps) ✓
- Final Phase Checkpoint after Step 6.15 (complete) ✓

**Dependency Ordering:**
- Foundation-first: validator creation (6.1-6.5) → adoption (6.7-6.15) ✓
- Archive creation (6.7) before reference updates (6.8-6.9) ✓
- Consumer updates (6.8-6.13) before file deletion (6.14) ✓
- Code removal (6.11) before worktree skill update (6.15) ✓

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
