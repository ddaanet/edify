# Agent Instructions

@agent-core/fragments/workflows-terminology.md

---

## Core Behavioral Rules

@agent-core/fragments/communication.md

@agent-core/fragments/deslop.md

@agent-core/fragments/execute-rule.md

@agent-core/fragments/pushback.md

**Pending task notation:**

When user says "pending: task description":
- Do NOT execute the task now
- Do NOT write to session.md immediately — task written during next handoff
- Assess model tier (opus/sonnet/haiku) with reasoning
- Respond: task name, model tier, restart flag if needed

@agent-core/fragments/execution-routing.md

@agent-core/fragments/delegation.md

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
- @agents/jobs.md - Plan lifecycle tracking (update when plans change status)

---

@agents/memory-index.md

---

## Operational Rules

@agent-core/fragments/error-handling.md

@agent-core/fragments/vet-requirement.md

@agent-core/fragments/token-economy.md

@agent-core/fragments/commit-skill-usage.md

@agent-core/fragments/no-estimates.md

@agent-core/fragments/code-removal.md

@agent-core/fragments/tmp-directory.md

## Reference & Tooling

@agent-core/fragments/bash-strict-mode.md

@agent-core/fragments/sandbox-exemptions.md

@agent-core/fragments/claude-config-layout.md

@agent-core/fragments/design-decisions.md

@agent-core/fragments/project-tooling.md

### Available Recipes

**Root justfile:**
@.cache/just-help.txt

**agent-core justfile:**
@.cache/just-help-agent-core.txt

@agent-core/fragments/tool-batching.md
