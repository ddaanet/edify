# Grounding Skill — Design Outline

## Approach

Create a skill that encodes the diverge-converge research methodology proven during prioritization skill creation. Prevents ungrounded confabulation when producing methodologies, frameworks, scoring systems, or best-practice documents.

**Pattern:** Follows prioritize skill structure — SKILL.md (~800 words) + references/ for detailed content.

**Research basis:** `plans/reports/ground-skill-research-synthesis.md` (Double Diamond + Rapid Review + RAG grounding).

## Key Decisions

**D-1: Skill triggers on claim type, not task type.**
The skill fires when output will contain methodological, framework, taxonomic, or best-practice claims — regardless of what skill/workflow initiated the work. This is a cross-cutting concern, not tied to a specific workflow step.

**D-2: Orchestrator-invoked, not self-invoked.**
The skill provides procedure for the agent doing the work. It does not auto-detect when grounding is needed — the invoking agent (or user) decides to load it. Trigger phrases in the description surface it during relevant tasks.

**D-3: Parameterization via inline skill instructions, not frontmatter.**
Parameters (internal branch type, model tier, research breadth, output format) are documented as decision points within the procedure, not as YAML frontmatter fields. The agent selects parameter values based on task context. Same approach as prioritize skill. Parameter selection guidance lives in `references/grounding-criteria.md` (when to use brainstorm vs explore, model tier matching, breadth tradeoffs).

**D-4: Grounding quality label is mandatory output.**
Every grounded output must declare Strong/Moderate/Thin/None with evidence basis. This is the skill's primary quality signal — it makes grounding depth visible rather than implicit.

**D-5: Two-branch diverge is the core innovation.**
Internal branch (brainstorm OR explore) captures project-specific dimensions. External branch (web search) provides established framework skeleton. Neither alone suffices — internal-only confabulates, external-only is generic.

**D-6: Output location follows existing convention.**
Grounded research output → `plans/reports/` (persistent, tracked). Scratch computation → `tmp/`. Aligns with learnings entry on research deliverable placement.

## Scope

**In scope:**
- SKILL.md with 4-phase procedure:
  - **Phase 1 (Scope):** Frame research question, define inclusion/exclusion criteria
  - **Phase 2 (Diverge):** Parallel branches — Internal (brainstorm/explore) + External (web search)
  - **Phase 3 (Converge):** Map internal dimensions to external framework, assess grounding quality
  - **Phase 4 (Output):** Reference document with grounding label and sources
- `references/grounding-criteria.md` with:
  - Trigger criteria (when grounding is mandatory vs optional)
  - Quality label definitions (Strong/Moderate/Thin/None with evidence requirements)
  - Parameterization guidance (branch type, model tier, breadth, output format selection)
  - Search query templates for external branch
- Integration guidance embedded in SKILL.md body (when to invoke from design/prioritize workflows)

**Out of scope:**
- Automated detection of when grounding is needed (future: hook-based)
- Changes to existing skills to invoke this skill (document integration points only)
- Script automation of the diverge-converge pattern

## Decisions (from Open Questions)

- **D-7:** Search query templates in grounding-criteria.md. Reduces confabulated search terms, provides starting patterns the agent can adapt.
- **D-8:** Convergence output uses structured template with required sections (Framework Mapping, Grounding Assessment, Sources). Similar to prioritize skill's scoring table structure but adapted for synthesis work.

## Structure

```
agent-core/skills/ground/
├── SKILL.md              (~800 words, 4-phase procedure + integration guidance)
└── references/
    └── grounding-criteria.md  (~900 words: trigger criteria + quality labels + parameterization + search templates + convergence template)
```
