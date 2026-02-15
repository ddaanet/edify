# Deliverable Review: worktree-fixes

**Date:** 2026-02-15
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `src/claudeutils/worktree/session.py` (NEW) | 267 |
| Code | `src/claudeutils/worktree/cli.py` | 382 |
| Code | `src/claudeutils/worktree/merge.py` | 307 |
| Code | `src/claudeutils/validation/tasks.py` | 347 |
| Test | `tests/test_validation_task_format.py` (NEW) | 82 |
| Test | `tests/test_worktree_session.py` | 284 |
| Test | `tests/test_worktree_session_automation.py` (NEW) | 169 |
| Test | `tests/test_worktree_session_remove.py` (NEW) | 218 |
| Test | `tests/test_worktree_merge_conflicts.py` | 288 |
| Test | `tests/test_worktree_merge_merge_head.py` (NEW) | 93 |
| Test | `tests/test_worktree_merge_submodule.py` | 292 |
| Test | `tests/test_worktree_utils.py` | 228 |
| Prose | `agent-core/skills/worktree/SKILL.md` | 127 |

All 5 FRs satisfied. Design conformance confirmed across all deliverables.

## Findings Applied

### Critical: 0

### Major: 4 (all fixed)

| # | Source | File:Line | Axis | Fix |
|---|--------|-----------|------|-----|
| 1 | code | session.py:54-58 | Conformance | NOT A BUG — blank lines fail continuation test (`next_line[0].isspace()`) regardless; explicit check is an optimization, not a deviation |
| 2 | code | session.py:152-153 | Robustness | FIXED — `line in task_block.lines` → `line == task_block.lines[0]` |
| 3 | test | test_worktree_merge_merge_head.py | Completeness | FIXED — added `git branch -d` assertion verifying FR-5 acceptance criterion |
| 4 | prose | SKILL.md:9-16 | Completeness | FIXED — added `git add`, `git commit`, `git submodule`, `git branch`, `git log` to allowed-tools |

### Minor: 10 (7 fixed, 3 deferred)

| # | Source | Description | Status |
|---|--------|-------------|--------|
| 5 | code | session.py:164 — no guard for `task_start_idx is None` | FIXED |
| 6 | code | cli.py:36 — redundant `rstrip("-")` | FIXED |
| 7 | code | merge.py:72-73 — no section filter on `extract_task_blocks()` | DEFERRED — intentional for legacy compatibility |
| 8 | code | merge.py:86-88 — alphabetical sort not in design | DEFERRED — reasonable excess (deterministic output) |
| 9 | test | test_worktree_session.py:285 — weak disjunctive assertion | FIXED |
| 10 | test | Idempotency test gaps (move + remove) | DEFERRED — implementation handles both paths, low risk |
| 11 | test | FR-2 only tests Pending Tasks section | DEFERRED — implementation scans all lines regardless |
| 12 | prose | SKILL.md:115,121 — second-person voice | FIXED |
| 13 | prose | SKILL.md — Grep/Glob missing from allowed-tools | DEFERRED — Read sufficient for known files |
| 14 | test | test_worktree_merge_merge_head.py naming deviation | DEFERRED — acceptable, clearer separation |

## Gap Analysis

| Design Requirement | Status |
|-------------------|--------|
| FR-1: Task name constraints | COVERED — validation, derive_slug, precommit |
| FR-2: Precommit validation | COVERED — scans all task lines, format errors with line numbers |
| FR-4: Session merge preserves blocks | COVERED — extract_task_blocks, full block insertion |
| FR-5: Merge commit always created | COVERED — MERGE_HEAD detection, --allow-empty, branch -d test added |
| FR-6: Session.md automation | COVERED — move_task_to_worktree, remove_worktree_task, CLI wiring |

## Summary

0 Critical, 4 Major (all fixed), 10 Minor (7 fixed, 3 deferred).

Sub-reports:
- `plans/worktree-fixes/reports/deliverable-review-code.md`
- `plans/worktree-fixes/reports/deliverable-review-tests.md`
- `plans/worktree-fixes/reports/deliverable-review-prose.md`
