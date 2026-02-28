# Cycle 1.5

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

## Cycle 1.5: Format dual-channel output

**RED Phase:**

**Test:** `test_format_output_produces_context_and_system_parts`
**Assertions:**
- Given 2 ResolvedEntry objects:
  - entry_1: content="## When Evaluating...\nAnti-pattern: ...", source_file="agents/decisions/operational-practices.md", entry with key="evaluating recall system effectiveness"
  - entry_2: content="## When Too Many Rules...\nLLM adherence degrades...", source_file="agents/decisions/prompt-structure-research.md", entry with key="too many rules in context"
- `format_output([entry_1, entry_2])` returns `TopicMatchResult`
- Assert `result.context` contains "When Evaluating" AND "When Too Many Rules" (both sections)
- Assert `result.context` contains "Source: agents/decisions/operational-practices.md" (attribution)
- Assert `result.system_message` starts with "topic (N lines):"
- Assert `result.system_message` contains "evaluating recall system effectiveness"
- Assert `result.system_message` contains "too many rules in context"
- Assert `format_output([])` returns `TopicMatchResult` with empty context and empty system_message

**Expected failure:** `AttributeError` — `format_output` and `TopicMatchResult` do not exist

**Why it fails:** Not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_format_output_produces_context_and_system_parts -v`

**GREEN Phase:**

**Implementation:** Add `TopicMatchResult` dataclass and `format_output()` to topic_matcher.py.

**Behavior:**
- `TopicMatchResult`: dataclass with `context: str` and `system_message: str`
- Context format: Each resolved entry as "heading\ncontent\nSource: file_path", joined with `\n\n`
- System message format: `"topic (N lines):\ntrigger1\ntrigger2"` where triggers are entry keys (with pipe extras if present from original index entry). N = total lines in context.
- Empty input → empty strings in both fields

**Approach:** String formatting with line counting

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `TopicMatchResult` dataclass and `format_output(resolved: list[ResolvedEntry]) -> TopicMatchResult`
  Location hint: After `resolve_entries()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_format_output_produces_context_and_system_parts -v`
**Verify no regression:** `just test`

---

**Light checkpoint** after Phase 1: `just dev` + verify `topic_matcher.py` exports `match_topics()` entry point (added in Phase 3 integration — at this point verify module structure is clean and all 5 functions exist).

---
