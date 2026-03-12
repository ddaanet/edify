# Session Handoff: 2026-03-12

**Status:** /proof completed on 7 rewritten briefs (22 items). 8 approved, 7 revised, 7 killed. Decision drift audit extracted to own plan. markdown-migration has no remaining scope. 3 new tasks created. Post-design-split convention established.

## Completed This Session

**/proof of 7 briefs (22 items):**
- Reviewed: quality-grounding, skill-agent-bootstrap, research-backlog, design-pipeline-evolution, review-agent-quality, diagnose-compression-loss, markdown-migration
- Verdicts: 8 approved, 7 revised, 7 killed (absorbed or no remaining scope)
- Key revisions:
  - quality-grounding SP-2 → extracted to `plans/decision-drift-audit/` (two phases: automated scan → human proof)
  - skill-agent-bootstrap SP-1 → validate on 3, batch-apply remaining
  - skill-agent-bootstrap SP-3 → un-killed, non-user-invocable skill for project conventions (spike: skills: frontmatter on skills?)
  - research-backlog SP-1/SP-2/SP-3 → absorbed into system-property-tracing
  - research-backlog SP-5 → reframed as degraded-function protocol
  - design-pipeline-evolution S-A → add grounding step before design
  - design-pipeline-evolution S-B → late-binding model selection per pipeline stage
  - review-agent-quality → merged two workstreams into unified corrector quality audit
- Kills: SP-4 prompt-composer (no need), token cache API (YAGNI), programmatic thresholds (absorbed into SP-2), prose thresholds (artificial AST dependency)
- Post-design-split addendum added to 5 briefs
- markdown-migration: all sub-problems killed/absorbed/subsumed — plan candidate for closure

**Process decisions:**
- Post-design-split convention: multi-SP plans stay together through design, split into separate tasks post-design. Parent delivers at "designed" (terminal). Learning added.
- Late-binding model selection: per pipeline stage, not per task
- merge-parent-generalization identified as enabler for worktree-from-worktree workflows

## In-tree Tasks

- [x] **Problem.md migration** — `/design plans/problem-md-migration/brief.md` | sonnet
  - Plan: problem-md-migration | Status: briefed

## Worktree Tasks

- [x] **Review recall gate** — `/deliverable-review plans/recall-gate` | opus | restart
- [x] **Fix recall-gate findings** — applied inline
- [x] **Interactive review** — delivered, plan archived
- [x] **Fix proof review findings** — applied inline
- [ ] **Session CLI tool** — `/orchestrate handoff-cli-tool` | sonnet | restart | 3.2
  - Plan: handoff-cli-tool | Status: ready
  - Absorbs: Fix task-context bloat
  - Note: Blocker resolved (Bootstrap tag support). Step files generated. `/orchestrate handoff-cli-tool`
- [ ] **Plugin migration** — `/orchestrate plugin-migration` (refresh outline first) | opus | 3.2
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
- [ ] **Merge any parent** — `/design plans/merge-parent-generalization/brief.md` | sonnet
  - Plan: merge-parent-generalization | Status: briefed
  - Generalize `_worktree merge` to accept arbitrary parent branch. Enables worktree-from-worktree workflows.
- [ ] **Directive skill promotion** — `/design plans/directive-skill-promotion/brief.md` | opus | 2.2
  - Plan: directive-skill-promotion | Status: briefed
  - Absorbs: Handoff insertion policy, wrap command, discuss protocol grounding, p: classification gap, discuss-to-pending chain
- [ ] **Decision drift audit** — `/design plans/decision-drift-audit/brief.md` | sonnet
  - Plan: decision-drift-audit | Status: briefed
  - Split from quality-grounding SP-2. Two phases: automated consistency scan → human proof. Feeds system-property-tracing.
- [ ] **System property tracing** — `/design plans/system-property-tracing/brief.md` | opus
  - Plan: system-property-tracing | Status: briefed
  - Two phases: (1) system invariants as formal requirements, (2) pipeline traceability
  - Absorbs: research-backlog SP-1 (ground state coverage), SP-2 (workflow formal analysis), SP-3 (context loss as grounding input)
