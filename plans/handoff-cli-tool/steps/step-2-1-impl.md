# Cycle 2.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/parse.py` with section parsing functions

**Behavior:**
- `parse_status_line(content: str) -> str | None` — find `# Session Handoff:` line, return text between it and first `## ` heading. Uses existing `find_section_bounds()` pattern from `worktree/session.py`
- `parse_completed_section(content: str) -> list[str]` — extract lines under `## Completed This Session` heading up to next `## ` or EOF
- `parse_tasks(content: str, section: str = "In-tree Tasks") -> list[ParsedTask]` — reuse `extract_task_blocks(content, section=section)` from `worktree/session.py` to get TaskBlocks, then call `parse_task_line()` from `validation/task_parsing.py` for each block's first line. Extend `ParsedTask` with `plan_dir` by calling existing `_extract_plan_from_block()` from `worktree/session.py`
- Section name parameter makes in-tree and worktree parsing identical — single function, different section argument

**Approach:** Compose existing functions rather than rewriting. Import `find_section_bounds`, `extract_task_blocks`, `_extract_plan_from_block` from `worktree/session.py` and `parse_task_line` from `validation/task_parsing.py`.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Create with `parse_status_line`, `parse_completed_section`, `parse_tasks`
  Location hint: New file

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---
