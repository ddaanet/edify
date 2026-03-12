# Session Handoff: 2026-03-12

**Status:** Interactive review design — grounding complete, outline written and reviewed via dogfooded item-by-item process. Supplementary grounding needed before design generation (4 domain-specific research gaps surfaced during review).

## Completed This Session

**Interactive review grounding + outline:**
- Full `/ground` pass: Fagan inspection, IEEE 1028, GitHub/Gerrit/Phabricator review UX, cognitive load research (Cisco/SmartBear, Microsoft)
- Grounding report: `plans/reports/interactive-review-grounding.md` (Strong label — 4 frameworks + empirical research)
- Branch reports: `plans/reports/interactive-review-internal-codebase.md`, `plans/reports/interactive-review-external-research.md`
- Outline written, corrector-reviewed (2 rounds), user-reviewed via dogfooded item-by-item process
- 14 items reviewed: 4 approved, 8 revised, 2 skipped
- Key design changes from review: verdict vocabulary is artifact-type-dependent (needs supplementary grounding), discuss is implicit (non-verdict input), no mode selection (single loop path — degenerate single iteration for whole artifacts), iteration guards (no direct edits, refuse execution chaining), `suspend → /design` removed (use pending instead)
- FR-5 lifted by user (batch-apply only, session resume handles interruption)
- Classification: Complex, agentic-prose destination

**Review findings that need supplementary grounding (4 gaps):**
- D-1: Per-domain verdict vocabularies (backlog refinement, architecture review, process review, defect triage)
- D-2: Batch vs immediate by review domain
- D-7: Per-item cognitive load threshold (Cisco data is per-session, not per-segment)
- D-8: Skip/deferred item outcome semantics

## In-tree Tasks

- [ ] **Interactive review** — `/ground` then `/design plans/interactive-review/outline.md` | opus | restart
  - Plan: interactive-review | Status: reviewed
  - Outline reviewed. Needs supplementary grounding (4 domain gaps: per-domain verdicts, batch-by-domain, per-item size threshold, skip outcome). Then resume design from outline.
- [ ] **Problem.md migration** — `/design plans/problem-md-migration/brief.md` | sonnet
  - Plan: problem-md-migration | Status: briefed
  - Rename 13 problem.md → brief.md with git history recovery, fix planstate `_derive_next_action`, add precommit gate
## Worktree Tasks

- [ ] **Session CLI tool** — `/orchestrate handoff-cli-tool` | sonnet | restart | 3.2
  - Plan: handoff-cli-tool | Status: ready
  - Absorbs: Fix task-context bloat
  - Note: Blocker resolved (Bootstrap tag support). Step files generated. `/orchestrate handoff-cli-tool`
- [ ] **Plugin migration** — `/orchestrate plugin-migration` (refresh outline first) | opus | 3.2
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
- [ ] **Worktree merge lifecycle** — `/runbook plans/worktree-merge-resilience/outline.md` | sonnet | 2.8
  - Plan: worktree-merge-resilience | Status: outlined
  - Absorbs: Merge lifecycle audit, Plan-completion ceremony (content migrated this session)
- [ ] **Active Recall** — `/design plans/active-recall/outline.md` | opus | 2.6
  - Plan: active-recall | Status: outlined
  - Outline Rev 2 reviewed. Next: Phase B (user discussion) → sufficiency gate → design or /runbook
  - Absorbs: Generate memory index (S-D), Recall learnings design (S-L), Codify branch awareness (S-L removes /codify)
  - S-B: **AR Recall Consolidate** [!] — merge recall/ + recall_cli/ + when/ into unified recall module. Blocked: runbook skill improvements
  - S-D: **AR Hierarchy Index** — migrate flat index to tree structure, parser updates, migration tooling. Blocked: S-A, S-B (design), S-J (impl)
  - S-E: **AR Trigger Metadata** — formalize trigger_class and category as IndexEntry metadata. Blocked: S-C, S-D
  - S-F: **AR Mode Simplify** — reduce 5 modes to 2, update 10 pipeline recall points. Blocked: S-D
  - S-G: **AR Doc Pipeline** — source docs to extraction agent to corrector to index regen. Blocked: S-C, S-D, S-K
  - S-H: **AR Integration** — end-to-end verification of recall-explore-recall pattern, cross-worktree memory visibility. Blocked: S-D, S-F, S-J, S-L (terminal)
  - S-I: **AR Submodule Refactor** [!] — extract 42 hardcoded agent-core refs into configurable submodule registry. Blocked: runbook pipeline updates
  - S-J: **AR Submodule Setup** — create memory submodule with shared branch, configure propagation. Blocked: S-I
  - S-K: **AR Memory Corrector** — agent definition with quality criteria, suppression taxonomy. Blocked: S-C
  - S-L: **AR Capture Writes** — /remember skill, eliminate learnings.md + /codify. Blocked: S-J, S-K, S-D, S-E
  - **AR How Verb Form** — Plan: ar-how-verb-form | Status: requirements
  - **AR IDF Weighting** — Plan: ar-idf-weighting | Status: requirements
  - **AR Threshold Calibration** — Plan: ar-threshold-calibration | Status: planned
