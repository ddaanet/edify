# Cycle 2.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

---

## Cycle 2.2: Full session.md parse — SessionData dataclass

**RED Phase:**

**Test:** `test_parse_session`, `test_parse_session_missing_file`, `test_parse_session_old_format`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_session(path)` returns `SessionData` with fields: `status_line: str | None`, `completed: list[str]`, `in_tree_tasks: list[ParsedTask]`, `worktree_tasks: list[ParsedTask]`, `date: str | None`
- All fields populated from the fixture session.md file
- `data.in_tree_tasks[0].name == "Build parser"` and `data.in_tree_tasks[0].plan_dir == "parser"`
- `data.worktree_tasks[0].worktree_marker == "my-slug"`
- `data.date` extracted from `# Session Handoff: 2026-03-07` → `"2026-03-07"`

**Error handling tests:**
- `test_parse_session_missing_file` — `parse_session(Path("nonexistent.md"))` raises `SessionFileError` (custom exception, not generic FileNotFoundError) — ST-2 fatal error
- `test_parse_session_old_format` — session.md with tasks lacking pipe-separated metadata → raises `SessionFileError` (exit 2). Mandatory metadata enforces plan-backed task rule — no silent defaults

**Expected failure:** `ImportError` — `SessionData` class doesn't exist

**Why it fails:** No `SessionData` dataclass or `parse_session()` function

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_session -v`

---
