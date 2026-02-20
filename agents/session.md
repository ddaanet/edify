# Session Handoff: 2026-02-20

**Status:** Merged all worktrees, wrote combined session CLI outline (handoff + commit + status).

## Completed This Session

**Worktree consolidation:**
- Removed merge-resolution worktree (discarded, no merge)
- Merged orchestrate-evolution (commits: focused session + D-5 ping-pong TDD design)
- Merged commit-cli-tool (commits: focused session + commit CLI design)
- Merged handoff-cli-tool (commits: focused session + outline + outline refinement)
- Post-merge learnings verification: no pre-consolidation duplicates in any merge

**Session CLI outline:**
- Combined handoff + commit outlines into unified `_session` group at `plans/handoff-cli-tool/outline.md` (355 lines)
- Added status subcommand section, unified shared infrastructure (S-1 through S-4), harmonized exit codes
- Resolved open question: completed section committed detection → auto-strip
- Deleted `plans/commit-cli-tool/` (absorbed)

**Discussion conclusions:**
- Outline-level merge > requirements restart (outlines post-sufficiency-gate, decisions validated through 7 review rounds)
- Single combined file > split files (LLM semantic integrity — cross-cutting consistency at write time)
- Pipeline fixes before 7-phase runbook (don't compound pipeline leaks at scale)

## Pending Tasks

- [ ] **When recall evaluation** — sonnet
- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet

- [ ] **PostToolUse auto-format hook** — PostToolUse hook on Write/Edit running formatter on changed file | sonnet | restart

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

- [ ] **SessionStart status hook** — Bundled hook: dirty tree warning, learnings limit, stale worktree detection, model tier display, tip rotation | sonnet | restart

- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate: `/deliverable-review` pending task at exit
  - Design skill: Phase 0 requirements-clarity gate
  - Absorbs: vet-invariant-scope, inline-phase-type
  - Insights input: Diamond TDD definition needed at `/design` (direct execution path), `/runbook` (step generation), `tdd-task` agent (cycle execution)
  - Discussion context in runbook-skill-fixes worktree session

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents (FR-3), Codebase quality sweep (FR-4)
  - Absorbs: integration-first-tests

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

- [ ] **Audit rules for design-history noise** — Scan fragments/skills for design history embedded in directives (rejected alternatives). Distinguish from functional motivation (why the rule exists) which stays. | opus
- [ ] **Design skill review gate fix** — Apply transition-gated wording to Phase B step 4 in design/SKILL.md. Include motivation (review validates cross-cutting consistency that individual approvals don't check). | sonnet
- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized (handoff and commit done) | sonnet
- [ ] **Pending task capture wording** — Fix agent tendency to capture pending tasks verbatim instead of rewording with context from the discussion | opus
- [ ] **Session CLI tool** — `_session` group (handoff, status, commit) | sonnet
  - Plan: handoff-cli-tool | Status: designed
  - Combined outline at `plans/handoff-cli-tool/outline.md` (355 lines, 7 phases)
  - Blocked on: Pipeline skill updates (fix pipeline leaks before running 7-phase runbook)
  - After pipeline fixes: outline review → sufficiency gate → `/runbook`

## Worktree Tasks

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

**Learnings at 150 lines — consolidation overdue:**
- 150 lines, 80-line soft limit. `/remember` needed urgently.

## Next Steps

Pipeline skill updates is the critical path — opus, restart required. Session CLI tool blocked on it.

## Reference Files

- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Combined session CLI outline (handoff + commit + status)
