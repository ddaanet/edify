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

## Cycle 3.1: Mode detection (trigger vs .section vs ..file)

**Design note:** Mode detection tests routing logic first (not simplest happy path). This is foundation for all three resolution modes — without mode detection, no mode can execute. Testing meta-behavior first is acceptable when it's minimal infrastructure.

**RED Phase:**

**Test:** `test_mode_detection`
**Assertions:**
- Query `"writing mock tests"` → trigger mode
- Query `".Mock Patching"` → section mode
- Query `"..testing.md"` → file mode
- Query `"."` → section mode (single dot prefix)
- Query `".."` → file mode (double dot with empty name — should error, tested in 3.9)

**Expected failure:** ImportError — `resolver` module doesn't exist

**Why it fails:** Module `src/claudeutils/when/resolver.py` not yet created

**Verify RED:** `pytest tests/test_when_resolver.py::test_mode_detection -v`

**GREEN Phase:**

**Implementation:** Create `resolver.py` with mode detection logic.

**Behavior:**
- `..` prefix → file mode (strip `..`)
- `.` prefix (single) → section mode (strip `.`)
- Anything else → trigger mode
- Check `..` before `.` (longer prefix first)

**Approach:** Simple string prefix check. Return enum or string indicating mode.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Create module with `resolve(operator, query, index_path, decisions_dir)` function and internal mode detection
  Location hint: New module

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_mode_detection -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.2: Trigger mode — fuzzy match against index entries

**Prerequisite:** Read `src/claudeutils/when/fuzzy.py` — understand score_match and rank_matches API

**RED Phase:**

**Test:** `test_trigger_mode_resolves`
**Assertions:**
- Given test index with entries including `/when writing mock tests`:
  - `resolve("when", "writing mock tests", index_path, decisions_dir)` returns string containing `"# When Writing Mock Tests"` (heading)
  - Output contains section content from the decision file
- Query `"mock test"` (approximate) also resolves to same heading (fuzzy match)
- Query includes operator prefix: internal query becomes `"when writing mock tests"` (not just `"writing mock tests"`)

**Expected failure:** AssertionError — resolve returns empty or wrong content

**Why it fails:** Trigger mode resolution not implemented

**Verify RED:** `pytest tests/test_when_resolver.py::test_trigger_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement trigger mode in resolver.

**Behavior:**
- Build candidate list from index entries (format: `"{operator} {trigger}"` for fuzzy matching)
- Use `fuzzy.rank_matches(query_with_prefix, candidates)` to find best match
- If match found, locate corresponding heading in decision file
- Extract section content (done in Cycle 3.5)
- For this cycle: return heading name on successful match

**Approach:** Parse index, build candidate strings, fuzzy match, map back to entry.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement trigger mode — index loading, candidate building, fuzzy matching
  Location hint: Within `resolve` function, trigger mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_trigger_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.3: Section mode — global unique heading lookup

**Prerequisite:** Read `agents/decisions/workflow-core.md:1-20` and `agents/decisions/testing.md:1-20` — understand heading structure across files

**RED Phase:**

**Test:** `test_section_mode_resolves`
**Assertions:**
- Given decision files with unique heading `"Mock Patching Pattern"`:
  - `resolve("when", ".Mock Patching Pattern", index_path, decisions_dir)` returns string containing:
    - Exact heading text "Mock Patching Pattern"
    - Content between that heading and next same-level heading (exclusive boundary)
    - Does NOT contain content from adjacent sections (boundary verification)
- Heading lookup is case-insensitive: `.mock patching pattern` also works
- Ambiguous heading (exists in multiple files) raises `ResolveError` with file disambiguation

**Expected failure:** AssertionError — section mode not implemented

**Why it fails:** Section mode resolution not yet in resolver

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement section mode.

**Behavior:**
- Scan all `.md` files in decisions_dir
- Build heading→file mapping (all H2+ headings)
- Lookup query heading (case-insensitive)
- If unique match: extract content
- If multiple matches: raise ResolveError with disambiguation info
- If no match: raise ResolveError (handled in 3.8)

**Approach:** Walk decision files, collect headings with file paths. Dict lookup.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement section mode — heading collection across files, lookup, uniqueness check
  Location hint: Within `resolve` function, section mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.4: File mode — relative path resolution

**RED Phase:**

**Test:** `test_file_mode_resolves`
**Assertions:**
- `resolve("when", "..testing.md", index_path, decisions_dir)` returns full content of `agents/decisions/testing.md`
- `resolve("when", "..nonexistent.md", index_path, decisions_dir)` raises `ResolveError`
- File path is relative to `decisions_dir` (no absolute paths accepted)

**Expected failure:** AssertionError — file mode not implemented

**Why it fails:** File mode resolution not yet in resolver

**Verify RED:** `pytest tests/test_when_resolver.py::test_file_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement file mode.

**Behavior:**
- Strip `..` prefix from query to get filename
- Resolve relative to `decisions_dir`
- Read and return full file content
- If file not found: raise `ResolveError` (handled in 3.9)

**Approach:** `(decisions_dir / filename).read_text()` with existence check.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement file mode — path resolution, file read, error handling
  Location hint: Within `resolve` function, file mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_file_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.5: Section content extraction from decision file

**Prerequisite:** Read `src/claudeutils/when/navigation.py` — understand heading hierarchy patterns and section boundary detection (flat H2 vs nested H2/H3)

**RED Phase:**

**Test:** `test_section_content_extraction`
**Assertions:**
- Given file with `### Heading A` followed by content, then `### Heading B`:
  - Extract content for "Heading A" returns everything between `### Heading A` and `### Heading B` (exclusive)
