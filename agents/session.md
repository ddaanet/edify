# Session Handoff: 2026-03-06

**Status:** Decomposition methodology grounded (Strong). 7 principles from DSM + Axiomatic Design + TRL adapted with project-specific desiderata. Outline redraft unblocked.

## Completed This Session

**Requirements update:**
- Incorporated 17 user REVIEW annotations into `plans/active-recall/requirements.md`
- FR-1: token-counted splits with new prereq, arbitrary nesting, recall loop re-evaluation, path → `agents/memory/index.md`
- FR-2: broadened `when` scope (methodologies, GOF, code smells, gotchas), per-entry class decision
- FR-4: entries can be `when` or `how`, methodology collections as valid sources, first targets = project deps
- FR-7: two modes (removed `everything`), no aliases, `default` recurses until entries
- FR-8: time-limited backward compat with planned deprecation
- New NFR-4 (token budget as design target), new C-3 (token counting before split)
- Q-1 resolved (agents/memory/ path), open questions consolidated to 2

**Design triage + outline (Phase A):**
- Classification: Complex (low implementation certainty, high requirement stability)
- Loaded plugin-dev:hook-development and plugin-dev:skill-development skills
- Recall pass: resolved 18 entries from recall artifact + 5 post-explore entries
- Codebase exploration: mapped all 3 CLI modules, 2 duplicate index parsers, 22 test files, 21 decision file sections (362 entries, ~64k tokens total)
- Wrote `plans/active-recall/outline.md` — 6 phases, dependency-ordered
- Outline corrector review: 4 major + 7 minor issues found and fixed (report: `plans/active-recall/reports/outline-review.md`)
- Classification written: `plans/active-recall/classification.md`
- Prototype: `plans/prototypes/index-stats.py` — entry distribution and token measurement

**Design discussion (d: mode) — 7 decisions:**
- Token count cache: sqlite via sqlalchemy (not JSON), md5 composite key `(md5_hex, model_id)`, `last_used` for eviction. JSON-as-database rejected for concurrency (parallel worktrees) and convention reasons.
- Token counting infrastructure already exists (`tokens.py`, `tokens_cli.py`). Phase 1 reduced to cache layer only.
- Index types: branch (index-of-indices) vs leaf (index-of-entries), no mixed indices. Mixed creates discoverability imbalance — inline entries more visible than child-referenced entries.
- Domain path mapping: space → `/` (hierarchical parent-child) or `-` (compound noun), contextual decision at domain creation time. Hyphen for compound separators (project convention).
- Version sub-domains: `pydantic/v2/` — version as hierarchy level, enables FR-3 subtree-scoped re-evaluation at version granularity.
- Branch index keywords: domain entries include keywords for selection without loading child indices.
- Anthropic API for token counting (not tiktoken) — exact counts, correct tokenizer, no wrong-ecosystem dependency.

**Outline critique (d: mode):**
- Current outline conflates "subtasks" (logical units of work) with "execution phases" (implementation ordering)
- Grounding (Phase 5) is a design input but sequenced as an execution phase after Phase 4 commits to metadata model — premature commitment
- Phase 4 ordering note (line 120) acknowledges the risk but mitigation ("fields are additive") is weak — if grounding invalidates when/how taxonomy, Phase 4 is rework
- Root cause: outline has no concept of decomposition without sequencing
- Identified need for a new tier above Tier 3 — decomposition of complex jobs into sub-problems with dependency graph, each sub-problem enters Tier 1-3 pipeline independently
- Decomposition methodology needs grounding before implementation (work breakdown structures, design readiness assessment)

**Decomposition methodology grounding:**
- 7 frameworks evaluated (DSM, Axiomatic Design, WBS, IDEF0, NASA V-Model, DAG/toposort, TRL)
- 3 primary frameworks selected: DSM (banding for partial ordering), Axiomatic Design (zigzag decomposition), TRL (readiness scale)
- 7 adapted principles: zigzag decomposition, dependency discovery during decomposition, banding for partial order, tearing for coupled sub-problems, readiness scale (groundable/designable/executable), 100% completeness rule, DAG as primary output
- 12 project-specific desiderata from internal conceptual analysis (context-window scoping, testable boundaries, type annotation, minimal interfaces, etc.)
- 5 dependency types identified: data, structural, knowledge, merge, validation
- Grounding quality: Strong (3 established frameworks with direct applicability)

## In-tree Tasks

- [x] **Decomposition grounding** — `/ground` | opus
  - How established design methodologies break complex jobs into sub-problems without premature sequencing
  - Work breakdown structures, dependency representation, design readiness assessment
  - Output: `plans/reports/decomposition-methodology-grounding.md`
  - Feeds new workflow tier (above Tier 3) and active recall outline redraft
- [ ] **Outline redraft** — `/design plans/active-recall/requirements.md` | opus
  - Apply decomposition methodology to produce sub-problems without premature sequencing
  - Current outline conflates subtasks with execution phases — grounding (design input) deferred as Phase 5
  - Design-time activities (format grounding FR-5, metadata model decisions) must not appear as execution phases
  - Consumes: decomposition grounding report + this session's diagnosis

## Worktree Tasks

- [>] **Active recall system** — `/design plans/active-recall/requirements.md` | opus
  - Plan: active-recall
  - Outline written and reviewed, design discussion in progress
  - 7 design decisions captured, outline diagnosed as needing redraft
  - Grounding tasks gate the outline redraft (see in-tree tasks above)
  - Relates to: recall tool consolidation, generate memory index, recall dedup, recall pipeline, recall learnings design

## Reference Files

- `plans/active-recall/outline.md` — 6-phase design outline (to be redrafted — conflates subtasks with execution phases)
- `plans/active-recall/requirements.md` — 8 FRs, 4 NFRs, 4 constraints, 2 open questions
- `plans/active-recall/recall-artifact.md` — 29 recall entry keys (updated with post-explore entries)
- `plans/active-recall/reports/outline-review.md` — corrector review with traceability matrix
- `plans/active-recall/classification.md` — Complex classification
- `plans/active-recall/brief.md` — architectural discussion distillation
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments, three-tier model
- `plans/reports/decomposition-methodology-grounding.md` — 7 principles from DSM + AD + TRL, Strong grounding
- `plans/reports/decomposition-internal-conceptual.md` — 12 desiderata, 5 failure modes, 5 dependency types
- `plans/reports/decomposition-external-research.md` — 7 frameworks evaluated with comparative matrix

## Next Steps

Run outline redraft (`/design plans/active-recall/requirements.md`). Decomposition grounding complete — apply methodology to produce sub-problems with dependency graph instead of linear phases.
