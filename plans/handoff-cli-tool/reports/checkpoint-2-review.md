# Review: Phase 2 Checkpoint — Session.md Parser

**Scope**: Phase 2 — Shared session.md parser (`session/parse.py`) consumed by handoff and status subcommands. New `plan_dir` field added to `ParsedTask`. Tests in `tests/test_session_parser.py`.
**Date**: 2026-03-15
**Mode**: review + fix

## Summary

Phase 2 delivers the shared session.md parser composing existing `worktree/session.py` and `validation/task_parsing.py` functions. The implementation is architecturally sound: correct composition, no duplication, proper error handling for missing files. Two issues found: (1) old-format task handling deviates from the step spec (ST-2 requires `SessionFileError`, implementation silently returns defaults), classified UNFIXABLE due to a valid design tension at the shared-parser layer; (2) minor cleanup items fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Old-format tasks return silent defaults instead of raising SessionFileError**
   - Location: `src/claudeutils/session/parse.py` (parse_tasks, parse_session), `tests/test_session_parser.py` (lines 94-105, 154-171)
   - Problem: Step-2-1-test.md specifies `test_parse_tasks_old_format` should raise `SessionFileError`. Step-2-2-test.md specifies `test_parse_session_old_format` should raise `SessionFileError`. Outline ST-2: "Old format (no metadata) → fatal error (exit 2). Mandatory metadata enforces plan-backed task rule — no silent defaults." Both tests and implementation use lenient defaults (model=None, restart=False) instead.
   - Fix: Raise `SessionFileError` in `parse_tasks` when a task lacks mandatory metadata, OR defer enforcement to the consuming command (status.py in Phase 3). The shared parser serving both handoff and status means strict enforcement here would break handoff if any old-format task exists during migration.
   - **Status**: UNFIXABLE (U-DESIGN)
   - **Investigation:**
     1. Scope OUT: not listed — old format handling is in scope for Phase 2
     2. Design deferral: not found — ST-2 is explicitly called out in the outline
     3. Codebase patterns: `parse_session` is shared by handoff and status; handoff legitimately reads session.md which may have tasks in various states
     4. Conclusion: Two valid approaches exist with different failure characteristics. (A) Strict at parse layer: matches step spec literally, but breaks handoff use-case if any old-format task exists. (B) Lenient at parse layer, strict at status command: ST-2 enforcement belongs in Phase 3 `_status` implementation which has the exit-2 contract. The step spec encoded approach (A) but approach (B) is architecturally consistent with a shared parser. User decision needed: should parse.py raise on old format, or should status.py enforce ST-2?

### Minor Issues

1. **Phase reference in module docstring**
   - Location: `src/claudeutils/session/parse.py:1`
   - Note: `"""Session.md parser — shared by handoff and status subcommands (Phase 2)."""` — "Phase 2" is an implementation artifact that should not appear in deployed module docstrings.
   - **Status**: FIXED

2. **Phase reference in test file docstring**
   - Location: `tests/test_session_parser.py:1`
   - Note: `"""Tests for session.md parser (Phase 2)."""` — same issue.
   - **Status**: FIXED

3. **Section banner comment in test file**
   - Location: `tests/test_session_parser.py:129`
   - Note: `# --- Cycle 2.2: Full session parse ---` — no existing pattern for section banners in tests or src (confirmed grep). Project code quality rules flag these.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/session/parse.py:1` — removed "Phase 2" from module docstring
- `tests/test_session_parser.py:1` — removed "Phase 2" from test module docstring
- `tests/test_session_parser.py:129` — removed `# --- Cycle 2.2: Full session parse ---` section banner

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| S-4: Status line (between `# Session Handoff:` and first `##`) | Satisfied | `parse.py:46-67` |
| S-4: Completed section (under `## Completed This Session`) | Satisfied | `parse.py:70-81` |
| S-4: Pending tasks with metadata (model, command, restart, plan_dir) | Satisfied | `parse.py:84-109`, `task_parsing.py:43` |
| S-4: `→ slug` and `→ wt` markers | Satisfied | `WORKTREE_MARKER_PATTERN` in `task_parsing.py:21`; `wt` matches pattern |
| S-4: Worktree tasks section | Satisfied | `parse_tasks(content, section="Worktree Tasks")` |
| S-4: Plan directory associations | Satisfied | `_extract_plan_from_block()` composed in `parse_tasks` |
| S-4: Reuse existing parsing functions | Satisfied | imports `extract_task_blocks`, `find_section_bounds`, `_extract_plan_from_block` from `worktree/session.py` |
| ST-2: Missing file → SessionFileError | Satisfied | `parse.py:130-137` |
| ST-2: Old format → SessionFileError | Partial | UNFIXABLE (U-DESIGN) — see major issue 1 |
| Tests: All parser functions covered | Satisfied | 11/11 tests pass |

**Gaps:** ST-2 old format enforcement deferred — see UNFIXABLE major issue.

---

## Positive Observations

- Composition over reimplementation: `parse_tasks` correctly delegates to `extract_task_blocks`, `parse_task_line`, `_extract_plan_from_block` rather than duplicating their logic.
- `plan_dir` pipe-suffix stripping (`re.sub(r"\s*\|.*$", "", plan_dir)`) handles the `Plan: parser | Status: outlined` format correctly.
- `_extract_date` is private (underscore prefix) and absent from `__all__` — correct encapsulation for an internal helper.
- `SessionFileError` defined locally in `parse.py` rather than in `exceptions.py` — reasonable given it is parse-module-specific and exceptions.py is not shown to be the centralization point for all custom exceptions.
- `SessionData` field ordering matches logical parse order: date → status_line → completed → in_tree_tasks → worktree_tasks.
- `worktree_tasks` has `default_factory=list` — allows constructing `SessionData` without explicitly passing worktree tasks, useful for sessions without a Worktree Tasks section.

## Recommendations

For Phase 3 (`_status` implementation): enforce ST-2 at the command level — after `parse_session()` returns, check that all `in_tree_tasks` have non-None `model` fields. Raise/exit-2 there. This satisfies the design requirement without breaking the shared parser's use by handoff.
