# Vet Review: hook-batch final quality review

**Scope**: All deliverables from 5 phases — `git diff --name-only ea706dca..HEAD` (changed files in parent repo) plus agent-core submodule changes
**Date**: 2026-02-21T17:20:09
**Mode**: review + fix

## Summary

The hook-batch implementation is structurally complete: all five hook event types are implemented (UserPromptSubmit, PreToolUse, PostToolUse, SessionStart, Stop), settings.json is correctly wired, and all hook scripts are executable and symlinked. One critical functional gap exists: the `--summary` flag for `learning-ages.py` was implemented on the agent-core `hook-batch` branch but not merged into the current HEAD, causing the health check scripts to always fall back to "⚠️ Learnings status unavailable". The flag has been added. Two minor issues were also fixed: a stale module docstring and a section banner comment.

**Overall Assessment**: Ready (post-fix)

## Issues Found

### Critical Issues

1. **`--summary` flag missing from `learning-ages.py`**
   - Location: `agent-core/bin/learning-ages.py`
   - Problem: Both `sessionstart-health.sh` and `stop-health-fallback.sh` call `learning-ages.py --summary` to get a one-liner for health output. The flag was implemented on the agent-core `hook-batch` branch (commit `1e699fb`) but not included in the current HEAD (`5f1848d`), which is the result of a separate merge path. The flag is absent from `main()`. Every health check run produces "⚠️ Learnings status unavailable" instead of the actual status.
   - Fix: Add `--summary` branch to `learning-ages.py:main()` after computing summary statistics, before the full markdown report output.
   - **Status**: FIXED — added `if '--summary' in sys.argv:` branch at `agent-core/bin/learning-ages.py:196-206`

### Major Issues

1. **`tdd-process-review.md` is an untracked deliverable**
   - Location: `plans/hook-batch/reports/tdd-process-review.md`
   - Problem: The TDD process review document (produced during Phase 5 orchestration review) is untracked by git. Per the "clean tree after every step" invariant, all generated artifacts must be committed. The file contains substantive analysis of 7 TDD cycles and process recommendations.
   - Fix: Commit the file.
   - **Status**: DEFERRED — this file was created outside the executed runbook steps (it appears to be a post-execution review document, not produced by a runbook step agent). Flagging for user to commit intentionally.

### Minor Issues

1. **Stale module docstring in `userpromptsubmit-shortcuts.py`**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py:1-11`
   - Note: Docstring said "Tier 2 - Directives: d:, p:" but implementation has d:, p:, b:, q:, learn: plus Tier 2.5 guards. Misleads readers about hook capability.
   - **Status**: FIXED — updated to list all directives and mention Tier 2.5 guards

2. **Section banner comment in `userpromptsubmit-shortcuts.py`**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py` (was line ~280)
   - Note: `# Context filtering constants` with no constants beneath it (only functions). Violates deslop rule: "No section banners."
   - **Status**: FIXED — removed the comment

3. **Extra blank line between functions in `userpromptsubmit-shortcuts.py`**
   - Location: Between `is_line_in_fence` and `scan_for_directives` (was line ~211)
   - Note: Three blank lines between top-level functions where PEP 8 requires two. Ruff would flag this.
   - **Status**: FIXED — removed extra blank line (ruff autoformat also applied additional cleanup)

## Fixes Applied

