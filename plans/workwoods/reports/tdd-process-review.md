# TDD Process Review: workwoods

**Date:** 2026-02-17
**Runbooks:** plans/workwoods/runbook-phase-{1..6}.md
**Commits Analyzed:** 6a98c85c..8c5661d6 (TDD cycles), 53a85f87 (Phase 5 batch), f4fc6854 (Phase 5 general)
**Phase 6 general:** 4fd11adf

---

## Executive Summary

The workwoods TDD execution shows strong fundamentals: individual cycles in Phases 1–4 maintained rigorous per-cycle commits with verified RED/GREEN/REFACTOR loops. Six planning gaps (cycles planned for already-implemented behavior) were identified and handled correctly — test written, RED documented, stop condition recorded. Two significant batch violations occurred: Cycles 5.2–5.8 and 6.1–6.4 were each committed as single units rather than per-cycle commits, trading auditability for throughput. A WIP commit label on Cycle 3.6 indicates an incomplete REFACTOR phase that was corrected only at the Phase 3 checkpoint. Test quality is high throughout, with strong assertion specificity and real git repos used for integration tests.

---

## Plan vs Execution

### Phases 1–4: Per-Cycle Commits

| Cycle | Planned | Committed | Status | Notes |
|-------|---------|-----------|--------|-------|
| 1.1 | Yes | 6a98c85c | Done | Full RED/GREEN/REFACTOR |
| 1.2 | Yes | b8a3a04e | Done | Full RED/GREEN/REFACTOR |
| 1.3 | Yes | cb307d3c | Done | Full RED/GREEN/REFACTOR |
| 1.4 | Yes | c6bf0f8a | Done | Full RED/GREEN/REFACTOR |
| 1.5 | Yes | 132639a4 | STOP | RED passed unexpectedly — already implemented |
| 2.1 | Yes | 9310a8f2 | Done | Full RED/GREEN/REFACTOR |
| 2.2 | Yes | 037b6d38 | Done | Full RED/GREEN/REFACTOR |
| 2.3 | Yes | c26c3e39 | STOP | "RED skipped — already implemented in 2.1" (commit message) |
| 2.4 | Yes | 02c3b6e7 | Done | Full RED/GREEN/REFACTOR |
| 2.5 | Yes | 759955a5 | Done | Full RED/GREEN/REFACTOR |
| 3.1 | Yes | 52b1e561 | Done | Full RED/GREEN/REFACTOR |
| 3.2 | Yes | c1a9d18b | Done | Full RED/GREEN/REFACTOR |
| 3.3 | Yes | 49ad8bdb | Done | Full RED/GREEN/REFACTOR |
| 3.4 | Yes | dee91e47 | Done | Full RED/GREEN/REFACTOR |
| 3.5 | Yes | 0bca9755 | Done | Full RED/GREEN/REFACTOR |
| 3.6 | Yes | 7b344da9 | WIP | Committed as "WIP" — REFACTOR incomplete |
| 3.7 | Yes | e4a2f2ca | Done | REFACTOR noted test file size issue (566 lines) |
| 4.1 | Yes | 1e48375e | Done | Full RED/GREEN/REFACTOR |
| 4.2 | Yes | 91d384fc | STOP | RED passed unexpectedly — behavior pre-implemented |
| 4.3 | Yes | 23388930 | Done | Full RED/GREEN/REFACTOR; no execution report |
| 4.4 | Yes | 18d50b2f | Done | Full RED/GREEN/REFACTOR |

### Phase 5: Mixed TDD

| Cycle/Step | Planned | Committed | Status | Notes |
|------------|---------|-----------|--------|-------|
| 5.1 | Yes | 5528dd81 | STOP | RED passed (function pre-implemented) |
| 5.2–5.8 | Yes | 53a85f87 | BATCH | All 7 cycles in single commit |
| 5.9–5.10 | Yes | f4fc6854 | Done | General steps committed together (expected) |

### Phase 6: Mixed TDD

