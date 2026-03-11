# Hook Batch 2

Two new hooks for tool-use governance. Builds on existing hook infrastructure in `agent-core/hooks/`.

## Requirements

### Functional Requirements

**FR-1: Tool deviation hook (PreToolUse)**
Block Bash invocations that use raw commands when dedicated tools exist. Fires before Bash tool use. Blocks: `grep`/`rg` (use Grep), `find` (use Glob), `cat`/`head`/`tail` (use Read). Allows: `sed` (occasionally useful, contentious), `ln` (blocked only as stopgap until `just sync-to-parent` habit sticks).
- Acceptance: `Bash(grep -r "pattern" .)` → PreToolUse blocks with "use Grep tool instead"
- Acceptance: `Bash(find . -name "*.py")` → PreToolUse blocks with "use Glob tool instead"
- Acceptance: `Bash(sed -i 's/foo/bar/' file.py)` → allowed (not blocked)
- Note: Complements existing `pretooluse-recipe-redirect.py` which handles recipe redirection

**FR-2: Block cd-chaining (PreToolUse)**
Prevent `cd <dir> && <command>` patterns in Bash tool invocations. Agents should use absolute paths or the `path` parameter instead.
- Acceptance: `Bash(cd src && python -m pytest)` → PreToolUse blocks with "use absolute path" message
- Acceptance: `cd` inside subshells `(cd dir && cmd)` or scripts → allowed (not top-level chaining)
- Acceptance: `cd /path && claude` → allowed (worktree launch commands use this pattern)

### Constraints

**C-1: Hook execution budget**
Each hook must complete in <500ms. Hooks run on every tool invocation — latency compounds across a session.

### Out of Scope

- Modifying existing hooks (pretooluse-recipe-redirect, pretooluse-recall-check) — those are separate maintenance
- UserPromptSubmit hooks (covered by existing userpromptsubmit-shortcuts.py)

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (both FRs are hooks)
