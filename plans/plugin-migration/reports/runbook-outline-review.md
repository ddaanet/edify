# Runbook Outline Review: Plugin Migration

**Artifact**: plans/plugin-migration/runbook-outline.md
**Design**: plans/plugin-migration/design.md
**Date**: 2026-02-07T21:30:00Z
**Mode**: review + fix-all

## Summary

The outline provides a solid structural foundation with clear phase boundaries and requirement mapping. However, it contains critical structural issues (Phase 2 skill investigation based on incorrect assumptions), major gaps in requirements coverage (NFR validation missing), and several minor clarity issues in step descriptions. All issues have been fixed in the outline file.

**Overall Assessment**: Ready (after fixes applied)

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1, 2 | 1.1-1.2, 2.1-2.3 | Complete | Plugin auto-discovery via manifest + skill/agent structure |
| FR-2 | 4 | 4.1-4.2 | Complete | Justfile import with `claude` recipe |
| FR-3 | 2 | 2.4 | Complete | `/edify:init` skill creation |
| FR-4 | 2 | 2.5 | Complete | `/edify:update` skill creation |
| FR-5 | 3 | 3.3 | Complete | Version check hook |
| FR-6 | 4 | 4.1-4.2 | Complete | Portable justfile recipes |
| FR-7 | 5 | 5.1-5.2 | Complete | Symlink cleanup |
| FR-8 | 2 | 2.1 (implicit) | Partial | Coexistence mentioned but not validated — added validation to Phase 5 |
| FR-9 | 3, 5 | 3.1-3.2, 5.2 | Complete | Hook migration + settings.json cleanup |
| NFR-1 | 5 | 5.3 (validation) | Partial | Validation listed but no performance comparison criteria — added checkpoint detail |
| NFR-2 | 5 | 5.3 (validation) | Partial | Token overhead mentioned but no measurement method — added checkpoint detail |

**Coverage Assessment**: All requirements mapped. NFR validation guidance strengthened in Phase 5.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 2 | Trivial | 12% | Balanced |
| 2 | 5 | Moderate | 29% | Balanced |
| 3 | 3 | Low | 18% | Balanced |
| 4 | 2 | Moderate | 12% | Balanced |
| 5 | 3 | Mixed | 18% | Balanced |
| 6 | 2 | Trivial | 12% | Balanced |

**Balance Assessment**: Well-balanced. No phase exceeds 30% of total work.

### Complexity Distribution

- **Trivial complexity phases**: 2 (Phases 1, 6)
- **Low complexity phases**: 1 (Phase 3)
- **Moderate complexity phases**: 2 (Phases 2, 4)
- **Mixed complexity phases**: 1 (Phase 5 — cleanup trivial, validation high)

**Distribution Assessment**: Appropriate. Skill creation (Phase 2) correctly assigned to Sonnet. File operations to Haiku. Validation retained in higher-tier model.

## Review Findings

### Critical Issues

1. **Phase 2 skill investigation based on incorrect premise**
   - Location: Phase 2 steps 2.2-2.3
   - Problem: Step 2.2 says "Verify no skills directory exists (design says 16 skills symlinked, but Glob shows none — investigate)". This is a misunderstanding. Design says "16 skill symlinks" in `.claude/skills/` pointing to `plugin/skills/`. The source directory `plugin/skills/` DOES exist with 16 subdirectories. Step searches for `*.md` files when skills use `SKILL.md` inside subdirectories.
   - Fix: Replaced steps 2.2-2.3 with single step verifying skill directory structure matches plugin auto-discovery requirements
   - **Status**: FIXED

2. **Missing explicit agent coexistence validation**
   - Location: Phase 2 step 2.1 note says "implicit"
   - Problem: FR-8 requires plan-specific agents coexist with plugin agents, but outline has no explicit validation step
   - Fix: Added validation checkpoint to Phase 5 step 5.3
   - **Status**: FIXED

### Major Issues

1. **NFR validation steps lack measurement criteria**
   - Location: Phase 5 step 5.3
   - Problem: NFR-1 (performance parity) and NFR-2 (token overhead) mentioned but no concrete measurement method specified
   - Fix: Added explicit validation criteria to Phase 5 success criteria and step 5.3 description
   - **Status**: FIXED

2. **Open questions include already-resolved items**
   - Location: Open Questions section
   - Problem: Question 1 "Skill directory mystery" is based on incorrect Glob pattern (searching for `*.md` instead of `*/SKILL.md`)
   - Fix: Removed question 1, kept questions 2-3 (bash prolog and symlink count verification)
   - **Status**: FIXED

3. **Phase 6 dependency description incomplete**
   - Location: Phase 6 Dependencies section
   - Problem: Says "Phase 4 (justfile import), Phase 5 (cleanup complete)" but cache regeneration only depends on Phase 4 changes (justfile import affects output) — Phase 5 doesn't change justfile
   - Fix: Corrected dependency to "Phase 4 (justfile import changes `just --list` output), Phase 5 (plugin justfile sync-to-parent removal)"
   - **Status**: FIXED

4. **Phase 2 complexity estimate incorrect**
   - Location: Phase 2 Estimated Complexity
   - Problem: Says "~400 lines total for both skills" but design shows `/edify:init` is dev-mode only with consumer-mode stubs, `/edify:update` is no-op in dev mode — total likely ~200 lines, not 400
   - Fix: Revised estimate to "~200-250 lines total (init skill primary, update skill minimal in dev mode)"
   - **Status**: FIXED

