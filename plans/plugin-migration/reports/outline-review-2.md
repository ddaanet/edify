# Runbook Outline Review: Plugin Migration

**Artifact**: plans/plugin-migration/runbook-outline.md
**Design**: plans/plugin-migration/design.md
**Date**: 2026-02-07T20:45:00Z
**Mode**: review + fix-all

## Summary

The runbook outline had a critical omission (missing Phase 0 for directory rename) and multiple alignment issues with the updated design. All issues have been fixed. The outline is now ready for full expansion.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1, 2 | 1.1-1.2, 2.1-2.3 | Complete | Plugin manifest + skills/agents structure |
| FR-2 | 0, 4 | 0.1, 4.1-4.2 | Complete | Added Phase 0 for directory rename dependency |
| FR-3 | 2 | 2.3 | Complete | `/edify:init` skill creation |
| FR-4 | 2 | 2.4 | Complete | `/edify:update` skill creation |
| FR-5 | 3 | 3.3 | Complete | Version check hook |
| FR-6 | 4 | 4.1-4.2 | Complete | Portable justfile recipes |
| FR-7 | 5 | 5.1-5.2 | Complete | Symlink cleanup |
| FR-8 | 2, 5 | 2.1, 5.3 | Complete | Agent coexistence verification |
| FR-9 | 3 | 3.1-3.3 | Complete | Hook migration with direct format |
| NFR-1 | 5 | 5.3 | Complete | Performance validation |
| NFR-2 | 5 | 5.3 | Complete | Token overhead validation |

**Coverage Assessment**: All requirements covered

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 0 | 1 | Trivial | 6% | Added (was missing) |
| 1 | 2 | Trivial | 12% | Balanced |
| 2 | 4 | Moderate | 24% | Balanced |
| 3 | 3 | Low | 18% | Balanced |
| 4 | 2 | Moderate | 12% | Balanced |
| 5 | 3 | Mixed | 18% | Balanced |
| 6 | 2 | Trivial | 12% | Balanced |

**Balance Assessment**: Well-balanced after adding Phase 0

### Complexity Distribution

- **Trivial phases**: 3 (Phase 0, 1, 6)
- **Low complexity phases**: 1 (Phase 3)
- **Moderate complexity phases**: 2 (Phase 2, 4)
- **Mixed complexity phases**: 1 (Phase 5 — cleanup low, validation high)

**Distribution Assessment**: Appropriate — validation work concentrated in final phase as expected

## Review Findings

### Critical Issues

1. **Missing Phase 0: Directory Rename**
   - Location: Phase structure
   - Problem: Design D-1 specifies git repo rename from plugin to edify-plugin. This is a fundamental structural change that must be a runbook step, but outline had no phase for it. All subsequent phases reference `edify-plugin/` paths but the directory rename was never specified.
   - Fix: Added Phase 0 with step 0.1 for directory rename (git mv + path updates in .gitmodules, justfile, settings.json, CLAUDE.md). Updated phase numbering, dependencies, and total step count (16→17 steps, 6→7 phases).
   - **Status**: FIXED

### Major Issues

1. **Design Decision D-7 and D-8 Missing from Summary**
   - Location: Key Design Decisions section
   - Problem: Outline listed D-1 through D-7, but design has D-8 (consumer mode deferred). Also, D-7 was incorrectly summarized as "consumer mode deferred" when D-7 is actually "Python package dependency" and D-8 is consumer mode.
   - Fix: Updated design decision summary to include both D-7 (Python package dependency with dual venv strategy) and D-8 (consumer mode deferred). Corrected D-7 description.
   - **Status**: FIXED

2. **hooks.json Format Not Specified in Phase 3**
   - Location: Phase 3 step 3.1
   - Problem: Design D-4 clarifies that hooks.json uses direct format `{"PreToolUse": [...]}`, not wrapper format. Outline step 3.1 said "wrapper format" which contradicts the design.
   - Fix: Updated step 3.1 to specify "direct format `{"PreToolUse": [...]}` using `$CLAUDE_PLUGIN_ROOT` paths (per D-4)".
   - **Status**: FIXED

3. **plugin References Not Updated**
   - Location: Multiple phases (1, 2, 3, 4, 5, 6)
   - Problem: All steps, checkpoints, and expansion guidance referenced `plugin/` paths when design specifies rename to `edify-plugin/`. This creates confusion and execution errors.
   - Fix: Updated all 24 references from `plugin` to `edify-plugin` across phase steps, checkpoints, expansion guidance, and dependency notes.
   - **Status**: FIXED

4. **Phase Dependencies Incorrect**
   - Location: Phase Dependencies diagram
   - Problem: Original diagram showed Phase 1 at root, but Phase 0 (directory rename) must precede it. Also, Phase 4 was listed as "parallel with other phases" but it depends on Phase 0 for path consistency.
   - Fix: Updated dependency diagram to show Phase 0 → Phase 1 → (Phases 2, 3, 4) → Phase 5 → Phase 6. Clarified that Phase 4 depends on Phase 0 for edify-plugin/ paths.
   - **Status**: FIXED

