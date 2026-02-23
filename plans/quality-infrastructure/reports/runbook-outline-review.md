# Runbook Outline Review: Quality Infrastructure Reform

**Artifact**: plans/quality-infrastructure/runbook-outline.md
**Design**: plans/quality-infrastructure/outline.md (design-as-outline)
**Requirements**: plans/quality-infrastructure/requirements.md
**Date**: 2026-02-22
**Mode**: review + fix-all

## Summary

Well-structured runbook outline with complete requirements coverage across 3 phases. Phase 1 (general, 7 steps) handles the complex cross-codebase rename; Phases 2-3 (inline) handle additive prose edits. Six issues found and fixed: missing step dependency declarations, two over-specified model selections, a line count inaccuracy, missing post-phase state awareness for Phase 2, and missing scope boundary annotations on the substitution table.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Items | Coverage | Notes |
|-------------|-------|-------------|----------|-------|
| FR-3a: review/correct renames | 1 | 1.1, 1.2, 1.4 | Complete | 6 renames + 1 embed + 1 deprecation |
| FR-3b: execution renames | 1 | 1.1, 1.4 | Complete | 5 renames |
| FR-3c: plan-specific deletions | 1 | 1.3 | Complete | 8 .claude/agents/ files verified present on disk |
| FR-3: skill + fragment renames | 1 | 1.5 | Complete | D-6 (review-requirement), D-7 (/review skill) |
| FR-3: terminology propagation | 1 | 1.6 | Complete | 24 files, substitution table |
| FR-3: symlink sync + verification | 1 | 1.7 | Complete | Stale removal, sync, grep |
| FR-3d: unchanged agents | -- | -- | Complete | No action needed (refactor, brainstorm-name already clean nouns) |
| FR-1: prose rules to communication.md | 2 | inline | Complete | 5 rules merged, examples stripped per D-4 |
| FR-1: code rules to project-conventions | 2 | inline | Complete | Missing "expose fields" rule added, skill frontmatter per D-3 |
| FR-1: deslop.md removal | 2 | inline | Complete | CLAUDE.md ref, file delete, 5 stale ref files |
| FR-2: code density entries | 3 | inline | Complete | 5 entries in cli.md sourced from grounding report |
| FR-2: memory-index triggers | 3 | inline | Complete | 5 /when triggers |

**Coverage Assessment**: All requirements covered. FR-3d (unchanged agents) correctly excluded from mapping -- no action needed.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Type | Assessment |
|-------|-------|------------|------|------------|
| 1 | 7 | High | general | Appropriate -- 37 files, cross-codebase coordination |
| 2 | 5 items | Low | inline | Appropriate -- additive prose, all decisions pre-resolved |
| 3 | 2 items | Low | inline | Appropriate -- additive entries from grounding report |

**Balance Assessment**: Well-balanced. Phase 1 is large but cannot be split further without breaking rename atomicity (partial renames leave inconsistent state). Phases 2-3 are correctly typed as inline -- they are additive prose edits with no implementation uncertainty.

### Complexity Distribution

- **Low complexity phases**: 2 (Phases 2, 3)
- **Medium complexity phases**: 0
- **High complexity phases**: 1 (Phase 1)

**Distribution Assessment**: Appropriate. The high complexity is inherent to the cross-codebase rename operation, not a structural problem.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing step dependency declarations**
   - Location: Steps 1.2, 1.4, 1.5, 1.6, 1.7
   - Problem: Steps reference output of prior steps (renamed files, embedded content) without explicit dependency declarations. Step 1.4 updates frontmatter in files renamed by 1.1; Step 1.6 propagates names from 1.1, 1.2, 1.4, 1.5.
   - Fix: Added `Depends on:` declarations to all dependent steps (1.2, 1.4, 1.5, 1.6, 1.7) with specific rationale for each dependency.
   - **Status**: FIXED

2. **Missing scope boundary annotations on substitution table**
   - Location: Substitution Table section
   - Problem: Substitution table is a cross-cutting concern spanning Steps 1.4-1.7 but had no explicit "addressed by steps X, Y" or "out of scope: Z" annotations. Executing agents need to know which steps handle which substitution categories.
   - Fix: Added scope boundary paragraph before the substitution tables listing which steps handle agent names, terminology, and deprecations, plus out-of-scope note for crew- prefix.
   - **Status**: FIXED

