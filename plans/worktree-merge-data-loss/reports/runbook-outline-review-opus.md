# Runbook Outline Review (Opus): Worktree Merge Data Loss

**Artifact**: plans/worktree-merge-data-loss/runbook-outline.md
**Design**: plans/worktree-merge-data-loss/design.md
**Prior review**: plans/worktree-merge-data-loss/reports/runbook-outline-review.md (automated)
**Date**: 2026-02-16
**Mode**: interactive review (grounded in design + source code)

## Summary

The outline is structurally sound and covers all 9 functional requirements. The automated review caught and fixed genuine issues (three-branch logic split, integration cycle, dependency ordering). This opus review found 3 substantive concerns the automated review missed, plus confirmed 2 of its flagged concerns. The outline is expansion-ready after addressing the findings below.

**Overall Assessment**: Ready (with notes for expansion)

## Requirements Coverage

| Requirement | Phase | Cycles | Coverage | Notes |
|-------------|-------|--------|----------|-------|
| FR-1 | 1 | 1.1-1.3 | Complete | `_is_branch_merged` + `_classify_branch` + orphan edge case |
| FR-2 | 1 | 1.4 | Complete | Guard refuses with exit 1 |
| FR-3 | 1 | 1.6 | Complete | Focused-session-only allowed with `git branch -D` |
| FR-4 | 1 | 1.4-1.7 | Complete | Exit codes exercised across guard scenarios |
| FR-5 | 1 | 1.8 | Complete | No `git branch -D` in output |
| FR-6 | 1 | 1.9-1.10 | Complete | MERGE_HEAD checkpoint + merged idempotency |
| FR-7 | 1 | 1.11 | **Partial** | See Finding 1 below |
| FR-8 | 1 | 1.7 | Complete | Success messages differentiate types |
| FR-9 | 2 | 2.1 | Complete | SKILL.md Mode C escalation |

## Findings

### Finding 1: FR-7 mapping ambiguity (Cycle 1.11 vs 1.12)

The requirements mapping table maps FR-7 (post-merge ancestry validation) to Cycle 1.11. But in the cycle list, Cycle 1.11 is described as "Post-merge ancestry validation — `_validate_merge_result(slug)` verifies ancestor." Meanwhile, the design's `_validate_merge_result` is called *after commit, before precommit* and also includes diagnostic logging (parent count warning). The mapping table initially (pre-automated-review) mapped FR-7 to 1.12, and the automated review renumbered to 1.11 after splitting Track 2 cycles.

**Impact:** Minor confusion during expansion. The cycle description is correct; the mapping just needs to be unambiguous. The diagnostic logging (parent count < 2 warning) is part of `_validate_merge_result` per the design but isn't mentioned in any cycle.

**Recommendation for expansion:** Cycle 1.11 should include the diagnostic logging (parent count warning) within its GREEN phase, not as a separate cycle. It's part of the same function. Mention this in expansion guidance.

### Finding 2: Cycle 1.8 vacuity concern (confirmed)

The automated review flagged this, and it's valid. Cycle 1.8 tests "No `git branch -D` in stderr output for any case." This is a presentation-format assertion — verifying absence of a string in output rather than testing behavior. The behavior (no destructive command suggestions) is already achieved by implementing the guard in Cycles 1.4-1.7. By the time Cycle 1.8 runs, the output is already determined by the guard implementation.

**However:** FR-5 ("CLI never suggests destructive commands in output") is a regression guard. The current code (cli.py:373) explicitly prints `"use: git branch -D {slug}"`. A test that asserts this string never appears in any code path is a legitimate regression test, not vacuous. The value is in *preventing reintroduction*, not in driving new behavior.

**Recommendation:** Keep Cycle 1.8 but mark it as a regression assertion cycle during expansion. The RED phase should assert against the *current* code (which emits the -D suggestion) and verify the GREEN implementation removes it. This gives it genuine RED/GREEN delta.

### Finding 3: `_validate_merge_result` placement in merge flow

The design specifies `_validate_merge_result` is called "after commit, before precommit" (design line 122). The outline places this in Cycle 1.11 as a standalone function test. During expansion, the integration point matters: the function must be called in `_phase4_merge_commit_and_precommit` after the commit block but before `just precommit`.

