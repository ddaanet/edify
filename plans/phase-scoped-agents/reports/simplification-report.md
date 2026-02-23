# Simplification Report

**Outline:** plans/phase-scoped-agents/runbook-outline.md
**Date:** 2026-02-23T00:00:00Z

## Summary

- Items before: 9 (Cycles 1.1–1.4, 2.1–2.5, Phase 3 inline)
- Items after: 8 (Cycles 1.1–1.4, 2.1–2.3, Phase 3 inline)
- Consolidated: 2 items across 2 patterns

## Consolidations Applied

### 1. Orchestrator plan format — merge 2.1 and 2.2

- **Type:** independent same-module functions
- **Items merged:** Cycle 2.1 (Agent field per step), Cycle 2.2 (Phase-Agent Mapping table)
- **Result:** Cycle 2.1 "Orchestrator plan format — Agent field and Phase-Agent Mapping table"
- **Rationale:** Both items modified `generate_default_orchestrator()` exclusively. The two changes are independent additive modifications to the same function — no inter-dependency, no ordering constraint between them. Both share the `1.4` dependency (phase type info). Total RED assertions: 2 sub-cases (a) and (b), well within 8-assertion limit. The original outline's Expansion Guidance flagged this pair as a consolidation candidate.

### 2. validate_and_create inline-skip — merge 2.4 into 2.3

- **Type:** sequential-addition
- **Items merged:** Cycle 2.3 (validate_and_create per-phase agents), Cycle 2.4 (inline phases produce no agent)
- **Result:** Cycle 2.2 "validate_and_create creates per-phase agents (with inline-skip)"
- **Rationale:** Cycle 2.4 was a conditional extension to 2.3's test coverage — the outline itself noted it "may be test-only (inline skip handled by type detection in 2.3)." The inline-skip behavior is a direct property of the same `validate_and_create()` function under test in 2.3. Adding a second RED sub-case (b) with the 3-phase-with-inline runbook covers 2.4's intent without a separate cycle. Total RED assertions: sub-case (a) 6 assertions + sub-case (b) 3 assertions = 8 total, at the limit.

## Patterns Not Consolidated

- **Phase 1 cycles (1.1–1.4):** Each creates a distinct function with different logic and different test structure. 1.1 adds params to an existing function; 1.2 adds a new classification function; 1.3 composes a full agent from layers; 1.4 adds a runbook-level detection function. Dependency chain: 1.3 depends on 1.1+1.2, 1.4 depends on 1.2. Different function signatures, different RED assertions — not identical-pattern.

- **Cycle 2.3 (regression updates):** Different operation type from 2.1–2.2 (API migration of callers, not feature addition). Separate dependency chain (depends on 2.2 signature change landing). Keep as distinct cycle.

- **Phase 3 (inline):** Single item, no consolidation applicable.

## Requirements Mapping

Updated FR-3 items column from `2.1–2.3, Phase 3 inline` to `2.1–2.2, Phase 3 inline` to reflect renumbered cycles. All FRs remain fully covered:

| Requirement | Phase | Items |
|---|---|---|
| FR-1: Per-phase agents with phase-scoped context | 1 | 1.1–1.4 |
| FR-2: Same base type, injected context differentiator | 1 | 1.2, 1.3 |
| FR-3: Orchestrate-evolution dispatch compatibility | 2, 3 | 2.1–2.2, Phase 3 inline |
