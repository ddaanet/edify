### Phase 2: Session.md parser (type: tdd, model: sonnet)

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

## Cycle 2.1: Parse all session.md sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_session_sections[status_line]`, `test_parse_session_sections[completed]`, `test_parse_session_sections[in_tree_tasks]`, `test_parse_session_sections[worktree_tasks]`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_status_line(content)` returns the text between `# Session Handoff:` date line and first `## ` heading, stripped
- `parse_completed_section(content)` returns list of lines under `## Completed This Session` heading (up to next `## `)
- `parse_tasks(content, section="In-tree Tasks")` returns list of `ParsedTask` objects with `model`, `command`, `restart`, `worktree_marker` fields populated. Task with `→ slug` has `worktree_marker="slug"`. Task with `→ wt` has `worktree_marker="wt"`
- `parse_tasks(content, section="Worktree Tasks")` returns same structure for worktree section
- Each task has `plan_dir` attribute populated from continuation lines (`Plan:` or `plans/<name>/` in command)

**Edge case tests:**
- `test_parse_status_line_missing` — content without `# Session Handoff:` returns None
- `test_parse_tasks_old_format` — task line without pipe-separated metadata returns ParsedTask with `model=None`, `restart=False`
- `test_parse_tasks_empty_section` — section heading present but no tasks returns `[]`
- `test_parse_completed_section_empty` — heading present, no content returns `[]`

**Fixture:** `SESSION_MD_FIXTURE` — realistic session.md with:
```markdown
# Session Handoff: 2026-03-07

**Status:** Phase 1 complete — infrastructure ready.

## Completed This Session

**Phase 1 infrastructure:**
- Extracted git helpers
- Created package structure

## In-tree Tasks

- [ ] **Build parser** — `/runbook plans/parser/design.md` | sonnet
  - Plan: parser | Status: outlined
- [ ] **Fix bug** — `just fix-bug` | haiku
- [x] **Done task** — `/commit` | sonnet

## Worktree Tasks

- [ ] **Parallel work** → `my-slug` — `/design plans/parallel/problem.md` | opus | restart
- [ ] **Future work** → `wt` — `/design plans/future/problem.md` | sonnet
```

**Expected failure:** `ImportError` or `AttributeError` — functions don't exist yet

**Why it fails:** No `session/parse.py` module with these functions

**Verify RED:** `pytest tests/test_session_parser.py -v`

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
- `test_parse_session_old_format` — session.md with tasks lacking pipe-separated metadata → `ParsedTask` objects with `model=None`, `restart=False` (defaults, not error)

**Expected failure:** `ImportError` — `SessionData` class doesn't exist

**Why it fails:** No `SessionData` dataclass or `parse_session()` function

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_session -v`

---

**GREEN Phase:**

**Implementation:** Add `SessionData` dataclass and `parse_session()` to `session/parse.py`

**Behavior:**
- `SessionData` dataclass with typed fields for all sections
- `parse_session(path: Path) -> SessionData` — reads file, calls section parsers from Cycle 2.1, assembles into `SessionData`
- Missing file → raise `SessionFileError` (defined in `session/parse.py` or `claudeutils/exceptions.py`)
- Date extraction: parse from `# Session Handoff: YYYY-MM-DD` header line via regex

**Approach:** Thin orchestration function composing the section parsers.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Add `SessionData` dataclass and `parse_session()` function
  Location hint: After section parser functions
- File: `src/claudeutils/exceptions.py` (if appropriate)
  Action: Add `SessionFileError(ClaudeUtilsError)` if exceptions are centralized there

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---

**Phase 2 Checkpoint:** All parser tests pass, `just precommit` clean.
