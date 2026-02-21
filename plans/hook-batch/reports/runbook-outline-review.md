# Runbook Outline Review: hook-batch

**Artifact**: plans/hook-batch/runbook-outline.md
**Design**: plans/hook-batch/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all

## Summary

The runbook outline is well-structured with complete requirements traceability (17 FRs mapped), appropriate phase typing (TDD for Phases 1-2, general for 3-5), and clear cross-phase dependency declarations. Three major issues were fixed: missing checkpoint in Phase 1's 8-cycle structure, missing Phase 3 step detail section, and incorrect justfile path convention in Step 5.3. Four minor issues were also fixed: over-declared dependencies in Cycle 1.4, missing hookEventName specificity in Cycle 2.1, scope count mismatch (9 features vs 8 cycles), and missing post-phase state note in Cycle 1.7.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles/Steps | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | Cycle 1.1 | Complete | Line-based matching |
| FR-2 | 1 | Cycle 1.2 | Complete | Graduated lookup |
| FR-3 | 1 | Cycle 1.3 | Complete | Bracket-style compression |
| FR-4 | 1 | Cycle 1.4 | Complete | D-7 additive scanning |
| FR-5 | 1 | Cycle 1.5 | Complete | Dual output pattern |
| FR-6 | 1 | Cycle 1.6 | Complete | 3 directives, 5 aliases |
| FR-7 | 1 | Cycle 1.7 | Complete | Two regex patterns |
| FR-8 | 1 | Cycle 1.8 | Complete | Platform keyword pattern |
| FR-9 | 2 | Cycles 2.1-2.3 | Complete | 3 redirect patterns |
| FR-10 | 3 | Steps 3.1-3.2 | Complete | ruff + docformatter |
| FR-11 | 4 | Step 4.1 | Complete | --summary flag |
| FR-12 | 4 | Step 4.2 | Complete | 3 health checks + flag write |
| FR-13 | 4 | Step 4.3 | Complete | Flag check + fallback |
| FR-14 | 5 | Step 5.1 | Complete | 5 event registrations |
| FR-15 | 5 | Step 5.2 | Complete | Merge + dedup logic |
| FR-16 | 5 | Step 5.3 | Complete | justfile recipe update |
| FR-17 | 5 | Step 5.4 | Complete | Run + verify + restart note |

**Coverage Assessment**: All 17 requirements mapped to specific cycles/steps with verification criteria.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Complexity | Assessment |
|-------|-------|------------|------------|
| 1 | 8 cycles + checkpoint | High | Largest phase; checkpoint added mid-phase |
| 2 | 3 cycles | Medium | Balanced |
| 3 | 2 steps | Low | Compact; appropriate for simple Bash script |
| 4 | 3 steps | Medium | Balanced |
| 5 | 4 steps | Medium | Balanced |

**Balance Assessment**: Phase 1 is disproportionately large (8 of 20 items, 40%) but justified — all 8 cycles modify the same file with shared test infrastructure. Checkpoint at mid-phase (after Cycle 1.4) mitigates the risk.

### Complexity Distribution

- Low complexity phases: 1 (Phase 3)
- Medium complexity phases: 3 (Phases 2, 4, 5)
- High complexity phases: 1 (Phase 1)

**Distribution Assessment**: Appropriate. High complexity concentrated where the behavioral logic density is highest (existing 839-line script with 8 behavioral changes).

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Phase 1 has 8 cycles with no checkpoint**
   - Location: Phase 1 cycle list
   - Problem: 8 cycles in a single phase exceeds the checkpoint spacing threshold (>=8 items). Cycles 1.1-1.4 are structural refactors (main() flow changes); cycles 1.5-1.8 build on top. No intermediate quality gate to catch regression from the Cycle 1.4 scan_for_directive refactor before 4 more cycles depend on it.
   - Fix: Added checkpoint between Cycle 1.4 and 1.5. Added Phase 1 Checkpoint Detail section with specific verification criteria.
   - **Status**: FIXED

2. **Missing Phase 3 step detail section**
   - Location: Cycle/Step Detail area — Phase 3 has no detail section
   - Problem: Phases 1, 2, 4, and 5 all have detail sections. Phase 3 has only the summary lines in the Phase Structure section. Step agents would lack specifics on JSON parsing approach, error handling behavior, and validation criteria.
   - Fix: Added Phase 3 Step Detail section with file creation details (Step 3.1) and validation criteria (Step 3.2).
   - **Status**: FIXED

3. **Step 5.3 uses shell `$(dirname "$0")` in justfile context**
   - Location: Phase 5 Step Detail, Step 5.3 code block
   - Problem: `$(dirname "$0")` resolves to the shell's `$0`, not the justfile path. Justfile recipes run from the project root directory. The path should be `agent-core/bin/sync-hooks-config.py` directly.
   - Fix: Replaced `$(dirname "$0")/bin/sync-hooks-config.py` with `agent-core/bin/sync-hooks-config.py`. Changed code fence language to `just`. Added note about justfile running from project root.
   - **Status**: FIXED

