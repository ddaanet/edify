# Holistic Runbook Review: Workwoods

**Artifact**: plans/workwoods/runbook-phase-{1-6}.md
**Date**: 2026-02-16
**Mode**: review + fix-all (cross-phase holistic)
**Phase types**: Mixed (4 TDD, 2 mixed)

## Summary

Six-phase runbook (33 TDD cycles + 10 general steps = 43 items) reviewed for cross-phase consistency after batching optimization. Found 1 major issue (dependency ordering in Phase 6 general steps), 5 minor issues (metadata gaps, stale file actions, formatting). All issues fixed. No unfixable issues.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Phase 6 dependency ordering: jobs.md deleted before validator removed**
   - Location: Steps 6.8-6.9
   - Problem: Step 6.8 deleted agents/jobs.md, but Step 6.9 removed validation/jobs.py. The jobs validator returns error "jobs.md not found" when the file is missing (line 94-95 of jobs.py). Running `just precommit` between these steps would fail.
   - Fix: Restructured Step 6.8 to remove only CLAUDE.md reference and focus_session (no file deletion). Moved jobs.md deletion to Step 6.10 (after validator removal in 6.9). Step 6.10 renamed to "Remove all jobs.md references from merge.py and delete jobs.md."
   - **Status**: FIXED

### Minor Issues

1. **Phases 3, 5, 6 missing Weak Orchestrator Metadata**
   - Location: Phase headers
   - Problem: No Total Steps/Cycles count or Restart required field. Orchestrator cannot validate item counts.
   - Fix: Added Weak Orchestrator Metadata sections: Phase 3 (7 cycles), Phase 5 (11 items: 8 TDD + 3 general), Phase 6 (11 items: 4 TDD + 7 general). All Restart required: No.
   - **Status**: FIXED

2. **Phase 4 informal metadata format**
   - Location: Phase 4 header, line 15
   - Problem: Used `**Total Steps:** 4 cycles` instead of proper Weak Orchestrator Metadata section. Missing Restart required field.
   - Fix: Replaced with standard Weak Orchestrator Metadata block (Total Cycles: 4, Restart required: No).
   - **Status**: FIXED

3. **Phase 1 metadata field name mismatch**
   - Location: Phase 1, line 20
   - Problem: "Total Steps: 5" for a pure TDD phase. Phase 2 uses "Total Cycles" for the same concept. Inconsistent terminology.
   - Fix: Changed to "Total Cycles: 5" to match Phase 2 convention.
   - **Status**: FIXED

4. **Phase 1 Cycle 1.2 stale file creation actions**
   - Location: Cycle 1.2 GREEN Phase, Changes section
   - Problem: Listed "Create module" for __init__.py and "Define PlanState dataclass" for models.py — both already created in Cycle 1.1. Stale actions from pre-consolidation.
   - Fix: Removed redundant __init__.py and models.py entries from Cycle 1.2 Changes. Remaining entries (inference.py, test file) updated to say "Existing file (from Cycle 1.1)."
   - **Status**: FIXED

5. **Phase 6 Step 6.5 double-bold model tag**
   - Location: Step 6.5, line 224
   - Problem: `**Model:** **Opus**` — inconsistent with all other model tags which use `**Model:** Opus`.
   - Fix: Changed to `**Model:** Opus (synthesis task...)`.
   - **Status**: FIXED

## Cross-Phase Validation Results

### Numbering Consistency
- Phase 1: 1.1-1.5 (sequential, no gaps)
- Phase 2: 2.1-2.5 (sequential, no gaps)
- Phase 3: 3.1-3.7 (sequential, no gaps)
- Phase 4: 4.1-4.4 (sequential, no gaps)
- Phase 5: 5.1-5.8 (TDD) + 5.9-5.11 (general) (sequential, no gaps)
- Phase 6: 6.1-6.4 (TDD) + 6.5-6.11 (general) (sequential, no gaps)
- All clean.

