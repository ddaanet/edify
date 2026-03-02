# Deliverable Review: Test Artifacts

**Reviewer:** Opus
**Date:** 2026-03-02
**Design reference:** `plans/orchestrate-evolution/design.md`

## Summary

12 test files reviewed against the design specification. The test suite provides strong coverage of the core agent caching model (D-2), orchestrator plan format, TDD agent generation (D-5), verification scripts, and inline phase support. Overall quality is high with good test independence and behavioral focus. A few gaps exist in coverage of specific design-specified scenarios.

**Verdict:** 0 Critical, 2 Major, 6 Minor findings.

## Requirement Coverage Matrix

| Requirement | Test Coverage | Files |
|-------------|--------------|-------|
| FR-2 (Post-step remediation) | Not testable at unit level (skill prose) | N/A |
| FR-3 (RCA task generation) | Not testable at unit level (skill prose) | N/A |
| FR-4 (Delegation deduplication) | Covered | agent_caching, agent_context |
| FR-5 (Commit footer) | Covered | agent_caching:204 |
| FR-6 (Scope footer) | Partially covered | agent_caching:201 |
| FR-7 (Precommit verification) | Covered | verify_step |
| FR-8 (TDD orchestration) | Covered | tdd_agents, orchestrator |
| FR-8a (RED gate) | Covered | verify_red |
| FR-8b (GREEN gate) | Not unit-testable (composes just test + verify-step) | N/A |
| FR-8c (Role-specific correctors) | Covered | tdd_agents |
| FR-8d (Agent resume) | Not unit-testable (runtime behavior) | N/A |
| NFR-1 (Context bloat) | Indirectly covered (file references) | orchestrator |
| NFR-2 (Backward compat) | Not unit-testable (clean break policy) | N/A |
| NFR-3 (Sonnet orchestrator) | Not unit-testable (skill prose) | N/A |

## Findings

### F-1: No test for `split_cycle_content` helper directly

- **File:** `tests/test_prepare_runbook_tdd_agents.py`
- **Axis:** Coverage
- **Severity:** Minor
- **Description:** The design specifies `split_cycle_content` as a helper that splits TDD cycles on `**GREEN Phase:**` marker into test/impl step files (D-5, Step File Separation). The function exists in `prepare-runbook.py:1363` but has no direct unit test. Its behavior is tested indirectly through `test_tdd_cycle_splits_into_test_and_impl_files` (line 258), which validates the end-to-end split. The indirect coverage is adequate for the simple splitting logic, but a direct unit test would catch regressions in edge cases (e.g., missing GREEN marker, extra GREEN markers).

### F-2: Missing test for TDD corrector agents' model field

- **File:** `tests/test_prepare_runbook_tdd_agents.py`
- **Axis:** Coverage
- **Severity:** Major
- **Description:** The design specifies (D-5, Agent Roles): "Model for corrector agent: Always sonnet." The test suite verifies that `<plan>-test-corrector.md` and `<plan>-impl-corrector.md` use the corrector baseline (lines 163-182), but never asserts that their frontmatter contains `model: sonnet`. The general corrector test in `agent_caching.py:347` (`assert "model: sonnet" in content`) covers the `<plan>-corrector.md` case, but the TDD corrector agents (`test-corrector`, `impl-corrector`) lack this assertion. If the generation logic used the runbook model instead of hardcoded sonnet, no test would catch it.

### F-3: Missing test for TDD agents' scope/commit footers

- **File:** `tests/test_prepare_runbook_tdd_agents.py`
- **Axis:** Coverage, Conformance
- **Severity:** Major
- **Description:** The design specifies (D-2) that task agents include scope enforcement and clean tree requirement footers. `test_prepare_runbook_agent_caching.py` verifies these for `{name}-task.md` (lines 201-205), but `test_prepare_runbook_tdd_agents.py` never verifies that `{name}-tester.md` or `{name}-implementer.md` contain equivalent footers. The design states these four TDD agents are generated with the "same pattern as D-2 `<plan>-task.md` generation," implying footers should be present. The corrector-typed agents (`test-corrector`, `impl-corrector`) have a different scope footer per the design. Neither variant is tested for TDD agents.

### F-4: `test_verify_step.py` does not test submodule pointer check

