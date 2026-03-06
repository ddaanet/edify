# Session Handoff: 2026-03-06

**Status:** Active recall system design in progress. Requirements updated with user annotations, outline written and reviewed, extensive design discussion produced architectural decisions on caching, index structure, and domain mapping.

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

## In-tree Tasks

- [>] **Active recall system** — `/design plans/active-recall/requirements.md` | opus
  - Plan: active-recall
  - Outline written and reviewed, design discussion in progress
  - Phase B (iterative discussion) partially complete — 7 design decisions captured
  - Open: Phase 4/5 ordering preference (metadata before or after grounding), outline sufficiency gate
  - Relates to: recall tool consolidation, generate memory index, recall dedup, recall pipeline, recall learnings design

## Reference Files

- `plans/active-recall/outline.md` — 6-phase design outline with discussion decisions integrated
- `plans/active-recall/requirements.md` — 8 FRs, 4 NFRs, 4 constraints, 2 open questions
- `plans/active-recall/recall-artifact.md` — 29 recall entry keys (updated with post-explore entries)
- `plans/active-recall/reports/outline-review.md` — corrector review with traceability matrix
- `plans/active-recall/classification.md` — Complex classification
- `plans/active-recall/brief.md` — architectural discussion distillation
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments, three-tier model

## Next Steps

Continue Phase B discussion on outline (user reviewing remaining phases). After outline validated, assess sufficiency gate — outline may be sufficient to skip full design.md and route to `/runbook`.
