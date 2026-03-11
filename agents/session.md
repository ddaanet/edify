# Session Handoff: 2026-03-07

**Status:** Worktree dispatch (5 trees) + blocker cleanup.

## Completed This Session

- **Reprioritization:** 65 tasks scored (file: `plans/reports/prioritization-2026-03-06b.md`)
  - Top 5: Session CLI tool (3.2), Plugin migration (3.2), Worktree merge lifecycle (2.8), Active Recall (2.6), Directive skill promotion (2.2)
- **Task consolidation (65 → 25):**
  - 3 rounds of absorption, merge, and thematic clustering
  - Absorptions (15): Generate memory index → Active Recall (S-D), Recall learnings design → Active Recall (S-L), Codify branch awareness → Active Recall (S-L removes /codify), Remove wt rm --force → Worktree lifecycle CLI, Pre-inline plan commit → Gate batch, Prose gate terminology → Quality grounding, Merge lock retry → Worktree merge lifecycle, Worktree CLI UX → split into Worktree lifecycle CLI, Handoff insertion policy → Directive skill promotion, Test diamond migration → Code quality, Infrastructure scripts → Code quality, Test diagnostic helper → Code quality, Wt new --base submodule → Worktree lifecycle CLI, Fix task-context bloat → Session CLI tool, Plan-completion ceremony → Worktree merge lifecycle, Decision drift audit → Quality grounding
  - Merges: Lint-gated recall + Lint recall gate + Tool deviation hook + Block cd-chaining → Hook batch; Recall dedup + Recall pipeline + Recall usage scoring → Recall pipeline; Skill-dev + Skill prompt-composer + Retrofit + Agent rule injection → Skill agent bootstrap; Merge resilience + Lifecycle audit → Worktree merge lifecycle; Corrector audit + Diagnostic opus review → Review agent quality; Model directive pipeline + Design decomposition tier → Design pipeline evolution; Ground workflow skills + Safety review + Decision drift + Prose gate → Quality grounding; Cross-tree requirements + Cross-tree test sentinel → Cross-tree operations
  - Collapsed: 5 low-priority opus research tasks → Research backlog umbrella
  - Stale: Retrospective materials → [x] (plan delivered)
  - Unblocked: Session CLI tool ([!] → [ ], no documented blocker found)
- **Prioritize skill updated:**
  - Added Step 4 "Consolidation Pass" with absorption, merge, thematic cluster, and stale check patterns
  - Removed model tier cohort from scheduling modifiers and parallel batch criteria (SKILL.md + scoring-tables.md)
- **Worktree dispatch:** Created 5 worktrees: session-cli-tool, plugin-migration, worktree-merge-lifecycle, active-recall, planstate-brief-inference
- **Blocker cleanup:** Removed 7 blockers:
  - git merge sandbox bypass — superseded by `_worktree merge` CLI
  - `_worktree new` sandbox bypass — documented in worktree skill Usage Notes
  - SessionStart hook #10373 — Stop hook fallback deployed, not blocking any task
  - Custom agents not discoverable — root cause was missing session restart
  - Claude Code skill caching — root cause was missing session restart
  - `test_merge_learnings` ordering dep — non-reproducible, no recurrence
  - brief.md in planstate inference — converted to Planstate brief inference task

## In-tree Tasks

- [ ] **AR Integration** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-H: end-to-end verification of recall-explore-recall pattern, cross-worktree memory visibility, capture-time write path
  - Blocked: S-D, S-F, S-J, S-L (terminal — runs after all other AR sub-problems)
- [!] **AR Recall Consolidate** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-B: merge recall/ + recall_cli/ + when/ into unified recall module. Band 0 — ready now
  - Blocked: runbook skill improvements needed before re-attempting
- [!] **AR Submodule Refactor** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-I: extract 42 hardcoded agent-core refs into configurable submodule registry. Band 0 — ready now
  - Blocked: outline exists but `/runbook` skill on this branch is behind main. Waiting for main's runbook pipeline updates to land, then merge.
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
  - Infrastructure built. Blocked on human: curate task-contexts.json, annotate ground-truth.md
  - After human steps: run harness then analysis (commands in README)

- [ ] **Fix TDD context scoping** — `/design` | sonnet
  - Note: DEFAULT_TDD_COMMON_CONTEXT injected at runbook level, should be phase-scoped. Brief: `plans/bootstrap-tag-support/brief.md`
