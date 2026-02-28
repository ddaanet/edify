# Cycle 3.1

**Plan**: `plans/userpromptsubmit-topic/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Integrates topic matching into `agent-core/hooks/userpromptsubmit-shortcuts.py` as a parallel detector block. Tests in `tests/test_ups_topic_integration.py`.

**Phase-specific recall:** "when mapping hook output channel audiences" — additionalContext agent-only, systemMessage user-only. "when writing hook user-visible messages" — terminal constraint ~60 chars for content.

**xfail integration test:** At phase start, write xfail test for full hook → topic injection pipeline. Remove xfail at cycle 3.1 GREEN.

**Prerequisite:** Read existing hook integration test patterns in `tests/` — check for `main()` import patterns, stdin mocking, env variable setup.

---

---

## Cycle 3.1: Topic detector block in hook

**Prerequisite:** Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 874-958 — understand `main()` structure, accumulator pattern, output assembly. Read existing test patterns for hook invocation.

**RED Phase:**

**Test:** `test_hook_topic_injection_produces_additional_context`
**Assertions:**
- Set up fixture: memory-index file with 2 entries under a decision file heading, corresponding decision file with matching section headings and body content, all in tmp_path
- Monkeypatch environment: set `CLAUDE_PROJECT_DIR` to tmp_path (or equivalent path resolution)
- Monkeypatch stdin with JSON `{"prompt": "how does the recall system work"}`
- Invoke hook `main()` (capture stdout)
- Parse JSON output
- Assert `output["hookSpecificOutput"]["additionalContext"]` contains resolved decision content (section body text)
- Assert `output["systemMessage"]` contains "topic" and trigger key text

**Expected failure:** Output contains no topic-related content — hook doesn't call topic matcher yet

**Why it fails:** Topic detector block not added to `main()`

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_hook_topic_injection_produces_additional_context -v`

**GREEN Phase:**

**Implementation:** Add topic injection detector block and `match_topics()` entry point.

**Behavior:**
- `match_topics(prompt_text: str, index_path: Path, project_dir: Path, threshold: float = 0.3, max_entries: int = 3) -> TopicMatchResult` — top-level entry point wrapping full pipeline: `get_or_build_index` → `get_candidates` → `score_and_rank` → `resolve_entries` → `format_output`
- In hook `main()`: after pattern guards (line ~928), before continuation parsing (line ~930):
  - Determine memory-index path and project_dir from environment
  - Call `match_topics(prompt, index_path, project_dir)`
  - If result has non-empty context: append `result.context` to `context_parts`
  - If result has non-empty system_message: append `result.system_message` to `system_parts`
  - Wrap in try/except (silent failure — topic injection should never break the hook)

**Approach:** Import topic_matcher at top of hook file. Environment-based path resolution.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `match_topics()` top-level entry point
  Location hint: End of module, before `if __name__`
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add import of `match_topics` from `claudeutils.recall.topic_matcher`. Add detector block between pattern guards and continuation parsing sections.
  Location hint: After line 928 (CCG_PATTERN block), before line 930 (Tier 3 continuation)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_hook_topic_injection_produces_additional_context -v`
**Verify no regression:** `just test`

---
