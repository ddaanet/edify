# TDD Process Review: phase-scoped-agents

**Date:** 2026-02-23
**Runbook:** plans/phase-scoped-agents/runbook.md
**Commits Analyzed:** 05fe807a (prepared artifacts) .. 129b2596 (Phase 3 complete)

## Executive Summary

The phase-scoped-agents TDD execution achieved full RED/GREEN sequencing discipline across all 7 planned cycles and the inline Phase 3. Execution order matched the plan exactly and all cycles produced GREEN results. Three minor compliance issues were identified: (1) out-of-scope validation reports committed in Cycle 1.4, (2) the REFACTOR commit pattern used separate WIP commits rather than amend-in-place as expected by the process, and (3) the Cycle 2.2 preamble assertion from the runbook spec was documented as "may be empty" rather than verified. Code quality is high with clear test structure and minimal implementations.

## Plan vs Execution

| Cycle | Planned | Executed | Status | Issues |
|-------|---------|----------|--------|--------|
| 1.1 | Yes | Yes (494fa0fb) | OK | None |
| 1.2 | Yes | Yes (64f8875a) | OK | None |
| 1.3 | Yes | Yes (d869ddbc) | OK | None |
| 1.4 | Yes | Yes (cb474eff) | OK | Minor: out-of-scope validation reports committed |
| 2.1 | Yes | Yes (642f1191) | OK | None |
| 2.2 | Yes | Yes (1e30c701) | OK | Minor: preamble assertions weakened vs spec |
| 2.3 | Yes | Yes (d8e08ba3) | OK | None |
| Phase 3 (inline) | Yes | Yes (129b2596) | OK | None |

**Summary:**
- Planned cycles: 7 TDD cycles + 1 inline phase
- Executed cycles: 7 TDD cycles + 1 inline phase
- Skipped: 0
- Combined: 0
- Out-of-order: 0
- Extra: 0

## Scope Compliance

| Agent | Assigned | Actually Executed | Scope Violation |
|-------|----------|-------------------|-----------------|
| Cycle 1.1 | Cycle 1.1 only | Cycle 1.1 only | None |
| Cycle 1.2 | Cycle 1.2 only | Cycle 1.2 only | None |
| Cycle 1.3 | Cycle 1.3 only | Cycle 1.3 only | None |
| Cycle 1.4 | Cycle 1.4 only | Cycle 1.4 + committed out-of-scope validation reports | Minor: committed untracked files from plans/runbook/reports/ |
| Cycle 2.1 | Cycle 2.1 only | Cycle 2.1 only | None |
| Cycle 2.2 | Cycle 2.2 only | Cycle 2.2 only | None |
| Cycle 2.3 | Cycle 2.3 only | Cycle 2.3 only | None |
| Phase 3 | Inline prose edit | Inline prose edit (submodule update) | None |

**Cycle 1.4 scope detail:** The Cycle 1.4 commit (cb474eff) included four validation reports under `plans/runbook/reports/` (`validation-lifecycle.md`, `validation-model-tags.md`, `validation-red-plausibility.md`, `validation-test-counts.md`). These were pre-execution validation artifacts generated for `plans/phase-scoped-agents/runbook.md` but stored in a sibling plan's report directory (`plans/runbook/reports/`). The files had timestamps of 15:19, over an hour before the Cycle 1.4 commit at 16:38 — they were leftover untracked files the agent committed as a cleanup side-effect. These are not part of Cycle 1.4 scope and should not have been committed by the step agent. This is minor (no data loss, no wrong model tier) — the orchestrator retained dispatch control throughout.

**Phase 3 step file bleed:** The step file `plans/phase-scoped-agents/steps/step-2-3.md` contains the Phase 3 inline content appended after Cycle 2.3. This is the known `extract_sections()` bug fixed by the fenced-blocks session (eb804b commit). However, the Cycle 2.3 agent did NOT execute Phase 3 work — Phase 3 was committed separately as 129b2596. This confirms the bug was present in the step file but did not cause a scope violation in this execution, possibly because Phase 3 was executed directly by the orchestrator (or the orchestrator intercepted correctly).

## TDD Compliance Assessment

