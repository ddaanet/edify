# Vet Review: Phase 2 Checkpoint — workflow-rca-fixes

**Scope**: Phase 2 — review logic updates for type-agnostic runbooks
**Date**: 2026-02-15T10:30:00Z
**Mode**: review + fix

## Summary

Phase 2 implementation restructures runbook review logic to support per-phase type tagging (TDD vs general) while maintaining unified LLM failure mode detection across all phases. All three functional requirements satisfied with consistent application of type-agnostic review axes.

**Changed files:** 7 files (decision docs, skills, memory index, step reports)
**Issues found:** 0 critical, 1 major, 3 minor
**Issues fixed:** 4
**Unfixable:** 0

**Overall Assessment**: Ready

## Issues Found

### Major Issues

#### M-1: Incomplete General subsection coverage in Section 11.1 Vacuity

**Location**: agent-core/skills/review-plan/SKILL.md:270-278

**Problem**: Section 11.1 Vacuity provides TDD and General criteria, but General subsection is missing the behavioral vacuity detection protocol (pairwise achievability test) that appears in runbook-review.md.

**Expected**: Section 11.1 should include the behavioral vacuity detection protocol for General phases: "For consecutive steps modifying the same artifact, verify step N+1 produces an outcome not achievable by extending step N's implementation alone."

**Fix**: Add behavioral vacuity detection to Section 11.1 General subsection.

**Status**: FIXED

### Minor Issues

#### m-1: Section 11.4 missing file growth axis

**Location**: agent-core/skills/review-plan/SKILL.md:298-300

**Problem**: Section 11 lists 4 subsections (11.1-11.4) but runbook-review.md defines 5 review axes (vacuity, ordering, density, checkpoints, file growth). File growth axis is missing from Section 11.

**Note**: File growth is covered in Section 9 (File Reference Validation) indirectly, but the explicit axis from runbook-review.md should appear in Section 11 for completeness.

**Fix**: Add Section 11.5 for file growth axis.

**Status**: FIXED

#### m-2: Heuristic LOC/20 formatting inconsistency

**Location**: agents/decisions/runbook-review.md:27

**Problem**: Line 27 uses `LOC/20` (math notation), while line 277 in review-plan/SKILL.md uses `steps > LOC/20` (comparison format). Same heuristic, different presentation styles across documents.

**Note**: Minor presentation inconsistency — does not affect functionality. Both are correct, but standardizing improves readability.

**Fix**: Standardize to comparison format: `cycles/steps > LOC/20` in both documents.

**Status**: FIXED

#### m-3: Memory index trigger phrasing divergence

**Location**: agents/memory-index.md:126-130

**Problem**: Trigger keys changed from old format to new format (e.g., `/when detecting vacuous tdd cycles` → `/when detecting vacuous items`), but the pipe-separated context hints are inconsistent:
- Line 126: `/when detecting vacuous items` (no hint)
- Line 127: `/when ordering runbook dependencies` (no hint)
- Line 128: `/when evaluating item density` (no hint)
- Line 130: `/when planning for file growth | lines-per-cycle projection split points` (has hint)

**Note**: Inconsistent use of context hints. Either all should have hints or none.

**Fix**: Remove context hint from line 130 for consistency (the trigger key is sufficiently descriptive).

**Status**: FIXED

## Fixes Applied

### Fix M-1: Add behavioral vacuity detection to Section 11.1

**File**: agent-core/skills/review-plan/SKILL.md:270-280

**Change**: Expanded General subsection in Section 11.1 to include behavioral vacuity detection protocol matching runbook-review.md. Also standardized heuristic formatting to use "items" (generic term).

**Applied**:
- Added behavioral vacuity detection line to General subsection
- Changed "steps > LOC/20" to "items > LOC/20" for consistency with runbook-review.md

### Fix m-1: Add Section 11.5 for file growth axis

**File**: agent-core/skills/review-plan/SKILL.md:298-306

**Change**: Added Section 11.5 to match the 5 review axes from runbook-review.md.

**Applied**: Inserted Section 11.5 File Growth after Section 11.4 Checkpoint Spacing, before the "---" separator.

### Fix m-2: Standardize heuristic formatting

**File**: agents/decisions/runbook-review.md:27

**Change**: Changed `cycles/steps > LOC/20` to `items > LOC/20` for consistency with review-plan/SKILL.md.

**Applied**: Updated heuristic line to use "items" as generic term covering both cycles and steps.

### Fix m-3: Remove context hint for consistency

**Files**:
- agents/memory-index.md:130
- agent-core/skills/memory-index/SKILL.md:152

**Change**: Removed pipe-separated context hint from both memory index files for consistency.

**Applied**: Changed `/when planning for file growth | lines-per-cycle projection split points` to `/when planning for file growth` in both locations.

**Rationale**: Trigger key "planning for file growth" is sufficiently descriptive. Context hints not used consistently across other entries in same section.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: runbook-review.md restructured with TDD/General subsections for all axes | Satisfied | runbook-review.md:10-105 — 5 axes all have TDD/General subsections with behavioral detection protocols |
| FR-2: review-plan Section 11 expanded with General detection criteria | Satisfied | review-plan/SKILL.md:270-303 — Section 11.1-11.5 all include General criteria (11.1, 11.2, 11.3 expanded, 11.5 added) |
| FR-3: runbook Phase 0.95 has LLM failure mode gate with 4 criteria | Satisfied | runbook/SKILL.md:342-348 — LLM failure mode gate checks vacuity, ordering, density, checkpoints before outline promotion |

**Gaps**: None. All Phase 2 requirements satisfied.

## Positive Observations

**Type-agnostic architecture**: The restructuring cleanly separates type-specific criteria (TDD discipline, step quality) from universal criteria (LLM failure modes), enabling mixed runbooks without duplicating review logic.

**Behavioral vacuity detection**: The pairwise achievability test (N+1 achievable by extending N alone → merge) provides a concrete, testable criterion for vacuity detection in general phases, matching the rigor of TDD's RED/GREEN constraint checking.

**Restart-reason verification**: Section 6 restart-reason verification distinguishes @-referenced files (loaded at startup) from indexed files (on-demand recall), preventing false restart requirements. This catches the M-1 error pattern from Step 2.2 report.

**LLM failure mode gate**: Phase 0.95 gate catches common planning defects before expensive expansion, reducing wasted context and iteration cycles. Fix-inline-or-fall-through pattern prevents blocking on unfixable outline defects.

**Consistency across artifacts**: All five review axes appear in both runbook-review.md (decision doc) and review-plan Section 11 (executable skill), ensuring reviewers apply the same criteria regardless of entry point.

## Recommendations

**None**. Phase 2 implementation is complete and ready for Phase 3.

---

**Review by**: vet-fix-agent (Sonnet 4.5)
**Timestamp**: 2026-02-15T10:30:00Z