- [ ] **Health check UPS fallback** — `/design` | sonnet
  - Note: Modify session health check to use UserPromptSubmit instead of Stop as fallback when SessionStart hook did not run
- [ ] **Hook error after clear** — `/design` | sonnet
  - Note: Diagnose "SessionStart:clear hook error" after /clear
- [ ] **Review bootstrap work** — `/deliverable-review plans/bootstrap-tag-support` | opus | restart

## Worktree Tasks

- [ ] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet | restart | 3.2
  - Plan: handoff-cli-tool | Status: outlined (6 review rounds)
  - Absorbs: Fix task-context bloat
  - Note: Blocker resolved (Bootstrap tag support). Regenerate step files via `prepare-runbook.py plans/handoff-cli-tool/`, then `/orchestrate handoff-cli-tool`
- [ ] **Plugin migration** — `/orchestrate plugin-migration` (refresh outline first) | opus | 3.2
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
- [ ] **Worktree merge lifecycle** — `/runbook plans/worktree-merge-resilience/outline.md` | sonnet | 2.8
  - Plan: worktree-merge-resilience | Status: outlined
  - Absorbs: Merge lifecycle audit, Plan-completion ceremony (merge-point side effects), Merge lock retry
- [ ] **Active Recall** — `/design plans/active-recall/requirements.md` | opus | 2.6
  - Plan: active-recall | Status: outlined
  - Outline Rev 2 reviewed. Next: Phase B (user discussion) → sufficiency gate → design or /runbook
  - Absorbs: Generate memory index (S-D), Recall learnings design (S-L), Codify branch awareness (S-L removes /codify)
- [ ] **Directive skill promotion** — `/design plans/directive-skill-promotion/brief.md` | opus | 2.2
  - Plan: directive-skill-promotion | Status: requirements
  - Absorbs: Handoff insertion policy, wrap command, discuss protocol grounding, p: classification gap, discuss-to-pending chain
- [ ] **Parallel orchestration** — `/design plans/parallel-orchestration/problem.md` | sonnet | 1.8
  - Plan: parallel-orchestration | Status: requirements
- [ ] **Gate batch** — `/design` | sonnet | 1.7
  - Artifact staleness gate + Entry gate propagation + Design context gate + Pre-inline plan commit
  - Mechanical checkpoints at skill entry/exit/transition points
- [ ] **Skill agent bootstrap** — `/design` | opus | 1.6
  - Retrofit skill pre-work + Agent rule injection + Skill-dev skill + Skill prompt-composer
- [ ] **Worktree lifecycle CLI** — `/design` | sonnet | 1.6
  - Exit ceremony + Wt rm task cleanup + Worktree ad-hoc task + CLI UX + --base submodule bug
  - Plans: wt-exit-ceremony, wt-rm-task-cleanup, worktree-ad-hoc-task (all requirements)
- [ ] **Registry cache to tmp** — `/inline` | sonnet | 1.5
  - Move continuation registry cache from TMPDIR to project-local tmp/
- [ ] **Code quality** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.4
  - Plan: codebase-sweep | Status: requirements
  - Codebase sweep + agent-core lint coverage + Test diamond migration + Infrastructure scripts + Test diagnostic helper
- [ ] **Hook batch** — `/design` | sonnet | 1.3
  - Tool deviation hook (PostToolUse) + Block cd-chaining (PreToolUse) + Lint recall integration (Pre+PostToolUse)
- [ ] **Update prioritize skill** — Phase 2: `claudeutils _prioritize score` CLI | sonnet | 1.2
  - Plan: update-prioritize-skill | Status: requirements
- [ ] **Recall pipeline** — `/design` | opus | 1.1
  - Recall deduplication + stdin format parsing + usage scoring
- [ ] **Quality grounding** — `/ground` each per audit | opus | 1.0
  - Ground workflow skills + Safety review expansion + Decision drift audit + Prose gate terminology
  - Audit: `plans/reports/workflow-grounding-audit.md`
- [ ] **Cross-tree operations** — `/design` | sonnet | 1.0
  - Cross-tree requirements (git show transport) + Cross-tree test sentinel (content-hash cache)
- [ ] **Review agent quality** — `/design` | sonnet | 1.0
  - Corrector audit (false positive evidence) + Diagnostic opus review (post-vet RCA)
- [ ] **Design pipeline evolution** — `/design` | opus | 1.0
  - Design decomposition tier + Model directive pipeline — both modify /design skill
