# Session Handoff: 2026-02-15

**Status:** Organized reports directory, merging worktree-fixes.

## Completed This Session

**Organized plans/reports directory:**
- Moved 7 RCA reports → `plans/process-review/reports/` (plan that produced them)
- Deleted 5 orphaned execution/debug reports (git history preserves)
- `plans/reports/` now contains only shared research (2 files)
- Updated all cross-references (session.md, internal RCA refs)
- Convention enforced: `plans/<plan>/reports/` = plan-specific, `plans/reports/` = shared research

## Pending Tasks

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
  - Validate session.md references point to versioned files (reject tmp/ references) — recurring failure mode
  - Validate session.md pending tasks/worktree structure
  - Reject references to tmp/ files in all committed content
  - Autofix or fail on duplicate memory index entries (blocked on memory redesign)

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 18 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Upstream plugin-dev: document skills frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Review all tests for vacuous tests
  - Deslop entire codebase
  - Review codebase for factorization
  - Remove deprecated code — init_repo_with_commit() in conftest_git.py

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Redesign markdown preprocessor — multi-line inline markup parsing
  - Session summary extraction prototype
  - Rewrite last-output prototype with TDD as claudeutils subcommand

- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements
  - Integrates with worktree-update (additive merge, bidirectional sync)

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
  - NOT UserPromptSubmit — correct event TBD (load hook skill when executing)

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
  - History cleanup tooling — git history rewriting, reusable scripts
  - Rewrite agent-core ad-hoc scripts via TDD to claudeutils package


- [ ] **Update /remember to target agent definitions** — blocked on memory redesign
  - When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional target

- [ ] **Inject missing main-guidance rules into agent definitions** — process improvements batch
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Design behavioral intervention for nuanced conversational patterns** — `/design` | opus
  - Requires synthesis from research on conversational patterns

## Worktree Tasks

- [ ] **Remember skill update** → `remember-skill-update` — Resume `/design` Phase B | sonnet
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Immediate sub-task: Migrate 64 learning titles to When/How format (FR-7)
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
  - Blocked on: workflow improvements
  - Outline: `plans/error-handling/outline.md`
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
  - RCA blocker resolved — reports at `plans/process-review/reports/rca-*-opus.md`
  - Input: `plans/orchestrate-evolution/design.md`, `plans/process-review/rca.md`
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Design skill: Phase C density checkpoint (TDD non-code marking handled by per-phase typing)
  - Workflow fixes from RCA — `plans/process-review/reports/rca-*-opus.md`, normalize runbook-review axes, execution-time split, vet investigation protocol, orchestrate template
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit
  - Fix skill-based agents not using skills prolog section — `skills:` frontmatter

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md (confirmed fully superseded)

**wt-merge session reconciliation incomplete:**
- merge.py has auto-resolvers for session.md, learnings.md, jobs.md
- Session merge loses continuation lines (single-line set diff) → worktree-fixes FR-4
- No-op merge skips commit → orphan branch → worktree-fixes FR-5

**workflow-improvements worktree has stale RCA paths:**
- Worktree references `plans/reports/rca-*-opus.md` — moved to `plans/process-review/reports/`
- Update references in worktree session.md after merge

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit
- Autofix only handles placement, ordering, and structural entry removal — not orphans

**Rule file directive adherence unreliable:**
- Agents ignore injected "load X before modifying" directives
- Same failure mode as passive index (2.9% baseline recall)
- Blocking hooks or inline code comments may be more effective than suggestion-based rules

**Learnings.md bloated after pushback merge (400 lines, 69 entries):**
- Pushback worktree accumulated 62 entries over its lifecycle
- Merge unioned both files — all worktree entries show 0 days (merge commit date)
- Cannot consolidate: 0 entries ≥7 active days despite 5x soft limit
- Many entries may already be consolidated in pushback's permanent docs — need manual review
- Title migration to When/How format (FR-7) should happen before or alongside consolidation

**Pushback S3 agreement momentum:**
- Known limitation — prompt-level self-monitoring can't detect agreement momentum without persistent state across turns
- Not pursuing further (arXiv 2509.21305 confirms sycophancy is mechanistically distinct)

## Reference Files

- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/remember-skill-update/outline.md` — Design outline (reviewed, Phase B ready)
- `plans/remember-skill-update/reports/explore-remember-skill.md` — Full pipeline exploration
- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
