# Simplification Report

**Outline:** plans/worktree-merge-from-main/runbook-outline.md
**Date:** 2026-03-02

## Summary

- Items before: 15
- Items after: 11
- Consolidated: 4 items across 2 patterns

## Consolidations Applied

### 1. Phase 1 independent merge.py function adaptations

- **Type:** independent same-module functions
- **Items merged:** 1.2 (`_phase1_validate_clean_trees`), 1.3 (`_phase4_merge_commit_and_precommit`), 1.4 (`_format_conflict_report`), 1.5 (`_phase3_merge_parent`)
- **Result:** Cycle 1.2 — Batch `from_main` adaptation of 4 independent merge.py functions
- **Rationale:** All four target `src/claudeutils/worktree/merge.py`, all depend only on Cycle 1.1 (no inter-dependencies), and each adds a small `from_main` conditional branch to an existing function. Functions are independent — no ordering constraint among them. Test assertions remain distinct per function within the batched cycle.

### 2. Phase 4 SKILL.md Mode D addition and enumeration site updates

- **Type:** sequential-addition
- **Items merged:** 4.1 (Add Mode D section), 4.2 (Update enumeration sites)
- **Result:** Step 4.1 — Add Mode D to SKILL.md and update all enumeration sites
- **Rationale:** Both target the same file (`agent-core/skills/worktree/SKILL.md`). Step 4.2 is a sweep of the same file that 4.1 modifies. No dependency separation — the enumeration site updates are naturally done while adding Mode D, as the author already has full SKILL.md context loaded.

## Patterns Not Consolidated

- **Phase 2 resolve/remerge pair (2.1 + 2.2):** Different target files (`resolve.py` vs `remerge.py`) and 2.2 depends on 2.1. Dependency chain prevents batching.
- **Phase 3 resolve/remerge pair (3.1 + 3.2):** Same reason as Phase 2 pair — different files and dependency chain.
- **Cross-phase session.md vs learnings.md patterns (Phase 2 vs Phase 3):** Different phases. Consolidation constraint: do not consolidate across phases.
- **Phase 2 Cycle 2.3 (delete/modify resolution):** Different target file from 2.1/2.2 (`merge.py` vs `resolve.py`/`remerge.py`), distinct problem domain (conflict detection vs content resolution).
- **E2E integration tests (2.4, 3.4):** Each depends on multiple prior cycles within their phase and tests different FR coverage. Cannot batch.

## Requirements Mapping

Updated mappings:
- C-1: Items changed from `1.1-1.5` to `1.1-1.2` (same coverage, fewer items)
- C-2: Item reference `1.2` now points to the batched cycle containing `_phase1_validate_clean_trees`
- Phase 4 references: `4.1, 4.2` collapsed to single `4.1`

All FR/NFR/C mappings preserved. No requirements lost.
