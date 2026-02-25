# Runbook Recall Expansion

## Problem

Recall content does not reach step agents during full orchestration. The pipeline has two patterns:

**Lightweight orchestration** (Tier 2, ad-hoc parallel): Orchestrator dispatches agents directly. Each agent runs `when-resolve.py` with keys from the recall artifact. Works today — agent has Bash access and the artifact has pure keys.

**Full orchestration** (Tier 3, prepare-runbook.py): Runbook → prepare-runbook.py → plan-specific agent + step files → `/orchestrate`. Step agents receive Common Context (extracted from runbook) but recall entries are either absent or present as unresolved keys/summaries. The agent cannot resolve them — it has no instruction to run `when-resolve.py`, and the content is not baked in.

**Root cause:** No pipeline stage resolves recall artifact keys into content and injects that content into the artifacts that step agents actually receive (agent definition or step files).

## Origin

Identified during skills-quality-pass runbook planning (2026-02-25). The recall artifact format was corrected from inline summaries to pure resolution keys, but the question "how does resolved content reach step agents?" exposed the gap.

Two orchestration patterns were distinguished:
- Lightweight: agent resolves at execution time (works today)
- Full: content must be baked at preparation time (gap)

## Functional Requirements

- FR-1: `prepare-runbook.py` reads recall artifact (`plans/<job>/recall-artifact.md`) during assembly
- FR-2: Resolve all entry keys via `when-resolve.py` (or equivalent) to produce full decision content
- FR-3: Inject resolved content into plan-specific agent definition (Common Context section) — shared entries available to all step agents
- FR-4: Support per-phase recall entries in phase preambles — injected into step files for that phase only, not into agent definition
- FR-5: Runbook skill Common Context template specifies recall entry format for both shared (Common Context) and phase-scoped (phase preamble) entries
- FR-6: Runbook skill documents the two orchestration patterns and where recall resolution happens in each
- FR-7: Corrector agent (`corrector.md`) receives recall context during orchestration checkpoint reviews. Currently `design-corrector.md` and `runbook-outline-corrector.md` have self-contained recall loading (Step 1.5: `recall-resolve.sh`), but `corrector.md` does not. The orchestrator is weak (sonnet/haiku) and cannot pass recall entries. Fix: add self-contained recall loading to `corrector.md` — derive job name from task prompt or plan directory in execution context, resolve `plans/<job>/recall-artifact.md`

## Non-Functional Requirements

- NFR-1: Token budget — resolved recall content in agent definition must not exceed context budget. Planner curates at planning time (existing constraint from runbook skill). prepare-runbook.py does not filter.
- NFR-2: No runtime resolution in step agents — step agents receive pre-resolved content, do not run `when-resolve.py` themselves
- NFR-3: Backward compatibility — runbooks without recall artifacts assemble as before (no recall section in output)

## Scope

**In scope:**
- `agent-core/bin/prepare-runbook.py` — recall artifact reading, key resolution, content injection
- `agent-core/skills/runbook/SKILL.md` — Common Context recall section format, two-pattern documentation
- `agent-core/agents/corrector.md` — add self-contained recall loading (FR-7)
- Recall artifact format specification (already key-based, may need section markers for shared vs phase-scoped)

**Out of scope:**
- Lightweight orchestration changes (already works)
- Recall artifact generation (handled by `/design` and `/runbook` Phase 0.5)
- `when-resolve.py` changes (existing tool, used as-is)
- Step file format changes beyond adding a recall content section

## Open Questions

- Should resolved content go in agent definition (all steps see it) or step files (per-step)? Likely: shared entries in agent, phase-specific in step files. prepare-runbook.py already extracts phase preambles into step files.
- What format marker in the runbook source triggers recall expansion? Could be a code block with keys, a dedicated `## Recall` subsection under Common Context, or the artifact path reference.
