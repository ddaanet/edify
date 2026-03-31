# Commit Drift Guard

## Problem

The `_commit` CLI accepts a `## Files` list but has no mechanism to verify those files haven't changed since the caller last reviewed them (via diff). Three failure modes:

1. **Full diff at commit** — wasteful (tokens already spent on review)
2. **Incremental diff** — shows changes since last diff but doesn't prevent drift from the reviewed state
3. **No check** — current behavior, silently commits whatever is on disk

## Questions

- How do other commit/CI tools handle pre-commit state verification?
- What's the right abstraction — content hash, timestamp, diff baseline?
- Should the guard be in the CLI, the skill, or both?

## Context

Surfaced during deliverable review round 2 when `edify _commit` was used interactively. The skill runs discovery (diff), then drafts a message, then calls `_commit` — time passes between review and commit. Background research needed on patterns.

