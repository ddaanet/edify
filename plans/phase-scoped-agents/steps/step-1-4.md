# Cycle 1.4

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Core functions for naming, composition, and per-phase baseline selection.

---

## Cycle 1.4: Phase type detection from assembled content

Depends on: 1.2 (reuses phase classification logic)

**RED Phase:**

**Test:** `test_detect_phase_types_mixed`
**Assertions:**
- Given content with 3 phases:
  - Phase 1 has `## Cycle 1.1:` headers (TDD content)
  - Phase 2 has `(type: inline)` in phase header
  - Phase 3 has `## Step 3.1:` headers (general content)
- `detect_phase_types(content)` returns `{1: "tdd", 2: "inline", 3: "general"}`

**Expected failure:** ImportError or NameError — `detect_phase_types` doesn't exist yet.

**Why it fails:** Function not yet defined.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "detect_phase_types"`

**GREEN Phase:**

**Implementation:** New function `detect_phase_types(content)`.

**Behavior:**
- Parses phase headers from content using `^###?\s+Phase\s+(\d+):` pattern
- For each phase, extracts content between its header and the next phase header (or end)
- Classifies each:
  - If phase header contains `(type: inline)` → `"inline"`
  - Otherwise, delegates to `get_phase_baseline_type(phase_content)` → `"tdd"` or `"general"`
- Returns dict of `{phase_num: type_str}`

**Approach:** Reuse `strip_fenced_blocks()` for safe header matching. Split content at phase boundaries, classify each segment.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `detect_phase_types()` after `get_phase_baseline_type()`
  Location hint: After the new `get_phase_baseline_type()` function

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "detect_phase_types"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---

### Phase 2: Orchestrator plan format and integration (type: tdd, model: sonnet)

Orchestrator plan format changes and integration through `validate_and_create()`.
