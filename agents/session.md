# Session Handoff: 2026-02-21

**Status:** Fixed broken agent-core submodule. Merged/removed 3 worktrees (compression-detail-loss, merge-artifact-validation, worktree-cli-default). 2 unmerged (session-cli-tool, hook-batch — large divergence).

## Completed This Session

**Agent-core submodule recovery:**
- `core.worktree` in `.git/modules/agent-core/config` pointed to stale `hook-batch/agent-core` path — reset to `../../../agent-core`
- `git worktree repair` for parent repo links
- `git -C agent-core worktree add --detach` to recreate 4 submodule worktrees (agent-core2–5)
- Fixed agent-core HEAD per worktree via `git ls-tree HEAD agent-core` (4 were at wrong commit)

**Worktree merges/removals (3):**
- `compression-detail-loss` — 0 commits ahead, removed via `_worktree rm --force`
- `merge-artifact-validation` — 1 focused-session commit, merged (session.md conflict → kept ours)
- `worktree-cli-default` — 1 focused-session commit, merged (session.md conflict → kept ours)
- Tasks returned to Pending (none were complete)

**Unmerged worktrees (2):**
- `session-cli-tool` — 235 files changed, 15K+ added, 9.5K removed. Diverged significantly from main.
- `hook-batch` — 17 commits. Execution in progress.

## Pending Tasks

- [ ] **Quality infra reform** — `/runbook plans/quality-infrastructure/outline.md` | sonnet
  - Plan: quality-infrastructure | Status: designed
  - 3 FRs: deslop restructuring (FR-1), code density decisions (FR-2), agent rename (FR-3)
  - Phase 1: agent rename (general), Phase 2: deslop restructure (inline), Phase 3: code density (inline)
  - Subsumes: Rename vet agents (FR-3a). Absorbs: integration-first-tests
  - vet-agent deprecated (D-1), vet-taxonomy embedded (D-2), stale symlink cleanup in Phase 1f

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring

- [ ] **Planstate delivered status** — `/runbook plans/planstate-delivered/outline.md` | sonnet
  - Plan: planstate-delivered | Status: designed
  - Grounded lifecycle: `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`
  - Single `lifecycle.md` per plan (append-only, last entry = status) replaces 4 marker files
  - 3 phases: core inference (TDD), merge integration (TDD), skill/prose updates (general)

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

- [ ] **Session CLI tool** — `_session` group (handoff, status, commit) | sonnet
  - Plan: handoff-cli-tool | Status: designed
  - Combined outline at `plans/handoff-cli-tool/outline.md` (355 lines, 7 phases)
  - After pipeline fixes (done): outline review → sufficiency gate → `/runbook`
  - New requirement: commit subcommand must output shortened commit IDs (session scraping)

- [ ] **Runbook generation fixes** — `/design` | sonnet
  - prepare-runbook.py: model propagation (defaults to agent base, not phase-specified), phase numbering (counts boundaries, not actual numbers), phase context not extracted to step files, single agent instead of per-phase
  - Phase expansion: expansion agent introduces defects (wrong file refs, contradictory instructions, missing context from outline) requiring review+fix on every phase
  - Orchestrator plan: unjustified phase interleaving
  - Evidence: hook-batch pre-execution review — `plans/hook-batch/reports/runbook-pre-execution-review.md` (3 critical, 4 major, 3 minor)

- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized (handoff, commit, opus-design-question, next done) | sonnet

- [ ] **Merge artifact validation** — post-merge orphan detection in `_worktree merge` | sonnet
  - Plan: worktree-merge-resilience | Diagnostic: `plans/worktree-merge-resilience/diagnostic.md`
  - Pattern: in-place edits + tail divergence → git appends modified line as duplicate
  - Also: focused-session section stripping → content leaks into wrong section

- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet

