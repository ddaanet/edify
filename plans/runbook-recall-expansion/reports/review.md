# Review: fix-recall-expansion

**Scope**: Uncommitted changes — `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_recall.py`
**Date**: 2026-03-01
**Baseline**: dc15caca
**Mode**: review + fix

## Summary

Three fixes from the deliverable review: FileNotFoundError handling in `resolve_recall_entries`, refactored e2e tests to call `main()` via `_run_main` helper, and a new e2e test `test_phase_recall_in_step_files` verifying phase-tagged recall appears in step files and is absent from other phases. All 17 tests pass and precommit is green.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Phase-recall e2e test uses ordering-dependent mock**
   - Location: `tests/test_prepare_runbook_recall.py:333-342`
   - Problem: `mock_run` assigns shared vs phase-2 content based on `call_count` (1st call → shared, 2nd → phase 2). This is correct today because `resolve_recall_for_runbook` resolves shared entries before phase entries, but the ordering is not contractually guaranteed. If the resolution order changes (e.g., phases resolved first), the mock silently produces incorrect content — phase 2 files would contain "Shared recall content." and the test would still pass because `"Phase 2 recall content"` would be absent from step files, triggering the assertion. Actually re-reading: the assertion `assert "Phase 2 recall content" in step_content` would FAIL if phase 2 got "Shared recall content." — so the test would correctly catch the regression. The concern is the reverse: if both calls return "Shared recall content.", phase 2 step files could contain "Shared recall content." which satisfies nothing meaningful for the assertion on phase isolation.
   - Re-evaluation: The assertion `assert "Phase 2 recall content" in step_content` is strong — it would only pass if the 2nd subprocess call (which returns "Phase 2 recall content.") was routed to phase 2 step files. And `assert "Phase 2 recall content" not in p1_content` ensures isolation. The test is effectively verifying correct routing even though it uses count-based mock ordering.
   - Conclusion: Not an actual defect. The assertions are sufficient to catch routing bugs regardless of whether the mock assignment is fragile.
   - **Status**: OUT-OF-SCOPE — initial analysis confirmed assertions are sound; no fix warranted

### Minor Issues

1. **`_run_main` returns 1 for non-integer SystemExit code**
   - Location: `tests/test_prepare_runbook_recall.py:222`
   - Note: `exc.code if isinstance(exc.code, int) else 1` — if `sys.exit(None)` is called (success path that uses SystemExit without code), this returns 1 and the test asserting `exit_code == 0` would fail. This is the correct behavior (distinguishes None from 0), but the comment says "return exit code" without clarifying the None-mapping. No functional issue since `main()` only exits via `sys.exit(1)` on error or falls off the end.
   - **Status**: OUT-OF-SCOPE — no functional defect, comment addition would be noise

2. **`test_phase_recall_in_step_files` glob pattern for TDD phase 1**
   - Location: `tests/test_prepare_runbook_recall.py:361-364`
   - Note: Phase 1 in `MULTI_PHASE_RUNBOOK` is type: tdd. TDD cycles produce `step-{major}-{minor}.md` (e.g., `step-1-1.md`), not `cycle-*.md` — confirmed in `prepare-runbook.py:1529`. The glob `step-1-*.md` is correct.
   - **Status**: OUT-OF-SCOPE — no defect; naming convention verified

## Fixes Applied

None — all issues were either out-of-scope or confirmed non-defects after investigation.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: prepare-runbook.py reads recall artifact | Satisfied | Unchanged from baseline; fix does not regress |
| FR-2: Resolve all entry keys | Satisfied | FileNotFoundError now handled gracefully |
| FR-3: Inject into agent definition Common Context | Satisfied | `test_shared_recall_in_agent` calls `main()` directly |
| FR-4: Per-phase recall in phase preambles → step files | Satisfied | `test_phase_recall_in_step_files` added, verifies FR-4 end-to-end |
| FR-5: Runbook skill template format | Satisfied | Unchanged; not in scope of fix |
| FR-6: Document two orchestration patterns | Satisfied | Unchanged; not in scope of fix |
| FR-7: Corrector self-contained recall loading | Satisfied | Unchanged; not in scope of fix |
| NFR-1: Token budget | Satisfied | Unchanged |
| NFR-2: No runtime resolution | Satisfied | Unchanged |
| NFR-3: Backward compatibility | Satisfied | `test_no_artifact_no_recall` calls `main()` directly |

**Gaps:** None — all deliverable-review findings resolved.

---

## Positive Observations

- `_run_main` helper is clean: single responsibility, captures `SystemExit`, no test-specific logic leaking into the helper
- The `test_phase_recall_in_step_files` test checks three distinct behavioral invariants: phase 2 step files receive phase 2 recall, phase 1 step files do NOT receive phase 2 recall, and both phase agents receive shared recall — strong coverage
- FileNotFoundError handling is consistent with the function's existing soft-failure pattern for non-zero exit codes
- `capsys` fixture captured and surfaced in error message on assertion failure — improves diagnosability

## Recommendations

None.
