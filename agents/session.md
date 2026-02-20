# Session Handoff: 2026-02-20

**Status:** Worktree setup for parallel tasks. Merging when-recall-evaluation.

## Completed This Session

- [x] **Pipeline skill updates** — design skill review gate fix, pending task capture wording, design-history noise audit, deslop 2 skills, batch decomposition in vet-requirement, verification scope in vet template
- [x] **When recall evaluation**
- Worktree setup: pipeline-skill-updates (opus), when-recall-evaluation (sonnet)

## Pending Tasks


- [ ] **Hook batch** — `/runbook plans/hook-batch/outline.md` | sonnet | restart
  - Absorbs: PostToolUse auto-format hook, SessionStart status hook
  - 5 phases: UserPromptSubmit (9 changes), PreToolUse recipe-redirect, PostToolUse auto-format, Session health (SessionStart + Stop fallback), Hook infrastructure (hooks.json + sync-to-parent merge)
  - Plan: hook-batch | Status: designed (outline complete)

- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet

- [ ] **Context optimization** — Fragment demotion from CLAUDE.md | sonnet
  - Plan: context-optimization | Status: designed
  - Depends on: Hook batch (denylist + PreToolUse hook replace project-tooling.md)
  - ~6.6k tokens demotable (26%), injection points in worktree/design/orchestrate/hook-dev/plugin-dev/token-efficient-bash skills

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

- [ ] **SessionStart status hook** — Absorbed into Hook batch
- [ ] **PostToolUse auto-format hook** — Absorbed into Hook batch

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents (FR-3), Codebase quality sweep (FR-4)
  - Absorbs: integration-first-tests

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

- [ ] **Session CLI tool** — `_session` group (handoff, status, commit) | sonnet
  - Plan: handoff-cli-tool | Status: designed
  - Combined outline at `plans/handoff-cli-tool/outline.md` (355 lines, 7 phases)
  - After pipeline fixes (done): outline review → sufficiency gate → `/runbook`
  - New requirement: commit subcommand must output shortened commit IDs (session scraping)

- [x] **Audit rules for design-history noise** — completed in pipeline-improvements
- [x] **Design skill review gate fix** — completed in pipeline-improvements
- [x] **Pending task capture wording** — completed in pipeline-improvements
- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized (handoff, commit, opus-design-question, next done) | sonnet

- [x] **When recall evaluation** — sonnet

## Worktree Tasks

(none — both merged)

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` → exit 128. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Fix: worktree-cli-default adds `--branch` flag

**Merge resolution silently corrupts learnings and blockers:**
- Learnings: line-set-difference reintroduces pre-consolidation entries when branch diverged before `/remember`. Blockers: focused sessions have no blockers section, so resolved blockers aren't detected
- **Manual post-merge check required:** After `wt merge`, verify learnings.md for pre-consolidation duplicates (diff against ancestor) and blockers for items fixed by the branch's work

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

**Learnings at 158 lines — consolidation deferred:**
- Past 150-line trigger but 0 entries ≥7 active days. Aging required before graduation.

**Skill activation ~20% baseline:**
- Platform limitation — skill matching is pure LLM reasoning with no algorithmic routing. UserPromptSubmit hook with targeted patterns is the structural fix (hook batch Phase 1 items 8-9).

**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback designed in hook batch Phase 4.

## Next Steps

Pipeline skill updates merged. Hook batch `/runbook` is next. Session CLI tool unblocked.

## Reference Files

- `plans/hook-batch/outline.md` — Hook batch outline (5 phases, 9 files, 8 decisions)
- `plans/hook-batch/userpromptsubmit-plan.md` — UserPromptSubmit details (partially superseded by outline D-5, D-7)
- `plans/hook-batch/reports/outline-review-2.md` — Final outline review
- `plans/hook-batch/reports/b-directive-brainstorm.md` — b: = brainstorm analysis
- `plans/hook-batch/brief.md` — Original brief (pre-design)
- `plans/context-optimization/brief.md` — Fragment demotion analysis (demotable/stays/blocked)
- `plans/handoff-cli-tool/brief.md` — Session CLI briefs (status subcommand + commit ID requirement)
- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Combined session CLI outline (handoff + commit + status)