| Cycle | RED | GREEN | REFACTOR | Regressions | Issues |
|-------|-----|-------|----------|-------------|--------|
| 1.1 | OK | OK | None needed | 36/36 pass | None |
| 1.2 | OK | OK | Redundant import removed | 39/39 pass | None |
| 1.3 | OK | OK | Lint fixes (D205, E501, ANN001, ANN401) | 1190/1191 pass (1 xfail) | Regression count inconsistency (see below) |
| 1.4 | OK | OK | Line-too-long fix | 41/41 pass | Out-of-scope files committed |
| 2.1 | OK | OK | Docstring wrap-summaries fixes | 43/43 pass | None |
| 2.2 | OK | OK | Docstring wrap-summaries fixes | 1195/1196 pass (1 xfail) | Preamble assertion weakened |
| 2.3 | OK (implicit REGRESSION) | OK | None (precommit clean) | 1195/1196 pass | None |
| Phase 3 | N/A (inline) | N/A | N/A | N/A | None |

**Summary:**
- Full compliance: 6 of 7 cycles (Cycle 1.4 and 2.2 have minor issues)
- Partial compliance: 1 cycle (Cycle 1.4: out-of-scope commit)
- Violations: 0

**RED phase detail:**
All cycles demonstrated correct RED phase execution. Failure messages matched expected types precisely:
- Cycle 1.1: `TypeError: generate_agent_frontmatter() got an unexpected keyword argument 'phase_num'`
- Cycle 1.2: `AttributeError: module 'prepare_runbook' has no attribute 'get_phase_baseline_type'`
- Cycle 1.3: `AttributeError: module 'prepare_runbook' has no attribute 'generate_phase_agent'`
- Cycle 1.4: `AttributeError: module 'prepare_runbook' has no attribute 'detect_phase_types'`
- Cycle 2.1: `TypeError: unexpected keyword argument 'phase_agents'`
- Cycle 2.2: `TypeError: validate_and_create() got an unexpected keyword argument 'agents_dir'`
- Cycle 2.3: REGRESSION — RED is implicit per runbook design; existing tests fail as expected

**REFACTOR WIP/amend pattern:** The agent-core submodule contains WIP commits (`WIP: Cycle 1.1`, `WIP: Cycle 1.2`, etc.) that appear as distinct commits in the submodule history rather than being amended into the cycle commit. The runbook process expects "create WIP commit, then amend to final." Instead, WIP commits remain in history as separate entries. This is an audit trail discrepancy (WIP commits are not clean cycle commits) but did not affect correctness — the parent repo's cycle commits correctly point to submodule commits that include all changes.

## Planning Issues

**Regression count inconsistency in Cycle 1.3:** The test count jumped from 39/39 (Cycle 1.2) to 1190/1191 (Cycle 1.3). This indicates the regression scope changed — Cycle 1.3 ran the full test suite rather than just `test_prepare_runbook_*.py`. Cycle 1.4 then reverted to 41/41 (matching the specific module scope). No impact on quality but suggests inconsistent regression verification scope between cycles. The runbook specifies `pytest tests/test_prepare_runbook_*.py -v` for all regression checks.

**Preamble assertion gap in Cycle 2.2:** The runbook specifies:
> Assert: Phase 1 agent contains Phase 1 preamble; Phase 2 agent contains Phase 2 preamble

The execution report notes: "Preambles may be empty for these test runbooks (no preamble text)." The comment in the test file at line 307 reads `# Preambles may be empty for these test runbooks (no preamble text)`. The assertion was not written. The test runbooks (`_RUNBOOK_2PHASE`, `_RUNBOOK_3PHASE_INLINE`) lack preamble text between the Phase header and first step/cycle header, making this assertion impossible with those fixtures. The agent correctly diagnosed the gap but documented it as a comment rather than either (a) adding preamble text to the fixture or (b) escalating as a spec gap. Result: the preamble injection path is untested.

**inline_phases parameter:** The Cycle 2.1 test uses `inline_phases={2: "inline content"}` as an additional parameter to `generate_default_orchestrator()`, which is not in the runbook spec. This was a test-driven design decision — the function needs to know inline phase content to include it in the mapping table. The agent extended the spec appropriately and the extension is sound.

**Model column not asserted:** The runbook GREEN phase specifies the mapping table has columns "Phase, Agent, Model, Type" but the test only asserts Phase, Agent, Type values. No assertion verifies the Model column exists or contains correct values. The runbook RED phase spec also omits Model column assertions from the test assertions list — this is a planning gap in the runbook itself, not an agent deviation.

## Execution Issues

