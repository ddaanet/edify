# Deliverable Review: Workwoods Test Deliverables

**Scope**: Test files for Phases 1-6 of the workwoods plan
**Date**: 2026-02-17
**Design reference**: `plans/workwoods/design.md`
**Review type**: Deliverable review (conformance, specificity, coverage, independence)

## Summary

The test suite covers the core behavioral contracts across all six phases. Tests generally verify behavior rather than implementation, use real git repos where appropriate, and avoid vacuous assertions. There are specific coverage gaps around design-specified edge cases (outline.md/problem.md status mapping, gate priority logic, VetStatus.any_stale property) and some tests that couple to internal structure rather than public API.

**Overall Assessment**: Needs Minor Changes

## Review Axes

### Conformance

Tests align with design specification for the primary behavioral contracts. Key conformance gaps:

**Phase 1 — State Inference:**
- Design specifies `outline.md` without `design.md` maps to `requirements` status (not `designed`). No test covers this scenario. The implementation in `_determine_status()` correctly handles it (outline.md is not checked — only `design.md` triggers `designed`), but the design explicitly calls out this refinement as a test-worthy edge case.
- Design specifies `problem.md` only maps to `requirements` status. No test for `problem.md` as sole artifact.
- Design specifies gate priority order: "design > runbook > phase-level". Implementation only handles `design.md` stale gate (line 89-90 of inference.py: only checks `chain.source == "design.md"` then breaks). Tests only verify design gate — but the implementation itself is incomplete (only produces one gate type), so tests correctly reflect implementation, not spec.

**Phase 2 — Vet Staleness:**
- `VetStatus.any_stale` property (models.py:24) has zero test coverage. Design specifies it as a "convenience" property. No test exercises it despite being part of the public API.
- Design specifies `plan_name` field on VetStatus. Implementation dropped it (models.py:18 — VetStatus has only `chains`). Tests don't verify plan_name because it doesn't exist. This is a design-implementation drift, not a test gap.

**Phase 3 — Aggregation:**
- Design specifies `TreeStatus` dataclass with fields: `path`, `slug`, `branch`, `is_main`, `commits_since_handoff`, `latest_commit_subject`, `latest_commit_timestamp`, `is_dirty`, `task_summary`. Implementation uses `TreeInfo` NamedTuple with reduced fields: `path`, `branch`, `is_main`, `slug`, `latest_commit_timestamp`. Missing from implementation: `commits_since_handoff`, `latest_commit_subject`, `is_dirty`, `task_summary`. These fields exist as standalone functions but are not aggregated into the tree object. Tests correctly test the standalone functions, but design conformance is incomplete.
- `AggregatedStatus` design specifies `vet_statuses: list[VetStatus]` field. Implementation has only `plans` and `trees`. No vet_statuses aggregation. Tests don't cover it because it's not implemented.

**Phase 5 — Merge:**
- Design D-5 classification table specifies "Completed This Session" as `Squash` strategy. Test file names it correctly and verifies the strategy. Conformance is good.
- Slug propagation through `resolve_session_md` to `_merge_session_contents` — covered by the dedicated integration test file (`test_worktree_merge_session_resolution.py`). This was the critical bug found in vet-fix.

### Specificity (fails for right reason only)

Most tests have good specificity — assertions target exact values, not broad patterns.

**Minor specificity concerns:**

1. `test_planstate_aggregation_integration.py:171` — `assert hasattr(result, "trees")` is a weak structural check. Could pass with any object having a `trees` attribute. The subsequent assertions are specific, so this is low risk.

2. `test_worktree_ls_upgrade.py:119` — CLI integration test checks `result.exit_code in (0, 1)`. This accepts both success and failure, reducing specificity. The test acknowledges it runs against real project root, so this is a pragmatic compromise.

3. `test_worktree_merge_strategies.py:150-152` — Keep-ours tests assert `ours_content in result` and `theirs_content not in result`. The `in` check for ours content is correct but could pass if content appears in a different section. Acceptable given the test structure.

### Coverage (specified scenarios covered)

**Well-covered scenarios:**
- Each status level (requirements, designed, planned, ready) — Phase 1 parametrized test
- Fresh/stale mtime comparison — Phase 2 explicit tests
- Missing report treated as stale — Phase 2 dedicated test
- Iterative review numbering (highest wins) — Phase 2 dedicated test
- All source types (outline, design, runbook-outline, phase) — Phase 2 parametrized test
- Fallback glob for naming variants — Phase 2 dedicated test
- Multiple trees + sorting — Phase 3 integration test
- Main-only (via standalone function tests) — Phase 3 unit tests
- Dirty/clean states — Phase 3 dedicated test
- Commit counting with/without session.md anchor — Phase 3 dedicated test
- Per-section merge strategies (all 7 from D-5 table) — Phase 5 comprehensive tests
- Blocker tagging with [from: slug] — Phase 5 dedicated tests
- Recognized artifacts validation — Phase 6 multiple tests
- Artifact consistency (steps/ without runbook, orchestrator without steps/) — Phase 6
- Plan-archive cross-check — Phase 6 dedicated test

