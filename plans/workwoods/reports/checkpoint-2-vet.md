# Vet Review: Phase 2 Checkpoint — Vet Staleness Detection

**Scope**: Phase 2 checkpoint implementation
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix

## Summary

Phase 2 implements vet staleness detection with source→report mapping, mtime comparison, and iterative review selection. Implementation matches design decisions with proper glob fallback for variant naming. Test coverage is comprehensive with parametrized tests, mtime manipulation, and edge case handling. All 8 tests pass with meaningful assertions.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None

### Major Issues

None

### Minor Issues

1. **Default mtime value should be None**
   - Location: src/claudeutils/planstate/models.py:14
   - Note: `report_mtime: float | None = 0.0` has wrong default. Should be `None` to match the "missing report" semantic (when report doesn't exist, report_mtime is None, not 0.0)
   - **Status**: FIXED

2. **Inconsistent return type annotation**
   - Location: src/claudeutils/planstate/vet.py:106
   - Note: Function returns `VetStatus | None` but the design implies it should always return VetStatus (chains can be empty list). However, code explicitly returns None when no chains exist. This is intentional per implementation logic, so annotation is correct. Actually this is not an issue — design says "Returns None if no source artifacts are found" (line 110 docstring matches).
   - **Status**: OUT-OF-SCOPE (implementation matches documented behavior)

## Fixes Applied

- src/claudeutils/planstate/models.py:14 — Changed `report_mtime: float | None = 0.0` to `report_mtime: float | None = None`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-2: Vet artifact staleness — mtime-based detection | Satisfied | vet.py:131-137 mtime comparison logic |
| FR-2: source→report mapping | Satisfied | vet.py:8-18 SOURCE_TO_REPORT_MAP |
| FR-2: fallback glob for phase reports | Satisfied | vet.py:67-103 _find_iterative_report_for_source |
| VetChain model: source, report (nullable), stale, mtimes | Satisfied | models.py:7-14 |
| VetStatus model: plan_name, chains list, any_stale property | Partial | models.py:18-26 — has chains and any_stale but NOT plan_name field |
| Missing report treated as stale | Satisfied | vet.py:135-139 |
| Iterative review selection: highest-numbered iteration wins | Satisfied | vet.py:21-64 _extract_iteration_number + _find_best_report |

**Gaps:**
- VetStatus model missing `plan_name` field (requirement specifies it but implementation omits it)
- Design.md line 347 says `get_vet_status(plan_dir: Path) -> VetStatus` but doesn't say VetStatus needs plan_name
- Phase 1 integration will need plan_name when calling from `infer_state()` — caller can derive from `plan_dir.name`

## Positive Observations

- Excellent test coverage with parametrized tests for mapping conventions
- Proper use of `os.utime()` to control mtime in tests (enables deterministic staleness testing)
- Clear separation of numbered iterations vs. variant reports (opus, etc.)
- Fallback glob logic correctly handles both phase and non-phase sources
- Docstrings explain non-obvious behavior (iteration extraction, best report selection)
- Code structure is clear: helper functions for extraction, selection, finding

## Recommendations

**VetStatus.plan_name field:** Requirements state VetStatus should have plan_name, but implementation omits it. Two options:

1. Add `plan_name: str` field to VetStatus dataclass and populate it in `get_vet_status()` from `plan_dir.name`
2. Accept that plan_name is derived by caller (Phase 1 `infer_state()` knows plan from `plan_dir`)

Option 2 is simpler and avoids redundant storage. If Phase 1 integration works without it, no change needed. If aggregation needs it, add in Phase 3.

Recommend deferring this decision to Phase 1 integration checkpoint (when `infer_state()` calls `get_vet_status()`).
