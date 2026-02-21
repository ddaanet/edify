# Cycle 2.2

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.2: All Redirect Patterns (ln + git worktree + git merge)

**Objective:** Add all three redirect patterns in one parametrized cycle. Each match injects additionalContext explaining why the command is blocked and what to use instead.

---

**RED Phase:**

**Prerequisite:** Read `agent-core/hooks/pretooluse-recipe-redirect.py` — understand current pass-through structure. Note command extraction uses `tool_input.command`.

**Test:** `test_ln_command_redirect`
**File:** `tests/test_pretooluse_recipe_redirect.py` — add to new class `TestRedirectPatterns`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf agent-core/skills .claude/skills"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"just sync-to-parent"`
- `result["hookSpecificOutput"]["hookEventName"]` equals `"PreToolUse"`
- `result` does NOT have `"systemMessage"` key

**Test:** `test_ln_bare_command_redirect`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "ln"}})["hookSpecificOutput"]["additionalContext"]` contains `"just sync-to-parent"`
  (bare `ln` with no args still redirects)

**Test:** `test_git_worktree_redirect`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "git worktree add --detach ../my-task HEAD"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"claudeutils _worktree"`
- `result["hookSpecificOutput"]["additionalContext"]` does NOT contain `"claudeutils _worktree merge"` (generic worktree, not merge-specific)

**Test:** `test_git_merge_redirect`

**Assertions:**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "git merge main"}})` → non-empty
- `result["hookSpecificOutput"]["additionalContext"]` contains `"claudeutils _worktree merge"`

**Test:** `test_passthrough_non_redirect_commands`

**Assertions (all return `{}`):**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "git status"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "git log --oneline"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})` → `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "python3 script.py"}})` → `{}` (python3 denied in settings.json but has no recipe redirect)

**Test:** `test_output_format_when_match_exists`
(This was failing RED from Cycle 2.1 — it now passes)

**Assertions (verify from Cycle 2.1):**
- `result = call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf x y"}})`
- `"hookSpecificOutput"` in result, `result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"`
- `"additionalContext"` in result["hookSpecificOutput"]
- `"systemMessage"` not in result

**Expected failure:** `AssertionError` — `call_hook({"tool_name": "Bash", "tool_input": {"command": "ln -sf ..."}})` currently returns `{}` (script has no redirect logic, just pass-through)

**Why it fails:** No pattern-matching logic in `pretooluse-recipe-redirect.py` yet.

**Verify RED:** `pytest tests/test_pretooluse_recipe_redirect.py::TestRedirectPatterns -v`

---

**GREEN Phase:**

**Implementation:** Add three redirect pattern checks to `pretooluse-recipe-redirect.py` main().

**Behavior:**
- Check order matters — check `git merge` BEFORE generic `git` patterns; check `git worktree` before other git subcommands
- `ln` match: `command.startswith('ln ') or command == 'ln'`
- `git worktree` match: `command.startswith('git worktree')`
- `git merge` match: `command.startswith('git merge ')` or `command == 'git merge'`
- On match: build output dict with hookEventName "PreToolUse" and additionalContext; print JSON; return (don't sys.exit)
- No systemMessage (D-6)

**Redirect messages:**
- `ln`: "`ln` is blocked. Use `just sync-to-parent` instead — it encodes correct symlink targets, ordering, and cleanup of stale links."
- `git worktree`: "Use `claudeutils _worktree` instead of `git worktree`. It handles session.md updates, submodule registration, focused sessions, and branch management."
- `git merge`: "Use `claudeutils _worktree merge` instead of `git merge`. It handles session.md conflict resolution, submodule lifecycle, and merge invariants."

**Approach:** Three `if/elif` checks at top of main() body, after command extraction. Each branch builds output and returns.

**Changes:**
- File: `agent-core/hooks/pretooluse-recipe-redirect.py`
  Action: Add redirect pattern checks in main() after command extraction
  Location hint: before the final `sys.exit(0)` pass-through

**Verify GREEN:** `pytest tests/test_pretooluse_recipe_redirect.py -v`
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py tests/test_pretooluse_recipe_redirect.py -v`

---