3. **Missing post-phase state awareness in Phase 2**
   - Location: Phase 2, skills frontmatter bullet
   - Problem: Phase 2 references artisan.md and test-driver.md without noting these are post-Phase-1 names. Agent executing Phase 2 needs to know these files were renamed in Phase 1.
   - Fix: Added parenthetical "(renamed from quiet-task.md in Phase 1)" and "(renamed from tdd-task.md in Phase 1)" to the affected bullet.
   - **Status**: FIXED

### Minor Issues

1. **vet-taxonomy line count inaccuracy**
   - Location: Step 1.2
   - Problem: States "63 lines" but actual file is 62 lines (`wc -l` verified).
   - Fix: Changed to "62 lines".
   - **Status**: FIXED

2. **Step 1.2 model over-specified**
   - Location: Step 1.2
   - Problem: Specified opus for "agent definition prose editing." The actual operations are mechanical: read taxonomy content, insert into corrector.md at specified location, delete two files. No architectural judgment needed.
   - Fix: Changed to sonnet with rationale "mechanical content insertion + file deletion".
   - **Status**: FIXED

3. **Step 1.4 model over-specified**
   - Location: Step 1.4
   - Problem: Specified opus for "agent definition prose." The actual operations are YAML frontmatter `name:` updates (11 files) and grep-and-replace of cross-references (4 files). Mechanical substitution, no prose judgment.
   - Fix: Changed to sonnet with rationale "mechanical YAML frontmatter + grep-and-replace substitutions".
   - **Status**: FIXED

## Fixes Applied

- Step 1.2 -- Added `Depends on: Step 1.1` declaration; fixed line count 63 to 62; changed model opus to sonnet
- Step 1.4 -- Added `Depends on: Step 1.1` declaration; changed model opus to sonnet
- Step 1.5 -- Added `Depends on: Step 1.1` declaration
- Step 1.6 -- Added `Depends on: Steps 1.1, 1.2, 1.4, 1.5` declaration
- Step 1.7 -- Added `Depends on: Steps 1.1-1.6` declaration
- Phase 2 -- Added post-phase state notes for artisan.md and test-driver.md (Phase 1 rename context)
- Substitution Table -- Added cross-cutting scope boundary paragraph
- Appended Expansion Guidance section with consolidation candidates, step expansion notes, checkpoint guidance, and model selection rationale

## Design Alignment

- **Architecture**: Aligned. Phase structure matches D-5 ordering (FR-3, FR-1, FR-2). Phase types match complexity.
- **Key decisions**: All 7 decisions (D-1 through D-7) traced to specific phases/steps in Key Decisions Reference section.
- **Substitution table**: Matches design's agent rename lists. 11 agent renames + 6 terminology changes + 2 deprecations.
- **Scope boundaries**: Outline's implicit scope matches design's explicit IN/OUT lists. No scope creep detected.
- **File inventory**: Step 1.6 lists 24 files across 5 categories, consistent with design Phase 1e and requirements Impact Inventory (~37 total including agent definitions).

## Positive Observations

- Substitution table is well-organized with clear old/new mappings, making mechanical execution straightforward
- Phase typing is correct: Phase 1 (general) warrants step decomposition; Phases 2-3 (inline) are additive prose with no implementation uncertainty
- Step 1.3 includes explicit "Do NOT delete" list for active plan agents -- prevents accidental deletion
- Step 1.7 verification grep includes complete old-name list (15 terms) as a catch-all safety net
- Requirements mapping table is complete with step-level traceability
- Prior outline review (outline-review.md) already caught and fixed 7 issues; this runbook-outline builds on that corrected foundation

## Recommendations

- Step 1.6 is the largest single step (24 files). During expansion, structure the step file with batched Read calls (parallel reads for files in same directory) followed by sequential edits. This reduces agent turns.
- The grep validation in Step 1.7 should be expanded to include both `.md` and `.py` file types, plus `.json` for any config files. The outline lists the grep targets but expansion should include the exact command.
- Phases 2-3 execute inline after Phase 1. The orchestrator should verify Phase 1 checkpoint passes before proceeding to Phase 2.

---

**Ready for full expansion**: Yes
