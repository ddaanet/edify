# Session Handoff: 2026-02-13

**Status:** Worktree-update recovery scoped, pushback worktree created, session cleanup.

## Completed This Session

**Worktree-update recovery triage:**
- Cross-referenced deliverable review findings against workwoods requirements
- C1 (wt-ls Python coupling) deferred — workwoods FR-1 redesigns wt-ls entirely
- R1 (session.md/jobs.md auto-combine) deferred — workwoods FR-5/FR-6 supersede
- C2-C5 + selected major findings: independent, fix now
- Decision: fix independent findings → merge → workwoods designs against merged baseline

**Session cleanup:**
- Removed "Agentic process review and prose RCA" — was completed at process-review merge (marked `[x]` in commit 5b79869), incorrectly re-added during task recovery (a74ed85)
- Recovered `plans/process-review/rca.md` from git history (commit 0ded1a3) — was deleted after merge per code removal rules, but workflow improvements task needs in-tree reference
- Added input file references to composite tasks (workflow improvements, both RCAs)
- Moved pushback to Worktree Tasks after `wt-task pushback` creation
- Updated workflow improvements blocker to reference current pending RCAs (file growth, vet over-escalation)

## Pending Tasks

- [ ] **Workflow improvements** — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
  - RCA blocker resolved — reports at `plans/reports/rca-*-opus.md`
  - Input: `plans/orchestrate-evolution/design.md`, `plans/process-review/rca.md`
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Design skill: Phase C density checkpoint (TDD non-code marking handled by per-phase typing)

- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [x] **RCA: Runbook planning missed file growth** — Completed in worktree, opus report at `plans/reports/rca-planning-file-growth-opus.md`

- [x] **RCA: Vet over-escalation persists post-overhaul** — Completed in worktree, opus report at `plans/reports/rca-vet-over-escalation-opus.md`

- [ ] **Workflow fixes from RCA** — Implement process improvements from 3 RCA reports | sonnet
  - Input: `plans/reports/rca-*-opus.md` (3 authoritative reports)
  - Key fixes: normalize runbook-review.md axes, add execution-time split enforcement, add vet investigation protocol + UNFIXABLE taxonomy, orchestrate template enforcement

- [ ] **Consolidate learnings** — learnings.md at 312+ lines (soft limit 80) | sonnet
  - Blocked on: memory redesign (/when, /how)

- [ ] **Worktree merge combines session context** — Confirm wt-merge combines pending tasks/jobs (not --ours) and requires agent review | sonnet
  - Blocked on: worktree-update delivery

- [ ] **Learning ages computation after consolidation** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
  - Validate session.md pending tasks/worktree structure
  - Reject references to tmp/ files in committed content
  - Autofix or fail on duplicate memory index entries (blocked on memory redesign)

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet
  - Blocked on: worktree-update delivery

- [ ] **Commit skill optimizations** — Remove handoff gate, optimize, branching fix | sonnet
  - Blocked on: worktree-update delivery
  - Remove handoff gate, optimize with minimal custom script calls
  - Commit Gate B — coverage ratio (artifacts:reports 1:1) not boolean
  - Commit/handoff branching — move git branching point after precommit passes

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Blocked on: worktree-update delivery (wt-* recipes change, justfile Phase 4 invalid)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 18 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Fix skill-based agents not using skills prolog section** — Agents duplicate content instead of referencing skills via `skills:` frontmatter | sonnet

- [ ] **Upstream plugin-dev: document `skills:` frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

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

## Worktree Tasks

- [x] **Execute worktree-update runbook + recovery** — Merged to main. Recovery C2-C5 fixed. C1/R1 deferred to workwoods.
- [ ] **Plan when-recall** → `wt/when-recall` — blocked on validator fix | sonnet
  - Fix validator for exact key matching (remove fuzzy, update _build_heading)
  - Then migrate memory-index.md to /when format (152 entries)
  - Findings: `plans/when-recall/reports/migration-findings.md`
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
  - Blocked on: workflow improvements
  - Outline: `plans/error-handling/outline.md`
- [ ] **Test feature** → `wt/test-feature`
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
  - Plan: pushback | Status: requirements

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md (confirmed fully superseded)

**Learnings.md over soft limit:**
- 312 lines, 0 entries >=7 days — consolidation blocked on memory redesign

**wt-merge uses --ours for session.md:**
- Worktree-side pending tasks and jobs.md changes lost on merge
- Manual reconciliation needed after every merge (this session: 6 manual fixups)
- Pending task to fix this in worktree-update

**All tasks with documentation must have in-tree file references.**

## Reference Files

- `plans/workwoods/requirements.md` — Workwoods requirements (6 FRs, cross-tree awareness)
- `plans/pushback/requirements.md` — Pushback requirements (3 FRs, sycophancy prevention)
- `plans/process-review/rca.md` — Process RCA (recovered from git history)
- `plans/worktree-update/` — Runbook (40 TDD cycles, 7 phases), design, orchestrator plan
- `plans/when-recall/design.md` — Vetted design document
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
