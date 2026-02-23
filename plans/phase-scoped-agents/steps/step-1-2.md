# Cycle 1.2

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Core functions for naming, composition, and per-phase baseline selection.

---

## Cycle 1.2: Per-phase baseline selection

**RED Phase:**

**Test:** `test_get_phase_baseline_type_tdd` and `test_get_phase_baseline_type_general`
**Assertions:**
- `get_phase_baseline_type("## Cycle 1.1: First\n**RED Phase:**\ntest\n**GREEN Phase:**\nimpl")` returns `"tdd"`
- `get_phase_baseline_type("## Step 1.1: First\nStep content here")` returns `"general"`
- `get_phase_baseline_type("No headers, just prose")` returns `"general"` (default)

**Expected failure:** ImportError or NameError — `get_phase_baseline_type` doesn't exist yet.

**Why it fails:** Function not yet defined in prepare-runbook.py.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "baseline_type"`

**GREEN Phase:**

**Implementation:** New function `get_phase_baseline_type(phase_content)`.

**Behavior:**
- Scans content for `## Cycle` header pattern (regex `^##\s+Cycle\s+\d+\.\d+:`)
- Returns `"tdd"` if found, `"general"` otherwise
- Uses `strip_fenced_blocks()` to avoid matching headers inside code fences

**Approach:** Simple regex search on stripped content.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `get_phase_baseline_type()` after `extract_phase_preambles()`
  Location hint: After line 647 (after `extract_phase_preambles`)

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "baseline_type"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---
