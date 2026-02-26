# Session Handoff: 2026-02-26

**Status:** Hook output audit complete; design decisions established, implementation pending.

## Completed This Session

**PreToolUse recipe-redirect consolidation:**
- Extended `agent-core/hooks/pretooluse-recipe-redirect.py` with 5 new patterns: python/python3 script redirect (FR-1), python -m tool strip (FR-2), python -c block (FR-3), uv run redirect (FR-4), rm index.lock block (FR-5)
- Routing table architecture: `_match_blocks` (hard block, exit 2) + `_match_python_uv` + `_match_tool_wrappers` (soft redirect, additionalContext)
- Absorbed `pretooluse-block-rm-lock.sh` into consolidated Python script, deleted shell script
- All hook messages include rationale for agent compliance
- Removed "Script invocation" prose rule from CLAUDE.md — hook enforces mechanically
- Shortened all hook commands in settings.json: dropped `python3`/`bash` prefixes and `$CLAUDE_PROJECT_DIR` — scripts have shebangs, hooks run from project root
- Recall artifact: `plans/precommit-python3-redirect/recall-artifact.md` (keys-only format)
- Requirements: `plans/precommit-python3-redirect/requirements.md`

**Hook output audit:**
- Empirically verified output channel audience model via test hook (`tmp/test-hook-channels.py`, TEST=1–7)
- `additionalContext` → agent-only; `systemMessage` → user-only; `permissionDecisionReason` → both (repeats twice in CLI); stderr+exit 2 → both (1 line, `[hook-path]:` prefix noise)
- `permissionDecisionReason` + empty string falls back to "Blocked by hook" platform label — same 4 UI lines; short non-empty reason is better
- Design decisions: all `_Redirect` cases become blocks; remove `_Redirect`/`_Block` distinction (single block type); use `permissionDecision:deny` + short reason + `additionalContext` + `systemMessage`
- `pretooluse-recall-check.py` is architecturally broken — exit 0 advisory arrives after Task dispatches (no model re-run between PreToolUse hook and tool execution); must block; gate by `subagent_type` discriminator
- EXECUTION_AGENTS set: `{artisan, test-driver, corrector, runbook-corrector, design-corrector, outline-corrector, runbook-outline-corrector, tdd-auditor, refactor}`
- `userpromptsubmit-shortcuts.py` systemMessage design: brief expansions (c, y) → same text both audiences; Tier 2 injections → behavioral outline + non-blank line count e.g. `discuss: assess, stress-test, state verdict. (N lines)`; Tier 2.5 guards → authored ~60 char user summary; ~60 char terminal constraint (29 char prefix, 90 char width)
- Token count preferred over line count for injection weight; deferred — `claudeutils tokens` cache plan not located

## Pending Tasks

- [ ] **Hook output improvements** — Implement audit design decisions: pretooluse-recipe-redirect.py (remove _Redirect/_Block, all blocks via permissionDecision:deny + short reason + additionalContext + systemMessage), pretooluse-recall-check.py rewrite (agent-type discriminator, EXECUTION_AGENTS block gate), pretooluse-block-tmp.sh + pretooluse-symlink-redirect.sh migrate from exit 2 to permissionDecision:deny, userpromptsubmit-shortcuts.py systemMessage improvements (behavioral outlines for Tier 2, authored summaries for Tier 2.5, add c/y shortcuts) | sonnet

## Blockers / Gotchas

**Autoformatter invalidates Edit batches:** PostToolUse autoformat hook fires between sequential Edit calls on same file, causing stale-read errors. Use Write for multi-edit rewrites instead of sequential Edits.

**claudeutils tokens cache plan not located:** Token count in hook systemMessage (preferred over line count) requires `claudeutils tokens` without API latency. Searched all plan requirements.md files — no plan explicitly captures adding a file cache to `claudeutils tokens`. Use line count (non-blank lines) as fallback; swap when cache lands.

## Next Steps

Implement hook output improvements per design decisions above. Start with `pretooluse-recipe-redirect.py` (simplest — remove two classes, convert all cases to permissionDecision:deny JSON), then recall-check rewrite, then UPS systemMessage.

## Reference Files

- `tmp/test-hook-channels.py` — empirical test hook (ephemeral, can delete after implementation)
- `plans/precommit-python3-redirect/recall-artifact.md` — recall artifact for hook work
