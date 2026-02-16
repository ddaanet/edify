# Prototype: Sub-Agent Output Capture

## Problem

Third-party sub-agents (plugin-dev's skill-reviewer, Explore) lack Write permission — they can Read/Grep/Glob but cannot write their own reports to disk. Their output exists only in the Task tool return value, which is:
- Visible to the calling agent's context (consumes tokens)
- Not persisted to a file (no audit trail, not referenceable by other agents)
- Lost after context compaction

This creates a gap: agents that produce valuable review output have no way to persist it. The calling agent must manually copy the output to a file, or the output is ephemeral.

**Concrete example:** plugin-dev's skill-reviewer reviewed the ground skill. It produced a detailed review with findings, fixes, and ratings — but couldn't write to disk because it lacks Write tools. The orchestrator had to read the Task result and apply fixes manually.

**Scope distinction:** Our own agents (outline-review-agent, vet-fix-agent) can be granted Write directly — that's a straightforward fix, not a prototype. This prototype addresses **third-party agents we don't control** (plugin-dev plugin agents, community plugins).

## Goal

Automatically capture sub-agent output to a file for:
- **Audit trail** — Review reports persist across sessions
- **Efficient orchestration** — Orchestrator can reference report file instead of holding full output in context
- **Cross-agent reference** — Other agents can Read the captured output without re-running the review

## Possible Approaches

**A. PostToolUse hook on Task tool:**
- Fires after Task completes in main session
- Captures the returned text from `tool_output`
- Writes to a predictable path (e.g., `tmp/agent-output/<agent-id>.md` or path specified in task prompt)
- Orchestrator references the file instead of holding output in context

**B. Wrapper script invoked by orchestrator:**
- Orchestrator calls a script that: invokes Task → captures output → writes to specified path
- More explicit control over what gets captured
- Doesn't require hook infrastructure

**C. Grant Write permission to review agents:**
- Only viable for our own agents (outline-review-agent — pending task exists)
- Not viable for third-party agents (plugin-dev's skill-reviewer, community plugins)
- This approach solves the local case; approaches A/B solve the general case

## Constraints

- PostToolUse hooks fire in main session only — won't capture nested sub-agent outputs
- Hook output visibility: `additionalContext` is injected but not written to disk
- Must not interfere with quiet execution pattern (agents report to files, return filepath)
- Background agents already have `output_file` — but that's the full transcript, not structured output

## Recommendation

For our own agents: grant Write directly (Approach C). Pending task exists for outline-review-agent.

For third-party agents: Approach A (PostToolUse hook on Task) is the general solution. Captures output transparently regardless of agent's tool permissions. Evaluate after hook infrastructure stabilizes.

## Status

Prototype concept for third-party agent capture. Local agents get Write permission directly.
