# Session Handoff: 2026-03-06

**Status:** Outline redrafted with decomposition methodology (8 sub-problems, DAG, banded partial ordering). Corrector-reviewed, discussion deltas applied. Phase B sufficiency gate next.

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
- Root cause: outline has no concept of decomposition without sequencing
- Decomposition methodology needs grounding before implementation

**Decomposition methodology grounding:**
- 7 frameworks evaluated (DSM, Axiomatic Design, WBS, IDEF0, NASA V-Model, DAG/toposort, TRL)
- 3 primary frameworks selected: DSM (banding for partial ordering), Axiomatic Design (zigzag decomposition), TRL (readiness scale)
- 7 adapted principles, 12 project-specific desiderata, 5 dependency types
- Grounding quality: Strong

**Outline redraft (Phase A.5 revision):**
- Applied 7 decomposition principles to replace linear Phase 1-6 with 8 sub-problems + DAG
- Sub-problems: S-A (token cache), S-B (module consolidation), S-C (format grounding), S-D (hierarchical index), S-E (metadata), S-F (mode simplification), S-G (conversion pipeline), S-H (integration validation)
- 4 bands: Band 0 (A,B,C parallel), Band 1 (D), Band 2 (E,F,G parallel), Band 3 (H)
- Phase 4/5 fix: S-E blocked on S-C via readiness propagation (T-2 not torn)
- Tear T-1: S-C/S-D torn — hierarchy structure independent of entry format
- Corrector review: 4 major + 3 minor fixed (report: `plans/active-recall/reports/outline-review-redraft.md`)

**Discussion refinements (Phase B):**
- S-F: `default` recall mode changed from "two-pass" to convergence-based — two recursion loops (structural + semantic). "Two-pass" was flat-index artifact. FR-7 in requirements.md updated.
- S-G: First pipeline target changed to anthropic plugins exploration report per brief.md — tests different input shape (comparative analysis vs API docs). Subsequent: pytest/click/pydantic.

**Skill update sequencing:**
- Decomposition methodology validated on real case (outline redraft) — codification unblocked
- Branch scope: skill updates are shared infrastructure, belong on main after merge

## In-tree Tasks

- [x] **Decomposition grounding** — `/ground` | opus
  - How established design methodologies break complex jobs into sub-problems without premature sequencing
  - Output: `plans/reports/decomposition-methodology-grounding.md`
- [x] **Outline redraft** — `/design plans/active-recall/requirements.md` | opus
  - Applied decomposition methodology, corrector-reviewed, discussion deltas applied

## Worktree Tasks

- [>] **Active recall system** — `/design plans/active-recall/requirements.md` | opus
  - Plan: active-recall
  - Outline redrafted with decomposition methodology, corrector-reviewed, discussion deltas applied
  - 7 prior design decisions + 2 discussion refinements (convergence mode, first target)
  - Next: brief.md update, then Phase B sufficiency gate
  - Relates to: recall tool consolidation, generate memory index, recall dedup, recall pipeline, recall learnings design
- [ ] **Design decomposition tier** — Encode decomposition methodology (DSM banding, readiness scale, zigzag) into `/design` as new workflow tier above Tier 3 | opus | restart
  - Consumes: validated methodology from outline redraft + grounding report
  - Methodology validated on real case — codification unblocked
  - Behavioral change to `/design` skill — shared infrastructure, merges to main

## Reference Files

- `plans/active-recall/outline.md` — 8 sub-problems with DAG, banded partial ordering (redrafted)
- `plans/active-recall/requirements.md` — 8 FRs, 4 NFRs, 4 constraints, 2 open questions (FR-7 updated)
- `plans/active-recall/recall-artifact.md` — 29 recall entry keys
- `plans/active-recall/reports/outline-review-redraft.md` — corrector review of redrafted outline
- `plans/active-recall/reports/outline-review.md` — corrector review of original outline (historical)
- `plans/active-recall/classification.md` — Complex classification
- `plans/active-recall/brief.md` — architectural discussion distillation (needs update with discussion conclusions)
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments, three-tier model
- `plans/reports/decomposition-methodology-grounding.md` — 7 principles from DSM + AD + TRL, Strong grounding
- `plans/reports/decomposition-internal-conceptual.md` — 12 desiderata, 5 failure modes, 5 dependency types
- `plans/reports/decomposition-external-research.md` — 7 frameworks evaluated with comparative matrix

## Next Steps

Continue active recall system design: update brief.md with discussion conclusions, then Phase B sufficiency gate on the redrafted outline.