| Cycle/Step | Planned | Committed | Status | Notes |
|------------|---------|-----------|--------|-------|
| 6.1–6.4 | Yes | 8c5661d6 | BATCH | All 4 cycles in single commit |
| 6.5–6.11 | Yes | 4fd11adf | Done | General steps committed together (expected) |

**Summary:**
- Planned TDD cycles: 25 (Phases 1–4: 21, Phase 5: 8, Phase 6: 4)
- Executed with per-cycle commits: 18 (72%)
- Planning gaps (RED passed): 6 (cycles 1.5, 2.3, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5 — 5.2–5.5 are part of batch)
- Batched execution: 11 cycles across 2 batch commits
- WIP commit (incomplete REFACTOR): 1 (cycle 3.6)

---

## TDD Compliance Assessment

### Phases 1–4

| Cycle | RED | GREEN | REFACTOR | Report | Issues |
|-------|-----|-------|----------|--------|--------|
| 1.1 | FAIL verified | PASS verified | lint+precommit | Yes | Clean |
| 1.2 | FAIL verified | PASS (4/4 params) | extracted helpers | Yes | Clean |
| 1.3 | FAIL verified | PASS verified | lint fix | No report | Inferred from commit |
| 1.4 | FAIL verified | PASS verified | lint fix | Yes (brief) | Clean |
| 1.5 | PASS unexpected | N/A | N/A | Yes | Planning gap — handled correctly |
| 2.1 | FAIL verified | PASS (4/4 params) | lint+precommit | Yes | Clean |
| 2.2 | FAIL verified | PASS verified | lint+precommit | Yes | Clean |
| 2.3 | SKIPPED | test-only | lint | No | Red phase not run; commit says "already implemented in 2.1" |
| 2.4 | FAIL verified | PASS verified | lint+precommit | Yes | Clean |
| 2.5 | FAIL verified | PASS verified | complexity refactor | Yes | Complexity 13→6 via helpers |
| 3.1 | FAIL verified | PASS verified | style fixes | Yes | Clean |
| 3.2 | FAIL verified | PASS verified | style fixes | Yes | Clean |
| 3.3 | FAIL verified | PASS verified | lint | Yes | Clean |
| 3.4 | FAIL verified | PASS verified | lint | Yes | Clean |
| 3.5 | FAIL verified | PASS verified | lint | Yes | Clean |
| 3.6 | FAIL inferred | PASS inferred | INCOMPLETE | No | WIP commit — REFACTOR deferred to checkpoint |
| 3.7 | FAIL verified | PASS verified | lint | Yes | Test file 566 lines (not split until Phase 5) |
| 4.1 | FAIL verified | PASS verified | lint (FBT001) | Yes | Clean |
| 4.2 | PASS unexpected | test-only | none | Yes (brief) | Planning gap — documented |
| 4.3 | FAIL inferred | PASS inferred | lint | No report | No execution report |
| 4.4 | FAIL verified | PASS verified | lint | Yes | Gate testing simplified (accepted deferral) |

### Phase 5

| Cycle | RED | GREEN | REFACTOR | Report | Issues |
|-------|-----|-------|----------|--------|--------|
| 5.1 | PASS (expected) | test-only | lint | Yes | Clean — planning gap handled |
| 5.2–5.8 | Mixed (see below) | Mixed | Batch | Batch report | Batched — cannot assess per-cycle |

**Cycles 5.2–5.8 breakdown (from batch report):**
- 5.2–5.5: RED passed (pre-existing behavior) — correct per planning guidance ("Why it might pass")
- 5.6: RED FAIL verified, GREEN implemented
- 5.7: RED FAIL verified, GREEN implemented with slug parameter
- 5.8: RED FAIL verified, integration bug found and fixed

The batch execution included a significant refactoring: merge.py conflict resolution extracted to resolve.py (409→265 lines), and test file split. This refactoring was appropriate and necessary but occurred across multiple conceptual cycles in one commit.

### Phase 6

