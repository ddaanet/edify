# Simplification Report

**Outline:** plans/worktree-merge-resilience/runbook-outline.md
**Date:** 2026-02-18

## Summary

- Items before: 14
- Items after: 12
- Consolidated: 2 items across 2 patterns

## Consolidations Applied

### 1. Untracked file collision cases (Cycles 3.2+3.3 → 3.2)
- **Type:** identical-pattern
- **Items merged:** Cycle 3.2 (same-content untracked file), Cycle 3.3 (different-content untracked file)
- **Result:** Cycle 3.2 parametrized with 2-row table (same-content → exit 0, different-content → exit 3)
- **Rationale:** Same function (`_phase3_merge_parent`), same test structure (set up untracked file, run merge, check behavior), same dependency chain (depends on 3.1). Only fixture data varies (file content). Combined assertions ~6, within 8-assertion limit.

### 2. Conflict report output fields (Cycles 4.1+4.2 → 4.1)
- **Type:** identical-pattern
- **Items merged:** Cycle 4.1 (file list + diff stats), Cycle 4.2 (divergence summary + hint)
- **Result:** Cycle 4.1 testing all output fields in single integration test
- **Rationale:** Same function (`_format_conflict_report`), same test setup (trigger conflict, capture output), only assertion targets differ. Combined assertions ~5, within 8-assertion limit. Single git state setup exercises all output fields.

## Patterns Not Consolidated

- **Cycles 1.1+1.2** (both route to Phase 4) — Distinct git state setups (`merged`: slug ancestor of HEAD vs `parent_resolved`: MERGE_HEAD + no conflicts). Outline explicitly notes these justify separate cycles. Phase 1 checkpoint after 1.3 depends on individually verifiable state routing. Shared fixture infrastructure recommended instead.
- **Cycles 1.3-1.5** — Each state (`parent_conflicts`, `submodule_conflicts`, `clean`) has different exit behavior and routing. Not structurally similar.
- **Phase 5 Steps 5.1-5.3** — Different files, different execution models (sonnet/haiku/opus), explicitly marked "must not be split" in outline. Independent but not same-pattern.

## Requirements Mapping

Updated in outline. All FRs preserved:

| Change | Before | After |
|--------|--------|-------|
| FR-3 | Cycles 3.2, 3.3 | Cycle 3.2 (parametrized, covers both cases) |
| FR-4 | Cycles 4.1, 4.2 | Cycle 4.1 (all output fields in single cycle) |
| All other FRs | unchanged | unchanged |
