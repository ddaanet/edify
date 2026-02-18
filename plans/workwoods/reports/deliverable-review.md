# Deliverable Review: Workwoods

**Date:** 2026-02-17
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `src/claudeutils/planstate/__init__.py` | 18 |
| Code | `src/claudeutils/planstate/models.py` | 38 |
| Code | `src/claudeutils/planstate/inference.py` | 118 |
| Code | `src/claudeutils/planstate/vet.py` | 157 |
| Code | `src/claudeutils/planstate/aggregation.py` | 230 |
| Code | `src/claudeutils/worktree/display.py` | 119 |
| Code | `src/claudeutils/worktree/resolve.py` | 135 |
| Code | `src/claudeutils/worktree/cli.py` | 399 |
| Code | `src/claudeutils/worktree/merge.py` | 262 |
| Code | `src/claudeutils/worktree/session.py` | 298 |
| Code | `src/claudeutils/validation/planstate.py` | 72 |
| Code | `src/claudeutils/validation/__init__.py` | 17 |
| Code | `src/claudeutils/validation/cli.py` | 178 |
| Test | `tests/test_planstate_inference.py` | 192 |
| Test | `tests/test_planstate_vet.py` | 184 |
| Test | `tests/test_planstate_aggregation.py` | 211 |
| Test | `tests/test_planstate_aggregation_integration.py` | 289 |
| Test | `tests/test_worktree_ls_upgrade.py` | 294 |
| Test | `tests/test_worktree_merge_sections.py` | 149 |
| Test | `tests/test_worktree_merge_strategies.py` | 375 |
| Test | `tests/test_worktree_merge_session_resolution.py` | 350 |
| Test | `tests/test_worktree_display_formatting.py` | 123 |
| Test | `tests/test_validation_planstate.py` | 120 |
| Agentic prose | `agent-core/skills/worktree/SKILL.md` | 128 |
| Agentic prose | `agent-core/skills/handoff/SKILL.md` | 329 |
| Agentic prose | `agent-core/skills/design/SKILL.md` | 410 |
| Agentic prose | `agent-core/fragments/execute-rule.md` | 214 |
| Human docs | `agents/plan-archive.md` | 152 |
| Config | `CLAUDE.md` | 91 |
| **Deleted** | `agents/jobs.md` | — |
| **Deleted** | `src/claudeutils/validation/jobs.py` | — |

**Totals:** 2041 code, 2287 test, 1081 agentic prose, 152 human docs, 91 config = 5652 lines across 28 active files + 2 deleted.

**Design conformance:** All 18 files from design's Affected Files Summary are accounted for. Two additional files (`display.py`, `resolve.py`) were extracted during implementation as refactoring — acceptable excess.

## Critical Findings

**C-1. Design skill A.1 missing plan-archive.md loading**
- File: `agent-core/skills/design/SKILL.md`
- Requirement: D-8 specifies "A.1 loads plan-archive.md" — the read path for the archive
- Impact: plan-archive.md accumulates entries that are never consumed during design research, defeating D-8's purpose. Write path exists (handoff step 6) but read path is absent.
- Source: prose review (confirmed by Layer 2 grep — "archive" absent from file)

## Major Findings

**M-1. Worktree skill: Mode C contradicts Usage Notes**
- File: `agent-core/skills/worktree/SKILL.md` line 92 vs line 126
- Mode C step 3 correctly says "Worktree preserved for bidirectional workflow." Usage Notes says "Mode C includes cleanup automatically." Mutually exclusive instructions — agent may follow either.
- Source: prose review

**M-2. Handoff skill Principles contradict Step 6**
- File: `agent-core/skills/handoff/SKILL.md` lines 293-296 vs 229-235
- Step 6 writes plan-archive.md (correct per D-8). Principles say "No separate archive files needed." Agent may skip Step 6 based on Principles.
- Source: prose review

