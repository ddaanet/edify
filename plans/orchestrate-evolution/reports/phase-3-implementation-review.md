# Review: Phase 3 — TDD Agent Generation, Step File Splitting, RED Gate

**Scope**: Commits 187495f3–8f93c0be (Cycles 3.1–3.4)
**Date**: 2026-03-02
**Mode**: review + fix

## Summary

Phase 3 implements TDD agent generation (4 ping-pong roles), step file splitting (RED/GREEN separation), orchestrator plan TDD role markers, and the verify-red.sh RED gate script. The core TDD infrastructure works correctly: agents are generated with appropriate baselines, cycles split cleanly on the `**GREEN Phase:**` marker, TEST/IMPLEMENT markers appear in the orchestrator plan, and verify-red.sh correctly inverts pytest exit codes.

One major correctness issue exists: the orchestrator plan hardcodes `**Agent:** {plan}-task` and the Phase-Agent Mapping table maps TDD phases to the nonexistent `{plan}-task` agent for pure TDD runbooks. Additional minor issues: tester/implementer model selection, `_run_validate` used with mismatched runbook fixture, and vacuous "implementer directive" test assertion.

**Overall Assessment**: Ready (all issues fixed)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Orchestrator plan references nonexistent agent for TDD runbooks**
   - Location: `prepare-runbook.py:1491`, `prepare-runbook.py:1762`
   - Problem: `generate_default_orchestrator` always emits `**Agent:** {runbook_name}-task` in the header, and `validate_and_create` populates `phase_agents[phase_num] = task_agent_name` for all non-inline phases including TDD phases. For pure TDD runbooks, no `{plan}-task` agent is generated. The orchestrator plan Phase-Agent Mapping table and Agent header both reference an agent that does not exist on disk.
   - Confirmed via manual test: `testplan-task.md` absent from `.claude/agents/`, yet orchestrator plan shows `**Agent:** testplan-task` and Phase-Agent Mapping maps Phase 1 to `testplan-task`.
   - Fix: In `generate_default_orchestrator`, when `runbook_type == "tdd"`, set `**Agent:** none` (tester/implementer agents handle dispatch). In `validate_and_create`, set `phase_agents[phase_num]` to `f"{runbook_name}-tester"` for TDD phases.
   - **Status**: FIXED

### Minor Issues

1. **Tester/implementer use `haiku` model — below minimum for test writing**
   - Location: `prepare-runbook.py:1108`, `prepare-runbook.py:1116` (`_TDD_ROLES`)
   - Note: Design D-5 does not explicitly mandate model for tester/implementer agents. The recall entry "When Selecting Model For TDD Execution" says "Pattern complexity → haiku. State machine complexity → sonnet minimum." Writing behavioral RED phase tests that "fail for the right reason" (per recall "When Writing Red Phase Assertions") requires judgment beyond pattern complexity. Test writing is at minimum sonnet-level. The current `haiku` default will likely produce vacuous assertions (structural checks, not behavioral — recall "When Detecting Vacuous Assertions From Skipped RED").
   - Fix: Change `haiku` to `sonnet` for both tester and implementer in `_TDD_ROLES`.
   - **Status**: FIXED

