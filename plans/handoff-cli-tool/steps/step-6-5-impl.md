# Cycle 6.5

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

**GREEN Phase:**

**Implementation:** Extract output formatting to testable functions

**Behavior:**
- Extract output formatting to a dedicated function that accepts submodule outputs (keyed by path), parent output string, and any warning messages
- Submodule outputs labeled with `<path>:` prefix
- Parent output appended unlabeled
- Warnings prepended as `**Warning:**` lines with blank line separator
- Strip git `hint:` and advice lines from output — LLM agents interpret these as instructions (e.g., "remove index.lock" → agent deletes the file)
- For failures: separate formatting per gate type already produces structured markdown

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Extract `format_commit_output()` from pipeline logic, include hint-line stripping

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---
