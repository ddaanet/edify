# Deliverable Review: runbook-recall-expansion (re-review)

**Date:** 2026-03-01
**Methodology:** agents/decisions/deliverable-review.md
**Prior review:** This report (same path). 3 findings (0 Critical, 1 Major, 2 Minor). All findings addressed by fix task `fix-recall-expansion`.

## Inventory

Fix deliverables from merge base `687d0c0b`:

| Type | File | + | - |
|------|------|---|---|
| Code | `agent-core/bin/prepare-runbook.py` | +5 | -1 |
| Test | `tests/test_prepare_runbook_recall.py` | +125 | -52 |

**Total:** 2 deliverables, 130 lines added, 53 removed.

## Prior Finding Resolution

### Major-1: No e2e test for phase-tagged recall injection into step files

**Status:** Resolved.

`test_phase_recall_in_step_files` added (lines 317-371). Calls `main()` via `_run_main` helper with a multi-phase runbook fixture (TDD phase 1, general phase 2). Verifies three behavioral invariants:
- Phase 2 step files contain `## Phase Recall` heading and phase-2-specific content
- Phase 1 step files do NOT contain phase 2 recall content (isolation)
- Both phase agents contain shared recall content

Uses `capsys` for diagnostic output on assertion failure. The test exercises the full pipeline: artifact parsing → resolution → phase partitioning → injection into preambles → step file generation.

### Minor-1: E2e tests replicate main() wiring instead of calling main()

**Status:** Resolved.

Both `test_shared_recall_in_agent` and `test_no_artifact_no_recall` refactored to use `_run_main` helper (lines 216-224). The helper sets `sys.argv` via monkeypatch and calls `_mod.main()` directly, replacing 25+ lines of manual wiring per test. Same assertions preserved — only the invocation mechanism changed.

### Minor-2: No subprocess exception handling in resolve_recall_entries

**Status:** Resolved.

`resolve_recall_entries` now wraps `subprocess.run()` in `try/except FileNotFoundError` (prepare-runbook.py lines 136-140). Warning printed to stderr, returns empty string — consistent with existing soft-failure pattern for non-zero exit codes. Test `test_returns_empty_on_binary_not_found` verifies the behavior.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## Gap Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: prepare-runbook.py reads recall artifact | Covered | Unchanged from baseline |
| FR-2: Resolve all entry keys | Covered | FileNotFoundError now handled gracefully |
| FR-3: Inject into agent definition Common Context | Covered | `test_shared_recall_in_agent` now calls `main()` directly |
| FR-4: Per-phase recall in phase preambles → step files | Covered | `test_phase_recall_in_step_files` — e2e through `main()` |
| FR-5: Runbook skill Common Context template format | Covered | Unchanged |
| FR-6: Document two orchestration patterns | Covered | Unchanged |
| FR-7: Corrector self-contained recall loading | Covered | Unchanged |
| NFR-1: Token budget | Covered | Unchanged |
| NFR-2: No runtime resolution in step agents | Covered | Unchanged |
| NFR-3: Backward compatibility | Covered | `test_no_artifact_no_recall` now calls `main()` directly |

**Gaps:** None — all 7 FRs and 3 NFRs satisfied. All prior findings resolved.

## Summary

- Critical: 0
- Major: 0
- Minor: 0

All 3 prior findings resolved cleanly. 17/17 tests pass. Code changes are minimal and consistent with existing patterns. Test refactoring improves independence (true e2e via `main()`) without sacrificing assertion coverage. Corrector review (plans/runbook-recall-expansion/reports/review.md) independently confirmed 0 fixes needed.
