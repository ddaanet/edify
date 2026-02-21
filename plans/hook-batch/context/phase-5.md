# Phase 5: Hook Infrastructure + Integration

**Type:** General | **Model:** haiku (except Step 5.3: sonnet)
**Target files:**
- `agent-core/hooks/hooks.json` (new — config source of truth)
- `agent-core/bin/sync-hooks-config.py` (new — merge helper)
- `agent-core/justfile` (modify — add hooks sync to sync-to-parent recipe)

## Prerequisites

- Step 5.3 requires Sonnet model (justfile edit requires careful placement and context); all other steps use phase default haiku.
- Verify Phases 1-4 complete: all 5 hook scripts exist:
  - `agent-core/hooks/userpromptsubmit-shortcuts.py` (existing, Phase 1 modified)
  - `agent-core/hooks/pretooluse-recipe-redirect.py` (Phase 2)
  - `agent-core/hooks/posttooluse-autoformat.sh` (Phase 3)
  - `agent-core/hooks/sessionstart-health.sh` (Phase 4)
  - `agent-core/hooks/stop-health-fallback.sh` (Phase 4)
- Read `.claude/settings.json` hooks section — understand existing hook registrations (3 existing entries: UserPromptSubmit, PreToolUse Write|Edit, PostToolUse Bash). Merge must preserve all.
- `settings.json` is in `denyWithinAllow` → Steps 5.2 and 5.4 require `dangerouslyDisableSandbox: true`

## Key Decisions

- D-8: hooks.json is config source of truth for agent-core hooks; settings.json is generated output
- Existing project-local hooks (pretooluse-block-tmp.sh, pretooluse-symlink-redirect.sh) stay in `.claude/settings.json` only — NOT in hooks.json (project-local, not agent-core portable)
- sync-hooks-config.py is idempotent (dedup by command string)
- sync-to-parent recipe calls sync-hooks-config.py after symlink sync

## Completion Validation

Success criteria:
- `agent-core/hooks/hooks.json` valid JSON with 5 event entries
- `agent-core/bin/sync-hooks-config.py` idempotent, handles all merge cases
- `agent-core/justfile` sync-to-parent calls sync-hooks-config.py
- `.claude/settings.json` has all new hooks merged
- All existing hooks preserved: UPS, PreToolUse Write|Edit (block-tmp + symlink-redirect), PostToolUse Bash (submodule-safety)
- `pytest tests/ -v` → all tests pass

Restart required: Session restart activates new hooks.
Depends on: All phases 1-4 must be complete before Step 5.4.