| Cycle | RED | GREEN | REFACTOR | Report | Issues |
|-------|-----|-------|----------|--------|--------|
| 6.1–6.4 | Inferred | Inferred | Batch | None (commit message only) | No per-cycle reports; no dedicated report file |

**Summary:**
- Full per-cycle compliance (RED+GREEN+REFACTOR, individual commit, report): 17 cycles
- Planning gap stops (correct behavior): 6 instances
- Partial compliance (WIP commit / deferred refactor): 1 (cycle 3.6)
- Batch compliance (correct TDD within batch, no per-cycle auditability): 11 cycles
- RED phase skipped without planning gap justification: 1 (cycle 2.3)
- Missing execution reports: cycles 1.3, 4.3, 6.1–6.4 (no individual reports)

**Violation Details:**
- RED skipped without justification: Cycle 2.3 (commit message says "already implemented in 2.1" but no stop condition documented in report — no report filed)
- REFACTOR incomplete at commit: Cycle 3.6 (WIP commit)
- Batched execution without per-cycle auditability: Cycles 5.2–5.8, 6.1–6.4

---

## Planning Issues

### Planning Gaps (RED Passed Unexpectedly)

Six cycles were planned for behavior that was already implemented. All were handled appropriately — test written, stop condition documented — but the gaps indicate over-estimation of implementation scope at planning time.

- **Cycle 1.5** — `list_plans()` fully implemented during Cycle 1.1 GREEN phase (over-implementation during Cycle 1.1)
- **Cycle 2.3** — Mtime comparison already built into Cycle 2.1 GREEN implementation (over-implementation)
- **Cycle 4.2** — Porcelain mode already routed to existing logic during Cycle 4.1 GREEN (over-implementation during 4.1)
- **Cycle 5.1** — `find_section_bounds()` implemented in a prior Phase 3 worktree-update (external dependency predating the runbook)
- **Cycles 5.2–5.5** — The D-5 "keep ours" strategies were already the implicit behavior of `_merge_session_contents()` (the function starts from ours)

The root cause pattern: when a GREEN implementation is straightforward, the agent implements adjacent related behavior to avoid revisiting the same file. This is efficient but creates planning debt — subsequent cycles find their work done.

**Recommendation:** During GREEN phase, implement ONLY what the current test requires. If adjacent behavior is obvious and cheap, note it in the report but do not implement it. This preserves TDD discipline and prevents planning gap accumulation.

### Design Assumption Violations

- **Cycle 5.2–5.5 strategy assumption** — The runbook expected these cycles to require new implementation. The design correctly specified a "keep ours" strategy, but the existing implementation already satisfied it. The planning could not have anticipated this without running the tests; this is acceptable.

- **Cycle 3.6 WIP commit** — The runbook specifies REFACTOR includes lint and precommit before committing. The WIP commit bypassed this. The Phase 3 checkpoint vet resolved the outstanding issues (commit `29de4aad`), but the single-cycle discipline was violated.

- **Phase 5 batch** — The runbook specifies Checkpoint 5.a after Cycle 5.4 and Checkpoint 5.mid after Cycle 5.8, implying individual cycle commits between checkpoints. The execution batched all 7 cycles into one commit. The runbook's "Why it might pass" notes on 5.2–5.5 likely encouraged the agent to treat them as low-resistance and batch them.

---

## Execution Issues

### Batch Operations

**Cycles 5.2–5.8 (commit 53a85f87):**
- 7 TDD cycles in a single commit with a single execution report
- The report explicitly states "Cycles 5.2–5.8 executed as a batch"
- The batch included a significant structural refactoring (merge.py→resolve.py extraction, test file split)
- Impact: Cannot audit individual cycle RED/GREEN transitions; cannot verify each cycle's regression check was run independently
- Mitigating factor: The batch report documents per-cycle status, including which cycles had genuine RED failures (5.6, 5.7, 5.8) vs pre-existing behavior (5.2–5.5)

