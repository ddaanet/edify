# Brief: Skill Agent Bootstrap

## Problem

Skills and sub-agents have two distinct bootstrap gaps:

**1. Skill pre-work is ad-hoc.** Each skill implements its own pre-work sequence (recall gate, context loading, continuation checks) or omits steps entirely. Examples from the codebase:
- `/design`, `/runbook`, `/inline`, `/requirements` all implement recall gates but with varying patterns (some read `memory-index.md` first, some don't; some write recall artifacts, some skip)
- `/proof`, `/deliverable-review` do per-item recall instead of upfront recall
- Several skills (`/commit`, `/handoff`, `/codify`, `/reflect`) have no recall gate at all
- The `cooperative-protocol-gaps` plan (archived) identified continuation protocol inconsistencies across `/design`, `/runbook`, `/worktree`, `/commit` and was superseded by this task

The inconsistency means new skills copy-paste from existing ones and miss steps. Recall gates that were added (e.g., recall-gate plan) required manual retrofit across multiple skills.

**2. Sub-agent operational rules are manually curated.** Agents launched via Task tool receive operational rules through the `skills` frontmatter field. Currently 9 of 13 agents include `project-conventions`; only 2 include `error-handling`; none include `no-confabulation` or `token-economy`. Adding a new operational rule requires updating every agent definition individually. There is no mechanism to inject a baseline set of operational rules into all sub-agents.

## Scope

Four sub-problems were originally bundled. Platform capability analysis (per design-backlog-review REFINE verdict) resolves two:

### SP-1: Standardized skill pre-work (IN SCOPE)

Define a pre-work protocol that all skills execute on invocation. Candidates for standardization:
- Recall gate (read index, select triggers, resolve, write artifact)
- Continuation detection (check if resuming interrupted skill execution)
- Plan context loading (read design/outline if plan-backed)
- Session context (read session.md for task metadata)

Not all skills need all steps. The protocol must support opt-out (e.g., `/commit` has no recall need) without requiring each skill to reimplement the opt-out logic.

**Delivery:** A pre-work specification. Validate on 3 high-value skills, then batch-apply remaining in one pass. Not a runtime framework — skills are prompt documents, not executable code.

### SP-2: Agent rule injection (IN SCOPE)

Mechanism to ensure all sub-agents receive baseline operational rules without manual per-agent maintenance.

Current state: `skills` frontmatter injects skill content into agent context. Each agent definition manually lists which skills to load. The set is inconsistent (some get `error-handling`, most don't; none get `no-confabulation`).

**Delivery:** Either a convention (standard skills set that all agents include) or a structural mechanism (default skills, inheritance, template).

### SP-3: Project skill authoring conventions (REVISED — was KILL)

Platform tools (`skill-creator`, `plugin-dev:skill-development`, `plugin-dev-validation`) cover generic skill structure. Project-specific conventions are not covered:
- D+B gating (when skills need deterministic anchors vs behavioral instructions)
- Skill description wording for CLI display and trigger matching
- Continuation handling (detecting and resuming interrupted execution)
- Workflow closure (ensuring skills don't leave execution in ambiguous state)
- Optimization methodology (measuring and improving skill effectiveness)

**Delivery:** Non-user-invocable skill documenting project-specific skill authoring conventions, layered on `plugin-dev:skill-development` as platform foundation. Two consumption contexts:
- **Agent context:** Co-loaded via `skills:` frontmatter alongside `plugin-dev:skill-development`
- **Interactive context:** Declarative dependency via `skills:` frontmatter on the skill itself (spike: does this work?), or PreToolUse hook enforcing load before first tool call

**Open spike:** Does `skills:` frontmatter on skills work for declarative dependency loading?

### SP-4: Skill prompt-composer (KILL -- no evidence of need)

Fragment composition is a mechanical editing task. Skills reference other content via `@`-includes and section cross-references. No evidence from the codebase that manual composition is a failure source. The problem statement was speculative.

## Sub-problem Analysis

### Independence

SP-1 and SP-2 are **independent**. They address different artifact types (skills vs agent definitions), different mechanisms (protocol specification vs frontmatter/injection), and can be designed and implemented separately.

### Coupling

SP-1 could inform SP-2: if the pre-work protocol includes recall, and sub-agents execute skills that have pre-work, the agent's skill set affects what pre-work runs. But this coupling is indirect -- the agent frontmatter `skills` field already controls skill loading. SP-2 is about which skills are in the baseline set, not about changing the skill loading mechanism.

### Sequencing

Either can go first. SP-2 is simpler (smaller surface area, clearer solution space). SP-1 requires auditing all 33 skills to classify their pre-work patterns and designing opt-out semantics.

## Dependencies

- **Active Recall (upstream):** AR plans to consolidate recall infrastructure. SP-1's recall gate standardization should use the current recall interface but be aware that the interface may change. Design for the current `claudeutils _recall resolve` API.
- **Plugin migration (related):** Plugin migration may restructure skill/agent file locations. SP-1 and SP-2 should be location-agnostic (reference skill names, not paths).
- **Cooperative-protocol-gaps (absorbed):** Archived plan covering continuation protocol compliance. SP-1 absorbs this scope.

## Success Criteria

- SP-1: Pre-work protocol documented. Audit of all skills classifies each into pre-work tiers (full, partial, exempt). Validate on 3 high-value skills, then batch-apply remaining in one pass.
- SP-2: All 13 agent definitions include a consistent baseline operational rule set. Adding a new operational rule requires editing one location, not 13.
- SP-3: Non-user-invocable skill exists with project conventions, loadable in both agent and interactive contexts. No duplication of platform capabilities — additive only.

## Post-Design Convention

After design phase, split independent sub-problems into separate tasks with explicit dependencies. Parent plan delivers at "designed" status (terminal). SP-1 and SP-2 are independent and split post-design. SP-3 is independent.

## References

- `plans/reports/design-backlog-review.md` line 64-65 -- REFINE verdict with platform overlap analysis
- `plans/reports/anthropic-plugin-exploration.md` -- Plugin inventory (skill-creator, plugin-dev details)
- `agents/plan-archive.md` cooperative-protocol-gaps entry -- superseded by this task
- `agent-core/skills/plugin-dev-validation/SKILL.md` -- Existing review criteria for plugin components
- `.claude/rules/skill-development.md`, `.claude/rules/agent-development.md` -- Platform skill triggers
