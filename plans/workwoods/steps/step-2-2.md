# Cycle 2.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.2: Phase-level fallback glob (runbook-phase-N naming variants)

**RED Phase:**

**Test:** `test_phase_level_fallback_glob`
**Assertions:**
- runbook-phase-3.md → reports/phase-3-review.md found (primary pattern)
- runbook-phase-3.md → reports/checkpoint-3-vet.md found (fallback pattern)
- runbook-phase-3.md → reports/phase-3-review-opus.md found (escalation variant)
- Most recent report wins when multiple patterns match (highest mtime)

**Expected failure:** Only primary pattern works, fallback glob not implemented

**Why it fails:** Hardcoded report paths don't handle naming variance

**Verify RED:** `pytest tests/test_planstate_vet.py::test_phase_level_fallback_glob -v`

**GREEN Phase:**

**Implementation:** Glob for phase-level reports when primary pattern not found

**Behavior:**
- Try primary pattern first: reports/phase-N-review.md
- If not found, glob: reports/*N*{review,vet}*.md for phase number N
- Parse filenames to extract phase number, filter matches
- If multiple matches, use highest mtime

**Approach:** Extract phase number from runbook-phase-N.md, glob with number in pattern

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add fallback glob logic for phase-level reports in get_vet_status()
  Location hint: In source→report mapping, after primary pattern check fails

- File: `tests/test_planstate_vet.py`
  Action: Create test with multiple report naming variants (phase-3-review, checkpoint-3-vet, phase-3-review-opus)
  Location hint: New test function, use os.utime() to set different mtimes

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_phase_level_fallback_glob -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---
