# Cycle 7.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.4: Suggest minimal unique trigger

**RED Phase:**

**Test:** `test_suggest_minimal_trigger`
**Assertions:**
- `compress_key("How to Encode Paths", corpus)` returns shortest unique trigger (e.g., `"how encode path"`)
- Result is verified unique against corpus
- If no unique candidate found (heading too generic), returns full heading lowercased as fallback
- For heading `"When Writing Mock Tests"`, result is shorter than the full heading

**Expected failure:** AttributeError — `compress_key` doesn't exist

**Why it fails:** Main entry point not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_suggest_minimal_trigger -v`

**GREEN Phase:**

**Implementation:** Create main compress_key function.

**Behavior:**
- Generate candidates from heading (7.2)
- Test each candidate for uniqueness (7.3), shortest first
- Return first unique candidate
- Fallback: full heading lowercased if no shorter candidate is unique

**Approach:** Linear scan of sorted candidates, return first passing uniqueness check.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Add `compress_key(heading, corpus)` function
  Location hint: Main entry point, after helper functions
- File: `agent-core/bin/compress-key.py`
  Action: Create CLI wrapper with shebang
  Location hint: New file

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_suggest_minimal_trigger -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 8: Skill Wrappers

**Type:** General
**Model:** haiku
**Dependencies:** Phase 5 (bin script must exist)
**Files:**
- `agent-core/skills/when/SKILL.md`
- `agent-core/skills/how/SKILL.md`

**Design reference:** Skill Wrappers section
**Skill guidance:** plugin-dev:skill-development (loaded in session)

---
