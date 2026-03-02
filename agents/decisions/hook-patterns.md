# Hook and Session Patterns

Claude Code hook configuration, output channels, session mechanics, and sub-agent constraints.

## .Claude Code Hooks and Sessions

### When Using Session Start Hooks

**Context:** SessionStart hook output is discarded for new interactive sessions.

**Issue:** [#10373](https://github.com/anthropics/claude-code/issues/10373) — `qz("startup")` never called for new interactive sessions.

**Works:** After `/clear`, `/compact`, or `--resume`.

**Workaround:** Use `@agents/session.md` in CLAUDE.md for task context (already loaded).

**Impact:** Don't build features depending on SessionStart until fixed upstream.

### How to Filter User Prompt Submit Hooks

**Decision:** UserPromptSubmit hooks fire on every prompt; no `matcher` field support.

**Pattern:** All filtering logic must be script-internal, not in settings.json configuration.

**Rationale:** Different hook events have different API capabilities; script-level filtering is more flexible.

**Example:** PreToolUse/PostToolUse support `matcher`, UserPromptSubmit does not.

### When Using Hooks In Subagents

**Anti-pattern:** Using PostToolUse hooks to capture Explore/claude-code-guide results.

**Problem:** Hooks don't fire in sub-agents spawned via Task tool. Task matcher fires on ALL Tasks (noisy).

**Correct pattern:** Session-log based capture (future work) or quiet agents that write their own reports.

**Impact:** Sub-agents can have tools (Bash, Write) but hook interceptors won't execute.

### When Needing Mcp Tools In Subagents

**Anti-pattern:** Assuming artisan or other sub-agents can call MCP tools (Context7, etc.).

**Correct pattern:** MCP tools only available in main session. Call directly from designer/planner, write results to report file for reuse.

**Confirmed:** Empirical test — artisan haiku has no access to `mcp__plugin_context7_context7__*` tools.

**Impact:** Context7 queries cost opus tokens when designer calls them, but results persist for planner reuse.

### When Skill Is Already Loaded

**Anti-pattern:** After `/clear`, treating loaded skill content as informational rather than actionable.

**Correct pattern:** If skill content is present in context (via command injection), execute it immediately.

**Rationale:** `/clear` resets conversation history but skill invocation injects actionable instructions. The skill IS the task — "fresh session" is not a reason to pause.

### When Hook Fragment Alignment Needed

**Decision:** Hook output must reinforce fragment instructions, never contradict.

**Anti-pattern:** Hook says "write now", fragment says "write on handoff" — agent follows hook (recency position).

**Rationale:** Hook content sits in recency zone, fragment in primacy zone. Contradictions resolve to recency — agent follows stronger signal.

### When Prompt Caching Differs From File Caching

**Decision:** Each Read appends new content block to conversation. "Caching" = prompt prefix matching at API level (92% reuse, 10% cost).

**Anti-pattern:** Assuming Claude Code deduplicates file reads or maintains a file cache.

**Rationale:** No application-level dedup. @-references (system prompt) are more cache-efficient than Read (messages) for always-needed content.

### When Sub-Agent Rules Not Injected

**Decision:** Rules files (`.claude/rules/`) fire in main session only; sub-agents don't receive injection.

**Anti-pattern:** Assuming sub-agents via Task tool receive rules file context.

**Consequence:** Domain context must be carried explicitly — planner writes it into runbook, orchestrator passes through task prompt.

### When Hook Commands Use Relative Paths

**Decision Date:** 2026-02-28

**Anti-pattern:** Hook command in settings.json uses relative path (`.claude/hooks/submodule-safety.py`). After agent cwd drifts (e.g., `cd subdir && ...`), the relative path resolves against the new cwd — hook script not found. Hook errors are non-blocking in Claude Code, so the guarded command proceeds without the hook.

**Irony:** The submodule-safety hook (designed to block cwd drift) was itself disabled by cwd drift.

**Correct pattern:** All hook commands must use `$CLAUDE_PROJECT_DIR/` prefix for absolute resolution. Claude Code sets this env var to the project root regardless of cwd.

**Evidence:** Agent ran 4+ bash commands from `agent-core/` subdirectory without the submodule-safety hook blocking. Hook errors visible on `git submodule status` confirmed the hook script wasn't found.

## .Hook Implementation Patterns

### When Writing Hook Redirect Messages

**Decision Date:** 2026-02-26

**Anti-pattern:** "Use X instead of Y" without explaining why. Agent sees the redirect but lacks rationale to internalize the preference — may override in future invocations.

**Correct pattern:** Include brief rationale in every hook message. Example: "Use X directly — python3 prefix breaks permissions.allow matching."

### When Mapping Hook Output Channel Audiences

**Decision Date:** 2026-02-26

Empirical findings (TEST=1–7):
- `additionalContext` → agent-only (system-reminder, no user output)
- `systemMessage` → user-only ("PreToolUse:Bash says: ...")
- `permissionDecisionReason` → both audiences, repeats twice in CLI
- stderr + exit 2 → both, 1 line, `[hook-path]:` prefix noise

**Correct pattern for PreToolUse blocks:** `permissionDecision:deny` JSON on exit 0. Short non-empty `permissionDecisionReason` (both audiences, keep brief); `additionalContext` for extended agent instructions (agent-only); `systemMessage` for user summary (user-only, ~60 chars). Supersedes command-shortening workaround — `permissionDecision:deny` eliminates path noise.

### When Writing Hook User-Visible Messages

**Decision Date:** 2026-02-26

Terminal constraint: "UserPromptSubmit says: " prefix = ~29 chars; ~90 char terminal = ~60 chars for content. Authored independently from additionalContext (agent text is for agents, not display).

**Patterns by tier:**
- Tier 2 injections (discuss, pending, brainstorm, quick, learn): behavioral outline + non-blank line count. Format: `discuss: assess, stress-test, state verdict. (N lines)`
- Tier 2.5 guards (1-line injections): authored human summary, not verbatim content
- Terse commands (c, y): same brief text for both audiences — instruction IS the summary

### When Hook Messages Conflict With Behavioral Rules

**Decision Date:** 2026-03-02

**Anti-pattern:** Hook blocks a dangerous action (correct) but gives misleading guidance that conflicts with behavioral rules. "Retry the git command" caused the agent to retry rm with a different path instead of stopping — the hook's "retry" directive competed with the "stop on unexpected results" rule.

**Correct pattern:** Hook messages must align with the behavioral rules they enforce. For lock contention: "Retry your git command — do not delete lock files" (specify what to retry). Not "STOP" (triggers halt-and-wait) nor ambiguous "retry" (agent retries the wrong command).

**Evidence:** Agent retried rm twice following hook's "retry" advice. Lock was from concurrent worktree session — transient contention that self-resolves via model latency.
