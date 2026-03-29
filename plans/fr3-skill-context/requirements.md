# FR-3: Skill Tool Context Parameter

Extracted from `plans/small-fixes-batch`.

## Requirements

Investigate the `context` parameter on the Skill tool (e.g., `context: fork`). Create a minimal test skill, invoke it with different `context` values, observe and document behavior differences.

## Acceptance

- Behavior documented: what does `context: fork` do vs default?
- Does AskUserQuestion work in a forked context?
- What context (session history, CLAUDE.md, tools) is visible to the skill?