### Minor Issues

1. **Purpose Line Still Referenced plugin**
   - Location: Document header
   - Problem: Purpose stated "Migrate plugin from symlink-based..." but should reference the renamed directory.
   - Fix: Updated to "Migrate edify-plugin (was plugin) from symlink-based..." to reflect the rename and provide historical context.
   - **Status**: FIXED

2. **Requirements Mapping Table Lacked Notes Column**
   - Location: Requirements Mapping section
   - Problem: FR-2 mapping changed with addition of Phase 0, but no explanation provided. Table was also less informative than it could be.
   - Fix: Added Notes column with clarifications for each requirement. Updated FR-2 to reference both Phase 0 and Phase 4.
   - **Status**: FIXED

3. **Cache Filename Not Updated for Rename**
   - Location: Phase 6 step 6.2
   - Problem: Step 6.2 referenced `.cache/just-help-plugin.txt` but filename should update to `just-help-edify-plugin.txt` after directory rename.
   - Fix: Updated step 6.2 to reference `.cache/just-help-edify-plugin.txt` and noted filename change in step description.
   - **Status**: FIXED

4. **D-1 Summary Too Brief**
   - Location: Key Design Decisions section
   - Problem: D-1 was listed as "Plugin name = edify" but design has full naming hierarchy table with three distinct concepts (product, git repo, marketplace plugin).
   - Fix: Expanded D-1 to "Naming hierarchy: product = edify, git repo = edify-plugin (was plugin), marketplace plugin = edify".
   - **Status**: FIXED

5. **D-4 Summary Lacked Format Specification**
   - Location: Key Design Decisions section
   - Problem: D-4 said "hooks.json separate file, not inline in plugin.json" but didn't mention the critical direct vs wrapper format distinction from the design update.
   - Fix: Updated D-4 to include format specification: "separate file with direct format `{"PreToolUse": [...]}`, not inline wrapper in plugin.json".
   - **Status**: FIXED

6. **Expansion Guidance Lacked Phase 0 Details**
   - Location: Expansion Guidance section
   - Problem: Added Phase 0 but no expansion guidance provided for it.
   - Fix: Added Phase 0 expansion section with details on affected files (.gitmodules, justfile, settings.json, CLAUDE.md), git mv command, grep search pattern, and post-rename testing.
   - **Status**: FIXED

7. **Notes Section Didn't Mention Directory Rename Priority**
   - Location: Notes section
   - Problem: Phase 0 is now the critical first step, but Notes section didn't emphasize this.
   - Fix: Added note "Directory rename first: Phase 0 must complete before other phases to ensure all paths reference edify-plugin/ consistently (D-1)".
   - **Status**: FIXED

8. **Notes Section Didn't Mention hooks.json Format**
   - Location: Notes section
   - Problem: D-4 format distinction is critical for Phase 3 execution but wasn't in Notes.
   - Fix: Added note "hooks.json format: Direct format `{"PreToolUse": [...]}`, not wrapper format (D-4)".
   - **Status**: FIXED

9. **Checkpoints Lacked Format Specification**
   - Location: Success Criteria section, Phase 3 checkpoint
   - Problem: Phase 3 checkpoint said "hooks fire correctly" but didn't mention the direct format requirement.
   - Fix: Updated Phase 3 checkpoint to "Hooks fire correctly (manual testing for each event type: PreToolUse, PostToolUse, UserPromptSubmit) with direct format hooks.json".
   - **Status**: FIXED

10. **Expansion Guidance Hook Format Reference Incorrect**
    - Location: Expansion Guidance, References to include
    - Problem: Listed "Design Component 2 (hook migration) — hooks.json wrapper format" when design specifies direct format.
    - Fix: Updated reference to "hooks.json with `$CLAUDE_PLUGIN_ROOT` paths" and added separate D-4 reference for format clarification.
    - **Status**: FIXED

## Fixes Applied

**Document header:**
- Updated purpose line: "edify-plugin (was plugin)" for rename context

**Requirements Mapping:**
- Added Notes column with clarifications for all requirements
- Updated FR-2 mapping to include Phase 0

**Key Design Decisions:**
- Expanded D-1 with full naming hierarchy
- Updated D-4 with direct format specification
- Added D-7 (Python package dependency)
- Corrected D-8 label (was mislabeled as D-7)

**Phase 0 addition:**
- Created new Phase 0: Directory Rename with step 0.1
- Updated total step count (16→17) and phase count (6→7)

**Phase 1:**
- Updated dependency from "None" to "Phase 0 (edify-plugin directory exists)"
- Updated step 1.1 path to `edify-plugin/.claude-plugin/plugin.json`
- Updated step 1.2 path to `edify-plugin/.version`

**Phase 2:**
- Updated all paths from `plugin/` to `edify-plugin/` (4 occurrences)
- Added D-8 reference for consumer mode deferral

**Phase 3:**
- Updated step 3.1 format from "wrapper" to "direct format `{"PreToolUse": [...]}`"
- Updated all paths from `plugin/` to `edify-plugin/` (3 occurrences)
- Added D-4 reference

