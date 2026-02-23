# Vet Review: Phase 1 Checkpoint — Phase Numbering Fix

**Scope**: Phase 1 implementation (RC-3 fix) — `assemble_phase_files()` header injection
**Date**: 2026-02-22T02:40:34Z
**Mode**: review + fix

## Summary

Phase 1 implements RC-3: `assemble_phase_files()` now injects `### Phase N:` headers from filenames when absent, and skips injection when a header already exists. Three TDD cycles (1.1, 1.2, 1.3) produce three well-scoped tests. The implementation is minimal and correct. One minor issue found: a dead regex alternative in the interleaving test.

**Overall Assessment**: Ready (after fix applied)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Dead regex alternative in item_pattern**
   - Location: `tests/test_prepare_runbook_mixed.py:179`
   - Note: The regex `r"^## step-(\d+)-(\d+)|^## step-(\d+\.\d+)|^## phase-(\d+)"` has a dead second alternative. `generate_default_orchestrator` uses hyphens for step file stems (`step-1-1`, not `step-1.1`), so `^## step-(\d+\.\d+)` never matches. The first alternative catches both cycle and step entries. The dead branch poses no correctness risk (the test still verifies the right behavior) but adds noise and signals a mismatch between the regex and the actual output format.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_prepare_runbook_mixed.py:178-179` — removed dead `^## step-(\d+\.\d+)` alternative from `item_pattern`, collapsed group handling accordingly

## Positive Observations

- Guard logic is correctly sequenced: unconditional injection in Cycle 1.1, guard added in Cycle 1.2. The phase-1-review caught and fixed the TDD RED/GREEN sequencing violation before execution, so the cycles landed clean.
- `assemble_phase_files()` implementation is minimal: single regex check, two branches (inject or passthrough), no new abstractions.
- `test_assembly_injects_phase_headers_when_absent` verifies ordering with position index checks (`p1_pos < p2_pos < p3_pos`) — stronger than substring presence alone.
- `test_assembly_preserves_existing_phase_headers` uses count assertions (`content.count("### Phase 1:") == 1`) — correctly catches duplication bugs.
- `test_mixed_runbook_phase_metadata_and_orchestrator_correct` is a verification-only cycle (no implementation changes expected), correctly testing that the Phase 1 fix propagates correctly through `extract_sections()` and `generate_default_orchestrator()`. PHASE_BOUNDARY label assertions and interleaving check cover M1 and M2 defects from the design.
- MIXED_RUNBOOK_5PHASE fixture covers all three phase types (general, tdd, inline) and uses 5 phases, reproducing the off-by-one scenario from the original defect (C2: phases 3-5 affected).
