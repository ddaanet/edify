# TDD Process Review: runbook-generation-fixes

**Date:** 2026-02-22
**Runbook:** plans/runbook-generation-fixes/runbook-phase-{1,2,3,4}.md
**Commits Analyzed:** 4a361f32..f1dce29f (19 commits)

## Executive Summary

13 TDD cycles across 4 phases executed with high overall compliance. All planned cycles were completed in the correct order with one-commit-per-cycle discipline maintained throughout. Three cycles had RED phase violations (1.1, 3.3 already passing; 2.3 planned as a regression guard that passes by design), and Cycles 3.1–3.3 produced recurring stop-condition escalations due to a test file line-limit violation that persisted across three cycles before being resolved in 4.2's REFACTOR phase. Phase checkpoint vets caught genuine defects (dead regex branch, stale haiku defaults, tautological assertion, redundant type override) and applied fixes cleanly. Code quality is strong: implementation is minimal and behavior-focused, test assertions are specific with diagnostic messages.

## Plan vs Execution

| Cycle | Planned | Executed | Commit | Status | Issues |
|-------|---------|----------|--------|--------|--------|
| 1.1 | Yes | Yes | bd344793 | Complete | RED phase violation — prior session left uncommitted implementation |
| 1.2 | Yes | Yes | 7b8eae07 | Complete | None |
| 1.3 | Yes | Yes | 3ce42fd9 | Complete | Planned as verification cycle (expected RED pass) |
| Phase 1 vet | Yes | Yes | 0ff96bed | Complete | None |
| 2.1 | Yes | Yes | a6a3a389 | Complete | None |
| 2.2 | Yes | Yes | f3de68fb | Complete | None |
| 2.3 | Yes | Yes | 2441e5d7 | Complete | Planned as regression guard (expected RED pass) |
| 2.4 | Yes | Yes | 8fc7a3de | Complete | None |
| 2.5 | Yes | Yes | 1eec657a | Complete | None |
| Phase 2 vet | Yes | Yes | b84679a1 | Complete | None |
| 3.1 | Yes | Yes | dd496683 | Stop condition | Precommit failure (line limit); WIP commit label carried into parent repo |
| 3.2 | Yes | Yes | 81e2c2db | Stop condition | Precommit failure (line limit) |
| 3.3 | Yes | Yes | a955d3d7 | Stop condition | RED violation (already passing) + precommit failure (line limit) |
| Phase 3 vet | Yes | Yes | 5adfd80e | Complete | Vet commit message is "Fix tautological ordering assertion" — not labeled as checkpoint |
| 4.1 | Yes | Yes | 7bb1a1c5 | Stop condition | Precommit failure (line limit) |
| 4.2 | Yes | Yes | 57b696c0 | Complete | Resolved line-limit by splitting TestOrchestratorPlan to new file in REFACTOR |
| Phase 4 vet | Yes | Yes | 2d30028e | Complete | None |
| Phase 5 | Yes | Yes | f1dce29f | Complete | Inline phase (prose edits, not TDD) |

**Summary:**
- Planned cycles: 13
- Executed cycles: 13
- Skipped: 0
- Combined: 0
- Out-of-order: 0

## TDD Compliance Assessment

| Cycle | RED | GREEN | REFACTOR | Regression Check | Issues |
|-------|-----|-------|----------|-----------------|--------|
| 1.1 | Violation | Pass | Clean | 7/7 + 1143/1144 | RED could not be verified — prior session left implementation + test uncommitted |
| 1.2 | Fail (expected) | Pass | Docstring fix | 9/9 + 1144/1145 | None |
| 1.3 | Pass (planned) | N/A | None needed | 10/10 | Verification cycle — RED pass is correct outcome |
| 2.1 | Fail (expected) | Pass | Docstring fix | 11/11 | None |
| 2.2 | Fail (expected) | Pass | None | 12/12 | None |
| 2.3 | Pass (planned) | N/A | None needed | 13/13 | Regression guard — RED pass is correct outcome |
| 2.4 | Fail (expected) | Pass | None | 14/14 | None |
| 2.5 | Fail (expected) | Pass | `_run_validate` extraction + deslopping | 15/15 | None |
| 3.1 | Fail (expected) | Pass (2 iterations) | Lint fix; precommit FAILED | 16/16 | STOP: line limit not resolved before commit |
| 3.2 | Fail (expected) | Pass | None; precommit FAILED | 16/16 | STOP: line limit not resolved before commit |
| 3.3 | Violation | N/A | None; precommit FAILED | 16/16 | RED violation (3.2 implementation covered 3.3 case); STOP: line limit unresolved |
| 4.1 | Fail (expected) | Pass | Lint fix; precommit FAILED | 16/16 | STOP: line limit not resolved before commit |
| 4.2 | Fail (expected) | Pass | TestOrchestratorPlan extracted to new file | 17/17 | Line limit finally resolved in REFACTOR |

