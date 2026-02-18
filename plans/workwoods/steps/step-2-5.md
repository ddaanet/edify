# Cycle 2.5

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.5: Iterative review handling (highest-numbered or highest-mtime wins)

**RED Phase:**

**Test:** `test_iterative_review_highest_wins`
**Assertions:**
- outline.md with reports/outline-review.md and reports/outline-review-3.md → outline-review-3.md used (highest number)
- If no numbers: use highest mtime among matching reports
- Escalation variants (*-opus.md) treated as additional reviews, highest mtime among all variants wins
- VetChain.report contains the winning report filename

**Expected failure:** Uses first report found or alphabetically first, not highest numbered or newest

**Why it fails:** No logic to compare review iteration numbers or mtimes

**Verify RED:** `pytest tests/test_planstate_vet.py::test_iterative_review_highest_wins -v`

**GREEN Phase:**

**Implementation:** Extract iteration numbers from filenames, use highest; fallback to mtime comparison

**Behavior:**
- Glob for all matching reports (e.g., reports/outline-review*.md)
- Extract iteration number from filename (outline-review-3.md → 3)
- If numbers found: use highest number
- If no numbers or tie: use highest mtime
- Escalation variants included in glob results

**Approach:** Regex to extract numbers, sort by (number, mtime) tuple

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add report selection logic (glob, number extraction, mtime comparison)
  Location hint: In source→report mapping, after finding report candidates

- File: `tests/test_planstate_vet.py`
  Action: Create test with multiple review files (outline-review.md, outline-review-2.md, outline-review-3.md, outline-review-opus.md)
  Location hint: New test function, use os.utime() to set mtimes for tie-breaking

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_iterative_review_highest_wins -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---
