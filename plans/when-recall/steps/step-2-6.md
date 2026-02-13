# Cycle 2.6

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.6: Format navigation links

**RED Phase:**

**Test:** `test_format_navigation_output`
**Assertions:**
- Given ancestors `["/when .Test Organization", "/when ..testing.md"]` and siblings `["/when testing strategy", "/when success metrics"]`:
  - Formatted output is:
    ```
    Broader:
    /when .Test Organization
    /when ..testing.md

    Related:
    /when testing strategy
    /when success metrics
    ```
- Empty ancestors → "Broader:" section omitted
- Empty siblings → "Related:" section omitted
- Both empty → empty string returned

**Expected failure:** AssertionError or AttributeError — formatting function doesn't exist

**Why it fails:** Navigation link formatting not yet implemented

**Verify RED:** `pytest tests/test_when_navigation.py::test_format_navigation_output -v`

**GREEN Phase:**

**Implementation:** Create navigation link formatting function.

**Behavior:**
- Format "Broader:" section with ancestor links (one per line)
- Format "Related:" section with sibling links (one per line)
- Blank line between sections
- Omit sections with no links
- Return empty string if both sections empty

**Approach:** String joining with conditional section headers.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add `format_navigation(ancestors, siblings)` function
  Location hint: End of module (output formatting)

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_format_navigation_output -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 3: Resolver Core

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy), Phase 1 (parser), Phase 2 (navigation)
**Files:** `src/claudeutils/when/resolver.py`, `tests/test_when_resolver.py`
**Checkpoint:** Full checkpoint after this phase (resolver complete = core system functional)

**Design reference:** resolver.py module responsibilities, "Note on heading levels" (flat H2 vs nested H2/H3)

**Prior state:**
- Phase 0: `fuzzy.score_match(query, candidate)` and `fuzzy.rank_matches(query, candidates, limit)` available
- Phase 1: `index_parser.parse_index(path)` returns `list[WhenEntry]`
- Phase 2: `navigation.compute_ancestors()`, `compute_siblings()`, `format_navigation()` available

---
