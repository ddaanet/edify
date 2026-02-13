# Phase 2: Navigation Module

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 1 (WhenEntry model for sibling computation)
**Files:** `src/claudeutils/when/navigation.py`, `tests/test_when_navigation.py`

**Design reference:** navigation.py module responsibilities, "Structural heading handling"

**Prior state:** Phase 1 provides `WhenEntry` model with operator, trigger, extra_triggers, line_number, section fields.

---

## Cycle 2.1: Extract heading hierarchy from file content

**Prerequisite:** Read `agents/decisions/testing.md:1-30` — understand decision file heading structure (structural `.` prefix, semantic headings, H2/H3 nesting)

**RED Phase:**

**Test:** `test_extract_heading_hierarchy`
**Assertions:**
- Given markdown content with `## Section A` containing `### Sub A1` and `### Sub A2`:
  - Returns hierarchy mapping `"Sub A1" → parent "Section A"`, `"Sub A2" → parent "Section A"`
- Given nested `## A` → `### B` → `#### C`:
  - Returns `"C" → parent "B"`, `"B" → parent "A"`
- Returns heading level for each heading (H2=2, H3=3, H4=4)

**Expected failure:** ImportError — `navigation` module doesn't exist

**Why it fails:** Module `src/claudeutils/when/navigation.py` not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_extract_heading_hierarchy -v`

**GREEN Phase:**

**Implementation:** Create `navigation.py` with heading hierarchy extraction.

**Behavior:**
- Parse markdown content line by line
- Track heading stack (H2 → H3 → H4)
- Build parent mapping: each heading maps to its nearest higher-level ancestor
- Return structured hierarchy (dict of heading → HeadingInfo with parent, level, line_number)

**Approach:** Stack-based parser. Push heading when level increases, pop when level decreases or equals.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Create module with heading hierarchy extraction function
  Location hint: New module

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_extract_heading_hierarchy -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 2.2: Compute ancestor headings (H4→H3→H2→file)

**RED Phase:**

**Test:** `test_compute_ancestors`
**Assertions:**
- For H3 heading "Mock Patching Pattern" under H2 "Test Organization" in `testing.md`:
  - `compute_ancestors("Mock Patching Pattern", "testing.md", content)` returns:
    - `/when .Test Organization` (parent H2)
    - `/when ..testing.md` (file link, always last)
- For H4 heading under H3 under H2:
  - Returns grandparent H2, parent H3, and file link (3 ancestors)
- For H2 heading (top-level):
  - Returns only file link (1 ancestor)

**Expected failure:** AttributeError — `compute_ancestors` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_compute_ancestors -v`

**GREEN Phase:**

**Implementation:** Create `compute_ancestors` function.

**Behavior:**
- Walk up heading hierarchy from target heading
- Collect all ancestor headings as `/when .SectionTitle` links
- Always append `..filename.md` as final link
- Skip the heading itself (only ancestors)

**Approach:** Use hierarchy from 2.1. Follow parent chain upward, collect links.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add `compute_ancestors(heading, file_path, file_content)` function
  Location hint: After hierarchy extraction

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_compute_ancestors -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 2.3: Handle flat H2 files (workflow-core pattern)

**Prerequisite:** Read `agents/decisions/workflow-core.md:1-30` — understand flat H2 structure (13 H2 sections, no H3 nesting)

**RED Phase:**

**Test:** `test_flat_h2_file_ancestors`
**Assertions:**
- For H2 heading "Oneshot workflow pattern" in `workflow-core.md` (flat H2, no H3):
  - `compute_ancestors("Oneshot workflow pattern", "workflow-core.md", content)` returns:
    - `/when ..workflow-core.md` only (no parent heading — it IS top level)
- Heading hierarchy extraction produces flat list (all H2, no parent relationships among headings)

**Expected failure:** AssertionError — flat H2 headings incorrectly assigned parents or missing file link

**Why it fails:** Hierarchy extraction may not handle files where all headings are same level

**Verify RED:** `pytest tests/test_when_navigation.py::test_flat_h2_file_ancestors -v`

**GREEN Phase:**

**Implementation:** Handle edge case where all headings are H2 (no nesting).

**Behavior:**
- H2 headings have no parent heading (they ARE top level)
- Ancestors for H2 = just the file link
- No hierarchy relationships among sibling H2 headings

**Approach:** Stack-based parser naturally handles this — H2 pushes clear the stack, so no parent recorded.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Verify flat H2 handling works correctly (may need no code changes)
  Location hint: Hierarchy extraction and ancestor computation

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_flat_h2_file_ancestors -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 2.4: Structural heading detection (skip `.` prefix)

**RED Phase:**

**Test:** `test_structural_headings_skipped_as_nav_targets`
**Assertions:**
- Given content with `## .Test Organization` (structural, `.` prefix) containing `### Mock Patching Pattern` (semantic):
  - `compute_ancestors("Mock Patching Pattern", "testing.md", content)` returns:
    - `/when ..Test Organization` (structural parent included in ancestry)
    - `/when ..testing.md` (file link)
  - HeadingInfo for ".Test Organization" has `is_structural=True` flag
- Given 2 WhenEntry objects: one under semantic H2, one under structural H2 `.Test Organization`:
  - `compute_siblings` for entry under structural heading returns empty list (structural headings excluded from sibling grouping)
- Structural headings ARE traversed for ancestry (parent chain walks through them)

**Expected failure:** AssertionError — structural headings treated as regular semantic headings

**Why it fails:** No `.` prefix detection in heading classification

**Verify RED:** `pytest tests/test_when_navigation.py::test_structural_headings_skipped_as_nav_targets -v`

**GREEN Phase:**

**Implementation:** Detect and handle structural headings.

**Behavior:**
- Headings starting with `.` after `#+ ` are structural (organizational)
- Structural headings still participate in hierarchy (they ARE parent nodes)
- Ancestor links for structural headings still generated (agent can navigate up through them)
- Structural headings excluded from sibling computation (they're containers, not content)

**Approach:** Check if heading text starts with `.` after stripping `#` prefix. Flag in HeadingInfo.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add structural heading detection (`.` prefix) and flag in hierarchy data
  Location hint: Heading parsing logic

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_structural_headings_skipped_as_nav_targets -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 2.5: Compute sibling entries (requires WhenEntry structures)

**RED Phase:**

**Test:** `test_compute_siblings`
**Assertions:**
- Given 3 WhenEntry objects all under same parent H2 "Test Organization":
  - Entry 1: trigger "mock patching pattern", section "Mock Patching Pattern"
  - Entry 2: trigger "testing strategy", section "Testing Strategy"
  - Entry 3: trigger "success metrics", section "Success Metrics"
  - `compute_siblings("Mock Patching Pattern", content, entries)` returns:
    - `/when testing strategy`
    - `/when success metrics`
  - The target heading itself ("mock patching pattern") is NOT included in siblings
- Entries under different parent headings are NOT included
- Empty list if heading has no siblings with index entries

**Expected failure:** AttributeError — `compute_siblings` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_compute_siblings -v`

**GREEN Phase:**

**Implementation:** Create `compute_siblings` function.

**Behavior:**
- Find the parent heading of the target heading
- Find all other headings under the same parent that have corresponding WhenEntry objects
- Return their triggers as `/when <trigger>` links
- Exclude the target heading itself

**Approach:** Map entries to their containing headings via hierarchy. Filter to same-parent group.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add `compute_siblings(heading, file_content, index_entries)` function
  Location hint: After `compute_ancestors`

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_compute_siblings -v`
**Verify no regression:** `pytest tests/ -q`

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