**Phase 4:**
- Updated dependency from "None (parallel)" to "Phase 0 (edify-plugin directory rename)"
- Updated step 4.1 path to `edify-plugin/just/portable.just`
- Updated step 4.1 recipe to include `--plugin-dir ./edify-plugin`
- Updated step 4.2 import path to `edify-plugin/just/portable.just`

**Phase 5:**
- Updated all paths from `plugin/` to `edify-plugin/` (4 occurrences in step descriptions)
- Updated validation command to `claude --plugin-dir ./edify-plugin`

**Phase 6:**
- Updated dependency note from "plugin justfile" to "edify-plugin justfile"
- Updated step 6.2 filename from `just-help-plugin.txt` to `just-help-edify-plugin.txt`

**Complexity Distribution:**
- Added Phase 0 row (1 step, Trivial, 6%)
- Updated percentages to reflect 7-phase structure

**Phase Dependencies:**
- Added Phase 0 at root of dependency tree
- Updated notes to clarify Phase 0 and Phase 4 dependency relationship

**Success Criteria:**
- Added Phase 0 checkpoint
- Updated all checkpoints to reference `edify-plugin/` paths (5 occurrences)
- Updated Phase 3 checkpoint with direct format note
- Updated Phase 6 checkpoint with edify-plugin filename

**Notes:**
- Added "Directory rename first" note
- Added "hooks.json format" note
- Updated dev mode note to reference D-8 instead of D-7

**Expansion Guidance:**
- Added Phase 0 expansion section
- Updated Phase 2 expansion fragment reference path
- Added Phase 3 expansion direct format note
- Added Phase 4 expansion plugin-dir consistency note
- Updated Phase 5 expansion fragment paths
- Updated References section with D-1, D-4 format clarification, corrected Component 2 format reference

## Design Alignment

**Architecture:**
- ✅ Phase 0 implements D-1 directory rename
- ✅ Phase 1 creates plugin manifest (Component 1)
- ✅ Phase 2 implements skill-based distribution (D-3)
- ✅ Phase 3 implements direct format hooks.json (D-4)
- ✅ Phase 4 implements justfile import (D-5)
- ✅ Phase 5 removes symlinks (Component 6)
- ✅ All phases reference edify-plugin paths consistently

**Module structure:**
- ✅ Phases 2.1-2.2 verify existing skills/agents structure matches plugin auto-discovery
- ✅ Phase 3 creates hooks.json with direct format per D-4
- ✅ Phase 5 preserves plan-specific agents (`*-task.md` regular files)

**Key decisions:**
- ✅ D-1 naming hierarchy reflected in Phase 0
- ✅ D-2 hook scripts unchanged (except deletion) reflected in Phase 3
- ✅ D-3 skill-based distribution reflected in Phase 2
- ✅ D-4 hooks.json direct format reflected in Phase 3 step 3.1
- ✅ D-5 justfile import reflected in Phase 4
- ✅ D-6 `.edify-version` marker reflected in Phase 1 and Phase 3
- ✅ D-7 Python package dependency noted (future work, not implemented)
- ✅ D-8 consumer mode deferral reflected in Phase 2 TODO markers

## Positive Observations

- **Dependency clarity:** Phase dependency diagram is clear and shows parallel opportunities (Phases 2, 3 can run concurrently)
- **Checkpoint discipline:** Every phase has explicit verification before proceeding
- **Consolidation notes:** Expansion guidance identifies trivial phases (Phase 1, Phase 6) as merge candidates
- **NFR validation:** Phase 5 includes concrete validation criteria for performance and token overhead
- **Rollback awareness:** Notes section identifies Phase 5 as point of no return
- **Idempotency:** Notes section emphasizes that runbook can be re-run safely

## Recommendations

**Phase 0 criticality:**
- The directory rename is foundational — emphasize in expansion that Phase 0 must be fully validated (just --list works, symlinks resolve) before proceeding
- Consider adding a pre-Phase-0 backup step: create git tag or stash for easy rollback

**Trivial phase consolidation:**
- Phase 1 (2 trivial steps) and Phase 6 (2 trivial steps) are good candidates for single-step consolidation during expansion
- Phase 0 (1 step) could potentially merge with Phase 1 if both are simple file operations, but keep separate for checkpoint clarity

**Hook testing thoroughness:**
- Phase 3 requires restart for validation — expansion should include specific test cases for each hook event type
- Version check hook requires mocking (create mismatched .edify-version) for full validation

**NFR baseline timing:**
- Phase 5 NFR validation needs pre-migration baseline captured at start of Phase 5 (before any changes). Expansion should add explicit "capture baseline" step.

**Expansion skill loading:**
- Phase 2 expansion requires `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills — note this in expansion preamble

---

**Ready for full expansion**: Yes

All requirements are traced, design decisions are reflected, phase structure is logical, and dependencies are clear. The addition of Phase 0 resolves the critical gap in the original outline.
