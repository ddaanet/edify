# Phase 2: PreToolUse Recipe-Redirect Hook

**Type:** TDD | **Model:** sonnet
**Target:** `agent-core/hooks/pretooluse-recipe-redirect.py` (new file)
**Test file:** `tests/test_pretooluse_recipe_redirect.py` (new file)

## Prerequisites

- Read `agent-core/hooks/userpromptsubmit-shortcuts.py` main() — understand hook output JSON structure: `{hookSpecificOutput: {hookEventName, additionalContext}, systemMessage}`. PreToolUse hook uses `hookEventName: "PreToolUse"` and additionalContext only (no systemMessage per D-6).
- Read `tests/test_userpromptsubmit_shortcuts.py` lines 1-35 — understand `call_hook()` helper pattern (importlib.util loading, stdin mock, stdout capture). Replicate this pattern for the new test file.
- Verify `agent-core/hooks/pretooluse-recipe-redirect.py` does NOT exist yet — this is a new file.

## Key Decisions

- D-1: Command hook (not prompt) — deterministic, fast, no LLM cost
- D-2: Python (complex pattern matching)
- D-6: Informative only — exit 0, additionalContext injection, no blocking, no systemMessage
- Hook receives PreToolUse event with `tool_name: "Bash"` and `tool_input.command`
- Three redirect patterns: `ln` → `just sync-to-parent`, `git worktree` → `claudeutils _worktree`, `git merge` → `claudeutils _worktree merge`
- NOT patterns: `python3` and `python` commands are denied in settings.json but have no project recipe equivalent — do NOT add redirect for these

## Completion Validation

```bash
pytest tests/test_pretooluse_recipe_redirect.py tests/test_userpromptsubmit_shortcuts.py -v
```

Success criteria:
- All new tests pass: script loads, pass-through works, all 3 redirects fire correctly
- `test_passthrough_non_redirect_commands` passes — no false positives
- `test_output_format_when_match_exists` passes (format validation)
- All Phase 1 tests (`test_userpromptsubmit_shortcuts.py`) still pass

## Stop Conditions

- RED fails to fail → STOP: verify `pretooluse-recipe-redirect.py` doesn't exist yet (Cycle 2.1) or has no redirect logic yet (Cycle 2.2)
- GREEN passes without implementation → STOP: test too weak
- `git merge` redirect also fires on `git merge-base` → fix: use `command.startswith('git merge ')` or `command == 'git merge'` to avoid false positive
- Implementation needs architectural decision → STOP, escalate
