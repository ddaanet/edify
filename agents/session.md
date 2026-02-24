# Session Handoff: 2026-02-24

**Status:** Prioritized backlog. Merged orchestrate-evolution (recall skill tweak only — runbook planning not started). planstate-delivered worktree active.

## Completed This Session

- Prioritization report — 37 tasks scored via WSJF, report at `plans/reports/prioritization-2026-02-24.md`
  - Top 5: orchestrate evolution (5.3), session CLI tool (4.0, blocked), planstate delivered (3.8), session.md validator (2.6), WT merge session loss dx (2.6)
  - Parallel batch A identified: 4 independent sonnet tasks
- Created worktrees: orchestrate-evolution, planstate-delivered
- Discussion: test sentinel versioning (rejected — local cache, not versionable), sentinel copy on wt new (accepted as task)
- Merged `orchestrate-evolution` — recall skill tweak only (runbook planning not started in that worktree)
  - Merge artifact: autostrategy duplicated task into Pending + kept in Worktree Tasks. Manually cleaned

## Pending Tasks

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring




- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized | sonnet

- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet


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
- [ ] **UserPromptSubmit topic detection hook** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
  - Complementary to recall pass (cheap first layer vs deep pipeline integration)


- [ ] **Prioritize script assistance** — Automate mechanical parts of prioritization scoring | sonnet

- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet

- [ ] **Worktree merge session loss diagnosis** — RCA why `_worktree merge` autostrategy drops session.md context | sonnet
  - Root cause: focused session.md in branch lacks main's Worktree Tasks, autostrategy favors branch version
  - Observed: Merge 1 (`f525d705`) dropped WT entry, Merge 2 (`c91c7628`) left orphan + malformed blocker. Pre-merge: `0c91d969`
  - Fix target: `src/claudeutils/worktree/merge.py` session autostrategy
  - Related: planstate-delivered (plan: planstate-delivered) would prevent "completed but no record" class
- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle
  - Absorbs: Task agent guardrails — tool-call limits, regression detection, model escalation (haiku→sonnet→opus on capability mismatch) all additive. Design covers agent→user escalation and context-size heuristic but not inter-tier promotion or tool-call budgets
  - Absorbs: RED pass protocol — classification taxonomy, blast radius procedure, defect impact evaluation. Design has remediation + escalation patterns but not formal classification or blast radius assessment

- [x] **WT new sentinel copy** — Copy `tmp/.test-sentinel` during `_worktree new` | sonnet

- [ ] **Execute orchestrate-evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
- [ ] **Fix prepare-runbook.py step file generation bugs** — sonnet
  - Bug 1: `extract_cycles()` line 150 — only terminates on H2, not H3 phase headers; last cycle captures next phase's preamble
  - Bug 2: `generate_cycle_file()` line 1048 / `generate_step_file()` line 1000 — writes non-existent `runbook.md` path as provenance metadata
  - Diagnostic: `plans/prepare-runbook-fixes/diagnostic.md`
- [ ] **Fix validate-runbook.py false positives** — sonnet
  - model-tags: bash scripts under `agent-core/skills/` falsely flagged as prose artifacts
  - lifecycle: pre-existing files flagged as "modified before creation"
- [ ] **Fix wt merge dirty-tree guard** — Remove worktree-side clean-tree check from merge | sonnet
  - Plan: wt-merge-dirty-tree | Bug: merge blocks on dirty worktree even though it merges branch ref not working tree
  - Fix target: `src/claudeutils/worktree/merge.py`

## Worktree Tasks

- [ ] **Planstate delivered status** → `planstate-delivered` — `/runbook plans/planstate-delivered/outline.md` | sonnet
  - Plan: planstate-delivered | Status: designed
  - Grounded lifecycle: `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`
  - Single `lifecycle.md` per plan (append-only, last entry = status) replaces 4 marker files
  - 3 phases: core inference (TDD), merge integration (TDD), skill/prose updates (general)

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

**Learnings consolidated — 28 lines, 5 entries:**
- Next consolidation when entries age past 7 active days or file approaches 80-line soft limit.

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

**Worktree merge drops session.md Worktree Tasks entries:**
- Focused session in branch lacks main's full Worktree Tasks section. Autostrategy resolves in favor of branch, dropping main-only entries. Manual post-merge validation required until merge.py fixed.

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

- Code was written outside TDD discipline due to mis-triage. Implementation is correct (tests pass) but process was not followed. Design skill Simple criteria now strengthened to prevent recurrence. [from: sentinel-copy]
- model-tags validator matches `agent-core/skills/` path prefix too broadly — catches bash scripts (verify-step.sh, verify-red.sh) meant for deterministic execution, not LLM-consumed prose [from: orchestrate-evolution]
- lifecycle validator treats first mention of pre-existing file as "creation" — all prepare-runbook.py modifications flagged [from: orchestrate-evolution]
- Non-blocking: violations are false positives, not actual runbook problems [from: orchestrate-evolution]
## Next Steps

Create sentinel-copy worktree. WT new sentinel copy (quick). Then WT merge session loss dx or codebase sweep.

## Reference Files

- `plans/recall-pass/brief.md` — 4-pass model, reference forwarding, discussion conclusions
- `plans/reports/recall-pass-grounding.md` — Moderate grounding (CE + Agentic RAG synthesis)
- `plans/reports/recall-pass-internal-brainstorm.md` — 27 dimensions, project-specific constraints
- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases)
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-24.md` — WSJF scoring, 37 tasks ranked