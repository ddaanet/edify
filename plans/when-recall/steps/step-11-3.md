# Cycle 11.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 11

---

## Cycle 11.3: Verify recall analysis produces valid reports

**RED Phase:**

**Test:** `test_recall_analysis_with_new_format`
**Assertions:**
- Given index file in new `/when` format and a session transcript:
  - Recall analysis runs without error
  - Report contains entry matches (if any topics overlap)
  - Entry count in report matches index entry count
- Empty index → report shows 0 entries, 0 matches (no crash)

**Expected failure:** Test fails — recall analysis crashes or report format incorrect

**Why it fails:** Recall modules (`relevance.py` or `report.py`) may use IndexEntry.description field which becomes empty string in new format, causing AttributeError or KeyError on dict access

**Verify RED:** `pytest tests/test_recall_integration.py::test_recall_analysis_with_new_format -v`

**GREEN Phase:**

**Implementation:** Ensure recall analysis pipeline handles updated IndexEntry format.

**Behavior:**
- Recall analysis should work with empty description field
- Keywords are sufficient for relevance matching (description was redundant with keywords)
- Report generation uses key field (trigger text) for display

**Approach:** Check all recall modules for description field usage. Update if needed. Most likely `relevance.py` and `report.py`.

**Changes:**
- File: `src/claudeutils/recall/relevance.py`
  Action: Verify keyword-based matching works without description (may need no changes)
- File: `src/claudeutils/recall/report.py`
  Action: Use key field for display if description is empty
  Location hint: Report formatting logic

**Verify GREEN:** `pytest tests/test_recall_integration.py::test_recall_analysis_with_new_format -v`
**Verify no regression:** `pytest tests/ -q`
