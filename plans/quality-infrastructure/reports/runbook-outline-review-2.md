# Runbook Outline Review (2nd pass): Quality Infrastructure Reform

**Artifact**: plans/quality-infrastructure/runbook-outline.md
**Design**: plans/quality-infrastructure/outline.md (design-as-outline)
**Requirements**: plans/quality-infrastructure/requirements.md
**Date**: 2026-02-22
**Mode**: manual review + fix-all
**Prior review**: plans/quality-infrastructure/reports/runbook-outline-review.md (6 fixes applied)

## Summary

Second-pass review after prior agent review fixed 6 issues. Grep verification of the Step 1.6 file inventory against on-disk vet references found 6 missing files and 1 false positive. All fixes applied. Remaining structure, requirements coverage, design alignment, and phase typing are sound.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Items | Coverage | Notes |
|-------------|-------|-------------|----------|-------|
| FR-3a: review/correct renames | 1 | 1.1, 1.2, 1.4 | Complete | 6 renames + 1 embed + 1 deprecation |
| FR-3b: execution renames | 1 | 1.1, 1.4 | Complete | 5 renames |
| FR-3c: plan-specific deletions | 1 | 1.3 | Complete | 8 .claude/agents/ files |
| FR-3: skill + fragment renames | 1 | 1.5 | Complete | vet→review dir, vet-requirement→review-requirement |
| FR-3: terminology propagation | 1 | 1.6 | Complete | ~30 files (was ~25, corrected after grep verification) |
| FR-3: symlink sync + verification | 1 | 1.7 | Complete | Stale removal, sync, grep |
| FR-1: prose rules → communication.md | 2 | inline | Complete | 5 rules merged |
| FR-1: code rules → project-conventions | 2 | inline | Complete | Missing rule added, skill frontmatter |
| FR-1: deslop.md removal | 2 | inline | Complete | CLAUDE.md ref, file delete, stale refs |
| FR-2: code density entries | 3 | inline | Complete | 5 entries in cli.md |
| FR-2: memory-index triggers | 3 | inline | Complete | 5 /when triggers |

**Coverage Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Incomplete file inventory in Step 1.6**
   - Location: Step 1.6, Skills and Decision files lists
   - Problem: Grep verification found 6 files with confirmed vet references missing from the propagation list. 4 decision files (workflow-planning.md with 6 refs, workflow-core.md with 2 refs, deliverable-review.md with 2 refs, prompt-structure-research.md with 1 ref) and 2 skill files (remember/SKILL.md with 1 ref, memory-index/SKILL.md with 1 ref).
   - Fix: Added all 6 files to Step 1.6 lists. Updated Skills count 9→11, Decision files count 6→9.
   - **Status**: FIXED

### Minor Issues

1. **False positive file in Step 1.6**
   - Location: Step 1.6, Decision files list
   - Problem: `workflow-advanced.md` listed as "vet delegation" but grep confirms zero vet references in the file. Design's Impact Inventory listed it but appears to be a false positive.
   - Fix: Removed from list. Executing agent saves one unnecessary Read.
   - **Status**: FIXED

2. **File count propagation**
   - Location: Phase 1 objective, Requirements mapping table
   - Problem: Phase 1 said "~37 files" and mapping table said "~25 files" — both stale after inventory corrections.
   - Fix: Updated to "~43 files" and "~30 files" respectively.
   - **Status**: FIXED

## Fixes Applied

- Step 1.6 Skills — added remember/SKILL.md, memory-index/SKILL.md; count 9→11
- Step 1.6 Decision files — added workflow-planning.md, workflow-core.md, deliverable-review.md, prompt-structure-research.md; removed workflow-advanced.md (false positive); count 6→9
- Phase 1 objective — ~37 files → ~43 files
- Requirements mapping — ~25 files → ~30 files

## Verification Method

Grepped `agents/decisions/` and `agent-core/skills/` for `vet-fix-agent|vet-agent|design-vet-agent|vet.taxonomy|vet.requirement|/vet|vetting|vet.report`. Cross-referenced matches against outline's file lists. Verified each flagged file with targeted content grep to confirm actual vet references exist.

## Design Alignment

- **Architecture**: Aligned. Phase structure matches D-5 ordering.
- **Key decisions**: All 7 decisions traced to phases/steps.
- **Scope boundaries**: No scope creep. Substitution table has cross-cutting annotations.

---

**Ready for full expansion**: Yes