- [ ] **Skill-gated session edits** — `/design plans/skill-gated-session-edits/brief.md` | opus
  - Plan: skill-gated-session-edits | Status: briefed
- [ ] **Parallel orchestration** — `/design plans/parallel-orchestration/brief.md` | sonnet | 1.8
  - Plan: parallel-orchestration | Status: briefed
- [ ] **Gate batch** — `/design plans/gate-batch/requirements.md` | sonnet | 1.7
  - Plan: gate-batch | Status: requirements
- [ ] **Skill agent bootstrap** — `/design plans/skill-agent-bootstrap/brief.md` | opus | 1.6
  - Plan: skill-agent-bootstrap | Status: briefed
  - SP-3 revised: non-user-invocable skill for project conventions (spike: skills: frontmatter on skills?)
- [ ] **Worktree lifecycle CLI** — `/design plans/worktree-lifecycle-cli/brief.md` | sonnet | 1.6
  - Plan: worktree-lifecycle-cli | Status: briefed
  - Exit ceremony + Wt rm task cleanup + Worktree ad-hoc task + CLI UX + --base submodule bug
- [ ] **Code quality** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.4
  - Plan: codebase-sweep | Status: requirements
- [ ] **Hook batch** — `/design plans/hook-batch-2/requirements.md` | sonnet | 1.3
  - Plan: hook-batch-2 | Status: requirements
- [ ] **Update prioritize skill** — `/design plans/update-prioritize-skill/requirements.md` | sonnet | 1.2
  - Plan: update-prioritize-skill | Status: requirements
- [ ] **Quality grounding** — `/design plans/quality-grounding/brief.md` | opus | 1.0
  - Plan: quality-grounding | Status: briefed
  - SP-2 extracted to decision-drift-audit. Remaining: SP-1 (ground skills), SP-3 (prose terminology), SP-4 (safety review)
- [ ] **Cross-tree operations** — `/design plans/cross-tree-operations/requirements.md` | sonnet | 1.0
  - Plan: cross-tree-operations | Status: requirements
- [ ] **Review agent quality** — `/design plans/review-agent-quality/brief.md` | sonnet | 1.0
  - Plan: review-agent-quality | Status: briefed
  - Unified corrector quality audit: false positives (bad auto-fixes) + false negatives (missed issues)
- [ ] **Design pipeline evolution** — `/design plans/design-pipeline-evolution/brief.md` | opus | 1.0
  - Plan: design-pipeline-evolution | Status: briefed
  - S-A: add grounding before design. S-B: late-binding model selection per stage.
- [ ] **Tweakcc** — `/design plans/tweakcc/requirements.md` | sonnet | 1.0
  - Plan: tweakcc | Status: requirements
- [ ] **Design review protocol** — `/design plans/resumed-review-protocol/brief.md` | opus | restart
  - Plan: resumed-review-protocol | Status: briefed
  - Two features: (1) runbook reuses corrector across phases, (2) orchestration ping-pong FIX/PASS
- [ ] **Markdown AST parser** — `/design plans/markdown-ast-parser/brief.md` | opus
  - Plan: markdown-ast-parser | Status: briefed
  - Preprocessor → standard parser → AST. Complex — new dependency, cross-cutting migration.
- [ ] **Design context gate** — `/design plans/design-context-gate/brief.md` | sonnet
  - Plan: design-context-gate | Status: briefed
- [ ] **Design JIT expansion** — `/design plans/design-jit-expansion/brief.md` | sonnet
  - Plan: design-jit-expansion | Status: briefed
- [ ] **Update tokens CLI** — `/design plans/update-tokens-cli/brief.md` | haiku
  - Plan: update-tokens-cli | Status: briefed
  - Make sonnet default model, update usage message
- [ ] **Threshold token migration** — `/design plans/threshold-token-migration/brief.md` | sonnet
  - Plan: threshold-token-migration | Status: briefed
  - Migrate line-based thresholds to token-based. Large blast radius expected.
