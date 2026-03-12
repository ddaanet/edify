# Brief: Design Pipeline Evolution

## Problem

The `/design` skill's triage routes jobs into three tiers (Simple, Moderate, Complex) plus a Defect path. Two capabilities are missing:

**1. Formal decomposition tier.** Large jobs requiring breakdown into independent sub-problems are handled informally: Tier 3 outlines sometimes produce multi-sub-problem structures (detected by the Multi-Sub-Problem Sufficiency Gate), but decomposition is an emergent outcome of outlining rather than a first-class triage classification. There is no way to classify a job as "needs decomposition first" at triage time — the designer discovers this during Phase A, after already committing to the Complex ceremony.

**2. Model-aware routing within design.** The pipeline assigns a single model tier per task at session scheduling time (`p:` directive, session.md metadata). The design skill runs at whatever model the session uses. It cannot express that specific design sections or sub-problems require different model capabilities — e.g., architectural decisions needing opus reasoning while implementation planning can use sonnet. Model selection is currently external to the pipeline: the `p:` directive's artifact-type override (agentic prose forces opus) and pushback.md's cognitive-complexity heuristic operate at task granularity, not within-task granularity.

## Scope

### In Scope

- Decomposition as a triage classification (Tier 4 or reclassified Tier 3)
- Model directives attached to decomposition outputs (sub-problems carry model tier metadata)
- Integration with existing Multi-Sub-Problem Sufficiency Gate
- Interaction between decomposition routing and existing `p:` model assignment

### Out of Scope

- Changes to Simple/Moderate/Defect tiers
- Runtime model switching (Claude Code `/model` command — platform capability)
- Recall pipeline changes
- Corrector/validator updates beyond what author-corrector coupling requires

## Sub-problems

### S-A: Decomposition Tier (REVISED — add grounding)

Ground triage classification against task decomposition literature (software project management, agile estimation, systems engineering) before designing the tier.

Define when triage should classify a job as "decomposition" rather than "complex."

Current state: Tier 3 (Complex) enters Phase A research + outline. If the outline happens to produce individually-scoped sub-problems with dependency graphs, the Multi-Sub-Problem Sufficiency Gate detects this post-hoc and routes each sub-problem back through the pipeline independently. The decomposition decision is latent in the outline content, not explicit in the classification.

Design questions:
- Should decomposition be a fourth tier or a sub-classification within Complex?
- What triage signals distinguish "needs decomposition" from "needs architectural design"? (Both have low implementation certainty.)
- What is the decomposition tier's output artifact? The current multi-sub-problem outline format may already be sufficient.
- How does the existing "Composite Task Decomposition" (pre-classification item-level breakdown of multi-item input artifacts) relate? That mechanism operates before classification on heterogeneous inputs; this tier would operate as a classification on homogeneous-but-large jobs.

### S-B: Late-Binding Model Selection (REVISED — was Model Directives)

Replace early-binding model directives in decomposition output with late-binding model selection per pipeline stage. Each stage picks its own model based on its constraints:
- Requirements/brief → design model (opus for architectural reasoning)
- Runbook writing → planning model (sonnet or opus by complexity)
- Orchestration → orchestration model (different for /inline vs /orchestrate)
- Test-driver → execution model (sonnet, maybe haiku for simple)
- Corrector → review model (sonnet or opus)

Design questions:
- What selection criteria does each stage use?
- How do per-stage criteria interact with the artifact-type override (agentic prose → opus)?
- How does this replace the current `p:` task-level model assignment?

### Coupling Analysis

S-A and S-B are loosely coupled. Decomposition (S-A) can be designed independently — it produces sub-problems regardless of whether they carry model metadata. Model directives (S-B) depend on S-A's output format to know where to attach metadata. Design S-A first; S-B extends S-A's output format.

Both modify `agent-core/skills/design/SKILL.md`. S-A changes triage classification and routing. S-B changes the outline format and sufficiency gate output.

## Current State

What exists today relevant to decomposition:

- **Triage classification** (SKILL.md §0): Simple/Moderate/Complex/Defect, two-axis (certainty × stability) with behavioral-code elevation rule
- **Multi-Sub-Problem Sufficiency Gate** (write-outline.md): Detects outlines containing individually-scoped sub-problems with dependency graphs. Treats the outline as terminal design artifact; caller dispatches sub-problems as independent pending tasks.
- **Composite Task Decomposition** (SKILL.md §0): Pre-classification breakdown of multi-item input artifacts into per-item classifications. Distinct from pipeline decomposition — this handles heterogeneous batch inputs.
- **Decision: decomposition vs sequencing** (workflow-planning.md): Sub-problems get tagged with design readiness, not execution order. Sequencing is a runbook concern.
- **`p:` model assignment**: Task-level model tier set at scheduling time. Artifact-type override forces opus for agentic prose.
- **Post-Outline Complexity Re-check**: Downgrade mechanism after outline resolves uncertainty. Does not upgrade or reclassify.

## Dependencies

- `/runbook` receives sub-problems routed from decomposition — no changes needed if sub-problems enter as independent tasks (current pattern)
- `outline-corrector` agent: review criteria may need update if outline format changes (author-corrector coupling check required)
- `session.md` task format: model metadata field already exists; model directives would inform but not change the format
- Decision: "outlines conflate decomposition with sequencing" (workflow-planning.md) — decomposition tier must maintain this separation

## Success Criteria

- Triage can classify jobs as "needs decomposition" before entering Phase A ceremony
- Decomposition tier produces sub-problems with per-sub-problem model tier metadata
- Existing Multi-Sub-Problem Sufficiency Gate integrates with (or is subsumed by) the decomposition tier output
- No regression in Simple/Moderate/Complex/Defect routing
- Boundary between decomposition tier and Tier 3 outline expansion is explicit and testable

## Post-Design Convention

After design phase, split sub-problems into separate tasks with explicit dependencies. S-A and S-B are loosely coupled — S-B depends on S-A's output format. Design together, execute as separate tasks with S-B depending on S-A.

## References

- `agent-core/skills/design/SKILL.md` — current triage and routing
- `agent-core/skills/design/references/write-outline.md` — Phase A/B, multi-sub-problem gate
- `agents/decisions/workflow-planning.md` §When Outlines Conflate Decomposition With Sequencing
- `agents/decisions/pipeline-contracts.md` — transformation table, composite task decomposition
- `agent-core/fragments/pushback.md` §Model Selection for Pending Tasks — artifact-type override