The outline doesn't specify WHERE in the Phase 4 flow this validation is inserted. Cycles 1.9-1.10 modify Phase 4's commit logic; Cycle 1.11 adds the validation function; but no cycle tests the integrated flow (commit + validate + precommit in sequence).

**Recommendation:** Cycle 1.12 (parent repo file preservation) serves as the integration test for the full modified Phase 4 flow. During expansion, make this dependency explicit: Cycle 1.12 exercises the complete path (Phase 3 merge → Phase 4 checkpoint → commit → validate ancestry → precommit).

### Finding 4: Existing test file overlap

The outline proposes two new test files: `test_worktree_rm_guard.py` and `test_worktree_merge_correctness.py`. The existing codebase already has:
- `test_worktree_rm.py` — 3 tests for rm (basic, dirty warning, branch-only)
- `test_worktree_merge_merge_head.py` — MERGE_HEAD detection tests
- `test_worktree_merge_parent.py` — parent merge operation tests

**Concern:** The new `test_worktree_merge_correctness.py` overlaps with `test_worktree_merge_merge_head.py` (both test Phase 4 commit paths). Cycles 1.9-1.10 modify the same `_phase4_merge_commit_and_precommit` function that `test_worktree_merge_merge_head.py` already tests.

**Recommendation:** During expansion, decide whether to:
- (a) Add new tests to existing `test_worktree_merge_merge_head.py` (co-locate related tests)
- (b) Keep separate file but import shared setup from existing patterns

Either way, verify the existing MERGE_HEAD tests still pass after Phase 4 modifications. Add this as a checkpoint validation step.

### Finding 5: Guard placement relative to existing rm flow

The design (lines 84-91) specifies the guard runs FIRST, before all existing operations. The current `rm` function (cli.py:349-382) starts with `_probe_registrations`. The design's flow is:

```
AFTER: check_exists → guard → probe → warn → remove_session_task → remove_worktrees → branch -d/-D → rmtree → clean
```

Cycle 1.7 is defined as the integration cycle for guard-before-destruction. During expansion, this cycle must test that when the guard refuses (exit 1), NONE of the following occur:
- `_probe_registrations` runs
- session task removed
- worktrees removed
- `shutil.rmtree` runs
- branch deleted

The outline's expansion guidance mentions the operation list but doesn't specify the negative assertion (things that must NOT happen when guard refuses). This is the core regression test — the incident occurred because `shutil.rmtree` ran before branch deletion could detect the problem.

**Recommendation:** Add negative assertion guidance for Cycle 1.7 expansion. The test must verify the directory still exists and the branch still exists after guard refusal. This is partially covered by the automated review's "Cycle 1.13 end-to-end test scenario" note, but the negative assertion belongs in Cycle 1.7 (guard integration), not 1.13 (end-to-end merge).

### Finding 6: Cycle 1.5 ordering — merged removal before guard refusal

The outline orders Track 1 cycles as:
- 1.4: Guard refuses unmerged (exit 1)
- 1.5: Guard allows merged branch removal (exit 0)
- 1.6: Guard allows focused-session-only removal (exit 0)

This ordering tests the refusal path before the success path. In TDD, the foundation-first ordering would be:
- Test the happy path first (merged branch removal succeeds)
- Then test refusal (unmerged branch refused)
- Then test the exception (focused-session-only allowed)

**Impact:** Low. Both orderings work. The current ordering has a minor advantage: it tests the guard's primary purpose (refusing unmerged) before testing pass-through. The success path (merged removal) is essentially the existing behavior with classification overhead.

**Recommendation:** Keep current ordering. The guard's raison d'etre is refusal; testing refusal first is defensible.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 13 cycles | Medium | 93% | Justified by dual-track independence |
| 2 | 1 step | Low | 7% | Prose-only |

Phase 1's size (13 cycles) is acceptable because Track 1 (8 cycles) and Track 2 (5 cycles) are independently executable. Effective parallelism reduces the cognitive load to ~8 cycles per track. The automated review's concern about >8 items is valid in general but mitigated here by track independence.

### Checkpoint Spacing