- Last heading in file: content extends to EOF
- Nested headings: `## Parent` with `### Child` — extracting "Child" gets Child's content only (not sibling content)
- Flat H2 file (workflow-core pattern): extracting H2 heading gets content until next H2

**Expected failure:** AssertionError — content extraction not working correctly

**Why it fails:** Section boundary detection not yet implemented

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_content_extraction -v`

**GREEN Phase:**

**Implementation:** Add section content extraction.

**Behavior:**
- Find target heading line in file content
- Collect all lines until next heading of same or higher level
- Return collected content (excluding the heading line itself)
- Handle both nested (H2/H3) and flat (all H2) structures

**Approach:** Find heading line, scan forward until next heading at same or lower level number. Slice content.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add `_extract_section_content(heading, file_content)` helper function
  Location hint: Private helper, before `resolve`

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_content_extraction -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.6: Output formatting (heading + content + navigation links)

**[Checkpoint: core resolver logic complete]**

**RED Phase:**

**Test:** `test_resolve_output_format`
**Assertions:**
- Full resolve output for trigger mode contains:
  - `"# When Writing Mock Tests"` (heading with `#` prefix)
  - Section content from decision file
  - `"Broader:"` section with ancestor links
  - `"Related:"` section with sibling links
- Sections separated by blank lines
- Heading uses H1 format (`#`) regardless of source level (H2/H3 in decision file)

**Expected failure:** AssertionError — output doesn't include navigation or formatting

**Why it fails:** Output formatting not yet combining content + navigation

**Verify RED:** `pytest tests/test_when_resolver.py::test_resolve_output_format -v`

**GREEN Phase:**

**Implementation:** Combine content extraction with navigation.

**Behavior:**
- Format heading as H1 (`# When/How to <Heading Text>`)
- Append section content
- Compute ancestors and siblings via navigation module
- Append formatted navigation links
- Return complete formatted string

**Approach:** Call navigation.compute_ancestors() and compute_siblings(), format_navigation(), concatenate.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Integrate navigation module output into resolve return value
  Location hint: End of `resolve` function, after content extraction

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_resolve_output_format -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.7: Error handling — trigger not found

**RED Phase:**

**Test:** `test_trigger_not_found_suggests_matches`
**Assertions:**
- `resolve("when", "nonexistent topic xyz", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"No match for"` and the query text
- Error message contains `"Did you mean:"` followed by up to 3 closest fuzzy matches
- Each suggestion formatted as `/when <trigger>`

**Expected failure:** ResolveError raised but without suggestions, or wrong message format

**Why it fails:** Error message doesn't include fuzzy suggestions

**Verify RED:** `pytest tests/test_when_resolver.py::test_trigger_not_found_suggests_matches -v`

**GREEN Phase:**

**Implementation:** Add error handling with fuzzy suggestions.

**Behavior:**
- When best fuzzy match is below threshold (no valid match): raise ResolveError
- Use `fuzzy.rank_matches(query, all_candidates, limit=3)` to get closest matches
- Format error: `"No match for '<query>'. Did you mean:\n  /when <suggestion1>\n  /when <suggestion2>"`
- If no suggestions at all: just `"No match for '<query>'."`

**Approach:** After rank_matches returns empty or below threshold, re-query for top 3 regardless of threshold for suggestions.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add ResolveError class and trigger-not-found error with suggestions
  Location hint: Error handling in trigger mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_trigger_not_found_suggests_matches -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.8: Error handling — section not found

**RED Phase:**

**Test:** `test_section_not_found_lists_headings`
**Assertions:**
- `resolve("when", ".Nonexistent Section", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"Section 'Nonexistent Section' not found."`
- Error message contains `"Available:"` followed by list of actual heading names
- Available headings formatted as `.HeadingName` (one per line)

**Expected failure:** ResolveError raised but without available headings list

**Why it fails:** Section-not-found error doesn't list alternatives

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_not_found_lists_headings -v`

**GREEN Phase:**

**Implementation:** Add section-not-found error with available headings.

**Behavior:**
- When heading lookup fails: raise ResolveError
- Collect all headings from all decision files
- Format: `"Section '<name>' not found. Available:\n  .Heading1\n  .Heading2"`
- Limit to first 10 suggestions (prevent overwhelming output)

**Approach:** Use already-collected heading mapping from section mode. Format as `.` prefixed list.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add section-not-found error formatting
  Location hint: Section mode error branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_not_found_lists_headings -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 3.9: Error handling — file not found

**RED Phase:**

**Test:** `test_file_not_found_lists_files`
**Assertions:**
- `resolve("when", "..nonexistent.md", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"File 'nonexistent.md' not found in agents/decisions/."`
- Error message contains `"Available:"` followed by list of actual `.md` files
- Available files formatted as `..filename.md` (one per line)

**Expected failure:** ResolveError raised but without available files list

**Why it fails:** File-not-found error doesn't list alternatives

**Verify RED:** `pytest tests/test_when_resolver.py::test_file_not_found_lists_files -v`

**GREEN Phase:**

**Implementation:** Add file-not-found error with available files list.

**Behavior:**
- When file doesn't exist: raise ResolveError
- List all `.md` files in decisions_dir
- Format: `"File '<name>' not found in agents/decisions/. Available:\n  ..cli.md\n  ..testing.md"`
- Files sorted alphabetically

**Approach:** `sorted(decisions_dir.glob("*.md"))` for file listing.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add file-not-found error formatting
  Location hint: File mode error branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_file_not_found_lists_files -v`
**Verify no regression:** `pytest tests/ -q`
