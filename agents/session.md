# Session Handoff: 2026-03-14

**Status:** Re-prioritized 42 tasks. Merged retro-repo-expansion + anchor-proof-state. 8 plans delivered via merges. Proof SKILL.md conflict resolved + review fixes applied. Worktrees dispatched for Session CLI tool + Plugin migration + Discussion.

## Completed This Session

**Re-prioritization (42 tasks):**
- Scored all pending tasks via WSJF using `plans/prototypes/score.py`
- Session CLI tool rises to #1 (3.7, ME=1). Plugin migration holds #2 (3.2, DP=8)
- Report: `plans/reports/prioritization-2026-03-12.md`

**Worktree merges:**
- Merged retro-repo-expansion — plans + learnings, worktree preserved
- Merged anchor-proof-state — resolved proof SKILL.md conflicts (4 regions, kept HEAD's item-level review protocol), worktree preserved

**Proof SKILL.md review fixes (skill-reviewer):**
- Removed `/review-plan` parenthetical from corrector dispatch table
- Simplified author-corrector coupling to point directly to `pipeline-contracts.md`
- Deduplicated kill sub-action description (reference file defers to SKILL.md)

**Plans delivered via merges (8):**
- skill-agent-bootstrap, quality-grounding, review-agent-quality, design-pipeline-evolution
- markdown-migration, diagnose-compression-loss, research-backlog, retrospective-repo-expansion

**Worktree dispatch:**
- Created session-cli-tool, plugin-migration, discussion worktrees

## In-tree Tasks

- [ ] **Centralize recall** — `/design plans/centralize-recall/brief.md` | opus | restart
  - Plan: centralize-recall | Segmented /recall skill (<1ktok core), replace inline recall across skills/agents. Depends on: remove-fuzzy-recall, remove-index-skill
- [ ] **Remove fuzzy recall** — `/design plans/remove-fuzzy-recall/brief.md` | sonnet
  - Plan: remove-fuzzy-recall | Hard failure on no-match, "read memory-index" guidance
- [ ] **Remove index skill** — `/design plans/remove-memory-index-skill/brief.md` | opus
  - Plan: remove-memory-index-skill | Delete vestigial skill, update corrector.md to Read file directly

## Worktree Tasks

- [ ] **Session CLI tool** → `session-cli-tool` — `/orchestrate handoff-cli-tool` | sonnet | restart | 3.7
  - Plan: handoff-cli-tool | Status: ready
  - Absorbs: Fix task-context bloat
  - Note: Blocker resolved (Bootstrap tag support). Step files generated. `/orchestrate handoff-cli-tool`
- [ ] **Plugin migration** → `plugin-migration` — `/orchestrate plugin-migration` (refresh outline first) | opus | 3.2
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
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
- [x] **Skill agent bootstrap** — plan delivered
- [ ] **Worktree lifecycle CLI** — `/design plans/worktree-lifecycle-cli/brief.md` | sonnet | 1.6
  - Plan: worktree-lifecycle-cli | Status: briefed
  - Exit ceremony + Wt rm task cleanup + Worktree ad-hoc task + CLI UX + --base submodule bug
- [ ] **Code quality** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.4
  - Plan: codebase-sweep | Status: requirements
- [ ] **Hook batch** — `/design plans/hook-batch-2/requirements.md` | sonnet | 1.6
  - Plan: hook-batch-2 | Status: requirements
- [ ] **Update prioritize skill** — `/design plans/update-prioritize-skill/requirements.md` | sonnet | 1.2
  - Plan: update-prioritize-skill | Status: requirements
- [x] **Quality grounding** — plan delivered
- [ ] **Cross-tree operations** — `/design plans/cross-tree-operations/requirements.md` | sonnet | 1.0
  - Plan: cross-tree-operations | Status: requirements
- [x] **Review agent quality** — plan delivered
- [x] **Design pipeline evolution** — plan delivered
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
- [ ] **Update tokens CLI** — `/design plans/update-tokens-cli/brief.md` | haiku | 0.8
  - Plan: update-tokens-cli | Status: briefed
  - Make sonnet default model, update usage message
- [ ] **Threshold token migration** — `/design plans/threshold-token-migration/brief.md` | sonnet | 1.3
  - Plan: threshold-token-migration | Status: briefed
  - Migrate line-based thresholds to token-based. Large blast radius expected.
- [x] **Markdown migration** — plan delivered
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart | 0.8
  - Plan: precommit-python3-redirect | Status: requirements
- [x] **Diagnose compression loss** — plan delivered
- [x] **Research backlog** — plan delivered
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
  - FR-4 added: remove bottom-to-top edit ordering refs
- [ ] **Incident counting** — `/design plans/incident-counting/brief.md` | opus | 0.6
  - Plan: incident-counting | Status: briefed
- [x] **Retro repo expansion** → `retro-repo-expansion` — plan delivered
- [ ] **Recall pipeline** — `/design` | sonnet | 1.0
  - Deduplication, stdin parsing, usage scoring for recall entries
  - Note: plan dir only exists in retro-repo-expansion worktree, not on main. Create plan dir before design.
- [ ] **Skill exit commit** — `/design plans/skill-exit-commit/requirements.md` | sonnet | 1.0
  - Plan: skill-exit-commit | Status: requirements
- [ ] **Discussion** → `discussion` — `d:` | sonnet
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet | 0.5
  - Blocked on human: curate task-contexts.json, annotate ground-truth.md
- [ ] **Anchor proof state** → `anchor-proof-state` — `/design plans/proof-state-anchor/brief.md` | opus | restart
  - Plan: proof-state-anchor | Visible state + actions output at each transition. D+B anchor + user feedback.
- [ ] **Fix brief trigger** — edit `agent-core/skills/brief/SKILL.md` description to lead with general mechanism | opus
  - Plan: none — direct edit. Brief skill description starts with "Transfer context... to a worktree task" causing mid-sentence `/brief` invocations to be missed
- [ ] **Outline density gate** → `outline-density-gate` — `/design plans/outline-downgrade-density/brief.md` | opus
  - Plan: outline-downgrade-density | Content density check in write-outline.md downgrade criteria
- [ ] **Review blog series** — `/deliverable-review plans/blog-series` | opus | restart

### Terminal

- [-] **Calibrate topic params** — UPS topic injection removed, moot
- [-] **Recall tool consolidation** — absorbed into Active Recall
- [-] **Execute flag lint** — superseded by session validator
- [-] **Registry cache to tmp** — fixed inline, plan killed

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

## Reference Files

- `plans/reports/prioritization-2026-03-12.md` — WSJF scoring, 42 tasks ranked
- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for workflow skills
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline
- `plans/active-recall/brief.md` — Active recall system
- `plans/system-property-tracing/brief.md` — System invariants + pipeline traceability
- `plans/decision-drift-audit/brief.md` — Decision file consistency audit (split from quality-grounding)
- `plans/merge-parent-generalization/brief.md` — Generalize merge to arbitrary parent branch
- `plans/threshold-token-migration/brief.md` — Line-based to token-based threshold migration

## Next Steps

Session CLI tool and Plugin migration active in worktrees. Discussion worktree available. Anchor-proof-state and outline-density-gate worktrees preserved from merge — continue or `wt-rm`.