### Minor Issues

1. **Cycle 1.4 over-declares dependencies**
   - Location: Cycle 1.4 detail, Depends on line
   - Problem: Says "Depends on: Cycles 1.1, 1.2, 1.3" but the scan_for_directive refactor only depends on Cycle 1.1 (Tier 1 main() structure). Cycles 1.2 and 1.3 modify COMMANDS dict strings — independent of Tier 2 scanning logic.
   - Fix: Changed to "Depends on: Cycle 1.1 (main() Tier 1 structure must be stable before refactoring Tier 2)."
   - **Status**: FIXED

2. **Cycle 2.1 hookEventName vague**
   - Location: Phase 2 Cycle Detail, Cycle 2.1
   - Problem: Says "same as userpromptsubmit hook" for output format but the hookEventName should be "PreToolUse", not "UserPromptSubmit." Implementer copying the UPS hook's hookEventName would produce wrong output.
   - Fix: Changed to explicit format with `hookEventName: "PreToolUse"`.
   - **Status**: FIXED

3. **Scope says "9 UPS improvements" but outline has 8 cycles**
   - Location: Scope Boundaries IN section
   - Problem: The design lists 9 feature items. The outline collapses b:, q:, and learn: into Cycle 1.6, producing 8 cycles. "9 UPS improvements" in Scope is misleading — an executor would look for a 9th cycle.
   - Fix: Changed to "8 UPS cycles (covering 9 feature items — b:, q:, learn: combined in Cycle 1.6)."
   - **Status**: FIXED

4. **Cycle 1.7 missing post-phase state note for Tier 2**
   - Location: Cycle 1.7 detail, Target line
   - Problem: Says "new detection block in main() after Tier 2" without noting that Tier 2 now collects directives without returning (post-Cycle 1.4 behavior). An implementer might add the guard after a `return` statement that no longer exists.
   - Fix: Added parenthetical noting that Tier 2 now collects without returning per Cycle 1.4.
   - **Status**: FIXED

## Fixes Applied

- Phase 1 cycle list — Added checkpoint between Cycles 1.4 and 1.5
- Cycle/Step Detail — Added Phase 1 Checkpoint Detail section with verification criteria
- Cycle/Step Detail — Added Phase 3 Step Detail section (Steps 3.1 and 3.2)
- Cycle 1.4 — Corrected dependency declaration (1.1 only, not 1.1-1.3)
- Cycle 1.7 — Added post-Cycle-1.4 state awareness note
- Cycle 2.1 — Specified hookEventName as "PreToolUse"
- Step 5.3 — Fixed path from `$(dirname "$0")/bin/` to `agent-core/bin/`; changed code fence to `just`; added project-root note
- Scope Boundaries — Changed "9 UPS improvements" to "8 UPS cycles (covering 9 feature items)"
- Appended Expansion Guidance section with consolidation candidates, cycle expansion notes, checkpoint guidance, growth projection, and reference line numbers

## Design Alignment

- **Architecture**: All hooks use `type: command` per D-1. Python for UPS + recipe-redirect, Bash for others per D-2.
- **Module structure**: hooks.json as source of truth per D-8. sync-hooks-config.py merges into settings.json.
- **Key decisions**: All 8 decisions (D-1 through D-8) referenced in Key Decisions Reference table with implementation impact. D-7 (additive directives) drives the most complex cycle (1.4). D-5 (b: = brainstorm) resolved in Cycle 1.6.

## Positive Observations

- Clear separation of phase types (TDD for pattern-matching logic, general for shell integration) matches the testability characteristics of each phase.
- Cross-phase dependency declarations are explicit and complete — Phase 5 correctly notes it depends on all prior phases.
- Cycle detail sections include target (exact function/line), change description, dependency declarations, and verification criteria — sufficient for step file generation.
- Post-phase state notes present on all phases ("Phase N state after completion").
- Test count reference acknowledges existing test infrastructure (282-line test file) and estimates new test counts per phase.

## Recommendations

- Cycles 1.2 and 1.3 are consolidation candidates (both modify COMMANDS dict strings, no branching). Noted in Expansion Guidance for planner decision during expansion.
- Test file growth (~282 → ~400 lines) should be monitored during Phase 1 expansion. If approaching 400 lines, split by tier (TestTier1Commands, TestTier2Directives, TestTier2_5Guards).
- Phase 3 uses haiku for Bash + JSON parsing. The JSON parsing via `python3 -c` adds complexity that may warrant sonnet. Low risk since the Phase 3 Step Detail now specifies the exact approach.

---

**Ready for full expansion**: Yes
