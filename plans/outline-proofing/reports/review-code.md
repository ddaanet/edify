# Review: inference.py implementation + test extraction

**Scope**: `src/claudeutils/planstate/inference.py`, `tests/test_planstate_inference.py`, `tests/test_planstate_inference_lifecycle.py` (new) — baseline `6373b3f6`
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

Implements `inline-planned` status, extracts `_determine_pre_ready_status` helper, fixes `outlined` → `/design` routing, adds `inline-plan.md` to artifact collection, and splits lifecycle tests into a separate module. All review criteria pass. One minor documentation gap in the new helper's docstring (missing `briefed` from priority list).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_determine_pre_ready_status` docstring omits `briefed` from priority list**
   - Location: `src/claudeutils/planstate/inference.py:69`
   - Note: Docstring says `Priority: ready > planned > inline-planned > designed > outlined > requirements` but the function also returns `"briefed"` (line 84). The priority comment is incomplete — `briefed` is a subordinate case of `requirements` (brief-only, no requirements.md), but it's missing from the list, making the docstring inaccurate.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/planstate/inference.py:69` — Updated `_determine_pre_ready_status` docstring priority list to include `briefed` (subordinate to `requirements`, brief-only case).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `inline-plan.md` added to `_collect_artifacts` baseline | Satisfied | `inference.py:18` |
| `_determine_pre_ready_status` helper extracted | Satisfied | `inference.py:66-84` |
| `inline-planned` detected between `planned` and `designed` | Satisfied | `inference.py:75-76` (after `planned` check, before `designed`) |
| `outlined` maps to `/design` (not `/runbook`) | Satisfied | `inference.py:102` |
| `inline-planned` next action: `/inline` command | Satisfied | `inference.py:103` |
| `_determine_pre_ready_status` has ≤6 return statements | Satisfied | 6 returns: lines 72, 74, 76, 78, 80, 84 |
| Tests cover inline-planned status detection | Satisfied | `test_planstate_inference.py:71-81` (two parametrize cases) |
| Tests cover inline-planned next action | Satisfied | `test_planstate_inference.py:138` |
| Tests cover outlined routing fix | Satisfied | `test_planstate_inference.py:136` (was `/runbook`, now `/design`) |
| `test_planstate_inference.py` ≤400 lines | Satisfied | 282 lines |
| `test_planstate_inference_lifecycle.py` ≤400 lines | Satisfied | 138 lines |
| Lifecycle test module has correct imports | Satisfied | imports `infer_state` from `claudeutils.planstate`; no `list_plans` or `PlanState` needed |

**Gaps:** None.

---

## Positive Observations

- `_determine_pre_ready_status` cleanly separates lifecycle vs pre-ready logic, enabling `_determine_status` to be a simple two-line coordinator.
- Return count of exactly 6 satisfies PLR0911 without requiring restructuring into a priority table or dispatch dict — the if-chain reads naturally.
- Priority ordering (planned → inline-planned → designed) correctly positions `inline-planned` as a subordinate of `planned` (inline-plan.md is simpler than full phase files) while remaining above `designed`.
- Test IDs on parametrize cases (`id="inline-planned-brief-plus-inline-plan"`) make failure messages self-documenting.
- Lifecycle test extraction lands at 138 lines, well under the 400-line limit, with correct minimal imports (only `infer_state` needed).
- All 43 tests pass.
