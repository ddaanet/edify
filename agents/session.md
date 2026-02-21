# Session Handoff: 2026-02-21

**Status:** Consolidated backlog/todo into session.md. Created 6 worktrees. Verified and removed 3 more delivered plan directories (brief-skill, vet-invariant-scope, worktree-rm-safety). Planstate-delivered designed (outline = design, grounded terminology).

## Completed This Session

**Task list consolidation:**
- Deleted `agents/todo.md` — all items completed (unification ✅) or superseded (prompt-composer, handoff-discussion, task-agent-pattern)
- Merged `agents/backlog.md` into session.md Backlog section, deleted source file
- Removed 4 delivered items from backlog: worktree-skill, worktree-merge-data-loss, pretool-hook-cd-pattern, remaining-workflow-items
- Removed absorbed task stubs from Pending (SessionStart status hook, PostToolUse auto-format hook)

**Unscheduled plan assessment (3 delivered, removed):**
- `brief-skill` — skill delivered at `agent-core/skills/brief/SKILL.md`
- `vet-invariant-scope` — all 3 changes verified: Verification scope in vet-requirement.md + pipeline-contracts.md, lifecycle audit in orchestrate/SKILL.md, resume completeness in outline-review-agent.md
- `worktree-rm-safety` — code delivered: `--force` flag, exit code 2, dirty tree checks, tests in worktree/cli.py

**Worktree setup (6 created):**
- planstate-delivered, merge-artifact-validation, hook-batch, compression-detail-loss, worktree-cli-default, tokens-user-config

**New task:** Tokens user config — user config for ANTHROPIC_API_KEY (`.envrc` interferes with `claude` CLI auth, API token counting is free)

**Planstate delivered — grounding + design:**
- Grounded lifecycle terminology: 5 web searches, 2 page fetches, opus internal brainstorm (`plans/reports/lifecycle-terminology-grounding.md`, `plans/reports/ground-internal-lifecycle.md`)
- Two name changes: `defective` → `rework` (SmartBear/VSM precedent), `completed` → `reviewed` (cross-domain collision avoidance)
- Outline produced, reviewed twice (R1 marker-file version, R2 lifecycle.md version)
- Discussion: adopted single `lifecycle.md` (append-only) over 4 marker files — resolves review loop cycle without file deletion, provides audit trail
- Outline at `plans/planstate-delivered/outline.md` serves as design (7 decisions, 3 phases, all affected files identified)

## Pending Tasks

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

- [ ] **Planstate delivered status** → `planstate-delivered` — `/runbook plans/planstate-delivered/outline.md` | sonnet
  - Plan: planstate-delivered | Status: designed
  - Grounded lifecycle: `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`
  - Single `lifecycle.md` per plan (append-only, last entry = status) replaces 4 marker files
  - 3 phases: core inference (TDD), merge integration (TDD), skill/prose updates (general)

- [ ] **Merge artifact validation** → `merge-artifact-validation` — post-merge orphan detection in `_worktree merge` | sonnet
  - Plan: worktree-merge-resilience | Diagnostic: `plans/worktree-merge-resilience/diagnostic.md`
  - Pattern: in-place edits + tail divergence → git appends modified line as duplicate
  - Also: focused-session section stripping → content leaks into wrong section

- [ ] **Hook batch** → `hook-batch` — `/runbook plans/hook-batch/outline.md` | sonnet | restart
  - Absorbs: PostToolUse auto-format hook, SessionStart status hook
  - 5 phases: UserPromptSubmit (9 changes), PreToolUse recipe-redirect, PostToolUse auto-format, Session health (SessionStart + Stop fallback), Hook infrastructure (hooks.json + sync-to-parent merge)
  - Plan: hook-batch | Status: designed (outline complete)

- [ ] **Diagnose compression detail loss** → `compression-detail-loss` — RCA against commit `0418cedb` | sonnet

- [ ] **Worktree CLI default** → `worktree-cli-default` — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

- [ ] **Tokens user config** → `tokens-user-config` — User config (`~/.config/claudeutils/`) for ANTHROPIC_API_KEY so `tokens` command works without env var | sonnet
  - Problem: setting ANTHROPIC_API_KEY in .envrc interferes with `claude` CLI auth
  - API token counting is free — only need key routing, not a local tokenizer

- [ ] **Quality infra reform** → `quality-infra-reform` — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents (FR-3), Codebase quality sweep (FR-4)
  - Absorbs: integration-first-tests

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

Planstate delivered `/runbook` (outline = design, ready for planning). Hook batch `/runbook`. Session CLI tool `/runbook`. 6 worktrees active.

## Reference Files

- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases, grounded terminology)
- `plans/planstate-delivered/brief.md` — Original discussion decisions (pre-grounding)
- `plans/reports/lifecycle-terminology-grounding.md` — Grounding research (SmartBear, CI/CD, VSM)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/hook-batch/outline.md` — Hook batch outline (5 phases, 9 files, 8 decisions)
- `plans/hook-batch/brief.md` — Original brief (pre-design)
- `plans/handoff-cli-tool/brief.md` — Session CLI briefs (status subcommand + commit ID requirement)
- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Combined session CLI outline (handoff + commit + status)
