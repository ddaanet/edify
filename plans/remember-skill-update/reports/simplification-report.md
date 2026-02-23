# Simplification Report

**Outline:** plans/remember-skill-update/runbook-outline.md
**Date:** 2026-02-23

## Summary

- Items before: 18
- Items after: 15
- Consolidated: 3 items across 2 patterns

## Consolidations Applied

### 1. Batch trivial removals into single step

- **Type:** sequential-addition (sequential removals from the codebase)
- **Items merged:** Step 2.2 (delete delegation agents), Step 2.6 (remove memory-index from CLAUDE.md)
- **Result:** Step 2.5: Remove deprecated artifacts (FR-8, FR-9, FR-13) -- deletes 2 agent files + removes 1 CLAUDE.md reference + grep verification
- **Rationale:** Three independent removal operations with no inter-dependencies. Outline explicitly noted these as "trivial -- merge candidates for consolidation gate" (line 216). Combined step has 5 sub-items, well under the 8-assertion limit. All three removals share the same verification pattern (grep for residual references).

### 2. Batch same-module agent routing additions

- **Type:** same-module
- **Items merged:** Step 3.1 (update SKILL.md with agent routing), Step 3.2 (update consolidation-patterns.md with agent routing)
- **Result:** Step 3.1: Add agent routing to remember skill (SKILL.md + consolidation-patterns.md)
- **Rationale:** Both steps add agent routing content to files within the same skill module (`agent-core/skills/remember/`). No inter-dependencies between the two additions. Combined step uses Target 1/Target 2 structure to preserve clarity. Phase 3 reduces from 2 items to 1 but remains a separate phase (dependency on Phase 2 completion prevents cross-phase merge).

## Renumbering Applied

Phase 2: Steps 2.1-2.6 (6 items) renumbered to Steps 2.1-2.5 (5 items)
- Step 2.3 was formerly Step 2.4 (consolidation-patterns.md)
- Step 2.4 was formerly Step 2.5 (handoff skill)
- Step 2.5 is the new merged step (formerly Steps 2.2 + 2.6)

Phase 3: Steps 3.1-3.2 (2 items) consolidated to Step 3.1 (1 item)

Requirements mapping table updated to reflect new numbering.

## Patterns Not Consolidated

- Phase 1 TDD cycles (1.1-1.3) -- distinct validation rules with different implementation logic; TDD cycles require separate RED-GREEN-regression flow
- Phase 2 prose edits (2.1, 2.2-2.4) -- Step 2.1 already has 5 sub-changes; merging with other steps would exceed 8-assertion equivalent
- Phase 4 TDD cycles (4.1-4.3) -- distinct CLI features (syntax, batching, validation); same TDD separation rationale as Phase 1
- Phase 5 inline items -- already consolidated as a single inline phase (4 mechanical substitutions)
- Phase 6 steps (6.1-6.2) -- step 6.1 (rename + replace) and 6.2 (sync + verify) have natural sequencing (verify after rename); 2 items is minimal
- Phase 7 -- single inline item, nothing to consolidate
- Phase 2 + Phase 3 cross-phase merge -- different dependency chains (Phase 3 depends on Phase 2 completion)

## Requirements Mapping

Updated in outline. All 11 active FRs (FR-1 through FR-5, FR-8 through FR-13, excluding struck FR-7) remain mapped. Key changes:

| FR | Old Items | New Items |
|----|-----------|-----------|
| FR-4 | Steps 2.1, 2.4 | Steps 2.1, 2.3 |
| FR-5 | Steps 2.1, 2.5 | Steps 2.1, 2.4 |
| FR-8 | Steps 2.1, 2.2, 2.3 | Steps 2.1, 2.2, 2.5 |
| FR-9 | Steps 2.1, 2.2 | Steps 2.1, 2.5 |
| FR-11 | Steps 3.1-3.2 | Step 3.1 |
| FR-13 | Step 2.6 | Step 2.5 |
