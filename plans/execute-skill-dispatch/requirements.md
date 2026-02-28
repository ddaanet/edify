# Execute Skill Dispatch

## Requirements

### Functional Requirements

**FR-1: Execute mode invokes task command as skill call**
When `#execute` picks up a pending task, invoke the task's backtick command via the Skill tool (for `/skill` commands) or Bash (for script commands). The agent must not reinterpret "start first pending task" as "assess and implement the work directly."

Acceptance criteria:
- Task with command `/design plans/foo/requirements.md` → `Skill(skill: "design", args: "plans/foo/requirements.md")`
- Task with command `/orchestrate foo` → `Skill(skill: "orchestrate", args: "foo")`
- Task with command `agent-core/bin/prepare-runbook.py plans/foo` → Bash execution
- Non-skill commands (e.g., inline prose instructions) → direct execution (current behavior, unchanged)

**FR-2: UPS hook injects task command for execute mode**
The UserPromptSubmit hook's `x` expansion should include the concrete command to invoke, not just "start first pending task." The hook reads session.md, extracts the first eligible pending task's backtick command, and injects it into `additionalContext`.

Acceptance criteria:
- Hook parses session.md pending tasks section
- Extracts backtick command from first non-blocked, non-failed, non-canceled pending task
- Injects command in additionalContext: `"Invoke: /design plans/foo/requirements.md"`
- Falls back to current generic expansion when session.md is missing or has no pending tasks
- Planstate-derived commands (from `claudeutils _worktree ls`) take priority over static session.md commands

**FR-3: Execute-rule prose aligns with structural enforcement**
The execute-rule MODE 2 section explicitly states that "start first pending task" means "invoke the task's stated command." Hook alignment: additionalContext (structural) and fragment prose (ambient) say the same thing.

Acceptance criteria:
- execute-rule.md MODE 2 says "invoke the task's backtick command via Skill tool (for /skill commands) or Bash (for scripts)"
- No contradiction between hook injection and fragment text (per "When Hook Fragment Alignment Needed" — recency zone must reinforce primacy zone)

### Constraints

**C-1: Hook performance budget**
The UPS hook fires on every prompt. Session.md parsing + planstate command derivation must not add perceptible latency. `claudeutils _worktree ls` spawns a Python process — acceptable only if cached or fast enough (<200ms).

**C-2: Structural fix, not prose strengthening**
Per "When Fixing Behavioral Deviations Identified by RCA": prose strengthening doesn't work for this class of deviation. FR-2 (hook injection) is the structural enforcement. FR-3 (prose alignment) reinforces but does not replace it.

**C-3: Backward compatibility**
Tasks without backtick commands, tasks with non-skill commands, and `#resume` mode behavior must be unchanged.

### Out of Scope

- Implementing `/inline` skill — separate plan (inline-execute, status: requirements)
- UPS topic injection — separate plan (userpromptsubmit-topic, status: outlined)
- Changing how planstate-derived commands are computed — existing `claudeutils _worktree ls` is authoritative
- Modifying `#resume` or `#status` modes — only `#execute` is affected

### Dependencies

- `agent-core/hooks/userpromptsubmit-shortcuts.py` — UPS hook that expands `x` shortcut
- `agent-core/fragments/execute-rule.md` — MODE 2 (EXECUTE) prose
- `agents/session.md` — task metadata format with backtick commands
- `claudeutils _worktree ls` — planstate-derived command source (optional, for enhanced accuracy)

### References

- Observed 2026-02-28: `x` on "Fix planstate detector" task → agent bypassed `/design` skill, implemented directly without recall pass
- "When Execution Routing Preempts Skill Scanning" (operational-practices.md) — same deviation class
- "When Fixing Behavioral Deviations Identified by RCA" (defense-in-depth.md) — structural fix required
- "When Companion Tasks Bundled Into Design Invocation" (workflow-optimization.md) — agent rationalizes skipping process
- "When Hook Fragment Alignment Needed" (hook-patterns.md) — hook/fragment alignment principle
