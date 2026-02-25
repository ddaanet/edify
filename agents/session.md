# Session Handoff: 2026-02-25

**Status:** Skills quality pass designed. Sonnet scouts produced skill inventory (30 skills graded) and gate audit (12 prose-only gates). Design document and recall artifact written, ready for `/runbook`.

## Completed This Session

- Designed skills-quality-pass: triage (Moderate), `/recall all`, 2 sonnet scouts, design.md + recall-artifact.md
  - Inventory: 30 skills graded A+ to C. 18/30 description anti-pattern, 15/30 "When to Use" preamble, 3 C-grade (review, orchestrate, token-efficient-bash)
  - Gate audit: 12 genuine prose-only gates across 7 files. 3 high (design skill routing gates), 4 medium, 5 low
  - Discussion: doc update for regression prevention (yes) vs optimize-skill skill (no — low recurrence)
  - Haiku scouts re-run at sonnet after user correction — haiku produced 3 false positives in gate audit, uncritical grading in inventory

## Pending Tasks

- [x] **Fix when-resolve double-to and cross-operator** — 4 bugs fixed via TDD | sonnet
- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Skills quality pass** — `/runbook plans/skills-quality-pass/design.md` | sonnet
  - Plan: skills-quality-pass | Status: designed
  - 3 workstreams: deslop (30 skills), D+B gate anchoring (12 gates/7 files), doc update (regression prevention)
  - Opus required for all prose edits (pipeline-contracts.md). Bootstrapping order: corrector agents first
  - Reports: `plans/skills-quality-pass/reports/skill-inventory.md`, `plans/skills-quality-pass/reports/full-gate-audit.md`

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

- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed (outline reviewed, ready for runbook)
  - `/prime` skill (ad-hoc plan context) + two-section task list (In-tree / Worktree Tasks)
  - Scope: `session.py`, `resolve.py`, `aggregation.py`, `session_structure.py`, handoff skill, execute-rule.md
- [ ] **Recall CLI integration** — Production `claudeutils _recall` CLI (check/resolve/diff), Click, TDD | sonnet
  - Prototype delivered via recall-tool-anchoring worktree
- [ ] **Prose gate anchoring terminology** — Find proper name for D+B pattern, ground, update docs | opus

- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet

- [ ] **Execute orchestrate-evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
- [ ] **Fix validate-runbook.py false positives** — sonnet
  - model-tags: bash scripts under `agent-core/skills/` falsely flagged as prose artifacts
  - lifecycle: pre-existing files flagged as "modified before creation"

- [ ] **Deliverable review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Worktree new fuzzy matching** — `_worktree new` accepts approximate task names instead of exact match | sonnet

- [ ] **Codify learnings** — `/codify` | opus
  - Learnings at 80 lines (AT soft limit) — consolidation urgent

- [ ] **Skill progressive disclosure** — `d:` discuss optimizing /runbook and /design for progressive disclosure: fast paths don't need whole skill loaded | opus

## Worktree Tasks

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping (resolved):**
- Operator prefix no longer used in matching — bare trigger matching handles both `/when` and `/how` entries
- `removeprefix("to ")` in resolver strips leftover "to" from "how to X" invocations

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

**Possible Claude Code skill caching:**
- On-disk skills current, but `/design` and `/reflect` invocations received older content. No structural fix — awareness only.

## Next Steps

Skills quality pass: `/runbook plans/skills-quality-pass/design.md`. Codify learnings urgent (78/80).

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
- `plans/recall-tool-anchoring/outline.md` — Recall gate tool-anchoring design (D+B + reference manifest)
- `plans/recall-tool-anchoring/recall-artifact.md` — 11 entries, reference manifest format
- `plans/recall-tool-anchoring/reports/recall-gate-inventory.md` — 31 gates inventoried across 13 files
- `plans/task-classification/outline.md` — `/prime` skill + two-section task list design (8 rounds, reviewed)
- `plans/task-classification/reports/outline-review.md` — Corrector review (0 critical, 3 major fixed)
- `plans/task-lifecycle/outline.md` — Planstate-derived commands + STATUS continuation design
- `plans/when-resolve-fix/diagnostic-double-to.md` — Double-to + cross-operator bugs, TDD plan, code paths
- `plans/when-resolve-fix/reports/corrector-review.md` — Corrector review of 4-bug fix (0 critical, 0 major)
- `plans/skills-quality-pass/design.md` — Skills quality pass design (3 workstreams, 7 FRs, 4 NFRs)
- `plans/skills-quality-pass/recall-artifact.md` — 12 recall entries for downstream consumers
- `plans/skills-quality-pass/reports/skill-inventory.md` — Sonnet scout: 30 skills graded, 5 anti-patterns identified
- `plans/skills-quality-pass/reports/full-gate-audit.md` — Sonnet scout: 12 prose-only gates, fix directions