- [ ] **Tweakcc** — `/design plans/tweakcc/requirements.md` | sonnet | 1.0
  - Plan: tweakcc | Status: requirements
- [ ] **Markdown migration** — `/design` | opus | 0.8
  - Lenient markdown parser, token counting API + sqlite cache, threshold migration
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart | 0.8
- [ ] **Diagnose compression loss** — RCA against commit `0418cedb` | sonnet | 0.8
- [ ] **Feature prototypes** — `/design plans/prototypes/requirements.md` | sonnet | 0.6
- [ ] **Upstream skills field** — `/design` PR/issue for missing skills frontmatter | sonnet | 0.5
- [ ] **Planstate brief inference** — `/inline` | sonnet
  - Fix planstate to infer correct next-action for brief-only plans (currently uses requirements.md template)
- [ ] **Research backlog** — `/design` | opus | 0.5
  - Ground state coverage, Workflow formal analysis, Design-to-deliverable (restart), Behavioral design, Compensate-continue skill

### Terminal

- [x] **Retrospective materials** — plan delivered
- [-] **Calibrate topic params** — UPS topic injection removed, moot
- [-] **Recall tool consolidation** — absorbed into Active Recall
- [-] **Execute flag lint** — superseded by session validator

- [ ] **AR Capture Writes** — `/design plans/active-recall/outline.md` | opus
  - S-L: /remember skill, eliminate learnings.md + /codify. Band 3 — blocked: S-J, S-K, S-D, S-E
- [ ] **AR Doc Pipeline** — `/design plans/active-recall/outline.md` | sonnet
  - S-G: source docs to extraction agent to corrector to index regen. Band 2 — blocked: S-C, S-D, S-K
- [ ] **AR Hierarchy Index** — `/design plans/active-recall/outline.md` | sonnet
  - S-D: migrate flat index to tree structure, parser updates, migration tooling, index generation. Band 1 — design blocked: S-A, S-B; impl blocked: S-J
- [ ] **AR Memory Corrector** — `/design plans/active-recall/outline.md` | opus
  - S-K: agent definition with quality criteria, suppression taxonomy. Band 2 — blocked: S-C
- [ ] **AR Mode Simplify** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-F: reduce 5 modes to 2, update 10 pipeline recall points. Band 2 — blocked: S-D
- [ ] **AR Submodule Setup** — `/design plans/active-recall/outline.md` | sonnet
  - S-J: create memory submodule with shared branch, configure propagation, update resolver paths. Band 1 — blocked: S-I
- [ ] **AR Trigger Metadata** — `/runbook plans/active-recall/outline.md` | sonnet
  - S-E: formalize trigger_class and category as IndexEntry metadata. Band 2 — blocked: S-C, S-D
- [ ] **Fix prefix tolerance** — `src/claudeutils/when/fuzzy.py` | sonnet
  - Zero tolerance for prefix noise (0.0 scores on one-token mismatch). Separate from format decision.
- [ ] **Review gate** — `/design` | sonnet
  - Precommit step: review report timestamp >= production artifact edit timestamp, no triviality exception
  - Implements defense-in-depth.md decision ("gate at chokepoint")
  - Evidence: JIT expansion commit skipped vet checkpoint

- [ ] **Design review protocol** — `/design plans/resumed-review-protocol/brief.md` | opus | restart
  - Plan: resumed-review-protocol
  - Note: Two features — (1) runbook reuses corrector across phases, (2) orchestration ping-pong FIX/PASS. Brief: `plans/resumed-review-protocol/brief.md`
- [ ] **Fix session search** — `claudeutils _session` | sonnet
  - Note: Make --project optional in session-scraper.py, support project globbing
- [ ] **Markdown AST parser** — `/design plans/markdown-ast-parser/brief.md` | opus
  - Plan: markdown-ast-parser
  - Note: Preprocessor → standard parser → AST. Blocks handoff-cli-tool S-4 if AST-first ordering chosen. Complex — new dependency, cross-cutting migration.
- [ ] **Test context-fork model** — create minimal skill with `context: fork` + `AskUserQuestion`, observe interaction behavior | haiku

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
- `plans/active-recall/brief.md` — Active recall system: hierarchical index, documentation conversion, trigger classes
- `tmp/active-recall.md` — Discussion decisions: recall-explore-recall, tree navigation, benchmark landscape

## Next Steps

5 active worktrees dispatched. Merge planstate-brief-inference first (smallest scope), then proceed with top-4 priority tasks in their worktrees.