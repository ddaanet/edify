# Simplification Report

**Outline:** plans/runbook-quality-gates/runbook-outline.md
**Date:** 2026-02-17

## Summary

- Items before: 14
- Items after: 13
- Consolidated: 1 item across 1 pattern

## Consolidations Applied

### 1. Phase 5 integration cycles merged

- **Type:** same-module
- **Items merged:** 5.1 (directory input), 5.2 (--skip-* flags)
- **Result:** Single cycle 5.1 covering directory assembly and --skip flags together
- **Rationale:** Both are Low complexity, target the same files, share no inter-dependency. Skip flags are argparse additions with no parsing logic — testing them alongside directory input is natural (directory input exercises all subcommands; skip flags suppress subsets). The outline's own Expansion Guidance section flagged this candidate. Combined item stays well under the 8-assertion limit (directory assembly + 4 skip flags = 5-6 assertions via parametrization).

## Patterns Not Consolidated

### Phases 2, 3, 4 (happy-path / violation / edge-case triplets)

**Not consolidated.** Although all three phases share the same structural template (happy-path exit 0, violation exit 1, edge-case), they fail the identical-pattern test:

- **Different parsing logic:** lifecycle parses `File:` + `Action:` fields and builds a dependency graph. test-counts parses `**Test:**` fields and checkpoint claims with `\d+ tests? pass` regex. red-plausibility parses `**Expected failure:**` text cross-referenced against `**Changes:**` sections.
- **Different data structures:** lifecycle builds a create/modify dependency graph. test-counts builds cumulative function counts with parametrization deduplication. red-plausibility does cross-phase function existence analysis.
- **Different exit code semantics:** Only red-plausibility uses exit 2 (ambiguous). The others use binary pass/fail.
- **Different production code per cycle:** Each cycle adds distinct implementation logic, not the same function with different fixture data.

The "identical-pattern" category requires same function modified with only fixture data varying. These subcommands have fundamentally different implementations behind a shared test structure.

### Phase 1 cycles 1.2-1.3 (model-tags happy/violation)

**Not consolidated.** Standard TDD RED/GREEN pair for a single subcommand. Two cycles is the minimum for testing both pass and fail paths. Merging would create a single cycle with mixed pass/fail assertions that obscures the TDD progression.

## Requirements Mapping

No changes -- all mappings preserved. The merged 5.1+5.2 cycle continues to cover NFR-1 (directory input) and NFR-2 (--skip flags, graceful degradation). Updated numbering: Phase 5 has 1 cycle (5.1) instead of 2 (5.1, 5.2).