**M-3. Prioritize skill references deleted jobs.md (broken)**
- Files: `agent-core/skills/prioritize/SKILL.md` (lines 30, 42), `agent-core/skills/prioritize/references/scoring-tables.md` (line 92)
- Skill tells agents to "Read `agents/jobs.md` for plan status" — file no longer exists. Marginal Effort scoring references jobs.md status column. Agents invoking `/prioritize` will fail on the first step.
- Source: Layer 2 cross-cutting (not in design's explicit removal list, but consequential breakage)

**M-4. Gate computation covers only 1 of 4 gate types**
- File: `inference.py:83-91`
- Design D-7 defines 4 gate conditions (design, outline, phase N, runbook outline). Implementation only checks `chain.source == "design.md"` then breaks. Distinct from the known "gate wiring incomplete" issue — even when vet_status_func IS passed, only 1 gate message can be produced.
- Source: code review

**M-5. SOURCE_TO_REPORT_MAP hardcodes phases 1-6**
- File: `vet.py:8-18`
- Plans with 7+ phases silently lack vet chain entries for phases beyond 6. Should discover phase files dynamically via glob.
- Source: code review

**M-6. TreeInfo missing most TreeStatus fields → display duplicates git queries**
- Files: `aggregation.py:16-31`, `display.py:9-63`
- Design's TreeStatus has 9 fields. TreeInfo NamedTuple has 5. display.py runs ~6 subprocess calls per tree that `aggregate_trees()` already knows how to compute. Different commit counting algorithm in display.py (counts from oldest session.md commit) vs aggregation.py (counts from last session.md change) — produces different numbers.
- Source: code review + Layer 2 cross-cutting

**M-7. Missing test coverage for design-specified edge cases**
- Files: `tests/test_planstate_inference.py`, `tests/test_planstate_vet.py`
- No test for outline.md-only → requirements status (design explicitly calls out this refinement)
- No test for problem.md-only → requirements status
- VetStatus.any_stale property (public API) has zero test coverage
- Source: test review

## Minor Findings

**Naming/model drift:**
- Design says TreeStatus, code says TreeInfo; AggregatedStatus missing vet_statuses field; VetStatus missing plan_name field — acceptable simplifications but undocumented

**Stale references:**
- `agent-core/README.md` has 2 jobs.md references
- `agent-core/docs/migration-guide.md` has 5 jobs.md references
- Worktree SKILL.md Mode C section header still says "cleanup" (line 86)

**Code:**
- `_derive_next_action` for ready returns `/orchestrate {plan_name}` — deviates from design spec but matches actual `/orchestrate` skill contract (design spec was wrong)
- `_find_iterative_report_for_source` non-phase glob `{report_base}*.md` is greedy (could match unrelated files)
- `exempt_paths` in merge.py uses substring matching — fragile but pre-existing

**Test:**
- Phase 3 unit tests couple to private API (_commits_since_handoff, _is_dirty, etc.)
- Rich CLI Task line not verified (test session.md lacks Pending Tasks section)
- Porcelain test bypasses CLI entry point (tests parser function directly)

**Human docs:**
- Plan-archive.md has duplicate `worktree-skill` entry (lines 50 and 146)
- Several archive entries below D-8 richness spec (single sentence, missing affected modules/key decisions)
- Entries not alphabetically sorted

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: Cross-tree status display | Partial | aggregation works; display duplicates queries (M-6) |
| FR-2: Vet artifact staleness | Satisfied | mtime-based detection with iterative review support |
| FR-3: Plan state inference | Satisfied | all 4 status levels, artifact scanning, list_plans() |
| FR-4: Bidirectional merge | Partial | Code correct; skill has contradiction (M-1) |
| FR-5: Per-section merge strategies | Satisfied | D-5 classification table faithfully implemented |
| FR-6: Eliminate jobs.md | Partial | Core elimination complete; prioritize skill broken (M-3) |
| NFR-1: No writes during status | Satisfied | all planstate functions read-only |
| NFR-2: No unversioned shared state | Satisfied | each tree owns its state |
| NFR-3: Git-native | Satisfied | all state versioned or computed from versioned artifacts |
| D-4: Bidirectional merge = skill only | Partial | Step 3 correct; Usage Notes contradict (M-1) |
| D-7: Workflow gates | Partial | Only design gate implemented (M-4) |
| D-8: Plan archive on demand | Partial | Write path exists; read path missing (C-1) |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 7 |
| Minor | ~15 |

**Assessment:** The core planstate module and jobs.md elimination are functionally complete. The critical finding (C-1) is a single skill edit. Major findings fall into two categories: (1) agentic prose contradictions that could cause agent misbehavior (M-1, M-2, M-3) — quick fixes; (2) code structural gaps that represent incomplete design conformance (M-4, M-5, M-6, M-7) — may warrant follow-up task rather than inline fix, depending on priority.

**Layer 1 reports:** `deliverable-review-code.md`, `deliverable-review-test.md`, `deliverable-review-prose.md`
