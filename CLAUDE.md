# Agent Instructions

@plugin/fragments/workflows-terminology.md

---

## Core Behavioral Rules

@plugin/fragments/communication.md

@plugin/fragments/execute-rule.md

@plugin/fragments/pushback.md

**Pending task notation:**

When user says "pending: task description":
- Do NOT execute the task now
- Do NOT write to session.md immediately — task written during next handoff
- Assess model tier (opus/sonnet/haiku) with reasoning
- Respond: task name (noun-phrase, not verbatim user text), model tier, restart flag if needed

@plugin/fragments/execution-routing.md

@plugin/fragments/delegation.md

---

## Documentation Structure

**Progressive discovery:** Don't preload all documentation. Read specific guides only when needed.

### Core Instructions
- **CLAUDE.md** (this file) - Agent instructions, workflows, communication rules

### Architecture & Design
- **agents/decisions/architecture.md** - Module structure, path handling, data models, code quality
- **agents/decisions/cli.md** - CLI patterns and conventions
- **agents/decisions/testing.md** - Testing conventions and patterns
- **agents/decisions/workflows.md** - Oneshot and TDD workflow patterns
- **agents/decisions/implementation-notes.md** - Detailed implementation decisions (read when implementing similar features)

### Current Work
- @agents/session.md - Current session handoff context (update only on handoff)
- @agents/learnings.md - Accumulated learnings (append-only, soft limit 80 lines)

---

## Operational Rules

@plugin/fragments/error-handling.md

@plugin/fragments/token-economy.md

@plugin/fragments/commit-skill-usage.md

@plugin/fragments/no-estimates.md

@plugin/fragments/no-confabulation.md

@plugin/fragments/source-not-generated.md

@plugin/fragments/code-removal.md

@plugin/fragments/tmp-directory.md

## Reference & Tooling

@plugin/fragments/design-decisions.md

@plugin/fragments/project-tooling.md

### Available Recipes

- `just precommit` — Run all checks
- `just test *ARGS` — Run test suite
- `just dev` — Format and run all checks
- `just format` / `just lint` / `just check` — Code formatting and style

@plugin/fragments/tool-batching.md