- [ ] **Directive skill promotion** — `/design plans/directive-skill-promotion/brief.md` | opus | 2.2
  - Plan: directive-skill-promotion | Status: briefed
  - Absorbs: Handoff insertion policy, wrap command, discuss protocol grounding, p: classification gap, discuss-to-pending chain
- [ ] **System property tracing** — `/design plans/system-property-tracing/brief.md` | opus
  - Plan: system-property-tracing | Status: briefed
  - Two phases: (1) system invariants as formal requirements, (2) pipeline traceability for FR survival across workflow stages
  - Partially absorbs: quality-grounding, review-gate
- [ ] **Skill-gated session edits** — `/design plans/skill-gated-session-edits/brief.md` | opus
  - Plan: skill-gated-session-edits | Status: briefed
  - Default read-only sessions, skill required for production edits. Motivated by regression investigation.
- [ ] **Parallel orchestration** — `/design plans/parallel-orchestration/problem.md` | sonnet | 1.8
  - Plan: parallel-orchestration | Status: requirements
- [ ] **Gate batch** — `/design plans/gate-batch/requirements.md` | sonnet | 1.7
  - Plan: gate-batch | Status: requirements
- [ ] **Skill agent bootstrap** — `/design plans/skill-agent-bootstrap/problem.md` | opus | 1.6
  - Plan: skill-agent-bootstrap | Status: requirements
- [ ] **Worktree lifecycle CLI** — `/design plans/worktree-lifecycle-cli/problem.md` | sonnet | 1.6
  - Plan: worktree-lifecycle-cli | Status: requirements
  - Exit ceremony + Wt rm task cleanup + Worktree ad-hoc task + CLI UX + --base submodule bug
  - Absorbed plan content migrated this session (wt-exit-ceremony, wt-rm-task-cleanup, worktree-ad-hoc-task)
- [ ] **Code quality** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.4
  - Plan: codebase-sweep | Status: requirements
  - Codebase sweep + agent-core lint coverage + Test diamond migration + Infrastructure scripts + Test diagnostic helper
- [ ] **Hook batch** — `/design plans/hook-batch-2/requirements.md` | sonnet | 1.3
  - Plan: hook-batch-2 | Status: requirements
- [ ] **Update prioritize skill** — `/design plans/update-prioritize-skill/requirements.md` | sonnet | 1.2
  - Plan: update-prioritize-skill | Status: requirements
- [ ] **Quality grounding** — `/design plans/quality-grounding/problem.md` | opus | 1.0
  - Plan: quality-grounding | Status: requirements
- [ ] **Cross-tree operations** — `/design plans/cross-tree-operations/requirements.md` | sonnet | 1.0
  - Plan: cross-tree-operations | Status: requirements
- [ ] **Review agent quality** — `/design plans/review-agent-quality/problem.md` | sonnet | 1.0
  - Plan: review-agent-quality | Status: requirements
- [ ] **Design pipeline evolution** — `/design plans/design-pipeline-evolution/problem.md` | opus | 1.0
  - Plan: design-pipeline-evolution | Status: requirements
- [ ] **Tweakcc** — `/design plans/tweakcc/requirements.md` | sonnet | 1.0
  - Plan: tweakcc | Status: requirements
- [ ] **Design review protocol** — `/design plans/resumed-review-protocol/brief.md` | opus | restart
  - Plan: resumed-review-protocol | Status: briefed
  - Note: Two features — (1) runbook reuses corrector across phases, (2) orchestration ping-pong FIX/PASS
- [ ] **Markdown AST parser** — `/design plans/markdown-ast-parser/brief.md` | opus
  - Plan: markdown-ast-parser | Status: briefed
  - Note: Preprocessor → standard parser → AST. Blocks handoff-cli-tool S-4 if AST-first ordering chosen. Complex — new dependency, cross-cutting migration.
- [ ] **Design context gate** — `/design plans/design-context-gate/brief.md` | sonnet
  - Plan: design-context-gate | Status: briefed
- [ ] **Design JIT expansion** — `/design plans/design-jit-expansion/brief.md` | sonnet
  - Plan: design-jit-expansion | Status: briefed
- [ ] **Markdown migration** — `/design plans/markdown-migration/problem.md` | opus | 0.8
  - Plan: markdown-migration | Status: requirements
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart | 0.8
  - Plan: precommit-python3-redirect | Status: requirements
