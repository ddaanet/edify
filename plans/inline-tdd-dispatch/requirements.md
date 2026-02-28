# Inline TDD Cycle Dispatch

## Requirements

### Functional Requirements

**FR-1: Cycle-scoped prompt composition in /inline skill**
Add prompt composition procedure to the inline skill's Tier 2 TDD dispatch section. The procedure specifies how to extract a single cycle from a runbook and compose the test-driver prompt.

Acceptance criteria:
- Procedure specifies extraction boundaries (`## Cycle X.Y:` to next `---` or `## Cycle`)
- Procedure includes common context (runbook's Common Context section) in each dispatch
- Procedure explicitly excludes adjacent/future cycles from test-driver prompt
- Procedure references recall artifact inclusion (already partially covered by sub-agent recall section)

**FR-2: Extend decision with prompt composition rationale**
Add prompt composition section to "When Delegating TDD Cycles To Test-Driver" in `agents/decisions/orchestration-execution.md`. Covers the *why*: structural enforcement via context absence at the test-driver level.

Acceptance criteria:
- Documents the anti-pattern (passing full runbook to test-driver)
- Explains structural enforcement: executing session extracts, test-driver receives only its cycle
- References "When Limiting Agent Scope" and "When Agent Context Has Conflicting Signals" as supporting decisions
- Documents the risk: visible future cycles cause GREEN phases to implement ahead

**FR-3: Update memory-index keywords**
Add prompt composition and cycle extraction keywords to the existing memory-index entry for discoverability via recall.

Acceptance criteria:
- Entry updated with keywords covering: prompt composition, cycle extraction, cycle scope, runbook extraction
- Entry remains on the `orchestration-execution.md` file heading

### Constraints

**C-1: Skill is delivery mechanism, decision is source of truth**
The /inline skill provides the procedure at point of use. The decision file provides the rationale for recall-based discovery. No duplication of content — skill has the how, decision has the why.

**C-2: No delegation.md changes**
The delegation fragment is always-loaded context. Cycle-scoped dispatch is a narrow concern — disproportionate for ambient injection. Skill + decision file cover both delivery paths (structural and recall).

### Out of Scope

- Modifying test-driver agent behavior — test-driver receives whatever prompt it's given; the constraint is on the *caller*
- Automating extraction (scripting cycle boundary parsing) — sonnet extraction of markdown sections is reliable
- Runbook-specific annotations — the skill handles this generically for all runbooks

### Dependencies

- `agent-core/skills/inline/SKILL.md` — edit target (Phase 3 Delegated Execution section, lines 94-116)
- `agents/decisions/orchestration-execution.md` — edit target (lines 364-372)
- `agents/memory-index.md` — edit target (line 245)

### References

- Discussion in this session: cycle conflation risk, structural enforcement via context absence
- "When Limiting Agent Scope" (orchestration-execution.md) — structural enforcement principle
- "When Agent Context Has Conflicting Signals" (orchestration-execution.md) — persistent context wins at haiku capability
