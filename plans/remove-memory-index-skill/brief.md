# Brief: Remove Memory-Index Skill

## Context

The `memory-index` skill (`agent-core/skills/memory-index/SKILL.md`) is a vestigial sub-agent injection mechanism that predates removal of memory-index from initial context. It duplicates `agents/memory-index.md` content and is the wrong mechanism for both main-session and sub-agent use.

Session evidence: main-session agent invoked `/memory-index` via Skill tool (wrong context — not a sub-agent). The correct path for main session is Read `agents/memory-index.md` directly or use `/recall` skill.

## Proposed Change

1. **Delete** `agent-core/skills/memory-index/` directory
2. **Update** `agent-core/agents/corrector.md` — remove `"memory-index"` from `skills:` frontmatter list. Corrector should Read `agents/memory-index.md` directly (consistent with outline-corrector, design-corrector, runbook-outline-corrector which already do this).
3. **Verify** no other consumers reference the skill by name (Grep confirmed: only corrector.md uses it via frontmatter).

## Evidence

- `corrector.md` line 7: `skills: ["project-conventions", "error-handling", "memory-index"]` — only agent-level consumer
- Other correctors (outline-corrector, design-corrector, runbook-outline-corrector) all Read `memory-index.md` directly
- Skill header: "Sub-Agent Memory Recall" — designed for sub-agents, but sub-agents can't invoke Skill tool
- Skill says "Synced from agents/memory-index.md" — it's a copy

## Scope

Delete skill directory, update one agent file. No behavioral change — corrector gains same information via Read that it previously got via skill injection.