### Dependency Correctness
- Phase 2 → Phase 1: planstate module dependency. Correct.
- Phase 3 → Phases 1+2: aggregates planstate + vet. Correct.
- Phase 4 → Phase 3: CLI consumes aggregation. Correct. Cycle 4.3 includes prerequisite gate ("If missing, STOP").
- Phase 5 → Phase 1: execute-rule.md uses planstate. Correct. External dependency (worktree-merge-data-loss) documented with CRITICAL warning.
- Phase 6 → Phases 1+5: completes elimination after adoption. Correct.
- No forward references detected.

### Model Tag Consistency
- All general steps have explicit Model tags (verified Phase 5 Steps 5.9-5.11, Phase 6 Steps 6.5-6.11).
- Cycle 5.5 has Model: Haiku override (mechanical parametrized pattern) — appropriate for complexity.
- Assignments match task complexity: Opus for skill/fragment edits and synthesis, Sonnet for code removal, Haiku for mechanical grep-and-delete.

### Checkpoint Coverage
- Phase 1: End checkpoint (5 cycles — adequate)
- Phase 2: End checkpoint (5 cycles — adequate)
- Phase 3: End checkpoint (7 cycles — adequate, below 8-cycle threshold for mid-phase)
- Phase 4: End checkpoint (4 cycles — adequate)
- Phase 5: Checkpoint 5.a after Cycle 5.4, Checkpoint 5.mid after Cycle 5.8, Phase 5 Complete after Step 5.11 (3 checkpoints for 11 items — well-spaced)
- Phase 6: TDD Checkpoint after Cycle 6.4, Checkpoint after Step 6.10, Phase 6 Complete after Step 6.11 (3 checkpoints for 11 items — well-spaced)
- No gaps >10 items. No >2 phases without checkpoint.

### Design Traceability
- FR-1 (Cross-tree status): Phase 3 (aggregation) + Phase 4 (CLI upgrade)
- FR-2 (Vet staleness): Phase 2 (mtime detection)
- FR-3 (Plan state inference): Phase 1 (planstate module)
- FR-4 (Bidirectional merge): Phase 5 Step 5.9 (skill update)
- FR-5 (Per-section merge): Phase 5 Cycles 5.1-5.8
- FR-6 (Eliminate jobs.md): Phase 6 (archive, validator, removals)
- All FRs covered. No gaps.

### Renumbering Artifacts
- Old outline numbers (5.9/5.10 as cycles, 3.8, 6.12-6.15) exist only in runbook-outline.md and historical review reports.
- Current phase files use clean renumbered sequences. No stale cross-references.

### TDD Discipline in Batched Cycles
- Cycle 1.2: Parametrized 4 status levels — clear RED (AttributeError on .status), distinct GREEN (priority chain implementation). Sound.
- Cycle 5.5: Parametrized 3 keep-ours sections — clear RED (theirs content in merged result), GREEN adds section names to strategy mapping. Sound.
- All parametrized cycles have per-parameter assertions with expected failure reasons.

### General Step Quality
- All general steps have: Objective, Implementation details, Expected Outcome, Validation criteria.
- No deferred decisions ("determine"/"evaluate options") found.
- Prerequisites specified where needed (Step 5.9 reads SKILL.md, Step 5.10 reads execute-rule.md).

### Heading Level Consistency
- Phases 1-4: `## Cycle` (H2) items under `### Phase` (H3) header
- Phases 5-6: `### Cycle`/`### Step` (H3) items under `## TDD Portion`/`## General Portion` (H2) groupings
- Structural difference is deliberate for mixed-type phases (H2 groups by type, H3 for items). Both formats accepted by review skill.

## Fixes Applied

- Phase 1: Changed "Total Steps: 5" to "Total Cycles: 5" in metadata
- Phase 1: Removed redundant __init__.py and models.py creation entries from Cycle 1.2 GREEN Changes
- Phase 3: Added Weak Orchestrator Metadata (Total Cycles: 7, Restart required: No)
- Phase 4: Replaced informal "Total Steps" with proper Weak Orchestrator Metadata block
- Phase 5: Added Weak Orchestrator Metadata (Total Steps: 11, Restart required: No)
- Phase 6: Added Weak Orchestrator Metadata (Total Steps: 11, Restart required: No)
- Phase 6: Fixed dependency ordering — removed jobs.md deletion from Step 6.8, moved to Step 6.10
- Phase 6: Fixed double-bold model tag in Step 6.5

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