**Summary:**
- Full compliance: 8 cycles (1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 4.2)
- Partial compliance (stop condition / line-limit): 4 cycles (3.1, 3.2, 3.3, 4.1)
- RED violation: 2 cycles (1.1 — involuntary; 3.3 — implementation pre-covered case)

**Violation Details:**
- RED phase not verifiable: Cycle 1.1 (prior session left uncommitted implementation in working tree; agent correctly identified cause and documented decision)
- RED passed unexpectedly: Cycle 3.3 (Cycle 3.2's implementation used `.strip()` guard which already handled the whitespace-only case; agent documented the root cause)
- REFACTOR incomplete (precommit failed, committed anyway): Cycles 3.1, 3.2, 3.3, 4.1
- Regression check count anomaly: Cycles 3.1–4.1 report 16/16 despite growing test suite — likely reflects the mixed.py suite only, not the full count

## Planning Issues

**Planned Cycles Covering Already-Implemented Work (Cycle 1.1):**
Cycle 1.1's RED phase violation resulted from the prior session leaving an uncommitted implementation in the working tree. The runbook could not anticipate this since it was created before the partial execution. The agent correctly identified the cause and made a documented decision to commit the pre-existing work. This is a process orchestration gap (clean tree invariant violated between sessions) rather than a runbook planning defect.

**Verification Cycles With Planned-Pass RED (1.3, 2.3):**
Both cycles were correctly designed as regression guards, not as test-first cycles. The phase files and step files explicitly label them: 1.3 is marked "Expected outcome (verification)" and 2.3 is marked "[REGRESSION] Test Phase." The RED-pass-by-design pattern is valid TDD use of regression guards when the behavior is already covered by prior cycles. No planning defect.

**Cycle 3.3 RED Violation From Over-Complete 3.2 Implementation:**
Cycle 3.2's GREEN implementation used `.strip()` in both `extract_phase_preambles()` and in the generation guards, which fully covered the whitespace-only case that Cycle 3.3 was planned to add. This is a GREEN over-implementation: the step file instructed minimal implementation for 3.2, but the implementation produced a more complete solution than required. The agent documented the discovery clearly and correctly proceeded with 3.3 as regression protection.

**Persistent Line-Limit Issue (Cycles 3.1–4.1):**
The runbook did not anticipate that `tests/test_prepare_runbook_mixed.py` would exceed the 400-line limit when Phase 3 tests were added. The test file started Phase 3 at ~381 lines. Adding `TestPhaseContext` (85–97 lines) pushed it past the limit. The correct resolution — splitting into a new test file — was documented in cycle reports from 3.1 onward but deferred until Cycle 4.2's REFACTOR. This is both a planning gap (line limit threshold not anticipated) and an execution gap (resolution deferred across four cycles).

## Execution Issues

**Recurring Stop Conditions Without Resolution (Critical):**
Cycles 3.1, 3.2, 3.3, and 4.1 all committed with `just precommit` failing on the test file line-limit check. The stop condition was correctly identified in each cycle report, but commits proceeded anyway. The correct protocol is to resolve precommit failures before committing. Instead, the line-limit violation accumulated across four cycles, with each cycle report noting the failure and recommending a split without acting on it.

- Cycle 3.1: 409 lines → STOP documented, WIP commit created
- Cycle 3.2: 478 lines → STOP documented, commit created
- Cycle 3.3: 465 lines → STOP documented (file shrank slightly from 3.2 because 3.3 test was added to phase_context.py not mixed.py), commit created
- Cycle 4.1: 446 lines (mixed.py still over limit), STOP documented, commit created
- Cycle 4.2: REFACTOR extracted TestOrchestratorPlan to `test_prepare_runbook_orchestrator.py`, resolving the limit

**WIP Commit Label Propagation:**
Cycle 3.1's parent repo commit is labeled `WIP: Cycle 3.1 [extract-phase-preambles]` — the WIP label was carried into the parent repo commit rather than being reserved for the submodule WIP commit. All other parent repo cycle commits have clean `Cycle X.Y: [name]` labels. The submodule shows WIP commits for cycles 1.1, 1.2, 2.1, 2.2, 2.4, 3.1, and 4.1, while clean commits exist for 2.5, 3.2, and 4.2 — indicating the REFACTOR phase successfully amended the WIP commit for some cycles but not others. For Cycle 4.1, the submodule shows `WIP: Cycle 4.1` while the parent shows a clean label.

**GREEN Required Two Iterations (Cycle 3.1):**
The cycle report documents that the initial `extract_phase_preambles()` implementation had a bug where the phase-match branch overwrote an already-saved preamble. This required a second implementation iteration during GREEN. Two-iteration GREEN is within acceptable bounds (not a batched implementation), but it signals that the implementation was not fully planned before coding. The bug was self-diagnosed and fixed within the same cycle.

**Regression Count Inconsistency:**
Cycles 3.1 through 4.1 all report "16/16 passed" for regression checks despite the test suite growing from 15 tests (end of Phase 2) to 17 tests (end of Phase 4). The 16/16 count appears to reflect only tests in `test_prepare_runbook_mixed.py` and `test_prepare_runbook_inline.py`, not including the new `test_prepare_runbook_phase_context.py` file. Cycle 4.2 correctly reports 17/17 after the file split. This is a minor documentation gap — the regression check command scope should match the actual test count.

## Code Quality Assessment

**Test Quality:**

- Good: Test names describe observable behavior throughout (e.g., `test_assembly_injects_phase_headers_when_absent`, `test_no_phase_context_when_preamble_empty`, `test_missing_model_produces_error`)
- Good: Assertions include diagnostic f-strings on failure (checkpoint-2-vet confirmed "assertions include diagnostic messages — makes test failures self-explanatory")
- Good: `test_assembly_preserves_existing_phase_headers` uses count assertions (`content.count("### Phase 1:") == 1`) rather than presence checks — catches duplication bugs that substring checks miss
- Good: `test_mixed_runbook_phase_metadata_and_orchestrator_correct` uses position-index checks (`p1_pos < p2_pos < p3_pos`) — stronger than substring presence
- Good: `test_no_phase_context_when_preamble_empty` verifies both the omission case (Phase 1) and the non-omission case (Phase 2) in one test — avoids false confidence from only testing the empty path
- Issue: Tautological ordering assertion in `test_step_and_cycle_files_include_phase_context` — `phase_ctx_pos < body_pos or phase_ctx_pos > metadata_pos` was always true because the second disjunct was redundant given prior assertions. Caught and fixed by Phase 3 checkpoint vet.
- Issue: Regression check scope in cycles 3.1–4.1 reports count (16/16) that doesn't include the growing `test_prepare_runbook_phase_context.py` file. Full suite count would be more accurate.

**Implementation Quality:**

- Good: `extract_phase_models()` uses `re.IGNORECASE | re.MULTILINE` and normalizes to lowercase — defensive against case variations
- Good: `validate_and_create()` validation loop collects all unresolved steps before failing (complete error reporting vs. stop-at-first)
- Good: `validate_and_create()` defaults `preambles = phase_preambles or {}` — prevents None-dereference from callers that don't pass preambles
- Good: `phase_context and phase_context.strip()` guard is defensive against both None and whitespace-only strings
- Good: Phase 2 checkpoint vet caught `model: None` in agent frontmatter when models were phase-only, and stale `default_model="haiku"` parameters in generator functions — both fixed before Phase 3 began
- Good: `_run_validate` helper extracted in Cycle 2.5 REFACTOR reduced boilerplate across 3 callers; extracted to `tests/pytest_helpers.py` in Phase 2 checkpoint for cross-file reuse
- Issue: Green implementation in Cycle 3.2 was more complete than the minimum required — it implemented the whitespace guard that was Cycle 3.3's planned contribution. This is mild over-implementation but posed no correctness risk.

**Anti-patterns:**

- None identified. No large functions introduced (Cycle 3.1 added 43-line `extract_phase_preambles()`), no deep nesting, no duplicated logic (duplication caught by vet and extracted to conftest).

**Submodule Commit Pattern:**

The implementation file (`prepare-runbook.py`) lives in a submodule (`agent-core`). The submodule shows WIP commits for most implementation cycles, with the expectation that the parent repo commit amends them into clean commits. Cycles 2.5, 3.2, and 4.2 show clean submodule commits (not prefixed WIP), suggesting successful amendment in those REFACTOR phases. The WIP pattern is intentional per the TDD protocol but creates two separate commit histories (parent + submodule) that must be kept in sync.

## Recommendations

### Critical (Address Before Next TDD Session)

1. **Resolve precommit failures before committing — no exceptions**
   - Issue: Cycles 3.1, 3.2, 3.3, and 4.1 committed with `just precommit` reporting a line-limit failure. The cycle report documented the stop condition but the commit proceeded. Deferring resolution across four cycles accumulated technical debt and violated the clean-commit invariant.
   - Impact: Commits with failing precommit are unreliable as a quality gate. The invariant "every commit passes precommit" is the foundation of the checkpoint vet process — if it's violated for four consecutive cycles, the vet's "clean tree" assumption is invalidated.
   - Action: When precommit fails during REFACTOR, the cycle is not complete. Either (a) split the test file immediately as the REFACTOR action, or (b) escalate to orchestrator. Specifically for line-limit violations: the split option was documented in every cycle report from 3.1 onward — it should have been executed in 3.1's REFACTOR, not deferred to 4.2.
   - File/Section: Step files `plans/runbook-generation-fixes/steps/step-3-1.md`, `step-3-2.md`, `step-3-3.md`, `step-4-1.md` — add a STOP directive under the REFACTOR section: "If `just precommit` fails with a line-limit error, split the test file as REFACTOR before committing."

2. **Establish clean working tree before each TDD session**
   - Issue: Cycle 1.1's RED phase was unverifiable because a prior session left uncommitted implementation in the working tree. The agent handled this well (documented the violation, identified the root cause, made an explicit decision), but the violation was avoidable.
   - Impact: A dirty working tree at session start can make RED verification impossible, invalidating the test-first guarantee for that cycle.
   - Action: Before each orchestration session begins, verify `git status` shows a clean tree. If untracked or modified files exist in the implementation target, commit them or stash them with a clear label before executing the first cycle.
   - File/Section: `plans/runbook-generation-fixes/orchestrator-plan.md` — add a pre-execution checkpoint: "Verify clean working tree (`git status`) before Step 1."

### Important (Address Soon)

3. **Anticipate test file growth in runbook planning**
   - Issue: Phase 3 started with `test_prepare_runbook_mixed.py` at 381 lines. Adding `TestPhaseContext` (85+ lines) was predictable to exceed the 400-line limit. The runbook did not include a REFACTOR instruction to split the file when adding the new test class.
   - Impact: Predictable violations cause avoidable stop conditions. Four cycles accumulated precommit failures that a single planned split would have prevented.
   - Action: When a runbook phase adds a significant new test class to an existing test file, include a REFACTOR step: "If `test_prepare_runbook_mixed.py` exceeds 400 lines after adding TestPhaseContext, extract the class to `tests/test_prepare_runbook_phase_context.py`."
   - File/Section: Phase 3 step files — the step for Cycle 3.1's REFACTOR section should have included this conditional split instruction.

4. **Label checkpoint vet commits consistently**
   - Issue: The Phase 3 checkpoint commit is labeled `Fix tautological ordering assertion in Phase 3 test` (5adfd80e) rather than `Phase 3 checkpoint: vet review + [description]`. Phases 1 and 2 checkpoints are labeled `Phase 1 checkpoint: vet review + regex fix` and `Phase 2 checkpoint: vet review + test helper extraction`.
   - Impact: Inconsistent labels make it harder to identify checkpoint commits in git log when reviewing history or resuming orchestration.
   - Action: Standardize checkpoint commit format to `Phase N checkpoint: vet review + [brief fix description]`. Apply consistently across all phase boundaries.
   - File/Section: `plans/runbook-generation-fixes/orchestrator-plan.md` — add commit message format specification for PHASE_BOUNDARY checkpoint commits.

5. **Track regression check scope explicitly**
   - Issue: Cycle reports for 3.1–4.1 report "16/16" regression counts, but the new `test_prepare_runbook_phase_context.py` tests (added in 3.1) are not reflected in this count. The actual suite was growing beyond 16 during this period.
   - Impact: Regression check counts that don't include all test files create a false sense of full coverage. A regression in `test_prepare_runbook_phase_context.py` would not appear in the 16/16 count.
   - Action: Regression check commands in cycle reports should specify the full file list being checked, or use a suite-wide count. Example: "Regression check: 16/16 passed (test_prepare_runbook_mixed.py + test_prepare_runbook_inline.py); test_prepare_runbook_phase_context.py: 2/2 (new)."
   - File/Section: Phase 3 step files — update REFACTOR verification commands to include all test files in scope.

### Minor (Consider for Future)

6. **Clarify GREEN implementation boundaries in step files when adjacent cycles share a guard**
   - Issue: Cycle 3.2's GREEN implementation included `phase_context.strip()` guards that were strictly Cycle 3.3's responsibility per the phase file. The step file for 3.2 instructed "inject `## Phase Context` when non-empty" without explicitly bounding what "non-empty" means. The agent chose the complete interpretation, covering both empty-string and whitespace-only cases.
   - Impact: Over-implementation in one cycle makes the next cycle's RED phase unverifiable (Cycle 3.3's RED passed unexpectedly). While handled correctly by the agent, clearer boundaries prevent the violation.
   - Action: In Cycle 3.2's step file, specify the guard as `if phase_context:` (bare truthiness, not `.strip()`), explicitly leaving the whitespace edge case for Cycle 3.3. This keeps RED verification verifiable for 3.3.
   - File/Section: `plans/runbook-generation-fixes/steps/step-3-2.md` — GREEN implementation guide: specify `if phase_context:` explicitly, not `if phase_context.strip():`.