- [ ] **Worktree CLI default** — `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

## Worktree Tasks

- [>] **Hook batch** → `hook-batch` — `/orchestrate plans/hook-batch/orchestrator-plan.md` | sonnet | restart
  - Plan: hook-batch | Status: executing (Phase 1 complete, Phase 2 Cycle 2.1 done)
  - Pre-execution fixes applied: per-phase agents (hb-p1–hb-p5), context files, model/phase metadata fixed
  - Pre-execution review: `plans/hook-batch/reports/runbook-pre-execution-review.md`



## Backlog

### Worktree
- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [ ] **Handoff wt awareness** — Only consolidate memory in main repo | sonnet
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution
- [x] **Worktree rm safety** — Exit code 2, dirty check, --force bypass (delivered, plan removed)

### Pipeline & Orchestration
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
- [ ] **Runbook evolution** — `/design plans/runbook-evolution/` | sonnet

### Memory & Learning
- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Plan: remember-skill-update | Outline reviewed, Phase B discussion next
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Absorbs: memory-index auto-sync, learning ages consol, rename remember skill (FR-10), remember agent routing (FR-11)
- [ ] **Merge learnings delta** — Reconcile learnings.md after diverged merge | sonnet
  - Plan: merge-learnings-delta | Strategy: main base + branch delta
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet

### Quality & Testing
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Migrate test suite to diamond** — Needs scoping | depends on runbook evolution
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator | FR-2/FR-4 depend on worktree-cli-default; FR-1/FR-3/FR-5 can proceed now

### Agents & Rules
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Task agent guardrails** — Tool-call limits, regression detection, model escalation | sonnet
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet

### Design (opus)
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state-machine review criteria** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart

### Prototypes & Exploration
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration prototype** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD cycle test optimization** — Selective test rerun via dependency analysis | sonnet

### Small Fixes
- [ ] **Simplify when-resolve CLI** — Single argument with when/how prefix | sonnet
- [ ] **Fix task-context.sh task list bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` → exit 128. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Fix: worktree-cli-default adds `--branch` flag

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate. Focused-session section stripping causes content to leak into wrong section positions.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

**Learnings at 174 lines — consolidation deferred:**
- Past 150-line trigger but 0 entries ≥7 active days. Aging required before graduation.

**Skill activation ~20% baseline:**
- Platform limitation — skill matching is pure LLM reasoning with no algorithmic routing. UserPromptSubmit hook with targeted patterns is the structural fix (hook batch Phase 1 items 8-9).

**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback designed in hook batch Phase 4.

**Submodule worktree refs — RESOLVED this session:**
- Root cause was `core.worktree` in `.git/modules/agent-core/config` overwritten by worktree submodule init. Fix: `git worktree repair` + `git -C agent-core worktree add --detach`. Use `git ls-tree HEAD agent-core` to get correct commit per worktree.

**Unmerged worktrees with large divergence:**
- session-cli-tool and hook-batch branches diverged significantly from main. session-cli-tool has 235 files changed (deletions of plans, tests, source that may have been re-added on main). Needs careful conflict resolution.

**`_worktree new` requires sandbox bypass:**
- Writes `.claude/settings.local.json` which is in sandbox deny list. Must use `dangerouslyDisableSandbox: true`.
- Partial failure leaves orphaned branch with focused-session commit. Clean up with `_worktree rm --force <slug>`.

- `/runbook` skill needs updates before it can process this outline [from: session-cli-tool]
- Outline is ready — blocker is skill-side, not artifact-side [from: session-cli-tool]
- learnings.md at 158 lines (>150 threshold), but consolidation was 1 day ago [from: session-cli-tool]
- Should consolidate on main branch, not in worktree [from: session-cli-tool]
## Next Steps

Hook batch executing in worktree. Quality infra reform `/runbook` next. Planstate delivered `/runbook`. 3 worktrees active (hook-batch, session-cli-tool, planstate-delivered). Submodule worktree refs fixed (core.worktree reset + `git worktree repair` + `git -C agent-core worktree add --detach`).

## Reference Files

- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases, grounded terminology)
- `plans/planstate-delivered/brief.md` — Original discussion decisions (pre-grounding)
- `plans/reports/lifecycle-terminology-grounding.md` — Grounding research (SmartBear, CI/CD, VSM)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/hook-batch/outline.md` — Hook batch outline (5 phases, 9 files, 8 decisions)
- `plans/hook-batch/brief.md` — Original brief (pre-design)
- `plans/handoff-cli-tool/brief.md` — Session CLI briefs (status subcommand + commit ID requirement)
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/outline.md` — Design outline (7 decisions, 3 phases, serves as design)
- `plans/quality-infrastructure/reports/explore-reviewer-usage.md` — vet-agent zero-usage evidence
- `plans/quality-infrastructure/reports/outline-review.md` — Review audit trail
- `plans/quality-infrastructure/requirements.md` — 3 FRs: deslop, code density decisions, agent rename
- `plans/quality-infrastructure/reports/agent-naming-brainstorm.md` — naming constraints and outcomes
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `plans/reports/code-density-grounding.md` — reframed general-first
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Combined session CLI outline (handoff + commit + status)