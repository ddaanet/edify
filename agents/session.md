# Session Handoff: 2026-03-24

**Status:** Completed 4 inline tasks: remove-memory-index-skill, fix brief trigger, update tokens CLI, FR-4 bottom-to-top cleanup.

## Completed This Session

**Worktree cleanup:**
- Merged and removed `anchor-proof-state` worktree (1 line delta: edify-rename/lifecycle.md)
- Removed `discussion` worktree

**Remove memory-index skill:**
- Deleted `agent-core/skills/memory-index/` directory
- Removed `"memory-index"` from `corrector.md` skills frontmatter (line 7)
- Only consumer was corrector.md — other files referenced `agents/memory-index.md` (data file), not the skill

**Fix brief trigger:**
- Updated `agent-core/skills/brief/SKILL.md` description to lead with general mechanism
- Added "brief this" as explicit trigger; worktree use case now secondary

**Update tokens CLI:**
- `claudeutils tokens` model arg → `--model` option with `sonnet` default
- Updated test: `test_cli_requires_model_argument` → `test_cli_model_is_optional`

**FR-4: Remove bottom-to-top edit ordering:**
- Removed from 6 files: `tool-batching.md`, `item-review.md`, 4 role sys.md files
- Replaced with accurate rule: parallel when strings non-overlapping, sequential when one edit's result is another's target
- Renamed "Sequential Same-File Edits" → "Same-File Edits" in 4 role files + SYSPROMPT_GENERATION_GUIDE.md

## In-tree Tasks

- [ ] **Centralize recall** — `/design plans/centralize-recall/brief.md` | opus | restart
  - Plan: centralize-recall | Segmented /recall skill (<1ktok core), replace inline recall across skills/agents. Prerequisite (remove-index-skill) now complete.
- [x] **Remove index skill** — completed this session

## Worktree Tasks

- [ ] **Session CLI tool** → `session-cli-tool` — `/orchestrate handoff-cli-tool` | sonnet | restart | 3.7
  - Plan: handoff-cli-tool | Status: ready
  - Absorbs: Fix task-context bloat
  - Note: Blocker resolved (Bootstrap tag support). Step files generated. `/orchestrate handoff-cli-tool`
- [ ] **Edify rename** — `/design plans/edify-rename/` | opus
  - Plan: edify-rename | Status: reviewed (requirements proofed)
  - Blocked on: session-cli-tool merge (C-1). Design after merge — new content will change file counts.
  - FR-13: File PEP 541 claim on pypi/support for `edify` name (parallel, non-blocking for rename)
- [ ] **Worktree merge lifecycle** — `/runbook plans/worktree-merge-resilience/outline.md` | sonnet | 2.8
  - Plan: worktree-merge-resilience | Status: outlined
  - Absorbs: Merge lifecycle audit, Plan-completion ceremony
- [ ] **Active Recall** — `/design plans/active-recall/outline.md` | opus | 2.6
  - Plan: active-recall | Status: outlined
  - Outline Rev 2 reviewed. Next: Phase B (user discussion) → sufficiency gate → design or /runbook
  - Absorbs: Generate memory index (S-D), Recall learnings design (S-L), Codify branch awareness (S-L removes /codify)
  - S-B: **AR Recall Consolidate** [!] — Blocked: runbook skill improvements
  - S-D: **AR Hierarchy Index** — Blocked: S-A, S-B (design), S-J (impl)
  - S-E: **AR Trigger Metadata** — Blocked: S-C, S-D
  - S-F: **AR Mode Simplify** — Blocked: S-D
  - S-G: **AR Doc Pipeline** — Blocked: S-C, S-D, S-K
  - S-H: **AR Integration** — Blocked: S-D, S-F, S-J, S-L (terminal)
  - S-I: **AR Submodule Refactor** [!] — Blocked: runbook pipeline updates
  - S-J: **AR Submodule Setup** — Blocked: S-I
  - S-K: **AR Memory Corrector** — Blocked: S-C
  - S-L: **AR Capture Writes** — Blocked: S-J, S-K, S-D, S-E
  - **AR How Verb Form** — Plan: ar-how-verb-form | Status: briefed
  - **AR IDF Weighting** — Plan: ar-idf-weighting | Status: briefed
  - **AR Threshold Calibration** — Plan: ar-threshold-calibration | Status: planned
- [ ] **Merge any parent** — `/design plans/merge-parent-generalization/brief.md` | sonnet | 1.4
  - Plan: merge-parent-generalization | Status: briefed
  - Generalize `_worktree merge` to accept arbitrary parent branch. Enables worktree-from-worktree workflows.
- [ ] **Directive skill promotion** — `/design plans/directive-skill-promotion/brief.md` | opus | 2.2
  - Plan: directive-skill-promotion | Status: briefed
  - Absorbs: Handoff insertion policy, wrap command, discuss protocol grounding, p: classification gap, discuss-to-pending chain
