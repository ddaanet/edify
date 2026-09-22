---
name: ground
description: >-
  Ground claims with external research before asserting methodology. Triggers on
  "ground", "create a scoring
  system", "design a methodology", "build a framework", or "synthesize best
  practices".
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, Agent
user-invocable: true
---

# Ground Claims with Research

Prevent ungrounded confabulation when producing methodologies, frameworks,
scoring systems, taxonomies, or best-practice documents. Encode the
diverge-converge research pattern proven during prioritization skill creation.

**Core principle:** Internal reasoning alone confabulates plausible structures.
External research alone produces generic frameworks. Parallel diverge +
synthesis produces grounded, project-adapted output.

## Procedure

### Phase 1: Scope

Frame the research question before searching.

- Define the topic: "What established frameworks exist for [X]?"
- Set inclusion criteria: relevance to project context, actionable methodology,
  procedural (not pure theory)
- Set exclusion criteria: wrong domain, no procedure, outdated
- Select parameters — Read `references/grounding-criteria.md` and select by it:
  - Internal scope: **codebase** (descriptive — "what patterns exist for X") or
    **conceptual** (generative — "what dimensions/constraints apply to X")
  - Model tier for internal branch: codebase → sonnet; conceptual → opus
    (generative divergence)
  - Research breadth: narrow (1-2 searches) or broad (3-5 searches)
  - Output format: reference document, skill body, or decision entry

### Phase 2: Diverge

Execute two branches as parallel Agent dispatches. Launch both in a single
message. Neither is optional — both are required.

**Branch A — Internal explore:** Scope determines agent type and model:
- **Codebase scope:** Delegate via the Agent tool (subagent_type:
  general-purpose, model: sonnet). Surface existing codebase patterns, prior
  decisions, current conventions. Output: inventory of existing patterns with
  file references. Write to `plans/reports/<topic>-internal-codebase.md`. Where
  the topic is a process skill, grounding-criteria.md §Process Skill Internal
  Sources binds: git history mining and session-log scraping are required
  alongside file inspection.
- **Conceptual scope:** Delegate via the Agent tool (subagent_type:
  general-purpose, model: opus). Generate project-specific dimensions,
  constraints, desiderata, evaluation axes. Focus on what no external source
  would surface. Write to `plans/reports/<topic>-internal-conceptual.md`.

**Branch B — External research:** Delegate via the Agent tool (subagent_type:
general-purpose, model: sonnet). Model is always sonnet. Agent prompt includes:
- Research topic and framing question from Phase 1
- Search query templates from `references/grounding-criteria.md`
- Evaluation criteria: relevant to project context? Actionable methodology?
  Named framework with structure?
- Output contract: framework names, component structures, scoring mechanics,
  known limitations

Write to `plans/reports/<topic>-external-research.md`.

Both agents write reports and return filepath only — the quiet execution pattern
at `../../fragments/delegation.md` §Quiet Execution Pattern.

### Phase 3: Converge

Synthesize both branches into grounded output.

- Map internal dimensions onto external framework skeleton
- Adapt scoring criteria or structural elements using project-specific evidence
- Apply convergence template from `references/grounding-criteria.md` (Framework
  Mapping, Adaptations, Grounding Assessment, Sources)
- Attach grounding quality label (mandatory): Strong / Moderate / Thin / None.
  See `references/grounding-criteria.md` for label definitions and evidence
  requirements.

**Framing rule — general first:** State each principle as the general insight
derived from external research. Project-specific implementation is an instance
that validates the principle, not the principle itself. The internal branch
confirms the principle applies locally; it does not define the principle.

- ❌ "Git state queries return booleans — `_git_ok(*args) -> bool`"
- ✅ "Expected states should return booleans, not raise exceptions — implemented
  as `_git_ok()` in this project"

### Phase 4: Output

Write the grounded reference document to `plans/reports/<topic>-grounding.md`
(persistent, tracked).

Required sections:
- Grounding quality label with evidence basis
- Research foundation (named sources with links)
- Adapted methodology — general principle per item, then project implementation
  as instance
- Sources section with retrieval context

**Branch artifacts:** Both branch reports in `plans/reports/` are retained as
audit evidence supporting the synthesis. The grounding report references both.

## References

- **`references/grounding-criteria.md`** — Trigger criteria, quality labels,
  parameter selection, search query templates, convergence template
