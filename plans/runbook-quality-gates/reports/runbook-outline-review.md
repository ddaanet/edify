# Runbook Outline Review: runbook-quality-gates (Phase B)

**Artifact**: plans/runbook-quality-gates/runbook-outline.md
**Design**: plans/runbook-quality-gates/design.md
**Requirements**: plans/runbook-quality-gates/requirements.md
**Date**: 2026-02-17
**Mode**: review + fix-all

## Summary

Well-structured outline for Phase B (validate-runbook.py TDD). Five phases map cleanly to the 4 subcommands plus integration, with logical progression from scaffold through increasing complexity. The outline had several minor-to-major gaps: a missing function in the import list, fixture strategy contradiction between two sections, missing FR-6 in the requirements mapping, and absent dependency declarations. All issues fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles | Coverage | Notes |
|-------------|-------|--------|----------|-------|
| FR-2 (mechanical) | Phase 1 | 1.2-1.3 | Complete | model-tags subcommand |
| FR-3 | Phase 2 | 2.1-2.3 | Complete | lifecycle subcommand |
| FR-4 (structural) | Phase 4 | 4.1-4.3 | Complete | red-plausibility subcommand |
| FR-4 (semantic, exit 2) | Phase 4 | 4.3 | Complete | exit code 2 for ambiguous |
| FR-5 | Phase 3 | 3.1-3.3 | Complete | test-counts subcommand |
| FR-6 (scaling) | -- | -- | Complete | Added: addressed by design (mandatory uniform execution) |
| NFR-1 (integration) | All | 1.1, 5.1 | Complete | argparse CLI, directory input |
| NFR-2 (incremental) | Phase 5 | 5.1-5.2 | Complete | --skip flags, graceful degradation |

**Coverage Assessment**: All requirements covered. FR-1 (simplification agent) is Phase A only, correctly excluded from this Phase B outline. FR-6 was missing from mapping table and has been added.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 1 | 3 | Medium | 21% | Balanced (scaffold + first subcommand) |
| 2 | 3 | Medium | 21% | Balanced |
| 3 | 3 | Medium | 21% | Balanced |
| 4 | 3 | High | 21% | Balanced (complexity justified by ambiguity detection) |
| 5 | 2 | Low | 14% | Lightweight — consolidation candidate noted |

**Balance Assessment**: Well-balanced. Phases 1-4 have identical cycle counts. Phase 5 is lighter but logically distinct (integration concerns vs individual subcommands).

### Complexity Distribution

- Low complexity phases: 1 (Phase 5)
- Medium complexity phases: 3 (Phases 1, 2, 3)
- High complexity phases: 1 (Phase 4)

**Distribution Assessment**: Appropriate. Phase 4 (red-plausibility) is correctly rated High — requires cross-cycle state analysis and ambiguity detection. Phase 5 is correctly Low — argparse wiring and integration of already-implemented subcommands.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing `extract_step_metadata` from import list**
   - Location: Phase 1 Context, Key Design Constraints D-7 section
   - Problem: The `model-tags` subcommand needs `extract_step_metadata` (prepare-runbook.py line 539) to extract `**Execution Model**:` tags from step content. The function was listed in design.md (line 274) but omitted from the outline's reuse list. Without it, Cycle 1.2-1.3 would need to re-implement the regex pattern.
   - Fix: Added `extract_step_metadata` to both the Phase 1 Context line and the D-7 reuse list.
   - **Status**: FIXED

2. **Fixture strategy contradiction**
   - Location: Fixture Plan section vs Expansion Guidance
   - Problem: Fixture Plan listed separate `.md` files in `tests/fixtures/runbooks/` directory. Expansion Guidance recommended inline strings in test file. These contradict — expanding agent would face conflicting instructions.
   - Fix: Aligned Fixture Plan with Expansion Guidance. Changed file-based fixtures to inline string constants (e.g., `VALID_TDD`, `VIOLATION_MODEL_TAGS`). Removed `tests/fixtures/runbooks/` from Phase 1 target files.
   - **Status**: FIXED

3. **FR-6 missing from requirements mapping table**
   - Location: Requirements Mapping section
   - Problem: FR-6 (scaling by runbook size) is addressed by the design's "mandatory uniform execution" approach but was absent from the mapping table. Traceability gap.
   - Fix: Added FR-6 row noting it's addressed by design.
   - **Status**: FIXED

### Minor Issues

