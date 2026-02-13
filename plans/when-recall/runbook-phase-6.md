# Phase 6: Validator Update

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy), Phase 1 (parser)
**Checkpoint:** Full checkpoint after this phase (validator critical for migration safety)
**Files:**
- `src/claudeutils/validation/memory_index.py` (facade)
- `src/claudeutils/validation/memory_index_checks.py` (check functions)
- `src/claudeutils/validation/memory_index_helpers.py` (autofix, extraction)
- `tests/test_validation_memory_index.py` (extend existing)
- `tests/test_validation_memory_index_autofix.py` (extend existing)

**Design reference:** Validator Changes section, "Validation checks (updated)" table

**Prior state:**
- Phase 0: `fuzzy.score_match()` and `fuzzy.rank_matches()` available
- Phase 1: `WhenEntry` model and `parse_index()` available
- Existing validator: em-dash format, exact lowercase match, 8-15 word count

**Weak Orchestrator Metadata:**
- Total Steps: 7
- Model: haiku
- Execution: sequential (each cycle builds on prior validation infrastructure)

---

## Cycle 6.1: Replace em-dash parsing with `/when` format parsing

**Prerequisite:** Read `src/claudeutils/validation/memory_index.py:35-60` and `src/claudeutils/validation/memory_index_helpers.py:1-50` — understand `extract_index_entries()` current parsing

**RED Phase:**

**Test:** `test_validator_parses_when_format`
**Assertions:**
- `extract_index_entries(index_with_when_format, root)` returns entries keyed by trigger text
- Entry `/when writing mock tests | mock patch` → key `"writing mock tests"`, section from H2
- Old em-dash format `Key — description` → not parsed (returns empty for that line)
- Entry count matches number of `/when` and `/how` lines

**Expected failure:** AssertionError — validator still parsing em-dash format, not `/when` format

**Why it fails:** `extract_index_entries` still uses em-dash parsing logic

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_validator_parses_when_format -v`

**GREEN Phase:**

**Implementation:** Update entry extraction to use `/when` format.

**Behavior:**
- Detect lines starting with `/when ` or `/how `
- Import and reuse `WhenEntry` model from `claudeutils.when.index_parser` for format consistency
- Key by trigger text (lowercase) instead of key text
- Preserve section tracking from H2 headings

**Approach:** Replace em-dash split logic with `/when`/`/how` prefix detection and pipe splitting. Reuse WhenEntry format spec.

**Changes:**
- File: `src/claudeutils/validation/memory_index.py`
  Action: Update `extract_index_entries()` to parse `/when` format
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update parallel extraction function if one exists there

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_validator_parses_when_format -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.2: Format validation (operator prefix, trigger non-empty, extras)

**RED Phase:**

**Test:** `test_format_validation_rules`
**Assertions:**
- `/when valid trigger` → passes format check
- `/when valid | extra1, extra2` → passes format check
- `/what invalid operator` → flagged as error (invalid operator)
- `/when` (no trigger) → flagged as error (empty trigger)
- `/when trigger | ,,,` → passes (empty extras silently dropped)
- Old em-dash format → flagged as error (no operator prefix)
- Each error includes line number and descriptive message

**Expected failure:** AssertionError — format validation still checking em-dash format

**Why it fails:** `check_em_dash_and_word_count()` still enforcing old rules

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_format_validation_rules -v`

**GREEN Phase:**

**Implementation:** Replace em-dash check with `/when` format validation.

**Behavior:**
- Check operator prefix (`/when` or `/how` required)
- Check trigger non-empty after stripping
- Check extras format (comma-separated, no empty segments — warning only)
- Remove word count check entirely (D-9: obsolete for trigger format)

**Approach:** Replace `check_em_dash_and_word_count()` with `check_trigger_format()`.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Replace `check_em_dash_and_word_count` with trigger format check
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update parallel check function if one exists

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_format_validation_rules -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.3: Fuzzy bidirectional integrity

**RED Phase:**

**Test:** `test_fuzzy_bidirectional_integrity`
**Assertions:**
- Index entry `/when writing mock tests` with heading `### When Writing Mock Tests` → passes (fuzzy match succeeds)
- Index entry `/when writing mock tests` with NO matching heading → error "orphan entry"
- Heading `### When Auth Fails` with NO index entry → error "orphan heading"
- Fuzzy matching bridges compression: trigger `"write mock test"` matches heading `"When Writing Mock Tests"` (fuzzy, not exact)

**Expected failure:** AssertionError — validation still using exact lowercase match

