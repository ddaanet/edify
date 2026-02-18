# Session Handoff: 2026-02-18

**Status:** Re-prioritized backlog (42 tasks, rev 3). Merged runbook-skill-fixes (7ff7c081). 2 worktrees active.

## Completed This Session

**Backlog prioritization (rev 3):**
- Scored 42 tasks using WSJF methodology — `plans/reports/prioritization-2026-02-18.md`
- Key dependency: orchestrate evolution (3.8) blocked on design runbook evolution (2.5) — can't `/runbook` before runbook skill fixed
- Top actionable: design runbook evolution (2.5), worktree merge resilience (2.6), quality infrastructure reform (2.6)
- 4 parallel batches identified, 6 blocked tasks mapped

**Merged runbook-skill-fixes worktree (7ff7c081):**
- validate-runbook.py: 4 subcommands (model-tags, lifecycle, test-counts, red-plausibility)
- 20 tests, 5-phase TDD orchestration, deliverable review findings fixed
- Conflicts resolved: jobs.md deleted (planstate replaces it), session/learnings via ours + manual extraction
- Extracted: "Pipeline skill updates" task, 4 learnings (CLI testing, runbook editing, review conclusions, finding routing)
- 1068 tests pass (up from 1048)

**Worktree operations:**
- Created worktree for worktree-merge-resilience (opus design session)
- Cleaned up design-workwoods and runbook-skill-fixes worktrees

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-18.md (rev 3) -->

- [ ] **Design runbook evolution** — `/design plans/runbook-evolution/` | opus | restart
  - Requirements at `plans/runbook-evolution/requirements.md`
  - Outline exists at `plans/runbook-evolution/outline.md` — resume from Phase A.6 (outline review)
  - Scope: runbook SKILL.md generation directives only
  - 5 FRs: prose atomicity, self-modification discipline, testing diamond, deferred enforcement, test migration


- [ ] **Fix worktree rm dirty check** — Must not fail if parent repo is dirty, only if target worktree is dirty | sonnet

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents task (FR-3), augments Codebase quality sweep (FR-4)

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Blocked on: Error handling design (needs D-3 escalation criteria, D-5 rollback semantics)
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Script commit vet gate** — Replace prose Gate B with scripted check (file classification + vet report existence) | sonnet
  - Part of commit skill optimization (FR-5 partially landed — Gate A removed, Gate B still prose)
  - Also: remove `vet-requirement.md` from CLAUDE.md `@`-references, move execution context template to memory index

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Vet delegation routing** — Route review to artifact-appropriate agent (correct for code, skill-reviewer for skills, agent-creator for agents) | sonnet
  - General rule affecting vet-requirement.md and /runbook review delegation
  - agent-creator: Write+Read, confirmed cooperative in review mode (decisions/project-config.md:266)
  - skill-reviewer: Read/Grep/Glob only — cannot autofix, would need tool additions
  - No hook reviewer exists; no doc reviewer exists (readme skill is creation, not review)
  - Precedent: agent-creator repurposed for review via prompting (`/when agent-creator reviews agents`)

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Learnings consolidation done (491→32 lines) — FR-7 migration partially addressed via consolidation
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Agent rule injection** — process improvements batch | sonnet
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Specific targets from quality-infrastructure FR-4: `_git_ok`, `_fail` helpers, 13 raw subprocess replacements, 18 SystemExit replacements, custom exception classes

- [ ] **Remember agent routing** — blocked on memory redesign | sonnet
  - When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional target

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart

- [ ] **Worktree skill adhoc mode** — Add mode for creating worktree from specific commit without task tracking | sonnet

- [ ] **Explore Anthropic plugins** — Install all 28 official plugins, explore for safety+security relevance | sonnet | restart
  - Repo: `github.com/anthropics/claude-plugins-official`

- [ ] **Ground state-machine review criteria** — Research state coverage validation in plan review | opus

- [ ] **Pre-merge untracked file fix** — `new --session` leaves session.md untracked on main | sonnet

- [ ] **Safety review expansion** — Implement pipeline changes from grounding research | opus
  - Input: `plans/reports/safety-review-grounding.md`
  - Depends on: Explore Anthropic plugins

- [ ] **Test diagnostic helper** — Replace `subprocess.run(..., check=True)` in test setup with stderr surfacing | sonnet

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)
  - **Blocked on:** Design runbook evolution — can't generate runbook with broken tool

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

