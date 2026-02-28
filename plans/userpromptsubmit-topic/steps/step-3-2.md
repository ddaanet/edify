# Cycle 3.2

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

## Cycle 3.2: Additive with existing features

**RED Phase:**

**Test:** `test_topic_injection_additive_with_commands`
**Assertions:**
- Same fixture setup as 3.1 (memory-index + decision files in tmp_path)
- Monkeypatch stdin with JSON `{"prompt": "s\nhow does recall work"}` (command "s" on first line + topic keywords on second)
- Invoke hook `main()` (capture stdout)
- Parse JSON output
- Assert `output["hookSpecificOutput"]["additionalContext"]` contains BOTH command expansion text (from "s" shortcut) AND topic decision content
- Assert `output["systemMessage"]` contains command expansion AND topic trigger info (both features visible)

**Expected failure:** Test should pass if parallel architecture works correctly. If it fails, accumulation logic has a bug.

**Why it fails:** If it fails — interference between command expansion and topic injection in accumulator logic

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_additive_with_commands -v`

**GREEN Phase:**

**Implementation:** No new code expected — the parallel accumulation architecture handles additive behavior. Both command expansion and topic injection append to `context_parts`/`system_parts` independently.

**Behavior:**
- If test passes immediately: confirms parallel architecture works. Mark cycle complete.
- If test fails: debug accumulation logic — check for early returns, overwriting, or conditional exclusions between features.

**Changes:**
- None expected. Debug-only if test fails.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_additive_with_commands -v`
**Verify no regression:** `just test`

---