5. **Dependency diagram shows incorrect parallelism**
   - Location: Phase Dependencies diagram
   - Problem: Shows Phases 2, 3, 4 with bidirectional arrows (↔) suggesting interdependencies, when design states they're independent and can run in parallel
   - Fix: Changed bidirectional arrows to unidirectional flow from Phase 1, clarified independence in notes
   - **Status**: FIXED

### Minor Issues

1. **Step 2.1 title vague**
   - Location: Phase 2 step 2.1
   - Problem: "Verify plugin/agents/ structure" — unclear what verification entails
   - Fix: Changed to "Verify plugin/agents/ contains 14 agent .md files (no moves needed for plugin discovery)"
   - **Status**: FIXED

2. **Step 3.3 missing hook behavior detail**
   - Location: Phase 3 step 3.3
   - Problem: Title says "once-per-session gating" but doesn't mention the temp file mechanism
   - Fix: Expanded description to include temp file path and gating mechanism
   - **Status**: FIXED

3. **Step 4.1 bash prolog detail unclear**
   - Location: Phase 4 step 4.1
   - Problem: Says "minimal bash prolog" but doesn't specify which functions need to be duplicated from root justfile
   - Fix: Added design reference to D-5 note about bash prolog scope (fail, visible, color variables)
   - **Status**: FIXED

4. **Step 5.2 lists multiple operations without clear order**
   - Location: Phase 5 step 5.2
   - Problem: Step says "Remove hooks section, remove sync-to-parent, update fragment docs" — unclear if order matters or which files affected
   - Fix: Split into three sub-operations with file targets listed
   - **Status**: FIXED

5. **Success criteria missing phase boundary checkpoints**
   - Location: Success Criteria section
   - Problem: Lists end-of-phase validation but doesn't specify checkpoint pattern for phase transitions
   - Fix: Added note that each phase ends with verification before proceeding to next
   - **Status**: FIXED

6. **Open Questions bash prolog question redundant**
   - Location: Open Questions section, question 2
   - Problem: Question asks "How much of root justfile's bash_prolog is needed" but design D-5 already specifies minimal prolog (fail, visible, color variables)
   - Fix: Removed question 2, rephrased as implementation note instead
   - **Status**: FIXED

## Fixes Applied

- Phase 2 Step 2.2-2.3 → Replaced with single verification step (skill directory structure check)
- Phase 2 Step 2.1 → Title clarified (specify 14 agents, no moves needed)
- Phase 2 Estimated Complexity → Reduced from 400 to 200-250 lines
- Phase 3 Step 3.3 → Expanded description (temp file gating mechanism)
- Phase 4 Step 4.1 → Added bash prolog scope reference
- Phase 5 Step 5.2 → Split into three sub-operations with file targets
- Phase 5 Step 5.3 → Added explicit NFR validation criteria (performance comparison, token count measurement, agent coexistence test)
- Phase 6 Dependencies → Corrected to Phase 4 + Phase 5 sync-to-parent removal
- Phase Dependencies diagram → Changed bidirectional arrows to unidirectional, clarified independence
- Success Criteria → Added phase checkpoint verification note
- Open Questions → Removed question 1 (skill directory mystery), removed question 2 (bash prolog already specified), kept question 3 (symlink count verification)

## Design Alignment

**Architecture**: Outline follows design's 8-component structure mapped to 6 phases. Phase grouping is logical (manifest first, parallel implementation, cleanup last).

**Module structure**: Phases 1-4 create files in design locations. Phase 5-6 cleanup aligns with design's symlink removal component.

**Key decisions**: All 7 design decisions (D-1 through D-7) reflected in outline:
- D-1 (plugin name edify) → Phase 1 step 1.1
- D-2 (hook scripts unchanged) → Phase 3 steps 3.1-3.2
- D-3 (fragment distribution via skill) → Phase 2 steps 2.4-2.5
- D-4 (hooks.json separate file) → Phase 3 step 3.1
- D-5 (justfile import) → Phase 4 steps 4.1-4.2
- D-6 (.edify-version marker) → Phase 1 step 1.2
- D-7 (consumer mode deferred) → Phase 2 skills note "dev mode only, consumer mode stubbed"

## Positive Observations

- **Clear phase boundaries**: Each phase has explicit scope and dependencies
- **Requirement traceability**: Mapping table connects all FR/NFR to phases and steps
- **Rollback strategy**: Notes identify Phase 5 as point of no return, preserving rollback capability
- **Design decision propagation**: Key decisions section ensures planner has context for expansion
- **Complexity assessment**: Model assignments (Haiku for file ops, Sonnet for reasoning) match task types appropriately
- **Open questions**: Acknowledges uncertainty (symlink count verification) rather than assuming correctness

## Recommendations

**For full runbook expansion:**

- **Phase 2 skill creation**: Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills before expanding Phase 2. Skills need to reference plugin auto-discovery rules.
- **Phase 3 hook testing**: Manual testing is required after Phase 3 (hooks only load at session start). Add explicit restart + test procedure to expanded runbook.
- **Phase 5 validation**: NFR-1 and NFR-2 require baseline measurement before migration. Add pre-migration baseline capture step.
- **Phase boundary checkpoints**: Each phase should end with explicit verification before proceeding. Expanded runbook should include checkpoint procedures.
- **Consumer mode stubs**: `/edify:init` and `/edify:update` skills should have clear TODO markers for consumer mode code paths. Design specifies this but outline doesn't emphasize it.

---

**Ready for full expansion**: Yes