**Batch Operations:** None. All cycles were implemented individually with one commit per cycle.

**Verification Skips:** None detected. All execution reports document both RED and GREEN verification commands and results.

**Discipline Violations:** None. Test-before-implementation ordering confirmed by error messages that match pre-implementation state.

**Out-of-scope commit in Cycle 1.4:** Four validation report files from `plans/runbook/reports/` (generated at 15:19, over 60 minutes before the 16:38 commit) were included in the Cycle 1.4 commit. These were leftover untracked files from pre-execution runbook validation, stored in the wrong directory (`plans/runbook/reports/` rather than `plans/phase-scoped-agents/reports/`). The agent cleaned them up by committing rather than deleting. These files do not belong in source control (they are ephemeral validation artifacts) and were misplaced in a sibling plan's report directory.

## Code Quality Assessment

### Test Quality

**Strengths:**
- Test class names clearly describe behavior: `TestAgentNamingConvention`, `TestPhaseBaselineType`, `TestGeneratePhaseAgent`, `TestOrchestratorAgentField`, `TestValidateCreatesPerPhaseAgents`
- Docstrings on all test methods describing the specific behavior being tested
- Layer ordering assertion in `test_generate_phase_agent_layers` is exemplary — verifies structural composition via index comparison rather than regex, making failures informative
- Negative assertions present: `assert "-p1" not in result` (single-phase naming), `assert "using testjob-task agent" not in result` (old naming gone), `assert not (agents_dir / "testmixed-task.md").exists()` (old file absent), `assert not (agents_dir / "crew-testinline-p2.md").exists()` (inline phase produces no agent)
- Fixture design decision documented in Cycle 1.3 report: test creates fake baseline files with "Test Driver" literal because actual `test-driver.md` doesn't contain that exact string — this is correct and transparent

**Issues:**
- `test_validate_creates_per_phase_agents` has weak preamble coverage: preamble injection is a named requirement (FR-1 context layering) but the test fixture lacks preamble text, leaving the preamble injection path exercised only by `test_generate_phase_agent_layers` (which uses direct function call, not the integration path)
- `test_orchestrator_phase_agent_mapping_table` does not assert the Model column exists despite the runbook and GREEN phase implementation specifying it
- Test file grows to 353 lines — approaching the 400-line limit noted in runbook constraints. If additional coverage is added (Model column, preamble path), will require early split

**Test count: 353 lines for 11 tests** = 32 lines/test average. Acceptable given the integration test fixtures embedded in the file (`_RUNBOOK_2PHASE`, `_RUNBOOK_3PHASE_INLINE` at ~40 lines each).

### Implementation Quality

**Strengths:**
- Minimal implementations: Cycle 1.1 added 10 lines (+2 params, updated format string), Cycle 1.2 added 12 lines (new function), Cycle 1.3 added 20 lines (new function), Cycle 1.4 added 38 lines (new function with phase parsing), Cycle 2.1 added 32 lines (+params + table + Agent: emission), Cycle 2.2 added 86 lines (+26 deletions) — appropriate given it replaced the entire agent creation subsystem
- GREEN phase implementations were surgical: no over-implementation detected
- Cycle 2.3 correctly identified that `test_prepare_runbook_inline.py` needed no changes (uses `derive_paths()` which was already updated to return a directory) — agent did not blindly apply the runbook's change template

**Cycle 2.2 scope was large but justified:** The 86+26 change is the core feature integration — replacing single-agent creation with per-phase loop. The runbook correctly specified this cycle as the largest. Minimal GREEN discipline was maintained.

### Code Smells

- `detect_phase_types()` at 38 lines is the largest new function — acceptable for the parsing complexity
- No duplication observed across the new functions

## Recommendations

### Important (Address Soon)

1. **Add preamble integration test coverage**
   - **Issue:** The preamble injection path through `validate_and_create()` is not tested. The `_RUNBOOK_2PHASE` and `_RUNBOOK_3PHASE_INLINE` fixtures have no preamble text between phase headers and step/cycle headers.
   - **Impact:** FR-1 (context layering) is only partially validated. A regression in preamble extraction or injection would not be caught by the integration tests.
   - **Action:** Add preamble text to `_RUNBOOK_2PHASE` fixture (e.g., text between `### Phase 1:` header and `## Cycle 1.1:`) and add assertions `assert "Phase 1 preamble" in p1_content` and `assert "Phase 1 preamble" not in p2_content` to verify isolation.
   - **File:** `tests/test_prepare_runbook_agents.py`, `_RUNBOOK_2PHASE` fixture starting at line ~155, `test_validate_creates_per_phase_agents` test