Single checkpoint after Cycle 1.12 (13 cycles in). The automated review recommended this placement. Given track independence, an optional mid-phase checkpoint after Cycle 1.8 (Track 1 complete) would allow early validation of the removal guard before proceeding to Track 2. Not critical — the tracks don't depend on each other.

## Growth Projection

| File | Current lines | Projected delta | Projected total | Status |
|------|--------------|-----------------|-----------------|--------|
| cli.py | 382 | +35 | 417 | **Exceeds 400-line threshold** |
| merge.py | 307 | +25 | 332 | OK |
| utils.py | 38 | +8 | 46 | OK |
| SKILL.md | ~130 | +6 | ~136 | OK |

**cli.py at 382 lines + 35 delta = 417.** This exceeds the 400-line enforcement threshold. The `_classify_branch` function (~15 LOC) and guard logic (~20 LOC) push it over. However, `_classify_branch` is rm-specific (per design: "rm-specific" in cli.py), not a candidate for extraction to utils.py.

**Recommendation:** During expansion, monitor cli.py growth. If it exceeds 400 after guard implementation, consider extracting `_create_session_commit` (lines 154-178, ~25 LOC) to utils.py to make room. The outline doesn't need to change — this is an expansion-time decision.

## Design Alignment

- **Track structure**: Outline mirrors design's three tracks exactly
- **Module placement**: `_is_branch_merged` in utils.py, `_classify_branch` in cli.py — matches design D-7
- **Exit codes**: D-2 (0/1/2) consistently applied across cycles
- **Marker text detection**: D-1 referenced in Cycle 1.2 (`_classify_branch` checks exact message format)
- **Guard ordering**: D-6 (guard before destruction) implemented as Cycle 1.7 integration
- **MERGE_HEAD checkpoint**: D-4 implemented as Cycles 1.9-1.10 (three-branch logic)
- **Ancestry validation**: D-5 implemented as Cycle 1.11

All 7 design decisions map to specific cycles. No contradictions detected.

## Automated Review Assessment

The prior automated review (runbook-outline-review.md) caught genuine issues:
- **Three-branch logic split** (Major 3) — correctly identified missing `else` branch from design
- **Integration cycle** (Major 2) — correctly added guard integration as Cycle 1.7
- **Dependency ordering** (Minor 1) — correctly noted Cycle 1.1 as shared prerequisite

Concerns the automated review flagged but that this review re-evaluates:
- **Phase 1 size (13 cycles)**: Acceptable given track independence
- **Cycle 1.8 vacuity**: Valid concern but not vacuous — it's a regression guard (see Finding 2)
- **Cycle 1.13 TDD discipline**: The parent repo file preservation test is a regression/integration test. RED may pass without code changes (design notes this explicitly). This is fine — the test has value as a regression guard even if it doesn't drive new behavior via RED/GREEN.

## Expansion Guidance Additions

Based on this review, the following should be incorporated during expansion (in addition to existing guidance in outline):

- **Cycle 1.7 negative assertions**: Test must verify directory and branch still exist after guard refusal. The guard's purpose is preventing the incident where `shutil.rmtree` ran before the merge problem was detected.
- **Cycle 1.8 regression framing**: RED phase should run against current code (which emits `-D` suggestion at cli.py:373). GREEN phase removes the suggestion. This gives genuine RED/GREEN delta.
- **Cycle 1.11 diagnostic logging**: Include parent count warning (`parent_count < 2`) in the `_validate_merge_result` function. This is part of the design but not called out in the cycle description.
- **Cycle 1.12 integration scope**: This cycle exercises the full modified Phase 4 flow. Make dependency on Cycles 1.9-1.11 explicit.
- **Existing test compatibility**: After Phase 4 modifications, verify `test_worktree_merge_merge_head.py` tests still pass. The existing tests assert on the current Phase 4 behavior; modifications must not break them (or tests must be updated as part of the same cycle).
- **cli.py growth**: File at 382 lines, projected to 417. If exceeding 400, extract `_create_session_commit` to utils.py during implementation.

---

**Ready for full expansion**: Yes

All requirements traced, all design decisions reflected, phase structure justified, growth projection noted. Findings are expansion-time concerns, not structural issues requiring outline revision.
