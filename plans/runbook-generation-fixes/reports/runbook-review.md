# Runbook Review: runbook-generation-fixes

**Artifact**: plans/runbook-generation-fixes/ (4 phase files, 13 step files, orchestrator plan)
**Date**: 2026-02-22
**Mode**: review + fix-all
**Phase types**: Mixed (4 TDD phases, 1 inline phase)
**Reviewer**: Manual review against plan-reviewer criteria (SKILL.md)

## Summary
- Total items: 13 cycles across 4 TDD phases + 1 inline phase (5 items)
- Issues found: 1 critical, 3 major, 1 minor
- Issues fixed: 5
- Unfixable (escalation required): 0
- Overall assessment: Ready

## Critical Issues

### Issue 1: Trailing next-phase preamble in PHASE_BOUNDARY step files
**Location**: step-1-3.md, step-2-5.md, step-3-3.md
**Problem**: Last step file in each phase contained the complete preamble of the next phase (prerequisites, post-state, completion validation). Caused by prepare-runbook.py extracting cycle content through end of assembled content without recognizing phase headers as boundaries. Executing agents would see next phase's context as part of their current step, contaminating scope.
**Fix**: Removed trailing phase preamble from all 3 step files.
**Status**: FIXED

## Major Issues

### Issue 2: Cycle 1.3 Expected Failure contradicts fixture design
**Location**: step-1-3.md (RED phase), runbook-phase-1.md (Cycle 1.3)
**Problem**: RED phase claims "Expected failure: phases 3-5 will have incorrect step_phases mappings" but note says fixture "already has phase headers." extract_sections() handles well-formed content correctly — test would PASS in RED, not fail. Agent would be confused when RED passes.
**Fix**: Reframed as "[VERIFICATION]" test. Replaced expected failure with "Expected outcome (verification): test should PASS in RED" with investigation guidance if it fails.
**Status**: FIXED

### Issue 3: Cycles 3.2 and 3.3 missing model specification
**Location**: step-3-2.md (setup), step-3-3.md (fixture), runbook-phase-3.md
**Problem**: After Cycle 2.5 removes haiku fallback, all pipeline tests need explicit model at frontmatter or phase level. Cycle 3.2 setup had no model; Cycle 3.3 Phase 2 header had `(type: general)` without model. Both tests would hit model validation error before reaching Phase Context testing.
**Fix**: Added `model: sonnet` to Cycle 3.2 setup (frontmatter + both phase headers) and Cycle 3.3 Phase 2 header.
**Status**: FIXED

### Issue 4: Cycle 4.1 missing model in phase file headers
**Location**: step-4-1.md (setup), runbook-phase-4.md (Cycle 4.1)
**Problem**: Phase file setup for PHASE_BOUNDARY test didn't specify models on phase headers. After Cycle 2.5, these would fail model validation.
**Fix**: Added `(model: sonnet)` to both phase file descriptions in setup.
**Status**: FIXED

## Minor Issues

### Issue 5: Cycle 2.3 stale "write before 2.2" instruction
**Location**: step-2-3.md, runbook-phase-2.md (Cycle 2.3)
**Problem**: Execution note says "Write this test before implementing Cycle 2.2" but orchestrator plan runs 2.3 after 2.2. The instruction contradicts the actual execution order.
**Fix**: Reframed to "Cycle 2.2 is already implemented at this point. This test should PASS; if it fails, Cycle 2.2 introduced a regression."
**Status**: FIXED

## Fixes Applied
- step-1-3.md: Removed 18 lines of trailing Phase 2 content; reframed expected failure to verification outcome
- step-2-3.md: Reframed execution note for post-2.2 execution context
- step-2-5.md: Removed 19 lines of trailing Phase 3 content
- step-3-2.md: Added frontmatter `model: sonnet` and phase-level models to test setup
- step-3-3.md: Removed 20 lines of trailing Phase 4 content; added `model: sonnet` to Phase 2 fixture header
- step-4-1.md: Added `(model: sonnet)` to phase file setup descriptions
- runbook-phase-1.md: Reframed Cycle 1.3 expected failure (source consistency)
- runbook-phase-2.md: Reframed Cycle 2.3 execution note (source consistency)
- runbook-phase-3.md: Added models to Cycle 3.2 setup and Cycle 3.3 Phase 2 fixture (source consistency)
- runbook-phase-4.md: Added models to Cycle 4.1 phase file descriptions (source consistency)

## Unfixable Issues (Escalation Required)
None — all issues fixed.
