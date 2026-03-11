# Brief: Measure Spontaneous Agent Recall

Measure how often agents spontaneously invoked `when-resolve.py` (later `_recall resolve`) without being prompted by a user message, hook injection, or skill procedure.

## Context

The existing 4.1% figure from the retrospective measures user-initiated `/when`/`/how` skill invocations — the user testing the tool, not agents recalling decisions. No measurement of actual agent-initiated recall exists.

The original concept was an "actionable index" — entries loaded in context that would self-trigger agent recognition. The theory: if the agent sees "when X → do Y" in context, it recognizes situation X and acts. This was never directly measured.

## What to measure

Scan session JSONL logs for `when-resolve.py` or `_recall resolve` in Bash tool calls. Classify each invocation:

- **User-triggered:** Appears in response to a user message containing `/when`, `/how`, or explicit recall instruction
- **Hook-injected:** Appears after a system-reminder containing recall directive (UPS hook, PreToolUse hook)
- **Skill-procedural:** Appears within a skill execution that mandates recall (e.g., /design triage recall gate)
- **Spontaneous:** None of the above — agent independently decided to look something up

## Expected outcome

Likely 0% spontaneous rate, confirming the recognition bottleneck diagnosis by direct measurement rather than inference. Even 0% is a meaningful data point for the retrospective narrative.

## Tools

- Session scraper: `plans/prototypes/session-scraper.py` (scan, parse, tree, correlate)
- Session logs: `~/.claude/projects/` (~980 sessions)
