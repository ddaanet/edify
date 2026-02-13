# Design Review: `/when` Memory Recall System (Round 2)

**Design Document**: plans/when-recall/design.md
**Review Date**: 2026-02-12
**Reviewer**: design-vet-agent (opus)
**Prior Review**: plans/when-recall/reports/design-review.md (2026-02-09)

## Summary

Second review of the `/when` memory recall design, focused on drift since the first review and validation against the current codebase state. The design was written and first-reviewed in a different worktree; this review validates against the `when-recall` worktree where the implementation will occur. The primary finding is a ghost file reference (`agent-core/bin/validate-memory-index.py`) that does not exist in this repository and never has -- the exploration report that informed the design examined a different worktree's filesystem. Additionally, entry and heading counts have drifted as the index grew from ~122 to ~160 entries since the corpus analysis. All issues have been fixed.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

1. **Ghost file: `agent-core/bin/validate-memory-index.py` does not exist**
   - Problem: Design referenced this file as a "480-line standalone bin script" requiring parallel updates, appearing in Validator Changes, Validator Refactoring, Existing Code Reuse, and Migration Sequencing sections. The file does not exist in this repository (`git log --all --oneline` returns no history). The reference originated from `explore-design-context.md` which examined `/Users/david/code/claudeutils-memory-index-recall/` (a different worktree).
   - Impact: Planner would create/modify a nonexistent file, waste cycles, and misunderstand the validation architecture. The actual validation is a single-location implementation in `src/claudeutils/validation/memory_index*.py`, invoked via `claudeutils validate` (justfile recipe).
   - Fix Applied: Removed all bin script references. Replaced with accurate description: validation lives entirely in `src/claudeutils/validation/`, invoked by `claudeutils validate` via justfile `precommit` recipe. Updated 4 sections (Validator Changes, Validator Refactoring, Existing Code Reuse, Migration Sequencing step 6).

### Major Issues

1. **Stale entry counts (122/140 vs actual 160)**
   - Problem: FR-6 said "~140 entries" with "(corpus analysis counts 122 non-exempt entries)". Current `memory-index.md` has 160 em-dash entries (grown since corpus analysis).
   - Impact: Migration scope underestimated by ~25%. Planner's time estimates and phase sizing would be wrong.
   - Fix Applied: FR-6 updated to reference current count (~160) with note that scope depends on count at execution time. D-3 corpus analysis reference annotated as historical.

2. **Stale heading counts (~102 vs actual ~123)**
   - Problem: Design said "~102 unique semantic H3 headings across 9 decision files". Actual count: ~123 semantic H3+ headings across 11 decision files, plus 13 flat H2 semantic headings in workflow-core.md. 70 structural headings (not ~38 implied by "140-102").
   - Impact: Heading rename scope underestimated. Planner might not account for additional decision files (data-processing.md, cli.md, markdown-tooling.md, validation-quality.md, defense-in-depth.md) which exist but lack dedicated memory-index sections.
   - Fix Applied: Updated heading counts to current values. Added note about exact scope determined at execution time. D-2 updated to use approximate count.

3. **Out-of-scope contradiction with recall tool parser**
   - Problem: Out of Scope said "Measurement tooling changes (existing recall tool works as-is)" but Implementation Notes documented that `recall/index_parser.py` will break after migration. Step 12 was added to migration sequencing in this review.
   - Impact: Contradictory scope signals. Planner might skip the parser update based on the Out of Scope statement, then discover measurement is broken.
   - Fix Applied: Updated Out of Scope to clarify: no architectural changes to recall analysis, but parser format update is in scope (step 12). Updated Implementation Notes to reference step 12 instead of calling it a "follow-up."

4. **Missing file sections in migration scope**
   - Problem: The "Technical Decisions (mixed)" exempt section contains entries for 5 decision files that currently lack dedicated index sections: `data-processing.md`, `cli.md`, `markdown-tooling.md`, `validation-quality.md`, `defense-in-depth.md`. The design mentioned redistribution but didn't enumerate the new sections to be created.
   - Impact: Planner might not realize migration creates new sections (not just reformats existing ones).
   - Fix Applied: Added explicit list of files needing new sections to the Exempt Section Changes note.

