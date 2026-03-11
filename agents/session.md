# Session Handoff: 2026-03-08

**Status:** Band 0 worktrees created — 4 parallel sub-problems dispatched to worktrees.

## Completed This Session

**Design JIT expansion:**
- Added multi-sub-problem detection in `/design` skill artifact check (SKILL.md)
- Added multi-sub-problem sufficiency gate in write-outline.md with 6 criteria (concrete scope, dependency graph, FR traceability, scope boundaries, readiness routing, tear points)
- Exit behavior: outline is terminal design artifact, sub-problems dispatched independently — no `/runbook` prepend
- Classification: Simple, agentic-prose, opus (file: plans/design-jit-expansion/classification.md)
- Fix-forward: disambiguated re-entry routing (skill-reviewer finding — "Phase B" implied discussion on already-discussed outlines)

**Active Recall design:**
- Multi-sub-problem sufficiency gate passed — all 6 criteria met
- Outline (Rev 2) confirmed as terminal design artifact (file: plans/active-recall/outline.md)
- 12 sub-problems dispatched as independent pending tasks with dependency graph and band ordering

## In-tree Tasks

- [x] **Design JIT expansion** — `/design plans/design-jit-expansion/classification.md` | opus
  - Plan: design-jit-expansion
- [x] **Active Recall** — `/design plans/active-recall/outline.md` | opus
  - Plan: active-recall | Decomposed into 12 sub-problem tasks below
  - Absorbs: Generate memory index (S-D), Recall learnings design (S-L), Codify branch awareness (S-L removes /codify)
- [ ] **AR Integration** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-H: end-to-end verification of recall-explore-recall pattern, cross-worktree memory visibility, capture-time write path
  - Blocked: S-D, S-F, S-J, S-L (terminal — runs after all other AR sub-problems)

- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
  - Infrastructure built. Blocked on human: curate task-contexts.json, annotate ground-truth.md
  - After human steps: run harness then analysis (commands in README)

## Worktree Tasks

- [ ] **Review gate** — `/design` | sonnet
  - Precommit step: review report timestamp >= production artifact edit timestamp, no triviality exception
  - Implements defense-in-depth.md decision ("gate at chokepoint")
  - Evidence: JIT expansion commit skipped vet checkpoint
- [ ] **AR Token Cache** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-A: sqlite cache via sqlalchemy for count_tokens_for_file(). Band 0 — ready now
- [ ] **AR Recall Consolidate** → `ar-recall-consolidate` — `/runbook plans/active-recall/outline.md` | sonnet
  - S-B: merge recall/ + recall_cli/ + when/ into unified recall module. Band 0 — ready now
- [ ] **AR Format Grounding** — `/ground` | opus
  - S-C: research trigger format, when/how distinction, index hierarchy validation. Band 0 — ready now
  - Input: plans/active-recall/outline.md
- [ ] **AR Submodule Refactor** → `ar-submodule-refactor` — `/runbook plans/active-recall/outline.md` | sonnet
  - S-I: extract 42 hardcoded agent-core refs into configurable submodule registry. Band 0 — ready now
- [ ] **AR Submodule Setup** — `/design plans/active-recall/outline.md` | sonnet
  - S-J: create memory submodule with shared branch, configure propagation, update resolver paths. Band 1 — blocked: S-I
- [ ] **AR Hierarchy Index** — `/design plans/active-recall/outline.md` | sonnet
  - S-D: migrate flat index to tree structure, parser updates, migration tooling, index generation. Band 1 — design blocked: S-A, S-B; impl blocked: S-J
- [ ] **AR Trigger Metadata** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-E: formalize trigger_class and category as IndexEntry metadata. Band 2 — blocked: S-C, S-D
- [ ] **AR Mode Simplify** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-F: reduce 5 modes to 2, update 10 pipeline recall points. Band 2 — blocked: S-D
- [ ] **AR Memory Corrector** — `/design plans/active-recall/outline.md` | opus
  - S-K: agent definition with quality criteria, suppression taxonomy. Band 2 — blocked: S-C
- [ ] **AR Doc Pipeline** — `/design plans/active-recall/outline.md` | sonnet
  - S-G: source docs to extraction agent to corrector to index regen. Band 2 — blocked: S-C, S-D, S-K
- [ ] **AR Capture Writes** — `/design plans/active-recall/outline.md` | opus
  - S-L: /remember skill, eliminate learnings.md + /codify. Band 3 — blocked: S-J, S-K, S-D, S-E

- [ ] **Fix prefix tolerance** — `src/claudeutils/when/fuzzy.py` | sonnet
  - Zero tolerance for prefix noise (0.0 scores on one-token mismatch). Separate from format decision.

## Reference Files

- `plans/active-recall/outline.md` — Terminal design artifact: 12 sub-problems with dependency graph, bands, tear points, completeness check
- `plans/active-recall/brief.md` — Active recall system vision and 2026-03-07 discussion conclusions
- `plans/active-recall/requirements.md` — FR-1 through FR-11, NFR-1 through NFR-4, C-1 through C-6

## Next Steps

Band 0 worktrees active: ar-token-cache (S-A), ar-recall-consolidate (S-B), ar-format-grounding (S-C), ar-submodule-refactor (S-I). Merge completed worktrees with `wt merge <slug>`.