**Cycles 6.1–6.4 (commit 8c5661d6):**
- 4 TDD cycles in a single commit
- No individual execution reports exist (only the commit message summary)
- The commit message provides high-level coverage: "9 tests covering all validation scenarios"
- Impact: Cannot verify RED phase for each cycle; cannot confirm each GREEN was minimal; no regression check documentation per cycle

### Verification Skips

**Cycle 2.3 RED phase:**
- The commit message states "RED skipped — already implemented in 2.1"
- This is ambiguous: if `test_mtime_comparison_staleness` was written and run, RED should have been verified (pass = planning gap, with report). If the test was not run, it is a RED skip violation.
- No execution report exists to resolve the ambiguity. The commit was created (c26c3e39) without a planning-gap stop-condition report, suggesting the test may not have been run at all.

**Cycle 3.6 REFACTOR phase:**
- Committed as "WIP" — precommit and lint not run before commit
- Resolved at Phase 3 checkpoint (commit 29de4aad) which included aggregation fixes and docstring cleanup
- The checkpoint vet caught and resolved 89 deletions from aggregation.py (significant cleanup)

**Missing execution reports:**
- Cycle 1.3: No dedicated report
- Cycle 4.3: No dedicated report (behavior inferred from commit 23388930)
- Cycles 6.1–6.4: No per-cycle reports (batch commit only)

### Discipline Violations

**Cycle 3.6 WIP commit:** The REFACTOR phase was deferred to the phase checkpoint. While the checkpoint resolved the issues, the per-cycle REFACTOR discipline was violated. This matters because deferred refactoring can compound — the Phase 3 checkpoint vet required 89 lines removed from aggregation.py, suggesting non-minimal GREEN implementation that should have been caught at cycle level.

**Cycles 5.2–5.8 batch:** The orchestrator (Sonnet, direct execution) chose to execute 7 cycles as a batch rather than per-cycle. The batch execution report notes this explicitly. The runbook text for 5.2–5.5 included "Why it might pass" notes suggesting pre-existing behavior, which may have cued batch treatment. However, cycles 5.6–5.8 had genuine NEW behavior to implement and should have received individual commits.

---

## Code Quality Assessment

### Test Quality

**Strengths:**
- Assertions are specific throughout: exact string equality checks, exact object field comparisons, exact None checks (`result is None`, not just falsy), boolean identity checks (`is True`, not just truthy)
- Real git repositories used for all aggregation tests (Cycles 3.1–3.7, Phase 4) — no subprocess mocking
- Parametrized tests used appropriately where pattern repetition would obscure signal (Cycles 1.2, 2.1, 5.5)
- Test names clearly describe the behavior under test: `test_empty_directory_not_a_plan`, `test_mtime_comparison_staleness`, `test_blockers_evaluate_strategy`
- Integration test (5.8) caught a genuine pre-existing bug (Worktree Tasks task leakage)
- Edge cases consistently covered: missing files, empty sections, nonexistent directories

**Issues:**
- `test_worktree_merge_strategies.py` at 375 lines is approaching the project's 400-line soft limit; test file split in Phase 5 helped but the strategies file itself is at risk
- Cycle 4.4 deferred gate detection testing: "Simplified gate testing to verify absence of gate lines (gate detection requires vet_status_func passed to infer_state, which will be set up in later cycles)." This deferral was undocumented in the runbook and constitutes accepted technical debt in the test suite — there is no subsequent cycle that adds vet_status_func integration to the CLI path
- Cycle 3.7 noted test file at 566 lines without splitting, relying on a later cycle to address it

### Implementation Quality

**Strengths:**
- Complexity violations caught and resolved at cycle level (Cycle 2.5: complexity 13→6 via helper extraction; Cycle 1.2: helpers `_collect_artifacts()` and `_determine_status()` extracted during REFACTOR)
- Module extraction done when file size exceeded limits (merge.py→resolve.py in Phase 5 REFACTOR)
- Models designed with appropriate nullability (`str | None`, `float | None`) discovered and added during GREEN phases rather than over-engineered upfront
- Dependency injection pattern used for testability (Cycle 1.4: `vet_status_func` parameter)
- No obviously over-large functions in final implementation

