# Vet Review: Phase 5 Final Checkpoint — Hook Batch

**Scope**: Phase 5 artifacts: hooks.json, sync-hooks-config.py, justfile, settings.json, .claude/.gitignore
**Date**: 2026-02-21T17:30:00
**Mode**: review + fix

## Summary

Phase 5 infrastructure is correctly designed and mostly implemented. The critical problem is that Phase 3 (`posttooluse-autoformat.sh`) and Phase 4 (`sessionstart-health.sh`, `stop-health-fallback.sh`) scripts were created on the agent-core `hook-batch` branch but were NOT merged into the commit that the submodule pointer tracks (`760287e`). settings.json and hooks.json reference these scripts but they are absent from `agent-core/hooks/` on disk. `just dev` passes only because precommit does not validate hook script existence.

The sync-hooks-config.py merge logic is correct and idempotent. The justfile integration is correct. settings.json hook entries correctly match hooks.json definitions.

**Overall Assessment**: Needs Significant Changes (pre-fix) → Needs Minor Changes (post-fix)

## Issues Found

### Critical Issues

1. **Phase 3/4 hook scripts missing from agent-core HEAD**
   - Location: `agent-core/hooks/` (filesystem)
   - Problem: `posttooluse-autoformat.sh`, `sessionstart-health.sh`, `stop-health-fallback.sh` exist on the agent-core `hook-batch` branch (commits `229bf1b`, `aa52d3d`, `b904b43`) but are not on the current HEAD (`760287e`). The merge at `118cd8b` was a one-sided merge — Phase 3/4 commits were left on the unmerged `hook-batch` branch. settings.json and hooks.json reference all three scripts. Any hook event that triggers these paths will fail silently with a missing script error.
   - Fix: Cherry-pick or merge Phase 3/4 scripts from the `hook-batch` branch into agent-core. Scripts are valid (reviewed at Phases 3/4) — just not present on HEAD.
   - **Status**: FIXED — scripts extracted from git history and written to agent-core/hooks/; agent-core submodule committed; parent submodule pointer updated.

### Major Issues

1. **Dead variable `new_hook_commands` in sync-hooks-config.py**
   - Location: `agent-core/bin/sync-hooks-config.py:68`
   - Problem: `new_hook_commands = {get_command_string(h) for h in new_entry.get("hooks", [])}` is computed but never used. The actual dedup logic constructs `existing_commands` separately for each branch. The dead variable is misleading — it implies the set is used for dedup but it is not.
   - Suggestion: Remove the dead variable.
   - **Status**: FIXED — removed line 68.

### Minor Issues

1. **Merge logic duplication in sync-hooks-config.py**
   - Location: `agent-core/bin/sync-hooks-config.py:70-110`
   - Note: The `matcher is None` and `matcher is not None` branches are nearly identical (differ only in the matcher equality check). Could be collapsed to a single function. Not blocking — the duplication is contained in one function.
   - **Status**: DEFERRED — refactoring for two identical branches is out of scope for this checkpoint. Code is correct.

## Fixes Applied

- `agent-core/hooks/posttooluse-autoformat.sh` — Created from git history commit `229bf1b`
- `agent-core/hooks/sessionstart-health.sh` — Created from git history commit `aa52d3d`
- `agent-core/hooks/stop-health-fallback.sh` — Created from git history commit `b904b43`
- `agent-core/bin/sync-hooks-config.py:68` — Removed dead `new_hook_commands` variable

## Lifecycle Audit (D-7)

**Flag files (`$TMPDIR/health-{session_id}`):**
- SessionStart writes flag on fire (sessionstart-health.sh)
- Stop reads flag to detect duplicate (stop-health-fallback.sh), writes if absent
- No explicit cleanup — flag files accumulate in $TMPDIR across sessions. TMPDIR is typically cleaned by OS on reboot; per-session file size is negligible (empty touch). No leak risk.

**settings.json merge state:**
- sync-hooks-config.py reads → merges → writes atomically (single write_json call). No partial state.
- Idempotency verified: dedup by command string; second run finds existing commands in `existing_commands` set, skips append. Correct.

**sync-hooks-config.py re-run:**
- All 5 event types present in hooks.json. On re-run, each event's matcher is found in existing_hooks → `matching_entry_idx` resolves → `existing_commands` is built from current settings.json entries → new hooks already present, not appended. Idempotent. Confirmed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| hooks.json as config source of truth (D-8) | Satisfied | `agent-core/hooks/hooks.json` contains all 5 event types |
| sync-to-parent merges hooks.json into settings.json | Satisfied | `agent-core/justfile` sync-to-parent calls `python3 bin/sync-hooks-config.py` |
| Idempotent merge (dedup by command string) | Satisfied | `sync-hooks-config.py` merge_hooks uses `existing_commands` set |
| Existing hooks preserved (PreToolUse Write\|Edit, PostToolUse Bash) | Satisfied | settings.json retains block-tmp, symlink-redirect, submodule-safety |
| SessionStart and Stop events registered | Satisfied | Both present in settings.json and hooks.json |
| PreToolUse Bash: recipe-redirect alongside submodule-safety | Satisfied | settings.json PreToolUse Bash has both hooks |
| PostToolUse Write\|Edit: auto-format registered | Satisfied | settings.json PostToolUse Write\|Edit has posttooluse-autoformat.sh |
| UserPromptSubmit: unchanged (same script, new behavior) | Satisfied | settings.json UserPromptSubmit matches hooks.json |
| .claude/hooks symlinks gitignored | Satisfied | `.claude/.gitignore` contains `hooks/` |
| All hook scripts present on disk | Partial (pre-fix) → Satisfied (post-fix) | Phase 3/4 scripts were missing; restored from git history |

## Positive Observations

- hooks.json JSON is valid; all 5 event types match settings.json entries exactly after sync.
- sync-hooks-config.py path resolution handles both `CLAUDE_PROJECT_DIR` env var and relative path fallback correctly.
- write_json adds trailing newline (`f.write('\n')`) — consistent with project JSON style.
- justfile uses `python3 bin/sync-hooks-config.py` (correct relative path from agent-core working directory after Step 5.4 fix).
- `just dev` passes (tests cached, no regressions).
- `.gitignore` correctly targets `hooks/` (the generated symlink directory) without gitignoring the hooks source files in agent-core.