- [ ] **Debug failed merge** — Investigate the original merge failure (exit 128 during session.md conflict resolution) | sonnet
  - Context: Merge of `remaining-workflow-items` worktree on 2026-02-16
  - Branch had 1 post-merge commit (683fc7d), conflicts on `agent-core` submodule + `agents/session.md`
  - Main at 9bb45d0, merge result at 5e024c2
  - `git add agents/session.md` returned exit 128 during `_resolve_session_md_conflict` in `_phase3_merge_parent`
  - Now that error handling is fixed, we can reproduce and see the actual git error message

- [ ] **Runbook model assignment** — apply design-decisions.md directive (opus for skill/fragment/agent edits)
  - Partially landed via remaining-workflow-items merge
- [ ] **Runbook quality gates Phase B** — TDD for validate-runbook.py (4 subcommands) | sonnet
  - Depends on Phase A merge (SKILL.md references script)
  - Graceful degradation bridges gap (NFR-2)
  - model-tags, lifecycle, test-counts, red-plausibility

- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main tree from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Planstate `infer_state()` now auto-discovers plans (workwoods merged) — no jobs.md write needed


- [ ] **Revert cross-tree sandbox access** — Remove `additionalDirectories` code from `_worktree new` | sonnet
  - Superseded by git show transport — sandbox access unnecessary for cross-tree operations
  - Affects: cli.py `_setup_worktree()`, justfile, `test_new_sandbox_registration`

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)

- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution
  - Different scope and execution profile

- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate skill: create `/deliverable-review` pending task at exit (opus, restart)
  - Deliverable-review skill Phase 4: create one pending task for all findings → `/design`; no merge-readiness language
  - Design skill: add Phase 0 requirements-clarity gate (well-specified → triage, underspecified → `/requirements`)
  - Discussion context in runbook-skill-fixes worktree session

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

<!-- runbook-skill-fixes merged: orchestration + deliverable review complete, findings fixed -->

<!-- design-workwoods removed: merged (84c3029d), wt-rm clean -->

<!-- design-runbook-evolution removed: wt deleted, task back in Pending -->
<!-- worktree-merge-resilience removed: wt deleted, task back in Pending -->

- [ ] **Worktree merge resilience** → `worktree-merge-resilience` — `/design plans/worktree-merge-resilience/requirements.md` | opus
  - Plan: worktree-merge-resilience | Status: requirements
  - 5 FRs: submodule conflict pass-through, leave merge in progress, untracked file handling, conflict context output, idempotent resume
  - Addresses root cause of merge difficulties observed this session

## Blockers / Gotchas

**Merge tool aborts on conflict (Python only — justfile fixed):**
- `_worktree merge` still aborts and returns clean tree on source conflicts
- `just wt-merge` now leaves merge in progress, exits code 3 (FR-2 implemented)
- Python merge.py fix now unblocked (workwoods merged, resolve.py available)
- Requirements for remaining FRs: `plans/worktree-merge-resilience/requirements.md`

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files
- Always use `dangerouslyDisableSandbox: true` for any merge operation

**Transient git index.lock during merge:**
- `claudeutils _worktree merge` hits `index.lock` race condition during multi-step git operations
- Likely caused by file watcher (IDE/direnv) touching the index concurrently

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit

**`wt rm` leaves stale submodule config:**
- Removing a worktree can leave `.git/modules/agent-core/config` `core.worktree` pointing to the deleted directory
- Breaks all `git -C agent-core` operations on main until manually fixed

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Headings must include "To" (e.g., "How To Augment Agent Context")
- Index keys must NOT include "to" — validator adds it automatically

**User feedback annotations in working tree:**
- `src/claudeutils/cli.py` has 12 FIXME/TODO/antipattern comments from user code review
- `git checkout -- src/claudeutils/cli.py` to discard, or preserve as reference for quality-infrastructure design

**Merge ours resolution loses worktree content:**
- `just wt-merge` uses `checkout --ours` for session.md, learnings.md, jobs.md
- Drops worktree-side changes silently (learnings, completed work, design intent like deletions)
- Must verify post-merge: compare `git show <branch>:<file>` against merged result

## Next Steps

2 worktrees active: error-handling-design, worktree-merge-resilience. Learnings at 195/80 lines — run `/remember` when entries reach 7 days (0 entries ≥7 days currently).

## Reference Files

- `plans/reports/prioritization-2026-02-18.md` — WSJF task prioritization (rev 3, 42 tasks)
- `plans/worktree-merge-resilience/requirements.md` — 5 FRs for merge conflict handling
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
- `plans/reports/code-density-grounding.md` — Grounded research on exception handling + Black formatter interaction
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)
- `plans/runbook-evolution/requirements.md` — Runbook evolution (5 FRs, testing diamond, prose atomicity)
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
