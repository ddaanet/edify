# Session Handoff: 2026-03-30

**Status:** Edify rename outlined and proofed. Design skill triage recall pointed at /recall.

## Completed This Session

**Edify rename outline:**
- Classified as Complex (multi-sub-problem, ~2500 total references across tree)
- Wrote `plans/edify-rename/outline.md` — 3 sub-problems: SP-3 (plan cleanup) → SP-1 (submodule rename) → SP-2 (package rename)
- Proofed with /proof: 5 revisions (FR-9b dual coverage, .gitmodules name field, reinstall step, SP-3 prerequisite ordering, tables→lists)
- Moved task from Worktree Tasks to In-tree Tasks (user preference)

**Design skill triage recall fix:**
- Identified: triage recall blind-fires trigger phrases without reading memory-index
- Initial fix (inline memory-index reading) reverted — duplicates recall logic
- Pointed at `/recall triage` (strategy parameter pending centralize-recall plan)

**Exploration:**
- Scout agent mapped full blast radius: `plans/edify-rename/reports/explore-rename-scope.md`
- Measured counts exceed requirements estimates (tests/agent-core: 172 vs FR-6's 106)

## In-tree Tasks

- [>] **Edify rename** — `/inline plans/edify-rename` | opus
  - Plan: edify-rename | Status: outlined (multi-sub-problem, terminal design artifact)
  - SP-3 (plan cleanup) → SP-1 (submodule rename) → SP-2 (package rename)
  - SP-3: `/inline plans/edify-rename` | sonnet — enumerate delivered plans, archive, delete
  - SP-1: `/runbook plans/edify-rename/outline.md` | sonnet — agent-core → plugin (~1679 refs)
  - SP-2: `/runbook plans/edify-rename/outline.md` | sonnet — claudeutils → edify (~817+ refs)
- [ ] **Centralize recall** — `/design plans/centralize-recall/brief.md` | opus | restart
  - Plan: centralize-recall | Segmented /recall skill (<1ktok core), replace inline recall across skills/agents. Prerequisite (remove-index-skill) now complete.
- [ ] **Outline template trim** — `/design plans/outline-template-trim/brief.md` | opus | restart
- [ ] **Review skill-CLI** — `/deliverable-review plans/skill-cli-integration` | opus | restart
- [ ] **Skill-CLI completion** — `/design plans/skill-cli-completion/brief.md` | opus | restart
  - Commit discovery (_git changes), commit --test flag, handoff composition. Before deliverable review.

## Worktree Tasks

- [x] **Fix batch findings** — plan archived
- [ ] **Skill context probe** — `/design plans/fr3-skill-context/requirements.md` | sonnet
  - Plan: fr3-skill-context | Investigate `context:` param on Skill tool; create test skill, document behavior
- [x] **Session CLI tool** → `session-cli-tool` — merged this session
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
- [x] **Small fixes batch** — plan delivered; FR-3 extracted to fr3-skill-context
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

- [ ] **Commit drift guard** — `/design plans/commit-drift-guard/brief.md` | opus
  - Design how _commit CLI verifies files haven't changed since last diff
- [ ] **Design context prereq** — `/design plans/design-context-prerequisite/brief.md` | opus | restart
  - Agents modifying code need design spec in context. Fragment change.
- [ ] **Design segmentation gate** — `/design plans/design-segmentation-gate/brief.md` | opus | restart
  - Add sub-problem split gate after design finalization, before runbook. Prevents monolithic review scope.
- [ ] **Historical proof feedback** — `/design plans/historical-proof-feedback/brief.md` | sonnet
  - Prerequisite: updated proof skill integrated in all worktrees
- [ ] **Inline dispatch recall** — `/design plans/inline-dispatch-recall/brief.md` | sonnet
  - Fix review-dispatch-template to enforce artifact-path-only recall pattern
- [ ] **Inline resume policy** — `/design plans/inline-resume-policy/brief.md` | sonnet
  - Add resume-between-cycles directive to /inline delegation protocol
- [ ] **Learnings startup report** — `/design plans/learnings-startup-report/brief.md` | sonnet
- [ ] **Pending brief generation** — `/design plans/pending-brief-generation/brief.md` | sonnet
  - p: directive should create plans/<slug>/brief.md to back the task
- [ ] **Planstate disambiguation** — `/design plans/planstate-disambiguation/brief.md` | sonnet
- [!] **Resolve learning refs** — `/design plans/resolve-learning-refs/brief.md` | sonnet
  - Blocker: blocks invariant documentation workflow (recall can't resolve learning keys)
- [ ] **Runbook integration-first** — `/design plans/runbook-integration-first/brief.md` | sonnet
  - Addendum to runbook-quality-directives plan
- [ ] **Submodule vet config** — `/design plans/submodule-vet-config/brief.md` | sonnet
- [ ] **Worktree ls filtering** — `/design plans/worktree-ls-filtering/brief.md` | sonnet
  - _worktree ls dumps all plans across all trees; handoff only needs session.md plan dirs
- [ ] **Stop hook plugin wire** — `/design plans/hook-batch-2/requirements.md` | sonnet
  - Wire `src/claudeutils/hooks/stop_status_display.py` into plugin Stop hook. Merged from session-cli-tool but not yet in plugin.json.

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

- `/codify` overdue — next session should consolidate older learnings [from: session-cli-tool]
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Brief at `plans/inline-dispatch-recall/brief.md` covers fix. [from: session-cli-tool]
- `test_worktree_merge_learnings.py::test_merge_learnings_segment_diff3_prevents_orphans` — intermittent merge conflict failure. Passes on retry. [from: session-cli-tool]
- User questioning entire design → runbook → orchestrate pipeline, behavioral guardrails, and planning-first paradigm [from: session-cli-tool]
- No decisions made yet — discussion only. Next session should not assume pipeline continuity. [from: session-cli-tool]
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

Edify rename ready for execution: SP-3 (plan cleanup) first, then SP-1 (submodule), then SP-2 (package). Design skill triage recall now points at `/recall triage` — centralize-recall plan owns the implementation. User feedback: tables → lists, stop hook should explain FR/SP/C jargon.