5. **Overly broad skill allowed-tools pattern**
   - Problem: Skill YAML specified `Bash(claudeutils:*)` which would match any claudeutils subcommand. Existing skills use specific patterns (e.g., worktree skill uses `Bash(claudeutils _worktree:*)`).
   - Impact: Skills would have unnecessarily broad permissions.
   - Fix Applied: Narrowed to `Bash(agent-core/bin/when-resolve.py:*)` only, matching the actual execution path. Added tool permission note explaining the pattern.

### Minor Issues

1. **Validator internal duplication not documented**
   - Problem: `memory_index_helpers.py` and `memory_index_checks.py` both define `check_em_dash_and_word_count` and `check_duplicate_entries`. The facade imports from helpers. This duplication was not mentioned.
   - Fix Applied: Added "Note on internal duplication" to Validator Changes section so planner updates both files consistently.

2. **Documentation Perimeter stale reference caveat**
   - Problem: `explore-design-context.md` is listed as required reading but contains stale paths from a different worktree (the ghost bin script originated here).
   - Fix Applied: Added inline caveat noting the stale reference and that the bin script does not exist.

3. **Recall tool sequencing promoted from follow-up to step 12**
   - Problem: First review recommended adding recall tool parser update to migration sequencing. It was noted as "follow-up" which risks being forgotten.
   - Fix Applied: Added as step 12 in migration sequencing. Updated Implementation Notes cross-reference.

## Requirements Alignment

**Requirements Source:** Inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Resolver script + skill wrappers |
| FR-2 | Yes | Fuzzy engine (fuzzy.py, D-4, D-7) |
| FR-3 | Yes | Navigation module + output format |
| FR-4 | Yes | Validator Changes section |
| FR-5 | Yes | `/remember` Skill Update section |
| FR-6 | Yes | Migration sequencing step 9 |
| FR-7 | Yes | Three resolution modes in resolver |
| NFR-1 | Yes | Fuzzy engine shared across 3 consumers (D-4) |
| NFR-2 | Yes | Testing strategy (TDD for all components) |
| NFR-3 | Yes | Success criteria + recall tool parser update (step 12) |
| NFR-4 | Yes | Consumption header update, index stays @-loaded |

**Gaps:** None.

## Positive Observations

- **Architecture is sound.** Module boundaries (fuzzy, parser, resolver, navigation, CLI) are well-defined with clear dependency ordering. Pure functions separated from I/O. No circular dependencies.

- **Fuzzy engine design is well-researched.** The fzf V2 algorithm choice is grounded in the fzf-research.md report with specific scoring constants. Custom implementation (~80 lines) is justified over library alternatives with concrete reasoning.

- **Migration strategy is pragmatic.** Atomic migration (D-8) avoids dual-format validator complexity. Script-assisted heading renames + precommit validation form a safety net. The compress-key tool closes the "is this trigger unique?" question during migration.

- **First review fixes were durable.** Navigation dependency ordering, Pydantic BaseModel convention, backward compatibility decision (D-8), test directory convention, requirements traceability table -- all changes from the first review are intact and consistent.

- **Validator changes section is thorough.** The comparison table (current vs new checks) gives planner a clear migration checklist for each validation rule.

## Recommendations

1. **Re-run corpus analysis before migration.** The index has grown 31% since analysis (122 to 160 entries). The operator split (73% when / 27% how) may have shifted. A fresh count would validate assumptions and produce more accurate phase sizing.

2. **Consider deduplicating validator check functions before format migration.** `memory_index_helpers.py` and `memory_index_checks.py` have identical check function implementations. Migrating both is error-prone. Deduplication first (one defines, one imports) would reduce the surface area for migration bugs. This could be a pre-migration phase or part of phase 6.

3. **Validate the `explore-design-context.md` report against current state before planning.** Beyond the bin script issue, other structural assumptions (skill count, 17 skills listed) may have drifted. A quick re-exploration or diff would catch additional staleness.

## Next Steps

1. Design is ready for `/plan-tdd` -- all critical/major/minor issues resolved
2. Load `plugin-dev:skill-development` before planning (skill wrappers in step 8)
3. Fuzzy engine spike may precede formal TDD cycles (scoring constant tuning)
