# Session Handoff: 2026-02-23

**Status:** Worktree management session — merged 4 worktrees, created 4 new ones, merged backlog into pending.

## Completed This Session

**Worktree merges:**
- `runbook-fenced-blocks` — merged (commit: 073f4ad7) + removed. Clean merge, task complete
- `remember-skill-update` — merged (commit: 38fa0d80). `rm` failed at amend step (merge-commit issue) then `--force` failed at submodule removal. Directory needs manual `rm -rf /Users/david/code/claudeutils-wt/remember-skill-update`. Task completed on branch; successor task (UserPromptSubmit topic detection hook) came through
- `merge-artifact-validation` — merged (commit: 7071b523). Conflict in `tests/test_validation_learnings.py` (orphan detection vs preamble line count). Resolved: dropped filler line to keep `---` within 10-line preamble zone, split test file (438 → 284 + 159 lines). Workaround — see pending task for real fix
- `session-cli-tool` — merged (commit: d51c6459) + removed. Task still live (blocked)

**Session housekeeping:**
- Merged Backlog section into Pending Tasks — eliminated separate section, 30 items in flat list to prevent bitrot
- Removed "Simplify when-resolve CLI" — absorbed into remember-skill-update worktree
- Removed fenced code block parsing blocker (fix shipped)
- Added "Phase-scoped agent context" task — per-phase agent generation in prepare-runbook.py
- Added "Worktree new error formatting" task — error output cleanup
- Added "Learnings validator structural boundaries" task — orphan detector uses line count not structure

**Worktrees created:**
- `merge-artifact-validation` — merged this session
- `session-cli-tool` — merged this session
- `phase-scoped-agents` — Phase-scoped agent context (sonnet)
- `wt-new-errors` — Worktree new error formatting (sonnet)

## Pending Tasks

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
  - Absorbs: Task agent guardrails — tool-call limits, regression detection, model escalation (haiku→sonnet→opus on capability mismatch) all additive. Design covers agent→user escalation and context-size heuristic but not inter-tier promotion or tool-call budgets
  - Absorbs: RED pass protocol — classification taxonomy, blast radius procedure, defect impact evaluation. Design has remediation + escalation patterns but not formal classification or blast radius assessment
  - Depends on: Phase-scoped agent context (prepare-runbook.py generates per-phase agents, orchestrate dispatches)

- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized | sonnet

- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet

- [ ] **Consolidate learnings** — `/remember` | sonnet
  - learnings.md at 227 lines (>150 trigger), 0 entries ≥7 active days

- [ ] **Worktree rm confirm gate fix** — fix `rm --confirm` gate | sonnet
  - Separated from CLI default task as orthogonal

- [ ] **Precommit python3 redirect** — `/design plans/precommit-python3-redirect/brief.md` | sonnet
  - PreToolUse hook: intercept python3/uv-run/ln patterns, redirect to correct invocations

- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [ ] **Handoff wt awareness** — Only consolidate memory in main repo | sonnet
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **Merge learnings delta** — Reconcile learnings.md after diverged merge | sonnet
  - Plan: merge-learnings-delta | Strategy: main base + branch delta
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Migrate test suite to diamond** — Needs scoping | depends on runbook evolution (delivered)
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator | worktree-cli-default merged; all FRs can proceed
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state-machine review criteria** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration prototype** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD cycle test optimization** — Selective test rerun via dependency analysis | sonnet
- [ ] **Fix task-context.sh task list bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [!] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet
  - Plan: handoff-cli-tool | Status: designed (outline reviewed 6 rounds, ready for runbook)
  - `_session` group (handoff, status, commit)
  - Discussion conclusions baked into outline: amend, git passthrough, deviation-only output, submodule labeling
  - Blocked on: Phase-scoped agent context (mixed-type runbook needs per-phase agent generation)
- [ ] **UserPromptSubmit topic detection hook** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
- [ ] **Learnings validator structural boundaries** — orphan detector should use `---`/first `## ` as preamble boundary, not hardcoded 10-line count | sonnet
  - Current: `_detect_orphaned_content()` skips first 10 lines, flags non-heading content after. `---` on line 11+ flagged as orphaned
  - Fix: detect preamble end structurally. Test fixtures updated as workaround (test_validation_learnings.py)

## Worktree Tasks

- [ ] **Phase-scoped agent context** → `phase-scoped-agents` — `/design` | sonnet
  - prepare-runbook.py emits per-phase agents with phase-scoped shared context instead of one agent per runbook
  - Same base type can serve multiple phases — differentiator is injected context, not protocol
  - Orchestrate-evolution depends on this for dispatch side

- [ ] **Worktree new error formatting** → `wt-new-errors` — clean up `derive_slug` error output (duplicated traceback, no agent-friendly guidance) | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

**Learnings at 227 lines — consolidation deferred:**
- Past 150-line trigger but 0 entries ≥7 active days. Aging required before graduation.

**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback deployed (Phase 4).

**`_worktree new` requires sandbox bypass:**
- Writes `.claude/settings.local.json` which is in sandbox deny list. Must use `dangerouslyDisableSandbox: true`.

**Custom agents not discoverable as subagent_types:**
- `.claude/agents/*.md` files with proper frontmatter weren't available via Task tool. Built-in types work. May need platform investigation.

**`_worktree rm --force` doesn't restore task to Pending:**
- `rm --force` removes worktree but leaves task in Worktree Tasks section. Manual session.md edit needed to move back to Pending.

**`_worktree rm` fails on merge commits:**
- `_update_session_and_amend` calls `git commit --amend` which fails on merge commits (exit 128). Then `--force` can fail on submodule removal. Manual `rm -rf` of directory needed after.

**Orphaned remember-skill-update directory:**
- `/Users/david/code/claudeutils-wt/remember-skill-update` — git deregistered but directory remains. Needs manual removal.

## Next Steps

Two worktrees active: `phase-scoped-agents` (sonnet), `wt-new-errors` (sonnet). Manual cleanup needed for remember-skill-update directory.

## Reference Files

- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases)
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