- **File:** `tests/test_verify_step.py`
- **Axis:** Coverage
- **Severity:** Minor
- **Description:** The design specifies three checks in `verify-step.sh`: git status, submodule pointer consistency, and precommit. The test file covers clean state (line 80) and dirty states for uncommitted/untracked files (line 106), but does not test the submodule pointer check path. The script does implement it (`verify-step.sh:14-18`). Testing submodule scenarios requires setting up a submodule in the temp repo, which is more complex but feasible.

### F-5: `test_verify_step.py` does not test precommit failure path

- **File:** `tests/test_verify_step.py`
- **Axis:** Coverage
- **Severity:** Minor
- **Description:** The design specifies `just precommit` as one of three verification checks. The test creates a `justfile` with `@echo 'ok'` (always passing). There is no test for the case where `just precommit` fails. Adding a test with a justfile recipe that exits non-zero would cover this path.

### F-6: `test_verify_red.py` missing test for no-argument invocation

- **File:** `tests/test_verify_red.py`
- **Axis:** Coverage
- **Severity:** Minor
- **Description:** The `verify-red.sh` script validates that exactly one argument is provided (lines 5-8). The test covers: failing test (exit 0), passing test (exit 1), and missing file (exit 1), but does not test the zero-arguments case. This is a minor robustness gap since the script does handle it.

### F-7: Orchestrator plan `**Agent:**` field for pure-TDD runbooks

- **File:** `tests/test_prepare_runbook_orchestrator.py:234`
- **Axis:** Conformance
- **Severity:** Minor
- **Description:** The test asserts `**Agent:** none` for pure-TDD runbooks (line 234). The design (D-2, Orchestrator Plan Format) specifies `**Agent:** <runbook-name>-task` as the header format. For TDD runbooks where dispatch goes to tester/implementer instead of a task agent, the "none" value is a reasonable implementation choice, but the design's orchestrator plan example shows `**Agent:** <runbook-name>-task`. The test matches the implementation, which is defensible since TDD dispatch uses role-specific agents. This is a design-implementation deviation, not a test error.

### F-8: Weak assertion in `test_tester_contains_test_quality_directive`

- **File:** `tests/test_prepare_runbook_tdd_agents.py:211`
- **Axis:** Specificity
- **Severity:** Minor
- **Description:** The assertion `assert "test quality" in tester_content.lower()` is case-insensitive and matches any occurrence of "test quality" as a substring. This could match incidentally in baseline content or plan context. A more specific assertion against the actual directive text would be stronger. Compare with `test_implementer_contains_implementation_directive` (line 222) which checks for `"Role: Implementer"` -- a more specific marker.

## Tests Not Requiring Findings

The following aspects were reviewed and found satisfactory:

- **Test independence:** All tests use `tmp_path` fixtures and `monkeypatch.chdir()`. No shared mutable state between tests. Module-level constants are all immutable strings/dicts.
- **Vacuity:** All tests assert specific behavioral outcomes, not just "no exception raised." The pattern of checking both positive (file exists, content contains X) and negative (old format not present, wrong content absent) is consistent.
- **Excess:** No test files contain dead code or tests for functionality outside the design scope.
- **Conformance of step file splitting:** `test_tdd_cycle_splits_into_test_and_impl_files` (tdd_agents:258) verifies RED content in test file, GREEN content in impl file, absence of cross-contamination, and metadata headers in both -- thorough coverage.
- **Orchestrator plan format:** Pipe-delimited entries, PHASE_BOUNDARY markers, inline phase format, Phase Summaries, max_turns extraction and propagation -- all well tested.
- **Agent context embedding:** Design, outline, and Common Context embedding tested with priority chain (runbook section > outline.md > fallback) and fallback notes.
- **Corrector agent lifecycle:** Multi-phase generates corrector, single-phase skips corrector -- both tested.
- **Recall artifact integration:** Comprehensive e2e tests with mock subprocess, covering shared entries, phase-tagged partitioning, error cases (nonexistent phase, inline phase), and injection into generated agents and step files.

## Conclusion

The test suite provides solid coverage of the prepare-runbook.py changes and verification scripts. The two Major findings (F-2, F-3) represent gaps where TDD-specific agents lack assertions for design-mandated properties (model field, scope/commit footers) that are tested for the general task agent. The Minor findings are robustness improvements and edge case coverage. No Critical issues found.