2. **Add Model column assertion to Phase-Agent Mapping table test**
   - **Issue:** `test_orchestrator_phase_agent_mapping_table` does not assert the Model column exists despite the GREEN phase implementation specifying columns: Phase, Agent, Model, Type.
   - **Impact:** The Model column could be silently dropped in a refactor without any test catching it.
   - **Action:** Add assertions for model values in mapping table rows. Requires passing model info through `phase_models` to `generate_default_orchestrator()`.
   - **File:** `tests/test_prepare_runbook_agents.py`, `test_orchestrator_phase_agent_mapping_table`

3. **Delete out-of-scope validation reports from plans/runbook/reports/**
   - **Issue:** Four validation reports (`validation-lifecycle.md`, `validation-model-tags.md`, `validation-red-plausibility.md`, `validation-test-counts.md`) in `plans/runbook/reports/` are ephemeral pre-execution artifacts committed by the Cycle 1.4 agent as a cleanup side effect. They belong to `plans/phase-scoped-agents/` not `plans/runbook/`.
   - **Impact:** Pollutes `plans/runbook/` with artifacts from an unrelated plan. Creates confusion about which plan's validation results are present.
   - **Action:** `git rm plans/runbook/reports/validation-lifecycle.md plans/runbook/reports/validation-model-tags.md plans/runbook/reports/validation-red-plausibility.md plans/runbook/reports/validation-test-counts.md`
   - **File:** `plans/runbook/reports/` (all 4 files)

### Minor (Consider for Future)

4. **Standardize regression verification scope in step files**
   - **Issue:** Cycle 1.3 ran the full test suite (1190 tests) while other cycles ran only `test_prepare_runbook_*.py` (39-43 tests). The runbook specifies `pytest tests/test_prepare_runbook_*.py -v` for regressions, but Cycle 1.3 deviated.
   - **Impact:** Inconsistent scope makes regression counts in reports incomparable. No compliance risk since broader scope is strictly safer.
   - **Action:** Runbook step files should explicitly specify the regression command. Current step files inherit from runbook Common Context but agents may override to full suite.
   - **File:** `plans/phase-scoped-agents/steps/step-*.md` REFACTOR section regression command

5. **WIP commit naming in submodule**
   - **Issue:** The agent-core submodule has 6 commits named `WIP: Cycle X.Y [...]` as distinct entries in linear history. The expected REFACTOR pattern is "create WIP commit, REFACTOR, then amend to final." The WIP commits were not amended — they remain as permanent history entries.
   - **Impact:** Submodule history is messier than intended but functionally correct. The parent repo cycle commits correctly reference submodule state after all changes.
   - **Action:** For future cycles, step files should explicitly state: "After GREEN passes, run precommit. If lint fixes needed, amend the WIP commit before creating the parent-repo cycle commit." Alternatively, accept that multiple WIP commits in the submodule are acceptable given parent-repo cycles are clean.
   - **File:** Runbook template or Common Context REFACTOR guidance section

## Process Metrics

- Cycles planned: 7 TDD cycles + 1 inline phase
- Cycles executed: 7 TDD cycles + 1 inline phase
- Compliance rate: 86% (6 of 7 cycles with full scope compliance; all 7 with correct RED/GREEN sequencing)
- RED/GREEN sequencing: 100% (all cycles test-first)
- Code quality score: Good
- Test quality score: Good (negative assertions, layer ordering verification, fixture design documented; preamble gap and Model column omission noted)

## Conclusion

The phase-scoped-agents TDD execution demonstrated strong discipline: all 7 cycles followed test-first ordering, RED failures matched expected messages, GREEN implementations were minimal, and REFACTOR runs addressed lint findings cycle-by-cycle. No cycles were skipped, combined, or executed out of order. The inline Phase 3 was correctly handled as orchestrator-direct.

Two substantive issues warrant follow-up: the untested preamble injection path (FR-1 partial validation) and the out-of-scope validation reports committed in Cycle 1.4. The remaining observations are minor process consistency items. The implementation is correct and the test suite provides solid foundation coverage for the new per-phase agent generation system.