- `agent-core/bin/learning-ages.py:196-206` — Added `--summary` flag branch: one-liner output for hook injection, exits before full markdown report
- `agent-core/hooks/userpromptsubmit-shortcuts.py:1-14` — Updated module docstring to list all implemented tiers and directives
- `agent-core/hooks/userpromptsubmit-shortcuts.py` (was ~280) — Removed `# Context filtering constants` section banner
- `agent-core/hooks/userpromptsubmit-shortcuts.py` (was ~211) — Removed extra blank line between `is_line_in_fence` and `scan_for_directives`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Line-based shortcut matching | Satisfied | `main()` splits on `\n`, checks each line; tests in `test_userpromptsubmit_shortcuts.py:60-72` |
| r expansion graduated lookup | Satisfied | `COMMANDS['r']` includes conversation context → session.md → git status steps |
| xc/hc bracket compression | Satisfied | `COMMANDS['xc']`/`COMMANDS['hc']` use `[execute, commit]`/`[handoff, commit]` format |
| Additive directives (D-7) | Satisfied | `scan_for_directives` returns all matches; `main()` collects all into `context_parts` |
| p: dual output | Satisfied | p: adds to both `context_parts` (full) and `system_parts` (concise) |
| b: brainstorm directive | Satisfied | `_BRAINSTORM_EXPANSION`, `DIRECTIVES['b']`, tests in `test_userpromptsubmit_new_directives.py:64-75` |
| q: + learn: directives | Satisfied | `_QUICK_EXPANSION`, `_LEARN_EXPANSION`, tested |
| Skill-editing guard | Satisfied | `EDIT_SKILL_PATTERN`, `EDIT_SLASH_PATTERN`, tests in `test_userpromptsubmit_shortcuts.py:103-128` |
| CCG pattern guard | Satisfied | `CCG_PATTERN`, tests in `test_userpromptsubmit_shortcuts.py:129-153` |
| PreToolUse recipe-redirect | Satisfied | `agent-core/hooks/pretooluse-recipe-redirect.py`, 21 tests passing |
| PostToolUse auto-format | Satisfied | `agent-core/hooks/posttooluse-autoformat.sh`, registered in settings.json |
| SessionStart health | Satisfied | `agent-core/hooks/sessionstart-health.sh`, 3 health checks, flag file mechanism |
| Stop health fallback | Satisfied | `agent-core/hooks/stop-health-fallback.sh`, flag file check → skip or run |
| learning-ages.py --summary | Satisfied (post-fix) | Added in this review; health scripts call with `\|\| echo` fallback |
| hooks.json source of truth (D-8) | Satisfied | `agent-core/hooks/hooks.json` exists, `sync-hooks-config.py` merges it |
| sync-to-parent update | Satisfied | `agent-core/justfile` calls `python3 bin/sync-hooks-config.py` |
| settings.json integration | Satisfied | All 5 hook event types registered in `.claude/settings.json` |
| Hook scripts executable | Satisfied | All scripts have `rwxr-xr-x` permissions |
| Hook symlinks in .claude/hooks/ | Satisfied | 9 symlinks verified with `ls -la` |

**Gaps**: None — all design requirements satisfied post-fix.

---

## Positive Observations

- `pretooluse-recipe-redirect.py` is minimal (35 lines) and correctly orders checks: `git merge` before generic `git worktree`, bare `ln` alongside `ln ` prefix. No over-engineering.
- Health scripts degrade gracefully: `|| echo "⚠️ Learnings status unavailable"` means failure of any health check doesn't break the hook.
- Flag file mechanism (SessionStart writes, Stop checks) correctly handles the #10373 bypass design without race conditions (Stop runs after session completes).
- Test coverage is thorough: fence detection, additive directive scanning, pattern guard false positive exclusion, and redirect command boundaries all have dedicated tests.
- `sync-hooks-config.py` idempotent merge logic (dedup by command string) prevents duplicate hook registrations on repeated sync runs.
- posttooluse-autoformat.sh correctly reads stdin once via `python3 -c` and degrades silently on failure, consistent with PostToolUse non-fatal contract.

## Recommendations

- Commit `plans/hook-batch/reports/tdd-process-review.md` — substantive analysis with actionable process recommendations (dedup `call_hook` across 3 test files, fix execution report cycle ordering).
- The `call_hook` helper is duplicated across `test_userpromptsubmit_shortcuts.py`, `test_userpromptsubmit_scanning.py`, and `test_userpromptsubmit_new_directives.py`. The tdd-process-review correctly identifies a `tests/helpers.py` module as the resolution path — worth addressing before adding more tests.