**Coverage gaps:**

1. **`outline.md` without `design.md` maps to `requirements`** — Design explicitly calls this out as a refinement. No test. The implementation handles it correctly by omission (outline.md doesn't trigger any status change in `_determine_status`), but the design spec says "from planstate's perspective, designed requires design.md" — worth a test to lock this behavior.

2. **`problem.md` only → `requirements`** — Design lists it in the artifact table. No test. Implementation handles it in `_collect_artifacts` but `_determine_status` would classify it correctly only because nothing else triggers higher status.

3. **`reports/` only directory** — Design spec mentions this as an edge case in test strategy. `list_plans` test covers `reports/` exclusion at the scanning level, but no test verifies `infer_state` on a directory containing only a `reports/` subdirectory returns None.

4. **Gate priority (design > runbook > phase-level)** — Only design gate tested. Implementation only produces design gate, so other gate types are untestable. But design specifies the priority table (D-7). This is a known incomplete production path (session handoff notes "Gate wiring incomplete in display path").

5. **`VetStatus.any_stale` property** — No test. Public API, defined in models.py.

6. **Rich CLI Task line** — Design specifies `Task: <first pending task name>` in rich output. `test_rich_mode_header_and_task` creates a session.md but without a Pending Tasks section, so the Task line is never verified in output. The test verifies header format and commit count but not the Task display line.

7. **Porcelain backward compatibility via CLI** — `test_porcelain_mode_backward_compatible` tests the parsing function `_parse_worktree_list` from `worktree.utils`, not the CLI `ls --porcelain` command's actual output. The test bypasses the CLI and calls the parser directly on raw git output. `test_porcelain_flag_exists` invokes the CLI but only checks exit code and help text.

8. **Merge strategies: no `slug` parameter → blockers not tagged** — `test_merge_session_preserves_new_blockers` calls `_merge_session_contents(ours, theirs)` without slug. The blocker is added but not tagged. However, the test doesn't explicitly assert the absence of `[from:` tag. The behavior is implicitly correct (no slug → no tag), but not explicitly tested.

### Independence (verifies behavior, not implementation)

**Good independence patterns:**
- Phase 1 tests use public API (`infer_state`, `list_plans`) and verify behavioral outputs (status, name, artifacts, next_action, gate)
- Phase 2 tests use public API (`get_vet_status`) and verify chain properties
- Phase 5 tests verify merge output content (what's preserved, what's discarded) without checking internal merge mechanics
- Phase 6 tests verify error messages and absence of errors, not internal validation logic

**Coupling concerns:**

1. **Phase 3 tests import private functions:** `test_planstate_aggregation.py` imports `_commits_since_handoff`, `_is_dirty`, `_latest_commit`, `_parse_worktree_list` — all private (underscore-prefixed). These test implementation details directly. The integration test (`test_planstate_aggregation_integration.py`) correctly uses public API (`aggregate_trees`, `_task_summary`, `AggregatedStatus`). `_task_summary` is also private but is tested because it's designed infrastructure for FR-1.

2. **Display test mocks aggregate_trees:** `test_worktree_display_formatting.py` patches `aggregate_trees` to inject test data. This is an appropriate test pattern (mock boundary dependency), not a coupling issue.

### Vacuity

No vacuous tests detected. All tests make specific assertions that would fail if the implementation were removed or broken. The weakest assertion is `result.exit_code in (0, 1)` in the CLI integration test, which is documented as a pragmatic compromise.

### Excess

No excess tests detected. Each test file covers distinct functionality. The two Phase 5 merge test files (`test_worktree_merge_strategies.py` and `test_worktree_merge_session_resolution.py`) overlap slightly on blocker merging scenarios, but one tests the pure function while the other tests the full integration through git conflict resolution — this is appropriate layered coverage.

## Issues Found

### Major Issues

1. **No test for `outline.md` without `design.md` → `requirements` status**
   - Location: `tests/test_planstate_inference.py`
   - Problem: Design explicitly documents this as a refinement ("from planstate's perspective, designed requires design.md"). No test locks this behavior. The parametrized test only covers `requirements.md` → `requirements`, not `outline.md` → `requirements`.
   - Suggestion: Add parametrized case `("requirements_outline", ["outline.md"], "requirements", {"outline.md"})` to `test_status_priority_detection`

2. **No test for `problem.md` only → `requirements` status**
   - Location: `tests/test_planstate_inference.py`
   - Problem: Design artifact table specifies `problem.md` as a valid sole artifact for `requirements` status. No test.
   - Suggestion: Add parametrized case `("requirements_problem", ["problem.md"], "requirements", {"problem.md"})`

3. **`VetStatus.any_stale` property untested**
   - Location: `tests/test_planstate_vet.py`
   - Problem: Public API property on `VetStatus` (models.py:23-25) with zero test coverage. Design specifies it as "Convenience: any chain stale?"
   - Suggestion: Add assertions to existing tests: `assert vet_status.any_stale is True/False` after chain-level assertions

4. **Phase 3 unit tests couple to private API**
   - Location: `tests/test_planstate_aggregation.py`
   - Problem: All 4 tests import private functions (`_parse_worktree_list`, `_commits_since_handoff`, `_is_dirty`, `_latest_commit`). These test internal implementation, not behavior. If internals are refactored (e.g., using a different git library), all tests break despite unchanged behavior.
   - Suggestion: The integration test file covers the public API well. Consider whether the unit-level tests add enough value to justify the coupling. If kept, acknowledge them as implementation tests, not behavioral tests.

### Minor Issues

1. **Rich CLI Task line not verified**
   - Location: `tests/test_worktree_ls_upgrade.py:98-189`
   - Note: `test_rich_mode_header_and_task` creates session.md without Pending Tasks section, so the Task display line is never verified. Adding a task to the session.md fixture would enable asserting `Task:` appears in output.

2. **Porcelain test bypasses CLI**
   - Location: `tests/test_worktree_ls_upgrade.py:26-95`
   - Note: `test_porcelain_mode_backward_compatible` calls `_parse_worktree_list` from `worktree.utils` instead of invoking `worktree ls --porcelain` via CliRunner and checking the tab-separated output format. The flag existence test runs the CLI but doesn't verify output format.

3. **Weak assertion in aggregation integration**
   - Location: `tests/test_planstate_aggregation_integration.py:171`
   - Note: `assert hasattr(result, "trees")` is a structural check that could be replaced with `assert isinstance(result, AggregatedStatus)` for stronger type verification.

4. **Design-implementation drift on data models not documented in tests**
   - Location: design.md vs models.py
   - Note: Design specifies `TreeStatus` with 9 fields; implementation uses `TreeInfo` NamedTuple with 5 fields. Design specifies `VetStatus.plan_name`; implementation omits it. Design specifies `AggregatedStatus.vet_statuses`; implementation omits it. These drifts are not tracked as known items in session.md or test comments.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Cross-tree status display | Satisfied | Aggregation integration tests verify multi-tree sorting, plan discovery, deduplication. CLI tests verify rich output format. |
| FR-2: Vet artifact staleness | Satisfied | All source types, fresh/stale/missing, iterative reviews, fallback glob tested. |
| FR-3: Plan state inference | Partial | 4 status levels tested, but outline-only and problem-only edge cases missing. `list_plans` scanning and exclusions tested. |
| FR-4: Bidirectional merge | Satisfied | Merge tests verify content strategies. No auto-rm is a skill-level change (not code-testable). |
| FR-5: Per-section merge strategies | Satisfied | All 7 D-5 strategies tested: squash (status, completed, worktree tasks, reference, next steps), additive (pending tasks), evaluate (blockers with tagging). Integration test combines all. |
| FR-6: Eliminate jobs.md | Satisfied | Validator tests cover: missing artifacts, reports exclusion, artifact consistency (steps/runbook, orchestrator/steps), archive orphans, CLI integration. |
| NFR-1: No writes during status | Satisfied | Aggregation uses read-only git commands and file reads. No write operations in planstate module. |
| NFR-2: No unversioned shared state | Satisfied | All state computed from versioned artifacts. |
| C-1: Filesystem mtime | Satisfied | `os.utime()` used in vet tests to control mtimes precisely. |
| C-2: Git commit hash anchor | Satisfied | `_commits_since_handoff` uses `git log -1 --format=%H -- agents/session.md` as anchor. |

**Gaps:** FR-3 edge cases (outline-only, problem-only) not tested. VetStatus.any_stale untested.

## Positive Observations

- **Real git repos over mocks:** Phases 3-5 use `tmp_path` with actual git operations, matching the design's stated test strategy. This catches real integration issues (the slug propagation bug was found through this approach).
- **Parametrized tests reduce duplication:** Phase 1 uses parametrized tests for status detection and next-action derivation. Phase 2 uses parametrized tests for source-report mapping. Phase 5 uses parametrized tests for keep-ours strategies.
- **Integration test layering:** Phase 5 has both unit tests (`_merge_session_contents` pure function) and integration tests (full git conflict resolution through `resolve_session_md`). This catches issues at different levels.
- **Edge case coverage for blockers:** Tests cover single blocker, two blockers, multiline blocker, missing section, and section-creation-when-absent scenarios.
- **Deduplication in aggregation:** Tests verify main tree wins on name conflict — a subtle correctness property.
- **Full D-5 integration test:** `test_full_session_md_merge_integration` exercises all 7 merge strategies in a single realistic scenario with comprehensive positive and negative assertions.

## Recommendations

- Add parametrized cases for `outline.md`-only and `problem.md`-only to Phase 1 tests — these are explicitly called out in the design as edge cases
- Add `any_stale` assertions to Phase 2 tests as a low-cost coverage improvement
- Consider documenting the design-implementation drift (TreeStatus vs TreeInfo, missing vet_statuses field) so future reviewers understand these are intentional simplifications

## Next Steps

- Address major issues 1-3 (add missing parametrized cases and any_stale assertions)
- Evaluate major issue 4 (private API coupling) — may be acceptable as implementation tests
