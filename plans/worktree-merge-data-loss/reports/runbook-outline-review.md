# Runbook Outline Review: Worktree Merge Data Loss

**Artifact**: plans/worktree-merge-data-loss/runbook-outline.md
**Design**: plans/worktree-merge-data-loss/design.md
**Date**: 2026-02-16T00:00:00Z
**Mode**: review + fix-all

## Summary

Outline covers all functional requirements with clear TDD cycles for Track 1 (removal guard) and Track 2 (merge correctness). Phase structure is balanced (13 cycles in Phase 1, 1 step in Phase 2). Original outline had minor gaps in cycle specificity, dependency ordering, and expansion guidance. All issues fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Cycles/Steps | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1 | 1.1-1.3 | Complete | Branch classification helper and edge cases |
| FR-2 | 1 | 1.4 | Complete | Guard refusal with exit 1 |
| FR-3 | 1 | 1.6 | Complete | Focused-session-only branch removal allowed |
| FR-4 | 1 | 1.4-1.6 | Complete | Exit code coverage (0/1/2) across scenarios |
| FR-5 | 1 | 1.7-1.8 | Complete | Guard integration + output verification |
| FR-6 | 1 | 1.9, 1.11 | Complete | MERGE_HEAD checkpoint prevents single-parent for unmerged |
| FR-7 | 1 | 1.12 | Complete | Post-merge ancestry validation |
| FR-8 | 1 | 1.5-1.6 | Complete | Success messages differentiate removal types |
| FR-9 | 2 | 2.1 | Complete | SKILL.md Mode C escalation guidance |

**Coverage Assessment**: All requirements covered with explicit cycle mappings.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 13 | Medium | 93% | Appropriate for TDD implementation phase |
| 2 | 1 | Low | 7% | Prose-only, minimal scope |

**Balance Assessment**: Well-balanced. Phase 1 implements all behavioral changes (Track 1 + Track 2). Phase 2 updates documentation after behavior exists. 13 cycles is within acceptable range for a cohesive TDD phase (under the 8-item soft guideline but justified by track independence).

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 2 — prose edit)
- **Medium complexity phases**: 1 (Phase 1 — TDD with real git operations)
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. Phase 1 is Medium (git operations, dual-track implementation, but straightforward test patterns). No unjustified High complexity.

## Review Findings

### Critical Issues

None identified.

### Major Issues

**1. Missing cycle specificity — outcome clarity**
- Location: Cycles 1.4-1.8, 1.9-1.12
- Problem: Cycle titles lacked concrete outcomes (e.g., "Guard refuses unmerged" without specifying exit code or message format)
- Fix: Added exit codes, message content, and concrete assertions to cycle titles. Example: "Guard refuses unmerged real history (exit 1, stderr message with count)"
- **Status**: FIXED

**2. Missing integration cycle**
- Location: Track 1 cycles
- Problem: Cycles 1.4-1.6 test guard logic in isolation, Cycle 1.8 tests output, but no cycle integrates guard into cli.py rm() function's control flow
- Fix: Redefined Cycle 1.7 as integration cycle — guard must run before all destructive operations (probe, warn, remove_session_task, etc.)
- **Status**: FIXED

**3. Track 2 coverage gap — three-branch logic**
- Location: Cycles 1.9-1.11
- Problem: Design Phase 4 has three commit paths (MERGE_HEAD present, staged changes + merged, no MERGE_HEAD + no staged). Original outline had 2 cycles, missing the third branch.
- Fix: Split into 3 cycles: 1.9 (MERGE_HEAD path refusal), 1.10 (staged + merged idempotency), 1.11 (no MERGE_HEAD + no staged case)
- **Status**: FIXED

**4. Cycle numbering inconsistency**
- Location: Requirements mapping table, checkpoint reference
- Problem: Added cycle 1.11 shifted end-to-end test to 1.13, but mapping table still referenced old 1.12
- Fix: Updated all references (FR-6 → 1.9+1.11, FR-7 → 1.12, checkpoint → after 1.13)
- **Status**: FIXED

### Minor Issues

**1. Missing dependency declaration**
- Location: Expansion Guidance
- Problem: Cycle 1.1 (`_is_branch_merged`) is prerequisite for Track 1 (1.4-1.6) and Track 2 (1.9-1.11) but not explicitly stated
- Fix: Added "Shared dependency ordering" section in Expansion Guidance noting foundation-first requirement
- **Status**: FIXED

**2. Vague integration guidance**
- Location: Expansion Guidance (Cycle 1.7 note)
- Problem: Integration cycle existed but guidance didn't enumerate which cli.py operations must follow guard check
- Fix: Added explicit operation list (probe, warn, remove_session_task, remove_worktrees, branch deletion, rmtree) to integration note
- **Status**: FIXED

