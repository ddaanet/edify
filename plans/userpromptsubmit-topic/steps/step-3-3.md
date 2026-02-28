# Cycle 3.3

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

## Cycle 3.3: No-match passthrough

**RED Phase:**

**Test:** `test_topic_injection_silent_on_no_match`
**Assertions:**
- Same fixture setup as 3.1 (memory-index + decision files in tmp_path)
- Monkeypatch stdin with JSON `{"prompt": "hello world"}` (no matching keywords for any index entry)
- Invoke hook `main()` (capture stdout)
- Assert either: (a) no output at all (complete pass-through, exit 0), or (b) if other features match, output contains no topic-related content in additionalContext or systemMessage
- Specifically: if output exists, assert "topic" not in `output.get("systemMessage", "")`

**Expected failure:** Test should pass if `match_topics()` correctly returns empty result on no matches

**Why it fails:** If it fails — `match_topics()` injects content even with no keyword overlap, or raises an exception

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_silent_on_no_match -v`

**GREEN Phase:**

**Implementation:** Ensure `match_topics()` returns empty `TopicMatchResult` when no candidates score above threshold. Hook checks for non-empty before appending.

**Behavior:**
- `format_output([])` returns `TopicMatchResult(context="", system_message="")`
- Hook: `if result.context:` guard before appending to `context_parts`
- Hook: `if result.system_message:` guard before appending to `system_parts`

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Verify `match_topics()` returns empty result on no matches (may already work from format_output empty-input handling)
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Verify guard conditions on result before appending (may already be in place from 3.1)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_silent_on_no_match -v`
**Verify no regression:** `just test`

---

**Full checkpoint** after Phase 3: `just dev` + review accumulated changes + verify dual-channel output in integration tests.