- [ ] **Markdown migration** — `claudeutils _planstate close markdown-migration` | sonnet
  - Plan: markdown-migration | Status: reviewed
  - All sub-problems killed/absorbed/subsumed. Parser → markdown-ast-parser. Thresholds → decision-drift-audit. Token cache → YAGNI.
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart | 0.8
  - Plan: precommit-python3-redirect | Status: requirements
- [ ] **Diagnose compression loss** — `/design plans/diagnose-compression-loss/brief.md` | sonnet | 0.8
  - Plan: diagnose-compression-loss | Status: briefed
- [ ] **Research backlog** — `/design plans/research-backlog/brief.md` | opus | 0.5
  - Plan: research-backlog | Status: briefed
  - SP-1/SP-2/SP-3 absorbed into system-property-tracing. Remaining: SP-4 (behavioral design), SP-5 (degraded-function protocol)
- [ ] **Fix TDD context scoping** — `/design plans/tdd-context-scoping/brief.md` | sonnet
  - Plan: tdd-context-scoping | Status: briefed
- [ ] **Health check UPS fallback** — `/design plans/health-check-ups-fallback/requirements.md` | sonnet
  - Plan: health-check-ups-fallback | Status: requirements
- [ ] **Review gate** — `/design plans/review-gate/requirements.md` | sonnet
  - Plan: review-gate | Status: requirements
- [ ] **Feature prototypes** — `/design plans/prototypes/requirements.md` | sonnet | 0.6
  - Plan: prototypes | Status: requirements
- [ ] **Planstate brief inference** — `/design plans/planstate-brief-inference/requirements.md` | sonnet
  - Plan: planstate-brief-inference | Status: requirements
- [ ] **Small fixes batch** — `/design plans/small-fixes-batch/requirements.md` | sonnet
  - Plan: small-fixes-batch | Status: requirements
  - FR-4 added: remove bottom-to-top edit ordering refs
- [ ] **Incident counting** — `/design plans/incident-counting/brief.md` | opus
  - Plan: incident-counting | Status: briefed
- [ ] **Retro repo expansion** → `retro-repo-expansion` — `/design plans/retrospective-repo-expansion/brief.md` | sonnet
  - Plan: retrospective-repo-expansion | Status: briefed
- [ ] **Recall pipeline** — `/design` | sonnet
  - Deduplication, stdin parsing, usage scoring for recall entries
  - Note: plan dir only exists in retro-repo-expansion worktree, not on main. Create plan dir before design.
- [ ] **Skill exit commit** — `/design plans/skill-exit-commit/requirements.md` | sonnet
  - Plan: skill-exit-commit | Status: requirements
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
  - Blocked on human: curate task-contexts.json, annotate ground-truth.md

### Terminal

- [x] **Retrospective materials** — plan delivered
- [x] **Review prose-infra** — `/deliverable-review plans/prose-infra-batch` | opus | restart
- [x] **Review bootstrap work** — plan delivered
- [x] **Design backlog review** — completed two sessions ago
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

**Reviewed plans show no derived command:**
- Plans at `[reviewed]` status (post-/proof) have no mapped command in planstate. Next action is `/design plans/{name}/brief.md`.

**`session.py:307` format mismatch:**
- Produces `# Session: Worktree — {name}` but validator expects `# Session Handoff: YYYY-MM-DD`.

**`git stash` on `.claude/settings.local.json` requires sandbox bypass**

**markdown-migration candidate for closure:**
- All sub-problems killed/absorbed/subsumed after /proof. No remaining deliverables.

## Reference Files

- `plans/reports/prioritization-2026-03-06b.md` — WSJF scoring, 65 tasks ranked
- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for workflow skills
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline
- `plans/active-recall/brief.md` — Active recall system
- `plans/system-property-tracing/brief.md` — System invariants + pipeline traceability
- `plans/decision-drift-audit/brief.md` — Decision file consistency audit (split from quality-grounding)
- `plans/merge-parent-generalization/brief.md` — Generalize merge to arbitrary parent branch
- `plans/threshold-token-migration/brief.md` — Line-based to token-based threshold migration

## Next Steps

Continue with highest-priority ready tasks (Session CLI tool, Plugin migration) via worktree setup, or close markdown-migration plan.
