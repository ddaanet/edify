# Cycle 1.4

**Plan**: `plans/userpromptsubmit-topic/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Builds `src/claudeutils/recall/topic_matcher.py` — the complete matching pipeline from index construction through scoring, resolution, and output formatting. Tests in `tests/test_recall_topic_matcher.py`.

**API promotions folded into GREEN phases:**
- Cycle 1.1: promote `_extract_keywords` → `extract_keywords` in `index_parser.py` (update internal callers at lines 113, 138)
- Cycle 1.4: promote `_extract_section` → `extract_section` in `when/resolver.py` (update internal callers at lines 117, 225)

**Heading reconstruction:** `IndexEntry.key` stores trigger text without `/when` or `/how` prefix. Try both `## When {key}` and `## How to {key}` heading forms — `extract_section()` returns empty string on miss, so the fallback is free. If both miss, skip the entry (FR-3 silent-skip).

---

---

## Cycle 1.4: Resolve matched entries with error-path coverage

**Prerequisite:** Read `src/claudeutils/when/resolver.py` lines 307-339 — understand `_extract_section_content()` and `_extract_section()` heading boundary detection

**RED Phase:**

**Test:** `test_resolve_entries` (parametrized)

**Case 1 — happy path:**
**Assertions:**
- Given a matched entry referencing decision file created in tmp_path with heading `## When Evaluating Recall System Effectiveness` and body text "Anti-pattern: Measuring..."
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns list of `ResolvedEntry`
- Assert len(result) == 1
- Assert result[0].content contains "Evaluating Recall System Effectiveness"
- Assert result[0].content contains "Anti-pattern"
- Assert result[0].source_file matches the decision file path

**Case 2 — missing file:**
**Assertions:**
- Given entry referencing nonexistent file path
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns empty list
- Assert len(result) == 0, no exceptions raised

**Case 3 — missing section:**
**Assertions:**
- Given entry referencing real file but with key that doesn't match any heading
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns empty list
- Assert len(result) == 0, no exceptions raised

**Expected failure:** `AttributeError` — `resolve_entries` does not exist

**Why it fails:** Function not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_resolve_entries -v`

**GREEN Phase:**

**Implementation:** Add `resolve_entries()` to topic_matcher.py. Promote `_extract_section` to public API.

**Behavior:**
- For each `(entry, score)` tuple:
  - Construct file path: `project_dir / entry.referenced_file`
  - Try heading `## When {entry.key}` first, then `## How to {entry.key}` if first returns empty
  - Call `extract_section(file_path, heading)` for content extraction
  - Skip entry if both headings return empty (silent skip per FR-3)
- Return list of ResolvedEntry (dataclass with content, source_file, entry fields)

**Approach:** Define `ResolvedEntry` dataclass. Loop with try-both-headings fallback.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Rename `_extract_section` → `extract_section` (public API). Update internal callers at lines 117 and 225.
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `ResolvedEntry` dataclass and `resolve_entries(entries: list[tuple[IndexEntry, RelevanceScore]], project_dir: Path) -> list[ResolvedEntry]`
  Location hint: After `score_and_rank()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_resolve_entries -v`
**Verify no regression:** `just test`

---