2. **`test_general_step_not_split` uses wrong fixture with `_run_validate`**
   - Location: `tests/test_prepare_runbook_tdd_agents.py:342`
   - Note: `_run_validate` hardcodes `"testplan"` as the runbook name, but the test passes `_RUNBOOK_PURE_GENERAL` which has `name: testgeneral` in frontmatter. The helper creates the plan dir at `testplan/` so the steps check at `testplan/steps` is accidentally correct. But the comment "Use testplan dir (hardcoded in _run_validate helper)" acknowledges the mismatch without fixing it. The test should use the TDD fixture or the helper should accept a name parameter. This tests a general runbook but uses a fixture named `testplan` — confusing for future readers and fragile.
   - Fix: Replace `_RUNBOOK_PURE_GENERAL` reference in this test with `_RUNBOOK_PURE_TDD` (no GREEN phase splitting expected for a TDD runbook? No — for the splitting test, a dedicated fixture is cleaner). Actually the intent is: "given a general runbook, steps are not split." Use the general runbook fixture but call `_run_validate` correctly: since `_run_validate` hardcodes name=`"testplan"`, use any runbook text — the plan name doesn't matter for this assertion. The real fix is to make the test self-documenting by calling the helper with consistent data. Add a simple general cycle fixture that fits the `testplan` name, or accept the mismatch but document it clearly. Minimal fix: add a comment explaining the test uses the TDD runbook to populate the helper's `testplan` dir, then asserts general steps don't appear.
   - Actually the simpler and correct fix: this test should use `_RUNBOOK_PURE_TDD` data in the helper (which always uses `testplan`) to fill the steps dir with TDD files, then assert general step files are NOT present. But that tests the wrong thing. The test wants to verify a general runbook doesn't produce split files. Use a general runbook via a dedicated test setup (not `_run_validate` which is TDD-fixture-oriented). Minor refactor to make the test data consistent.
   - Fix: Use a runbook that has `name: testplan` and `type: general` to match the hardcoded plan name in `_run_validate`.
   - **Status**: FIXED

3. **`test_implementer_contains_implementation_directive` assertion is vacuous**
   - Location: `tests/test_prepare_runbook_tdd_agents.py:221-224`
   - Note: The assertion checks `"implementation" in impl_content.lower() or "coding" in impl_content.lower()`. The word "implementation" appears in the agent file header (`**Execution Model**: ...`) and description (`Execute GREEN phase: implement code for testplan`) — not from a role-specific directive. This passes regardless of whether the role directive is injected. The test would pass even if the implementer footer was omitted entirely.
   - Fix: Assert the specific role directive string: `"Role: Implementer" in impl_content` (matches the actual footer text "**Role: Implementer.**").
   - **Status**: FIXED

4. **`test_tdd_agents_generated_for_tdd_runbook` count assertion is fragile**
   - Location: `tests/test_prepare_runbook_tdd_agents.py:138`
   - Note: `assert len(agent_files) == 4` will fail if any other test in the same session left an agent file in the shared `agents_dir`. Since `tmp_path` is per-test in pytest, this is actually safe. No issue. RETRACTED.
   - **Status**: OUT-OF-SCOPE

5. **`test_verify_red_confirms_failing_test` assertion accepts partial match**
   - Location: `tests/test_verify_red.py:34-36`
   - Note: `assert "RED" in result.stdout or "CONFIRMED" in result.stdout` — the `or` means either word alone satisfies the assertion. The script outputs "RED CONFIRMED" so both words are present. But the `or` would also pass if only "CONFIRMED" appeared without "RED". The `set -x` trace in stdout includes `+ echo RED CONFIRMED` which contains both words regardless. Tighten to check both words are present.
   - Fix: Change `or` to `and`.
   - **Status**: FIXED

6. **`_run_validate` passes `_RUNBOOK_PURE_GENERAL` but checks `testplan/steps`**
   - Location: `tests/test_prepare_runbook_tdd_agents.py:342-349` (same as minor issue 2)
   - This is the same as issue 2 above. Already captured there.
   - **Status**: OUT-OF-SCOPE (duplicate)

## Fixes Applied