**Why it fails:** Bidirectional integrity check not yet using fuzzy engine

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_fuzzy_bidirectional_integrity -v`

**GREEN Phase:**

**Implementation:** Replace exact match with fuzzy matching for entry↔heading validation.

**Behavior:**
- For each index entry: fuzzy match `"{operator} {trigger}"` against all headings
- Must resolve to exactly one heading (unique expansion)
- For each semantic heading: check that at least one index entry fuzzy-matches it
- Import `fuzzy.score_match` from `claudeutils.when.fuzzy`

**Approach:** Replace `key.lower() == title.lower()` checks with `fuzzy.rank_matches()` scoring. Threshold determines match/no-match.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Import fuzzy engine, replace exact match with fuzzy matching in orphan checks
  Location hint: `check_orphan_entries` and orphan heading validation

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_fuzzy_bidirectional_integrity -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.4: Collision detection

**RED Phase:**

**Test:** `test_collision_detection`
**Assertions:**
- Two entries `/when mock test` and `/when mock testing` both fuzzy-matching heading `"When Mock Testing"` → error "collision: multiple entries resolve to same heading"
- Two entries resolving to different headings → no collision error
- Error message identifies both colliding entries with line numbers

**Expected failure:** AssertionError — collisions not detected

**Why it fails:** Collision detection not yet implemented

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_collision_detection -v`

**GREEN Phase:**

**Implementation:** Add collision detection.

**Behavior:**
- After fuzzy matching all entries to headings, check for heading duplication
- If multiple entries resolve to the same heading → collision error
- Report all colliding entries with line numbers and the shared heading

**Approach:** Build heading→entries reverse mapping. Any heading with >1 entry is a collision.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Add collision detection after fuzzy matching
  Location hint: New check function or extension of orphan check

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_collision_detection -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.5: Remove word count check

**RED Phase:**

**Test:** `test_word_count_removed`
**Assertions:**
- `/when a b` (2 words) → passes validation (previously would fail 8-word minimum)
- `/when very long trigger with many many many words in it` (11 words) → passes (no upper limit)
- `check_em_dash_and_word_count` function no longer called in validation pipeline
- No word count errors in validation output for valid `/when` entries

**Expected failure:** AssertionError — word count check still rejecting short triggers

**Why it fails:** Old word count validation still active

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_word_count_removed -v`

**GREEN Phase:**

**Implementation:** Remove word count validation.

**Behavior:**
- Remove `check_em_dash_and_word_count` from validation pipeline
- No word count constraint on triggers (D-9: triggers are intentionally short)
- Function may remain for backward compatibility but must not be called

**Approach:** Remove call from main validation flow. Delete function if no other callers.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Remove or deprecate `check_em_dash_and_word_count`
- File: `src/claudeutils/validation/memory_index.py`
  Action: Remove call to word count check in validation flow

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_word_count_removed -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.6: Update autofix for new format

**Prerequisite:** Read `src/claudeutils/validation/memory_index_helpers.py` — understand `autofix_index()` mechanics (placement, ordering, structural entry removal)

**RED Phase:**

**Test:** `test_autofix_new_format`
**Assertions:**
- Entry `/when mock test` in wrong file section → autofix moves to correct section (based on heading location)
- Entries out of file order within section → autofix reorders
- Entry pointing to structural heading (`.` prefix) → autofix removes
- After autofix: re-running validation produces zero errors

**Expected failure:** AssertionError — autofix doesn't handle `/when` format entries

**Why it fails:** Autofix still expects em-dash format for parsing/rewriting

**Verify RED:** `pytest tests/test_validation_memory_index_autofix.py::test_autofix_new_format -v`

**GREEN Phase:**

**Implementation:** Update autofix to handle `/when` format.

**Behavior:**
- Parse entries using `/when` format (reuse parser)
- Section placement: determine correct section from heading location (unchanged logic)
- Ordering: sort entries by heading position in file (unchanged logic)
- Structural removal: detect entries matching structural headings and remove (unchanged logic)
- Output: write `/when` format entries (not em-dash)

**Approach:** Update entry parsing in autofix while preserving placement/ordering/removal mechanics.

**Changes:**
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Update `autofix_index()` entry parsing and output formatting for `/when` format
  Location hint: Entry parsing and reconstruction logic

**Verify GREEN:** `pytest tests/test_validation_memory_index_autofix.py::test_autofix_new_format -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 6.7: Update EXEMPT_SECTIONS

**RED Phase:**

**Test:** `test_exempt_sections_updated`
**Assertions:**
- After migration, EXEMPT_SECTIONS is empty set (no exempt sections remain)
- Validation runs on ALL sections (no skipping)
- Old exempt section names ("Behavioral Rules", "Technical Decisions") are not in EXEMPT_SECTIONS
- If index still has old exempt sections, they're validated like any other section

**Expected failure:** AssertionError — EXEMPT_SECTIONS still contains old section names

**Why it fails:** EXEMPT_SECTIONS constant not yet updated

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_exempt_sections_updated -v`

**GREEN Phase:**

**Implementation:** Update EXEMPT_SECTIONS constant.

**Behavior:**
- Set `EXEMPT_SECTIONS = set()` (empty — no exempt sections after migration)
- All sections validated equally
- Old section names no longer receive special treatment

**Approach:** Change constant value. May need to update in both checks.py and helpers.py if duplicated.

**Changes:**
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Set `EXEMPT_SECTIONS = set()`
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Same update if constant is duplicated here

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_exempt_sections_updated -v`
**Verify no regression:** `pytest tests/ -q`