- [ ] **Diagnose compression loss** — `/design plans/diagnose-compression-loss/problem.md` | sonnet | 0.8
  - Plan: diagnose-compression-loss | Status: requirements
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
- [ ] **Research backlog** — `/design plans/research-backlog/problem.md` | opus | 0.5
  - Plan: research-backlog | Status: requirements
- [ ] **Small fixes batch** — `/design plans/small-fixes-batch/requirements.md` | sonnet
  - Plan: small-fixes-batch | Status: requirements
  - FR-4 added: remove bottom-to-top edit ordering refs
- [ ] **Incident counting** — `/design plans/incident-counting/brief.md` | opus
  - Plan: incident-counting | Status: briefed
  - Fix codify's incident-specific rejection, ground methodology for recurrence tracking
- [ ] **Retro repo expansion** → `retro-repo-expansion` — `/design plans/retrospective-repo-expansion/brief.md` | sonnet
  - Plan: retrospective-repo-expansion | Status: briefed
  - Extend retrospective evidence base with 16 additional git repos (pre-claudeutils evolution + parallel projects)
- [ ] **Recall pipeline** — `/design` | sonnet
  - Deduplication, stdin parsing, usage scoring for recall entries
  - Note: plan dir only exists in retro-repo-expansion worktree, not on main. Create plan dir before design.
- [ ] **Skill exit commit** — `/design plans/skill-exit-commit/requirements.md` | sonnet
  - Plan: skill-exit-commit | Status: requirements
  - /design and /runbook commit dirty tree before routing to /inline
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
  - Infrastructure built. Blocked on human: curate task-contexts.json, annotate ground-truth.md
  - After human steps: run harness then analysis (commands in README)

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
- After every worktree merge, validate session.md (pending tasks from branch carried over) AND learnings.md (no entries lost from either side)
- Known failure modes: autostrategy drops branch pending tasks, orphaned duplicate lines in append-only files, branch overwrites main-only learnings entries
- Not automated — manual check required

**`_worktree rm` amend restored but task entry persists:**
- `_update_session_and_amend` restored after task-classification regression. Amend works but `remove_slug_marker` only strips marker — doesn't remove completed task entry. Pending in Worktree lifecycle CLI.

**Worktree merge drops session.md Worktree Tasks entries:**
- Focused session in branch lacks main's full Worktree Tasks section. Autostrategy resolves in favor of branch, dropping main-only entries. Manual post-merge validation required until merge.py fixed.

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

**Main is worktree-tasks-only:**
- Only trivial fixes belong in In-tree. Plan absence doesn't qualify for in-tree.

**Planstate CLI bug for briefed plans:**
- `_worktree ls` displays `requirements.md` path for plans at `briefed` status. Use the status field `[briefed]` as source of truth, not the displayed path.

- `plans/prototypes/recall-artifact.md` created as stub to satisfy pretooluse recall gate (hook infers plan from file path, not actual plan context)
- `test_markdown_fixtures.py::test_full_pipeline_remark` xfail renders full traceback in markdown report, visually identical to real failure. Fix is in `pytest-markdown-report` (separate repo).

- `session.py:307` produces `# Session: Worktree — {name}` but validator expects `# Session Handoff: YYYY-MM-DD`. Data-fixed this session. Code fix (validator or session.py) is separate behavioral change — not in scope here. [from: fix-prose-routing-bias] [from: session-cli-tool]

## Reference Files

- `plans/reports/prioritization-2026-03-06b.md` — WSJF scoring, 65 tasks ranked + consolidation analysis
- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/design-skill-grounding.md` — Design skill grounding
- `agents/decisions/pipeline-contracts.md` — Pipeline contract decision file
- `agents/decisions/pipeline-review.md` — Pipeline review patterns (split from pipeline-contracts.md)
- `plans/active-recall/brief.md` — Active recall system: hierarchical index, documentation conversion, trigger classes
- `tmp/active-recall.md` — Discussion decisions: recall-explore-recall, tree navigation, benchmark landscape
- `plans/prose-infra-batch/reports/deliverable-review.md` — Deliverable review report (0 critical, 0 major, 4 minor)
- `plans/skill-gated-session-edits/brief.md` — Causal chain: bare directive → no skill gates → regression committed
- `plans/system-property-tracing/brief.md` — System invariants + pipeline traceability concept
- `plans/interactive-review/brief.md` — Dogfooding feedback: presentation ergonomics, research gap, checkpoint-after-TOC
- `plans/reports/interactive-review-grounding.md` — Grounding report: Fagan, Gerrit, Phabricator, cognitive load (Strong)
- `plans/interactive-review/outline.md` — Reviewed outline with 4 grounding gaps marked

## Next Steps

Interactive review supplementary grounding (opus, restart, in-tree) — resolve 4 domain-specific research gaps in outline, then resume design.
