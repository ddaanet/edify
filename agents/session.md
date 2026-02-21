# Session Handoff: 2026-02-21

**Status:** Quality infra reform designed (outline = design, 7 decisions, 3 phases). Ready for `/runbook`.

## Completed This Session

**Quality infra reform — design (commit: 8e50563c):**
- Outline produced with 7 design decisions (D-1 through D-7)
- D-1: vet-agent deprecated (zero active call sites — `reports/explore-reviewer-usage.md`)
- D-2: vet-taxonomy.md embed in corrector. D-3: code deslop via project-conventions skill
- D-4: prose deslop → communication.md. D-5: phase ordering FR-3→FR-1→FR-2
- D-6: vet-requirement→review-requirement. D-7: vet skill → review skill
- Outline reviewed by outline-review-agent (3 major, 7 minor, all fixed)
- Reviewer open question resolved: deprecate vet-agent, not rename

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

- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized (handoff, commit, opus-design-question, next done) | sonnet

## Worktree Tasks


- [ ] **Merge artifact validation** → `merge-artifact-validation` — post-merge orphan detection in `_worktree merge` | sonnet
  - Plan: worktree-merge-resilience | Diagnostic: `plans/worktree-merge-resilience/diagnostic.md`
  - Pattern: in-place edits + tail divergence → git appends modified line as duplicate
  - Also: focused-session section stripping → content leaks into wrong section

- [ ] **Hook batch** → `hook-batch` — `/orchestrate plans/hook-batch/orchestrator-plan.md` | sonnet | restart
  - Plan: hook-batch | Status: ready (pre-execution review has 2 critical fixes needed)
  - 5 phases, 16 steps, agent + orchestrator plan generated
  - Pre-execution review: `plans/hook-batch/reports/runbook-pre-execution-review.md`

- [ ] **Diagnose compression detail loss** → `compression-detail-loss` — RCA against commit `0418cedb` | sonnet

- [ ] **Worktree CLI default** → `worktree-cli-default` — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`



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

**`_worktree new` requires sandbox bypass:**
- Writes `.claude/settings.local.json` which is in sandbox deny list. Must use `dangerouslyDisableSandbox: true`.
- Partial failure leaves orphaned branch with focused-session commit. Clean up with `_worktree rm --force <slug>`.

## Next Steps

Quality infra reform `/runbook` next. Planstate delivered `/runbook`. Hook batch `/orchestrate`. 6 worktrees active.

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