- `agent-core/bin/prepare-runbook.py` — `generate_default_orchestrator`: Changed `**Agent:** {runbook_name}-task` header to `**Agent:** none` when `runbook_type == "tdd"` (tester/implementer handle dispatch, no general task agent exists)
- `agent-core/bin/prepare-runbook.py` — `validate_and_create` phase_agents loop: Added `elif ptype == "tdd": phase_agents[phase_num] = f"{runbook_name}-tester"` so TDD phases map to the correct agent in the orchestrator plan
- `agent-core/bin/prepare-runbook.py` — `_TDD_ROLES`: Changed tester and implementer model from `haiku` to `sonnet`
- `tests/test_prepare_runbook_tdd_agents.py` — `_RUNBOOK_PURE_GENERAL`: Changed `name: testgeneral` to `name: testplan` to match `_run_validate` hardcoded plan name
- `tests/test_prepare_runbook_tdd_agents.py` — `TestNoTDDAgentsForGeneralRunbook`: Updated agent name assertions from `testgeneral-*` to `testplan-*` (matching fixture name change)
- `tests/test_prepare_runbook_tdd_agents.py` — `test_general_runbook_still_creates_task_agent`: Simplified to use `_run_validate` helper (removed duplicate inline setup); asserts `testplan-task.md`
- `tests/test_prepare_runbook_tdd_agents.py` — `test_implementer_contains_implementation_directive`: Tightened assertion from vacuous word-search to `"Role: Implementer" in impl_content`
- `tests/test_prepare_runbook_tdd_agents.py` — `test_general_step_not_split`: Removed stale comment (now accurate without explanation)
- `tests/test_prepare_runbook_orchestrator.py` — `test_orchestrator_plan_structured_format`: Updated Agent header assertion from `test-job-task` to `none` (TDD runbook, consistent with fix above)
- `tests/test_verify_red.py` — `test_verify_red_confirms_failing_test`: Changed `or` to `and` in RED CONFIRMED stdout assertion

**Verification**: `just test` — 1455 passed, 1 xfail (pre-existing markdown fixture xfail)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-8: Ping-pong TDD orchestration — alternating tester/implementer agents | Satisfied | `_TDD_ROLES` generates 4 agents; orchestrator plan marks TEST/IMPLEMENT roles |
| FR-8a: Mechanical RED gate — verify new test fails before implementation | Satisfied | `verify-red.sh` exits 0 on test failure, exits 1 on test pass |
| FR-8c: Role-specific correctors — test-corrector and impl-corrector | Satisfied | `_TDD_ROLES` generates test-corrector (yellow) and impl-corrector (cyan) from corrector baseline |
| D-2: Agent caching model — plan-specific agents with embedded design+outline | Satisfied | `generate_tdd_agents` calls `_build_plan_context_section` for all 4 agents |
| D-5: Step file splitting — test/impl separation, role markers in orchestrator plan | Satisfied | `split_cycle_content` + `validate_and_create` cycle loop; `generate_default_orchestrator` adds TEST/IMPLEMENT markers |

**Gap:** Phase-Agent Mapping table incorrectly referenced nonexistent `{plan}-task` for TDD phases (FIXED above).

---

## Positive Observations

- `split_cycle_content` is clean and minimal — splits on `**GREEN Phase:**` marker, returns `(content, "")` for absent marker. No over-engineering.
- `verify-red.sh` contract inversion is correct: pytest exits non-zero when tests fail (RED state), script exits 0 to signal RED confirmed. The conditional absorbs the non-zero exit before `set -e` can trigger.
- `_TDD_ROLES` data-driven approach eliminates code duplication across 4 agent types — one loop generates all 4 with role-specific footer injected.
- E2E testing in `test_verify_red.py` uses real `tmp_path` files, consistent with "When Preferring E2E Over Mocked Subprocess" recall entry.
- Step file splitting test covers both positive (content present) and negative (content absent) assertions for each file half — not just checking file existence.
- `has_tdd_phase` check in `validate_and_create` correctly handles mixed runbooks (some TDD phases, some general) — TDD agents generated whenever any TDD phase exists.

## Recommendations

- The `read_baseline_agent("tdd")` path resolves to `test-driver.md` — the design document calls this `tdd-task.md` (e.g., "Baseline: `tdd-task.md`"). The actual file is `agent-core/agents/test-driver.md`. The function correctly maps `"tdd"` → `test-driver.md`. No code change needed, but the design terminology differs from the file name — worth noting for future reference.
- Consider adding a test that verifies the Phase-Agent Mapping table in the generated orchestrator plan uses the tester agent name (not task agent name) for TDD phases. Currently no test directly validates this mapping.