**Issues:**
- Cycle 3.6 WIP commit required 89-line cleanup at Phase 3 checkpoint. The `aggregation.py` cleanup (vet commit 29de4aad: 89 deletions) suggests the WIP GREEN implementation was non-minimal — it included non-essential code that needed removal
- `test_planstate_aggregation.py` was split into unit + integration tests (commit `e019a94a`) outside the TDD cycle structure — this was a quality fix done at checkpoint rather than REFACTOR phase
- `display.py` module created in Cycle 4.3/4.4 is not listed in the Phase 4 runbook scope — it was a design decision made during execution without explicit runbook guidance. The decision was sound but was made autonomously

### Code Smells

- None identified at file or function level in the final committed code. File sizes are within bounds (all production files under 250 lines), complexity violations were resolved during REFACTOR phases.

---

## Recommendations

### Critical (Address Before Next TDD Runbook)

**1. Prohibit RED phase skipping without documented planning gap**
- **Issue:** Cycle 2.3 committed with "RED skipped — already implemented in 2.1" in the commit message, with no stop-condition report and no executed test run documented. This is ambiguous at best and a discipline violation at worst.
- **Impact:** An unrun RED test means the test's correctness is unverified; the implementation may satisfy the test for the wrong reason.
- **Action:** Add explicit rule to runbook template: "If RED passes unexpectedly, file a stop-condition report immediately (see Cycle 1.5 pattern). If RED was not run, do not commit — run the test first."
- **File/Section:** `agent-core/skills/orchestrate/SKILL.md` — per-cycle execution protocol

**2. Require per-cycle commits for all NEW behavior, even within planning-gap batches**
- **Issue:** Cycles 5.6, 5.7, and 5.8 all had genuine NEW behavior (extract_blockers, slug parameter, integration bug fix) but were batched with 5.2–5.5 into a single commit.
- **Impact:** Cannot audit the RED→GREEN transition for the cycles with real implementation. If a regression surfaces, the batch commit obscures which cycle introduced it.
- **Action:** Add rule to runbook: "Even when surrounding cycles are planning gaps (RED passes), cycles with genuine RED failures MUST be committed individually before proceeding."
- **File/Section:** `plans/workwoods/runbook-phase-5.md` as a reference pattern; generalize to orchestrate skill

### Important (Address Soon)

**3. Clarify REFACTOR completion requirement before WIP commit**
- **Issue:** Cycle 3.6 was committed as "WIP" without completing REFACTOR. The Phase 3 checkpoint vet then cleaned up 89 lines from aggregation.py — cleanup that should have been caught at REFACTOR time.
- **Impact:** Deferred REFACTOR compounds: the WIP code was visible for the next cycle (3.7) which built on it, and the checkpoint vet required significant cleanup that could have been caught immediately.
- **Action:** Clarify in the REFACTOR phase instructions: "Do NOT create the WIP commit until lint and precommit pass. If REFACTOR cannot complete in reasonable time, STOP and document the blocker — do not commit unfinished state."
- **File/Section:** `agent-core/skills/orchestrate/SKILL.md` — REFACTOR phase instructions

**4. Add execution report requirement to Phase 6 TDD batch**
- **Issue:** Cycles 6.1–6.4 have no per-cycle execution reports. Only a commit message summary exists ("9 tests covering all validation scenarios").
- **Impact:** Cannot verify RED phase was executed for each cycle, cannot audit what tests were run for regression checks, cannot determine if any planning gaps occurred.
- **Action:** For future batch commits where individual reports don't exist, require at minimum a batch report file (like `cycle-5-2-8-execution.md`) that documents per-cycle RED/GREEN status before the batch commit is made. The pattern from Phase 5 was appropriate; Phase 6 should have followed it.
- **File/Section:** `plans/workwoods/reports/` — create retrospective `cycle-6-1-4-execution.md` if feasible

