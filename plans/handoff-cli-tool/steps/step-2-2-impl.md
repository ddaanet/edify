# Cycle 2.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

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