7. **Use WIP commit label only in submodule, not parent repo**
   - Issue: Cycle 3.1's parent repo commit carries the label `WIP: Cycle 3.1 [extract-phase-preambles]`. All other parent repo commits use clean `Cycle X.Y: [name]` labels. WIP labels belong in submodule commits (as REFACTOR amend targets), not in the parent repo history.
   - Impact: Minor — git log of the parent repo has one anomalous WIP entry at Cycle 3.1.
   - Action: When committing a stop-condition cycle, the parent repo commit should still use the clean `Cycle X.Y: [name]` format even if the WIP work inside the submodule is not yet amended. Reserve WIP label for the submodule layer.
   - File/Section: Commit discipline — document this in orchestrator instructions or REFACTOR phase guidance.

## Process Metrics

- Cycles planned: 13
- Cycles executed: 13
- Compliance rate: 62% full compliance (8/13 cycles with full RED/GREEN/REFACTOR where precommit passed)
- Stop conditions escalated: 4 (Cycles 3.1, 3.2, 3.3, 4.1 — all from same root cause)
- Checkpoint vets: 4 (one per phase); all found genuine issues; all fixes applied before next phase
- Total defects caught by vets: 8 (1 minor Phase 1; 4 Phase 2 [1 major, 3 minor]; 1 minor Phase 3; 2 minor Phase 4)
- Code quality score: Good — minimal implementation, no code smells, clean abstractions
- Test quality score: Good — behavioral test names, specific assertions, diagnostic messages; one tautological assertion caught by vet

## Conclusion

The TDD execution for runbook-generation-fixes demonstrates strong overall discipline: all 13 cycles completed in order, one commit per cycle, no cycles combined or batched, and checkpoint vets applied at every phase boundary with real defects caught and fixed. The primary process failure is the four consecutive precommit failures (Cycles 3.1–4.1) where a predictable test file growth issue was documented but deferred rather than resolved. This single root cause accounts for the compliance rate dropping to 62%. The two RED phase violations were handled appropriately: Cycle 1.1's violation was involuntary and fully documented, and Cycle 3.3's violation was a natural consequence of an over-complete Cycle 3.2 implementation. Checkpoint vets provided genuine value — catching a tautological assertion, stale haiku defaults, and agent frontmatter writing `model: None`. The process is sound; the improvement opportunity is operationalizing precommit-failure resolution as a blocking gate rather than a documented-and-deferred stop condition.