**5. Address gate detection deferral in CLI tests**
- **Issue:** Cycle 4.4 simplified gate testing by verifying absence of gate lines only, with a note that "gate detection requires vet_status_func passed to infer_state, which will be set up in later cycles." No subsequent cycle set this up.
- **Impact:** The CLI (`wt ls`) never exercises the gate display path in tests. A stale vet chain will be silently ignored at the CLI level.
- **Action:** Add a test (or extend `test_rich_mode_plan_and_gate`) that passes a mock `vet_status_func` through the CLI path and verifies a Gate line appears. This is a gap in test_worktree_ls_upgrade.py.
- **File/Section:** `tests/test_worktree_ls_upgrade.py` — add gate display integration test

### Minor (Consider for Future)

**6. Document over-implementation risk in GREEN phase guidance**
- **Issue:** Six planning gaps originated from over-implementation during GREEN phases (agent implements adjacent behavior while in the file). Cycles 1.1 implemented list_plans() fully before Cycle 1.5 could do it; Cycle 2.1 implemented mtime comparison before Cycle 2.3 could do it; Cycle 4.1 implemented both flag and routing before Cycle 4.2 could do it.
- **Impact:** Planning gaps are minor disruptions individually, but six across 25 cycles (24%) is a signal. Each planning gap requires an extra commit, a stop-condition report, and orchestrator investigation.
- **Action:** Add to GREEN phase guidance: "Implement only what is needed to pass the current RED test. If the minimal implementation naturally covers the next cycle's behavior, note it in the report but do not pre-implement it — let the next cycle's RED confirm it."
- **File/Section:** `agent-core/skills/orchestrate/SKILL.md` — GREEN phase description

**7. Test file line limit enforcement during REFACTOR**
- **Issue:** Cycle 3.7 noted `test_planstate_aggregation.py` at 566 lines but deferred splitting to "escalation if needed." The split happened later in a separate commit (`e019a94a`). The 400-line soft limit for test files should be enforced at REFACTOR time.
- **Action:** Add to REFACTOR phase checklist: "Check test file line count. If >400 lines, split before committing. Do not defer file splits to later cycles or checkpoints."
- **File/Section:** `agent-core/skills/orchestrate/SKILL.md` — REFACTOR phase checklist

---

## Process Metrics

- TDD cycles planned: 25
- Cycles executed with per-cycle commits: 18 (72%)
- Cycles batched: 11 (Phases 5.2–5.8 and 6.1–6.4)
- Planning gap stops: 6
- RED phase compliance (verified fail or documented pass): 23/25 (92%); Cycle 2.3 ambiguous, Cycle 3.6 inferred
- REFACTOR compliance (lint+precommit before commit): 22/25 (88%); Cycle 3.6 WIP, 6.1–6.4 no per-cycle reports
- Execution report coverage: 19/25 cycles have dedicated reports (76%); gaps at 1.3, 4.3, and the 6.1–6.4 batch
- Code quality: Good — complexity violations caught and resolved at cycle level, appropriate module splits
- Test quality: Good — specific assertions, real git repos for integration tests, good edge case coverage; gate test gap in CLI tests noted

---

## Conclusion

The workwoods TDD execution demonstrates a mature baseline. The per-cycle discipline in Phases 1–4 is rigorous: RED failures documented, GREEN implementations minimal, REFACTOR phases resolving lint and complexity issues before commit. Planning gaps were identified and handled correctly throughout.

The Phase 5 and Phase 6 batch commits represent the primary process regression. The Phase 5 batch had a reasonable trigger (5 consecutive planning-gap cycles reducing resistance) but included cycles with genuine new behavior that should have been committed individually. The Phase 6 batch is harder to justify — all 4 cycles had new behavior, no planning gap cue existed, and no execution report was filed.

The most actionable improvements are process-level: (1) require per-cycle commits for cycles with genuine RED failures even within batches, (2) prohibit WIP commits without completed REFACTOR, and (3) mandate execution reports before batch commits. The code quality produced by this TDD session is sound and these process improvements would make future sessions more auditable without significantly increasing execution cost.