**3. Regression test ambiguity**
- Location: Cycle 1.13 (parent repo file preservation)
- Problem: Outline didn't specify what data to create in test (could be any parent repo change)
- Fix: Added test scenario to Expansion Guidance — "new file in parent" as concrete parent repo change type
- **Status**: FIXED

**4. End-to-end test expectation missing**
- Location: Expansion Guidance (Cycle 1.13 note)
- Problem: Design notes test "may or may not reproduce" the bug, but outline didn't transmit this context
- Fix: Added note to Expansion Guidance — test may pass without fixes if bug was environment-specific, defensive checks valuable regardless
- **Status**: FIXED

## Fixes Applied

- Cycles 1.4-1.6 — Added exit codes, message content, concrete flags to titles
- Cycle 1.7 — Redefined as guard integration cycle (was "Success messages differentiate types", now integration point)
- Cycle 1.8 — Clarified as output verification (no `git branch -D` in stderr/stdout)
- Cycles 1.9-1.11 — Split Track 2 checkpoint logic into three distinct branches (MERGE_HEAD present, staged+merged, no staged+no MERGE_HEAD)
- Cycle 1.12 — Added call site and exit 2 behavior to ancestry validation title
- Cycle 1.13 — Renamed from 1.12 (end-to-end parent file preservation test)
- Requirements mapping table — Updated FR-4, FR-5, FR-6, FR-7, FR-8 cycle references
- Checkpoint — Updated to "After Cycle 1.13"
- Phase 1 Complexity — Updated count from "~11" to "13 TDD cycles"
- Phase 1 Dependencies — Added explicit note that Cycle 1.1 is prerequisite for both tracks
- Expansion Guidance — Added shared dependency ordering section
- Expansion Guidance — Added Cycle 1.7 integration note (operation list, guard-before-destruction rule)
- Expansion Guidance — Added Cycle 1.13 end-to-end test scenario and expectation management

## Design Alignment

**Architecture**: Outline follows three-track structure from design (Track 1: cli.py guard, Track 2: merge.py correctness, Track 3: SKILL.md update).

**Module structure**: Matches design's file structure (cli.py, merge.py, utils.py shared helper, SKILL.md prose).

**Key decisions**: All 7 design decisions (D-1 through D-7) referenced in outline. Cycle titles commit to specific approaches from design (marker text detection, `_is_branch_merged` in utils.py, guard-before-destruction ordering).

**Implementation notes**: Test file split matches design's testing strategy (two files: rm guard, merge correctness). Fixture references (`repo_with_submodule`) align with design's Documentation Perimeter.

## Positive Observations

**Track independence**: Outline correctly identifies Track 1 and Track 2 as parallel-executable until checkpoint. Test files can be created concurrently.

**Foundation-first**: Cycle 1.1 establishes shared helper before dependent cycles. Track 1 classification (1.2-1.3) before guard logic (1.4-1.6).

**Concrete cycle scope**: Each cycle has clear test assertion implied by title (exit code, message content, file presence).

**Checkpoint spacing**: Light checkpoint after Phase 1 (13 cycles) is appropriate. Phase 2 is single-step, no checkpoint needed.

**Model tier assessment**: Haiku for both phases is correct (straightforward execution, git operations, prose edit).

**Traceability**: Requirements mapping table provides clear FR → cycle references. All 9 FRs mapped.

## Recommendations

**Cycle 1.7 validation**: During expansion, verify guard check placement in cli.py rm() is the first conditional after slug validation. All existing operations (probe → warn → remove_session_task → remove_worktrees → branch -d/-D → rmtree → clean) must follow guard.

**Cycle 1.13 evidence handling**: If test passes without code changes (bug was environment-specific), note this in cycle GREEN phase. Defensive checks (MERGE_HEAD checkpoint, ancestry validation) still provide value as belt-and-suspenders.

**Shared helper testing**: Cycle 1.1 tests `_is_branch_merged` in isolation (create merged branch, create unmerged branch, assert True/False). This helper is called by both tracks — thorough testing here reduces Track 1/2 test brittleness.

**Phase 2 expansion decision**: SKILL.md update is 6-line prose addition to existing Mode C step 3. Outline provides sufficient detail — full phase expansion may be skipped. If expanded, verify escalation message quotes match design ("Merge may be incomplete — branch {slug} has unmerged commits after merge reported success.").

---

**Ready for full expansion**: Yes

All requirements traced, all design decisions reflected, phase structure sound, all issues fixed.
