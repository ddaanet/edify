# Session Handoff: 2026-02-20

**Status:** Documented git -C and subshell patterns for agent-core submodule ops in commit skill.

## Completed This Session

**Commit skill CWD patterns:**
- Updated `agent-core/skills/commit/SKILL.md` section 1b: `git -C agent-core` for git commands, `( cd agent-core && <cmd> )` subshell for non-git commands
- Added `submodule-safety` hook explanation — bare `cd agent-core` persists cwd and blocks subsequent Bash calls

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

- [ ] **Commit CLI tool** — `/runbook plans/commit-cli-tool/outline.md` | sonnet
  - Design complete. Outline serves as design (sufficiency gate passed — no full design.md needed)
  - 5 phases: extract _git (general), parser+validation (TDD), gate (TDD), pipeline (TDD), integration (TDD)

## Worktree Tasks



- [ ] **Handoff CLI tool** → `handoff-cli-tool` — Mechanical handoff+commit pipeline in CLI | `/design` | sonnet
  - Same pattern as worktree CLI: mechanical ops in CLI, judgment stays in agent
  - Inputs: status line (overwrite), completed text (overwrite committed / append uncommitted), optional files to add/remove, optional commit message with gitmoji
  - Outputs (conditional): learnings age status, precommit result, git status+diff (skip if precommit red), worktree ls. Suppress "nothing to report" outputs
  - Cache on failure: inputs to state file, rerun without re-entering skill
  - Domain boundaries: Handoff CLI owns status line + completed section + git ops + checks. Worktree CLI owns `→ slug` markers. Agent Edit owns: pending task mutations (insertion point = judgment), learnings append + invalidation, blockers, reference files
  - Learnings flow: Agent writes learnings (Edit) → reviews for invalidation (semantic anchoring) → then calls CLI
  - Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors. Build initial script first, then validate against git log corpus (exact/acceptable/wrong match rates). Tune or reject based on empirical results

- [ ] **Commit CLI tool** → `commit-cli-tool` — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Absorbs: Script commit vet gate (Gate B → scripted check)
  - Single command: precommit → gate → stage → commit in main + agent-core submodule


- [ ] **Orchestrate evolution** → `orchestrate-evolution` — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete (refreshed Feb 13), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

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

## Next Steps

4 worktrees active.

## Reference Files

- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)