- [ ] **Decision drift audit** — `/design plans/decision-drift-audit/brief.md` | sonnet | 1.6
  - Plan: decision-drift-audit | Status: briefed
  - Split from quality-grounding SP-2. Two phases: automated consistency scan → human proof. Feeds system-property-tracing.
- [ ] **System property tracing** — `/design plans/system-property-tracing/brief.md` | opus | 1.7
  - Plan: system-property-tracing | Status: briefed
  - Two phases: (1) system invariants as formal requirements, (2) pipeline traceability
  - Absorbs: research-backlog SP-1 (ground state coverage), SP-2 (workflow formal analysis), SP-3 (context loss as grounding input)
- [ ] **Skill-gated session edits** — `/design plans/skill-gated-session-edits/brief.md` | opus | 1.6
  - Plan: skill-gated-session-edits | Status: briefed
- [ ] **Parallel orchestration** — `/design plans/parallel-orchestration/brief.md` | sonnet | 1.8
  - Plan: parallel-orchestration | Status: briefed
- [ ] **Gate batch** — `/design plans/gate-batch/requirements.md` | sonnet | 1.6
  - Plan: gate-batch | Status: requirements
- [ ] **Worktree lifecycle CLI** — `/design plans/worktree-lifecycle-cli/brief.md` | sonnet | 1.6
  - Plan: worktree-lifecycle-cli | Status: briefed
  - Exit ceremony + Wt rm task cleanup + Worktree ad-hoc task + CLI UX + --base submodule bug
- [ ] **Code quality** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.4
  - Plan: codebase-sweep | Status: requirements
- [ ] **Hook batch** — `/design plans/hook-batch-2/requirements.md` | sonnet | 1.6
  - Plan: hook-batch-2 | Status: requirements
- [ ] **Update prioritize skill** — `/design plans/update-prioritize-skill/requirements.md` | sonnet | 1.2
  - Plan: update-prioritize-skill | Status: requirements
- [ ] **Cross-tree operations** — `/design plans/cross-tree-operations/requirements.md` | sonnet | 1.0
  - Plan: cross-tree-operations | Status: requirements
- [ ] **Tweakcc** — `/design plans/tweakcc/requirements.md` | sonnet | 1.0
  - Plan: tweakcc | Status: requirements
- [ ] **Design review protocol** — `/design plans/resumed-review-protocol/brief.md` | opus | restart | 1.6
  - Plan: resumed-review-protocol | Status: briefed
  - Two features: (1) runbook reuses corrector across phases, (2) orchestration ping-pong FIX/PASS
- [ ] **Markdown AST parser** — `/design plans/markdown-ast-parser/brief.md` | opus | 1.0
  - Plan: markdown-ast-parser | Status: briefed
  - Preprocessor → standard parser → AST. Complex — new dependency, cross-cutting migration.
- [ ] **Design context gate** — `/design plans/design-context-gate/brief.md` | sonnet | 1.6
  - Plan: design-context-gate | Status: briefed
- [ ] **Design JIT expansion** — `/design plans/design-jit-expansion/brief.md` | sonnet | 1.4
  - Plan: design-jit-expansion | Status: briefed
- [x] **Update tokens CLI** — completed this session
- [ ] **Threshold token migration** — `/design plans/threshold-token-migration/brief.md` | sonnet | 1.3
  - Plan: threshold-token-migration | Status: briefed
  - Migrate line-based thresholds to token-based. Large blast radius expected.
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart | 0.8
  - Plan: precommit-python3-redirect | Status: requirements
- [ ] **Fix TDD context scoping** — `/design plans/tdd-context-scoping/brief.md` | sonnet | 1.4
  - Plan: tdd-context-scoping | Status: briefed
- [ ] **Health check UPS fallback** — `/design plans/health-check-ups-fallback/requirements.md` | sonnet | 0.6
  - Plan: health-check-ups-fallback | Status: requirements
- [ ] **Review gate** — `/design plans/review-gate/requirements.md` | sonnet | 1.4
  - Plan: review-gate | Status: requirements
- [ ] **Feature prototypes** — `/design plans/prototypes/requirements.md` | sonnet | 0.6
  - Plan: prototypes | Status: requirements
- [ ] **Planstate brief inference** — `/design plans/planstate-brief-inference/requirements.md` | sonnet | 1.0
  - Plan: planstate-brief-inference | Status: requirements
- [ ] **Small fixes batch** — `/design plans/small-fixes-batch/requirements.md` | sonnet | 1.0
  - Plan: small-fixes-batch | Status: requirements
  - FR-4 complete. FR-1, FR-2, FR-3 remain.
- [ ] **Incident counting** — `/design plans/incident-counting/brief.md` | opus | 0.6
  - Plan: incident-counting | Status: briefed
- [ ] **Recall pipeline** — `/design` | sonnet | 1.0
  - Deduplication, stdin parsing, usage scoring for recall entries
  - Note: plan dir only exists in retro-repo-expansion worktree, not on main. Create plan dir before design.
- [ ] **Skill exit commit** — `/design plans/skill-exit-commit/requirements.md` | sonnet | 1.0
  - Plan: skill-exit-commit | Status: requirements
