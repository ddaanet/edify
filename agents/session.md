# Session Handoff: 2026-02-13

**Status:** Worktree-fixes worktree created, FR-6 added (automate session.md edits).

## Completed This Session

**Worktree skill end-to-end testing (12 tests, all passing):**
- Mode A: create worktree via `claudeutils _worktree new --task`, focused session generation
- Mode C: merge ceremony via `claudeutils _worktree merge`, precommit validation
- Error handling: non-existent task (exit 1), duplicate worktree (exit 1), non-existent slug (exit 2)
- Special chars: backticks/colons stripped, slug truncated at 30 chars (finding → FR-1)
- Clean state: branch deleted, worktree removed, session.md references cleared
- Cleaned up test artifacts (test-feature worktree removed, test report deleted)

**Findings from testing → requirements:**
- Session merge loses continuation lines: `_resolve_session_md_conflict` set-diffs single lines, loses indented metadata
- No-op merge skips commit: when conflict resolves to no net changes, phase 4 skips merge commit → branch orphaned → `git branch -d` rejects
- Task name slugs truncate badly: 30-char limit cuts mid-word, special chars stripped silently

**Requirements captured:** `plans/worktree-fixes/requirements.md` (6 FRs)
- FR-1: Task name constraints — prose identifiers `[a-zA-Z0-9 ]`, no truncation
- FR-2: Precommit task name validation
- FR-3: Migrate existing task names
- FR-4: Session merge preserves full task blocks (continuation lines)
- FR-5: Always create merge commit when merge initiated (fix orphan branch)
- FR-6: Automate session.md task movement on worktree create/remove (added post-commit)

**Worktree setup:**
- Created `worktree-fixes` worktree, moved task to Worktree Tasks

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

- [ ] **Workflow fixes from RCA** — Implement process improvements from 3 RCA reports | sonnet
  - Input: `plans/reports/rca-*-opus.md` (3 authoritative reports)
  - Key fixes: normalize runbook-review.md axes, add execution-time split enforcement, add vet investigation protocol + UNFIXABLE taxonomy, orchestrate template enforcement

- [ ] **Consolidate learnings** — learnings.md at 418 lines (soft limit 80) | sonnet
  - Blocked on: memory redesign (/when, /how)

- [ ] **Worktree merge combines session context** — Confirm wt-merge combines pending tasks/jobs (not --ours) and requires agent review | sonnet
  - Worktree-update delivered — blocker cleared, but wt-merge still uses --ours
  - Partially addressed: merge.py now has `_resolve_session_md_conflict` (set diff) but loses continuation lines → FR-4 in worktree-fixes

- [ ] **Learning ages computation after consolidation** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
  - Validate session.md pending tasks/worktree structure
  - Reject references to tmp/ files in committed content
  - Autofix or fail on duplicate memory index entries (blocked on memory redesign)

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet

- [ ] **Commit skill optimizations** — Remove handoff gate, optimize, branching fix | sonnet
  - Remove handoff gate, optimize with minimal custom script calls
  - Commit Gate B — coverage ratio (artifacts:reports 1:1) not boolean
  - Commit/handoff branching — move git branching point after precommit passes

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
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

- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
  - Blocked on: workflow improvements
  - Outline: `plans/error-handling/outline.md`
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
  - Plan: pushback | Status: requirements
- [ ] **Worktree fixes** → `worktree-fixes` — `/design plans/worktree-fixes/` | opus
  - Plan: worktree-fixes | Status: requirements
  - 6 FRs: task name constraints, precommit validation, migration, session merge blocks, merge commit fix, automate session edits

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md (confirmed fully superseded)

**Learnings.md over soft limit:**
- 418 lines — consolidation blocked on memory redesign

**wt-merge session reconciliation incomplete:**
- merge.py has auto-resolvers for session.md, learnings.md, jobs.md
- Session merge loses continuation lines (single-line set diff) → worktree-fixes FR-4
- No-op merge skips commit → orphan branch → worktree-fixes FR-5

**All tasks with documentation must have in-tree file references.**

## Reference Files

- `plans/workwoods/requirements.md` — Workwoods requirements (6 FRs, cross-tree awareness)
- `plans/pushback/requirements.md` — Pushback requirements (3 FRs, sycophancy prevention)
- `plans/process-review/rca.md` — Process RCA (5 plans examined, root cause in planning skill)
- `plans/reports/rca-*-opus.md` — 3 RCA reports (file growth, vet over-escalation, general-step detection)
- `plans/workflow-fixes/` — Unified runbook skill, plan-reviewer, pipeline-contracts (complete)
- `plans/worktree-update/` — Runbook + reports (complete, merged)
- `plans/when-recall/design.md` — Vetted design document
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/worktree-fixes/requirements.md` — Worktree fixes requirements (6 FRs, task naming + merge fixes + session automation)