# Review: Phase 2 Checkpoint — Hook Migration

**Scope**: Phase 2 changed files: `.edify.yaml`, `plugin` (submodule pointer), `plans/plugin-migration/reports/hook-audit.md`
**Date**: 2026-03-21
**Mode**: review + fix

## Summary

Phase 2 delivers hook migration to plugin (hooks.json), consolidated setup hook (sessionstart-health.sh), and env var audit. The core deliverables are structurally correct: hooks.json is in wrapper format, all 9 surviving hooks are wired, `pretooluse-symlink-redirect.sh` is deleted, and sessionstart-health.sh integrates the setup responsibilities (env export, venv install, version write, staleness nag). One critical bug was found in `stop-health-fallback.sh` — it crashes when `CLAUDE_PLUGIN_ROOT` is not set. One minor inconsistency was found in hooks.json command invocation style.

`just dev` passes (precommit clean before fixes).

**Overall Assessment**: Needs Minor Changes (post-fix: Ready)

## Issues Found

### Critical Issues

1. **`stop-health-fallback.sh` crashes with unbound variable**
   - Location: `plugin/hooks/stop-health-fallback.sh:28`
   - Problem: `python3 "$CLAUDE_PLUGIN_ROOT/bin/learning-ages.py"` uses bare `$CLAUDE_PLUGIN_ROOT`. With `set -euo pipefail`, this triggers `unbound variable` when `CLAUDE_PLUGIN_ROOT` is not exported (e.g., direct test invocation, or if hook fires outside plugin context). Confirmed: `bash stop-health-fallback.sh <<< '...'` exits 1 with "CLAUDE_PLUGIN_ROOT: unbound variable". The identical line in `sessionstart-health.sh` correctly uses `${CLAUDE_PLUGIN_ROOT:-}` safe form (line 97).
   - Fix: Change to `${CLAUDE_PLUGIN_ROOT:-}` pattern, matching sessionstart-health.sh line 97.
   - **Status**: FIXED

### Major Issues

None.

### Minor Issues

1. **Inconsistent `python3` prefix in hooks.json commands**
   - Location: `plugin/hooks/hooks.json:22,61`
   - Note: `pretooluse-recipe-redirect.py` and `userpromptsubmit-shortcuts.py` are invoked as `python3 $CLAUDE_PLUGIN_ROOT/hooks/...py` while `submodule-safety.py` and `pretooluse-recall-check.py` are invoked directly (no `python3` prefix). All four scripts have shebangs (`#!/usr/bin/env python3`) and are executable. Notably, `pretooluse-recipe-redirect.py` itself blocks `python3 script.py` invocations from agent Bash commands — inconsistent that hooks.json uses that pattern. Fix: remove `python3` prefix from both commands.
   - **Status**: FIXED

## Fixes Applied

- `plugin/hooks/stop-health-fallback.sh:28` — Changed `"$CLAUDE_PLUGIN_ROOT/bin/learning-ages.py"` to `"${CLAUDE_PLUGIN_ROOT:-}/bin/learning-ages.py"` and `"$CLAUDE_PROJECT_DIR/agents/learnings.md"` to `"${CLAUDE_PROJECT_DIR:-$PWD}/agents/learnings.md"` — matches sessionstart-health.sh safe form pattern, prevents unbound variable crash when hook fires outside plugin context
- `plugin/hooks/hooks.json:22,61` — Removed `python3` prefix from `pretooluse-recipe-redirect.py` and `userpromptsubmit-shortcuts.py` command entries — all .py hook scripts have shebangs and are executable, consistent with submodule-safety.py and pretooluse-recall-check.py invocation style

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 (plugin auto-discovery) | Partial | hooks.json exists in plugin hooks/ dir for auto-discovery; symlink cleanup in Phase 6 |
| FR-5 (stale fragment nag) | Satisfied | sessionstart-health.sh§79-83: version comparison + additionalContext nag |
| FR-9 (all hooks migrate to plugin) | Satisfied | hooks.json contains all 9 surviving hooks across 5 event types |
| FR-10 (version provenance write) | Satisfied | sessionstart-health.sh§41-84: reads plugin.json version, writes .edify.yaml |
| FR-11 (CLI venv install) | Satisfied | sessionstart-health.sh§22-39: uv venv + pip install with fallback |

**Gaps**: FR-9 is satisfied at the plugin level but settings.json hooks section not yet cleared — that is Phase 6 scope (OUT for this phase).

---

## Positive Observations

- sessionstart-health.sh uses correct safe-form env var references (`${CLAUDE_PLUGIN_ROOT:-}`, `${CLAUDE_PROJECT_DIR:-$PWD}`) throughout setup section
- Consolidated setup hook approach (no separate edify-setup.sh) is cleaner than original design
- All setup failures are non-fatal — appended to `message`, script always outputs `systemMessage`
- `pretooluse-symlink-redirect.sh` correctly deleted (purpose eliminated)
- hooks.json wrapper format (`{"hooks": {...}}`) matches outline correction D-4 (corrects design.md)
- No remaining `plugin/` bare references in any hook script (grep confirms)
- hook-audit.md provides per-script findings with rationale — good traceability
- `.edify.yaml` version (`0.0.2`) matches plugin.json version (`0.0.2`) — version provenance working

## Deferred Items

The following items were identified but are out of scope:
- **settings.json hooks section not emptied** — Reason: Phase 6 scope (symlink cleanup + settings.json cleanup). Outline Component 6 explicitly defers this.