- [ ] **Discussion** — `d:` | sonnet
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet | 0.5
  - Blocked on human: curate task-contexts.json, annotate ground-truth.md
- [ ] **Anchor proof state** — `/design plans/proof-state-anchor/brief.md` | opus | restart
  - Plan: proof-state-anchor | Visible state + actions output at each transition. D+B anchor + user feedback.
- [x] **Fix brief trigger** — completed this session
- [ ] **Outline density gate** — `/design plans/outline-downgrade-density/brief.md` | opus
  - Plan: outline-downgrade-density | Content density check in write-outline.md downgrade criteria
- [ ] **Review blog series** — `/deliverable-review plans/blog-series` | opus | restart

### Terminal

- [-] **Calibrate topic params** — UPS topic injection removed, moot
- [-] **Recall tool consolidation** — absorbed into Active Recall
- [-] **Execute flag lint** — superseded by session validator
- [-] **Registry cache to tmp** — fixed inline, plan killed

- [ ] **Adaptive proof** — `/design plans/context-adaptive-proof/brief.md` | opus
  - Plan: context-adaptive-proof | Fork+summary when proof hits context limit
- [ ] **Interaction graph** — `/design plans/interaction-graph/brief.md` | sonnet
  - Plan: interaction-graph | DOT/HTML visualization of agentic-prose dependency structure
- [ ] **Invariant tracking** — `/design plans/invariant-tracking/brief.md` | opus
  - Plan: invariant-tracking | Prose-only exploration: express invariants as recall entries + corrector criteria
- [ ] **Proof verdict UX** — `/design plans/proof-verdict-ux/brief.md` | opus
  - Plan: proof-verdict-ux | Remove a/r/k/s; natural language carries verdicts
- [ ] **Sycophancy probe** — `/design plans/sycophancy-probe/brief.md` | sonnet
  - Plan: sycophancy-probe | Out-of-platform tool using session-scraper + API calls

## Blockers / Gotchas

**Post-merge validation (permanent):**
- After every worktree merge, validate session.md and learnings.md
- Known failure modes: autostrategy drops branch pending tasks, orphaned duplicates, branch overwrites main-only entries

**`_worktree rm` amend restored but task entry persists:**
- `remove_slug_marker` only strips marker — doesn't remove completed task entry. Pending in Worktree lifecycle CLI.

**Worktree merge drops session.md Worktree Tasks entries:**
- Focused session in branch lacks main's full Worktree Tasks section. Manual post-merge validation required.

**`just sync-to-parent` requires sandbox bypass**

**Main is worktree-tasks-only**

**Planstate CLI bug for briefed plans:**
- `_worktree ls` displays `requirements.md` path for `briefed` status. Use status field as source of truth.

**`session.py:307` format mismatch:**
- Produces `# Session: Worktree — {name}` but validator expects `# Session Handoff: YYYY-MM-DD`.

**`git stash` on `.claude/settings.local.json` requires sandbox bypass**

**Must complete both recall prerequisites before centralizing recall instructions**

- Handoff skill needs clarification: task name remains constant through lifecycle, must not specify next step [from: outline-density-gate]
- Plan artifact needed: `plans/handoff-task-naming/brief.md` [from: outline-density-gate]
- Must complete both prerequisites before centralizing recall instructions [from: retro-repo-expansion]
- Outline-proofing adds /proof to /runbook Tier 2. Remove-fuzzy-recall is Tier 2. If outline-proofing lands first, remove-fuzzy-recall gets the new /proof gate. No blocking dependency — order-independent. [from: retro-repo-expansion]
- SessionStart doesn't fire for new interactive sessions (#10373). Setup (env export, CLI install, staleness nag) only runs at session end via Stop fallback. [from: plugin-migration]
- Existing plan on main: `health-check-ups-fallback [requirements]` [from: plugin-migration]
- Contains 5 documented errors (see outline Design Corrections section). Outline supersedes design.md for all decisions. [from: plugin-migration]
- `remove-fuzzy-recall` planstate shows `[delivered]` but was pending in prior session — verify before deleting plan directory in FR-10
- pre-existing test failures: `tests/test_pretooluse_recipe_redirect.py` (3 tests) — not regressions

## Reference Files

- `plans/reports/prioritization-2026-03-12.md` — WSJF scoring, 42 tasks ranked
- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for workflow skills
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline
- `plans/active-recall/brief.md` — Active recall system
- `plans/system-property-tracing/brief.md` — System invariants + pipeline traceability
- `plans/decision-drift-audit/brief.md` — Decision file consistency audit (split from quality-grounding)
- `plans/merge-parent-generalization/brief.md` — Generalize merge to arbitrary parent branch
- `plans/threshold-token-migration/brief.md` — Line-based to token-based threshold migration
- `plans/edify-rename/requirements.md` — Full brand rename requirements (proofed)

## Next Steps

Centralize recall unblocked (remove-index-skill done). Session CLI tool active in worktree — highest priority next.