1. **Missing `--skip-model-tags` flag in Phase 5.2**
   - Location: Cycle 5.2 description
   - Problem: Listed 3 skip flags (`--skip-lifecycle`, `--skip-test-counts`, `--skip-red-plausibility`) but omitted `--skip-model-tags`. All 4 subcommands should have skip flags for symmetry and NFR-2 completeness.
   - Fix: Added `--skip-model-tags` to the flag list.
   - **Status**: FIXED

2. **Missing dependency declarations**
   - Location: Phase 2, 3, 4, 5 headers
   - Problem: Expansion Guidance stated "Declare `Depends on: Cycle 1.1` in cycles 2.1, 3.1, 4.1" but the phase bodies had no dependency declarations. Phase 5 also lacked dependency on all prior phases.
   - Fix: Added `Depends on:` lines to all phase headers (Phases 2-4 depend on Phase 1 scaffold; Phase 5 depends on Phases 1-4).
   - **Status**: FIXED

3. **Hardcoded test count in final checkpoint**
   - Location: Phase 5 final checkpoint
   - Problem: Claimed "all 14 tests pass" but actual count depends on parametrization decisions during expansion. With `@pytest.mark.parametrize` (recommended in Expansion Guidance), unique function count would differ from 14.
   - Fix: Changed to "all tests pass (count depends on parametrization decisions during expansion)".
   - **Status**: FIXED

4. **Expansion Guidance duplicated fixture strategy**
   - Location: Expansion Guidance "Fixture strategy" paragraph
   - Problem: Fixture strategy appeared in both Fixture Plan section and Expansion Guidance, creating a maintenance pair. After aligning Fixture Plan, the Expansion Guidance paragraph became redundant.
   - Fix: Removed redundant fixture strategy paragraph from Expansion Guidance. Fixture Plan section now serves as the single source.
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping table — added FR-6 row
- Phase 1 Context — added `extract_step_metadata` to import list
- Key Design Constraints D-7 — added `extract_step_metadata` to reuse list
- Phase 1 Target — removed `tests/fixtures/runbooks/` (fixtures are inline)
- Phase 2 header — added `Depends on: Phase 1`
- Phase 3 header — added `Depends on: Phase 1`
- Phase 4 header — added `Depends on: Phase 1`
- Phase 5 header — added `Depends on: Phases 1-4`
- Cycle 5.2 — added `--skip-model-tags` to flag list
- Phase 5 checkpoint — removed hardcoded "14" test count
- Fixture Plan section — converted from file-based to inline string constants
- Expansion Guidance — restructured: removed redundant fixture strategy, added consolidation candidates, growth projection, and design references

## Design Alignment

- **Architecture**: Outline follows design Phase B deliverables (validate-runbook.py, test file, fixtures). Correctly scoped to Phase B only.
- **Import approach (D-7)**: Outline specifies `importlib.util.spec_from_file_location` matching design decision. All 6 reusable functions now listed.
- **Exit codes (D-5)**: 0/1/2 convention consistent across all phases.
- **Report location**: `plans/<job>/reports/validation-{subcommand}.md` matches design spec.
- **Incremental adoption (NFR-2)**: `--skip-*` flags and subcommand granularity match design's approach.
- **Parsing targets**: Each subcommand's parsing targets match the design's subcommand specifications.

## Positive Observations

- Clean 1-subcommand-per-phase structure makes phases independently testable and reviewable
- Happy path → violation → edge case progression within each phase follows sound TDD practice
- Phase 4 (red-plausibility) correctly rated High complexity — the exit 2 ambiguity case requires nuanced state analysis
- Inline fixture constants are a better choice than file-based fixtures for this use case — enables parametrization and avoids file I/O in tests
- Expansion Guidance provides actionable detail (report writer signature, regex patterns, parametrization strategy) without reproducing design content

## Recommendations

- During expansion of Cycle 1.1, verify that `extract_step_metadata` returns the expected dict shape for model-tags validation. The function signature is at prepare-runbook.py:539.
- Phase 5 is a consolidation candidate (2 Low-complexity cycles). If expansion reveals that `--skip-*` flags are purely argparse additions with no parsing logic, merging 5.1 and 5.2 into a single cycle is appropriate.
- Phases 2, 3, and 4 have no inter-dependencies (each depends only on Phase 1). During orchestration, these could theoretically run in parallel if the expanding agent supports it.

---

**Ready for full expansion**: Yes
