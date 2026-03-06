# Plan Archive

Completed plans with summaries. Loaded on demand during design research (Phase A.1)
and diagnostic/RCA sessions.

## session-scraping

Session scraper prototype for extracting structured data from Claude Code session logs. Scans all `~/.claude/projects/` directories, treats agent files as first-class sources, supports many-to-many session↔commit mapping. Tool I/O noise filtered by default. Deliverable: `plans/prototypes/session-scraper.py` and supporting infrastructure.

## vet-false-positives

Added "Do NOT Flag" false positive suppression taxonomy to corrector agent prompts. Categories: pre-existing issues, out-of-scope items, pattern-consistent style, linter-catchable issues. Technique derived from Anthropic code-review plugin's confidence scoring pattern. Delivered via deliverable review cycle.

## grounding-skill

Ground skill with diverge-converge research procedure. Produces grounded reference documents via parallel internal + external research. Affected: agent-core/skills/ground/. Key decision: mandatory web search for methodology claims.

## pushback

Two-layer anti-sycophancy system: fragment (behavioral rules) + hook (agreement momentum tracking). Validated on S1/S2/S4 scenarios. Affected: agent-core/fragments/pushback.md, .claude/hooks/.

## pushback-improvement

Tier 1 direct implementation from pushback worktree. Incremental improvements to pushback fragment based on field observations.

## workflow-rca-fixes

20 functional requirements implemented: skill composition, type-agnostic review, vet taxonomy with subcategory codes, outline enhancements. Major cross-cutting workflow improvement.

## worktree-fixes

4 phases, 5 FRs satisfied, 25 TDD cycles + 4 prose edits. Fixes to worktree skill and CLI based on field usage. Affected: agent-core/skills/worktree/, src/claudeutils/worktree/.

## workflow-fixes

Unified /runbook skill, runbook-corrector agent, review-plan skill, pipeline-contracts. Consolidated fragmented workflow tooling into coherent pipeline. Affected: agent-core/skills/runbook/, agent-core/agents/.

## process-review

Root cause analysis of 5 plans. Identified root cause in planning skill (insufficient complexity triage). 5 recommendations for workflow improvement.

## memory-index-recall

Bug fixes + reanalysis of memory index recall system. M-1, M-2 fixed, confirmed 0.2% recall rate. 7 modules, 50 tests. Affected: src/claudeutils/when/.

## workflow-skills-audit

Superseded by runbook unification. All 12 audit items landed via workflow-fixes plan.

## reflect-rca-sequential-task-launch

Subsumed into process-review worktree. RCA on sequential task launch patterns.

## requirements-skill

Dual-mode extract/elicit requirements skill with empirical grounding. Supports extracting requirements from conversation or eliciting through structured questions. Affected: agent-core/skills/requirements/.

## worktree-skill

Worktree skill implementation. 42/42 cycles completed, merged to dev. Modes A (new), B (parallel group), C (merge ceremony). Design.md retained on disk for reference. Affected: agent-core/skills/worktree/.

## worktree-skill-fixes

27 fixes across 7 phases for worktree skill. Post-deployment corrections based on field usage patterns.

## handoff-validation

Killed: problems resolved by existing tooling. Investigation showed validation was unnecessary given commit hooks.

## continuation-passing

Continuation passing protocol. 15 steps, hook implementation, skill updates. 0% false positive rate. Enables tail-call chaining between skills. Affected: .claude/hooks/, agent-core/skills/.

## markdown

Test corpus implementation for markdown processing. 16 fixtures, 3 parametrized tests, all 5 FRs satisfied. Affected: tests/fixtures/.

## reflect-rca-parity-iterations

Parity test quality gap fixes. 11 steps, 8 design decisions. Improved test coverage patterns.

## domain-validation

Domain-specific validation infrastructure. Validation skill, rules file, plan skill updates. Foundation for automated artifact validation. Affected: src/claudeutils/validation/.

## validator-consolidation

Consolidated validators from scattered locations into claudeutils package. Unified validation interface. Affected: src/claudeutils/validation/.

## commit-unification

Unified commit skills, inlined gitmoji selection, decoupled handoff from commit. Simplified commit workflow. Affected: agent-core/skills/commit/.

## position-bias

Fragment reordering based on position bias research + token budget script. Optimized CLAUDE.md fragment ordering for adherence. Affected: agent-core/fragments/, agent-core/bin/.

## prompt-composer

Superseded by fragment system. Research distilled into position-bias and fragment architecture decisions.

## reflect-rca-prose-gates

D+B hybrid fix for prose gates. Ensures skill steps with prose instructions aren't skipped by agents. Key decision: combine directive + behavioral hook.

## statusline-wiring

Statusline CLI with TDD. 28 cycles, 6 phases. Wired status display into CLI infrastructure. Affected: src/claudeutils/statusline/.

## statusline-parity

All 14 cycles, 5 phases executed and validated. Parity testing for statusline output.

## learnings-consolidation

Learnings consolidation infrastructure. 7 steps, 4 phases. Automated consolidation of learnings.md into permanent documentation. Affected: agent-core/skills/codify/, agent-core/bin/.

## workflow-feedback-loops

Feedback loop infrastructure. 12 steps, 4 phases. Structured feedback collection and processing for workflow improvement.

## claude-tools-rewrite

Infrastructure rewrite of Claude tools CLI. Recovery and parity followups planned. Affected: src/claudeutils/.

## claude-tools-recovery

Account/provider/model CLI wired after claude-tools-rewrite. Restored functionality lost in rewrite.

## runbook-identifiers

Cycle numbering gaps relaxed. Allowed non-contiguous cycle numbers in runbooks for practical editing.

## robust-waddling-bunny

Memory index D-3 root cause analysis. Identified and documented memory retrieval failure modes.

## review-requirements-consistency

Requirements review process. Ensured requirements documents maintain internal consistency.

## majestic-herding-rain

Gitmoji integration. Added emoji prefixes to commit messages for visual categorization.

## handoff-lite-issue

RCA transcript for handoff-lite misuse. Documented failure mode where lite handoff was used for full session transitions.

## when-recall

Memory recall system using /when and /how triggers. 12 phases, merged to main. Affected: src/claudeutils/when/, agent-core/skills/when/. Key decision: bash transport for sub-agent consumption.

## worktree-update

40 TDD cycles, recovery (C2-C5), merged to main. Major update to worktree CLI and merge operations. Affected: src/claudeutils/worktree/.

## worktree-merge-data-loss

Removal guard + merge correctness. 13 TDD cycles, deliverable review. Prevented data loss during worktree removal when merge commits are amended. Affected: src/claudeutils/worktree/cli.py.

## worktree-rm-safety

5 FRs: dirty check, exit code 2, --force, --confirm. Tier 2 TDD, 6 cycles + 1 general step. Safety improvements for worktree removal. Affected: src/claudeutils/worktree/cli.py.

## remaining-workflow-items

5 FRs: reflect task output, tool-batching, delegate resume, agent output, commit simplification. Cross-cutting workflow improvements. Affected: agent-core/fragments/, agent-core/skills/.

## workwoods

Cross-tree worktree awareness with planstate inference, aggregation, rich ls display, section-based merge strategies, and vet tracking. 33 TDD + 10 general steps. Eliminated jobs.md in favor of filesystem-based plan state inference. Affected: src/claudeutils/planstate/, src/claudeutils/worktree/display.py, src/claudeutils/worktree/resolve.py.

## inline-phase-type

Inline phase type across pipeline. 7 pipeline artifacts updated, 7 integration tests. Added inline as third phase type (alongside TDD and general) for prose edits without feedback loops. Key decisions: coordination complexity discriminator (D-5), vet proportionality (D-7). Affected: pipeline-contracts.md, workflow-optimization.md, runbook/SKILL.md, runbook-corrector.md, review-plan/SKILL.md, orchestrate/SKILL.md, prepare-runbook.py.

## pipeline-skill-updates

9 design decisions (D-1 through D-9) addressing pipeline closure gaps and vet scoping deficits. Additive prose edits to 7 files. Requirements-clarity gate (D-1), coordination complexity execution readiness (D-5), deliverable-review task creation (D-2/D-3), lifecycle audit (D-7), verification scope (D-4/D-9), resume completeness (D-8), TDD integration-first (D-6). Absorbed vet-invariant-scope and inline-phase-type designs. Affected: agent-core/skills/ (design, orchestrate, deliverable-review), agent-core/fragments/review-requirement.md, agent-core/agents/ (outline-corrector, test-driver), agents/decisions/pipeline-contracts.md.

## brief-skill

Cross-tree context transfer skill. Producer (`/brief <slug>`) writes timestamped entries to `plans/<plan>/brief.md`. Consumer integration via execute-rule.md task pickup. Affected: agent-core/skills/brief/, agent-core/fragments/execute-rule.md.

## error-handling

Error handling framework across 5 layers. 9 files (7 modified, 2 new), ~163 net lines. Unified error handling across orchestration, task lifecycle, and CPS chains. Key decisions: Avižienis fault/failure vocabulary, 5-category taxonomy (D-1), task error states blocked/failed/canceled (D-2), escalation acceptance criteria (D-3), revert-to-step-start rollback (D-5), hook degraded mode (D-6). Calibrated max_turns ~150 from 938 observations. Affected: agent-core/fragments/ (6 files), agent-core/skills/ (2 files), .claude/rules/.

## hook-batch

5-phase hook implementation: UserPromptSubmit improvements (line-based matching, additive directives D-7, pattern guards, new b:/q:/learn: directives), PreToolUse recipe-redirect, PostToolUse auto-format, SessionStart+Stop health checks with flag-file coordination (#10373 bypass), hooks.json config source of truth with sync-hooks-config.py merge. 16 steps, 34 tests. Deliverable review found Tier 2.5/3 combination gap — TDD-fixed. Affected: agent-core/hooks/ (5 scripts + hooks.json), agent-core/bin/ (sync-hooks-config.py, learning-ages.py --summary), agent-core/justfile, .claude/settings.json.

## runbook-evolution

5 FRs: prose atomicity (FR-1), self-modification discipline (FR-2a/2b), testing diamond (FR-3a-d). Additive prose edits to runbook SKILL.md (Testing Strategy section, Phase 0.75 verification, TDD Cycle Planning) and anti-patterns.md (4 new entries, 1 rewritten). Side fix: review-requirement.md reviewer routing table. Affected: agent-core/skills/runbook/, agent-core/fragments/review-requirement.md.

## brief-skill

Cross-tree async context transfer skill. `/brief <slug>` writes timestamped entries to `plans/<plan>/brief.md` for worktree agents to read on pickup. Consumer integration via `git show main:plans/<plan>/brief.md` when plan dir only exists on main. Affected: agent-core/skills/brief/SKILL.md.

## vet-invariant-scope

3 prose changes to address vet pipeline gaps found during worktree-merge-resilience deliverable review. Added Verification scope field to review execution context template (review-requirement.md, pipeline-contracts.md), lifecycle audit criterion for final checkpoint (orchestrate/SKILL.md), resume completeness criterion (outline-corrector.md). No code changes.

## worktree-rm-safety

Safety gates for `_worktree rm`: dirty tree check (parent + submodule), exit code 2 for guard refusal, `--force` bypass flag, no destructive suggestions in CLI output. Affected: src/claudeutils/worktree/cli.py, tests/test_worktree_rm_dirty.py, tests/test_worktree_rm.py.

## worktree-cli-default

CLI interface redesign: task name as positional argument (was `--task` flag), `--branch` for bare slug override, sandbox removal from `_worktree new` (no more `additionalDirectories` in settings.local.json). Absorbed: pre-merge untracked file fix, worktree skill adhoc mode, `--slug` override, `rm --confirm` gate fix (separated as orthogonal). Affected: src/claudeutils/worktree/cli.py, agent-core/skills/worktree/SKILL.md.

## remember-skill-update

13 FRs: learnings.py prefix + content word validation (TDD, 12 tests), CLI rewrite to one-arg syntax + batched recall (TDD, 8 tests), skill docs updated (title guidance, mechanical trigger derivation, inline execution, agent routing for 13 agents), pipeline simplification (deleted remember-task + memory-refactor agents, inline execution), renamed /remember → /codify (~30 files), removed memory-index from always-loaded context (~5000 tokens), frozen-domain analysis recommends UserPromptSubmit hook. Affected: src/claudeutils/validation/learnings.py, src/claudeutils/when/cli.py, agent-core/skills/codify/, agent-core/skills/handoff/, agent-core/skills/when/, agent-core/skills/how/, agent-core/skills/memory-index/, agents/decisions/project-config.md.

## worktree-error-output

Migrated all `_worktree` CLI error output from stderr to stdout per LLM-native CLI convention. Added `_fail(msg, code) -> Never` helper consolidating `click.echo + raise SystemExit` pairs, caught `derive_slug` ValueError in `new()` with clean exit 2, removed `err=True` from 12 sites (8 error+exit converted to `_fail()`, 4 warning-only stripped). 5 steps across 3 phases (TDD × 2, general × 1), 13 commits. TDD audit: 50% compliance — Cycle 1.1 broken GREEN (lint not run before commit). Affected: `src/claudeutils/worktree/cli.py`, `tests/test_worktree_utils.py`, `tests/test_worktree_new_creation.py`.

## recall-pass

4-pass pipeline memory model integrated into design, runbook, orchestrate, and deliverable-review skills. Recall passes at cognitive boundaries: design recall (deep, whole decision files), runbook recall (+implementation +testing), task agent injection (orchestrator filters per phase), review recall (+failure modes). Reference forwarding eliminates convergence problem — each pass augments rather than re-discovers. Grounded against CE framework (Write/Select/Compress/Isolate) and Agentic RAG; deliberately inverts adaptive retrieval to prescriptive (fixed pipeline points, justified by 2.9% baseline). Added `/recall` skill, updated grounding skill to use scouts for diverge-converge. Delivered: 4 skill integrations, recall skill, grounding report, internal brainstorm (27 dimensions).

## merge-learnings-delta

Segment-level diff3 merge for learnings.md during worktree merges. Prevents consolidation reversion when branch diverges before a `/codify` on main. 7 TDD cycles, test fixtures refactored, justfile recipes added. Affected: src/claudeutils/worktree/merge.py, tests/.

## parsing-fixes-batch

7 bug fixes across prepare-runbook.py and validate-runbook.py: model-tags false positive, lifecycle false positive, model propagation, phase numbering, phase context extraction, 2 dead code removals. Tier 2 plan. Affected: agent-core/bin/prepare-runbook.py, agent-core/bin/validate-runbook.py, src/claudeutils/validation/memory_index_checks.py.

## planstate-delivered

Extended plan state machine with 4 post-execution states (review-pending, rework, reviewed, delivered). Single lifecycle.md file per plan, append-only. Two delivery paths: worktree (via merge) and in-main (via deliverable-review). Pre-ready states use functional artifact detection; post-ready use lifecycle.md. Affected: src/claudeutils/planstate/, agent-core/skills/orchestrate/, agent-core/skills/deliverable-review/.

## skills-quality-pass

30 skills (7,182 lines) compressed ~25% via Segment→Attribute→Compress framework. 10 FRs: description tightening, preamble removal, narrative extraction to references/, D+B gate anchoring (12 gates), redundant always-loaded content removal, tail section overhead removal, conditional path extraction. Bootstrapping order: corrector agents first. Affected: agent-core/skills/ (18+ files), agent-core/agents/.

## recall-tool-anchoring

D+B hybrid prototype for recall gate tool-anchoring. 3 shell scripts (_recall check/resolve/diff), reference manifest format replacing content dump in recall-artifact.md, D+B restructure of 8 skills/agents anchoring prose gates with tool calls, PreToolUse hook for recipe-redirect. Side fix: prepare-runbook-inline-regex. 3 new learnings codified. Affected: agent-core/skills/ (8 files), agent-core/hooks/, agent-core/bin/, plans/recall-tool-anchoring/.

## prepare-runbook-inline-regex

Fix inline phase detection in prepare-runbook.py for compound type tags (e.g., `general+inline`). Regex was matching only simple `inline` tag, missing compound forms. TDD with deliverable review. Affected: agent-core/bin/prepare-runbook.py.

## prepare-runbook-fixes

2 bug fixes in prepare-runbook.py: extract_cycles() H3 phase header termination (last cycle captured next phase's preamble), generate_cycle_file/generate_step_file provenance metadata pointing to non-existent runbook.md. TDD with edge-case tests and deliverable review. Affected: agent-core/bin/prepare-runbook.py.


## worktree-session-merge

RCA and fix for _worktree merge autostrategy dropping session.md content. Two manifestations: Worktree Tasks entries dropped (branch lacks main's section), branch-only content appended to wrong section (Blockers). Affected: src/claudeutils/worktree/merge.py.

## quality-infrastructure

3 FRs delivered: FR-3 renamed 11 agents (vet-fix-agent→corrector, quiet-task→artisan, tdd-task→test-driver, etc.) + deleted vet-agent + embedded vet-taxonomy in corrector + deleted 8 plan-specific detritus + propagated across ~45 files including prepare-runbook.py code paths. FR-1 split deslop.md into communication.md (prose rules, ambient) and project-conventions skill (code rules, injected). FR-2 added 5 grounded code density entries to cli.md + memory-index triggers. Affected: agent-core/agents/ (11 renames, 3 deletions), agent-core/skills/ (vet→review dir rename, 11 skill files updated), agent-core/fragments/ (vet-requirement→review-requirement, deslop deleted), agents/decisions/ (9 files), ~15 other files.

## unification

Original claudeutils consolidation project. Unified justfile recipes, pyproject.toml settings, and bash helpers across multiple projects (box-api, emojipack, pytest-md, home) into the claudeutils package. 7 phases, 3 sub-plans (consolidation, phase3-steps), 10+ step files per phase. Foundation of the current CLI and module structure. Affected: src/claudeutils/, justfile, pyproject.toml.

## runbook-quality-gates

5 FRs: outline-level simplification pass (parametrized consolidation of identical-pattern items), runbook-corrector agent, runbook-simplifier agent, outline-corrector agent, runbook validation pipeline. Full pipeline execution: requirements, design, 5 phases, 42 step files, deliverable review. Affected: agent-core/agents/ (3 new agents), agent-core/bin/prepare-runbook.py, agent-core/bin/validate-runbook.py.

## worktree-rm-fixes

Worktree rm edge case fixes discovered during field usage. Deliverable review completed Feb 20. Bug fixes for rm failure modes including submodule removal and merge commit interactions. Affected: src/claudeutils/worktree/cli.py, tests/test_worktree_rm.py.

## pretool-hook-cd-pattern

Allow `cd <project_root> && <command>` compound pattern in submodule-safety.py PreToolUse hook. Previously only bare `cd <dir>` was allowed, blocking sub-agents needing compound commands. TDD with vet review. Affected: agent-core/hooks/submodule-safety.py.

## skill-improvements

TDD workflow skill improvements addressing broken feedback loop across plan-tdd, review-tdd-plan, and tdd-task skills. Root cause: 37 GREEN cycles in claude-tools-rewrite all passed but features didn't work — weak RED tests enabled stub implementations. Fixes to RED test quality checks and escalation boundaries. Affected: agent-core/skills/ (plan-tdd, review-tdd-plan, tdd-task).

## handoff-lite-fixes

Fix handoff-lite skill misuse where Sonnet agent invoked Haiku-only skill, interpreted template as "replace" rather than "augment", deleting learnings section. Fix 1: decouple handoff from commit skill. Design review approved with changes. Affected: agent-core/skills/handoff/, agent-core/skills/commit/.

## handoff-haiku-import

Import handoff-haiku fix design documents and learnings from home repo into claudeutils. 3 commits imported, agent-core submodule synced. Provided context for commit-unification vet review (skill composition decisions). Affected: plans/, agents/session.md.

## feedback-fixes

Design and fixes for execution feedback processing patterns. Affected: agent-core/skills/.

## context-optimization

Brief for fragment demotion to reduce always-loaded context. Analysis: 25.5k tokens in memory files (50% of budget), ~6.6k demotable. Scoped but absorbed into skills-quality-pass FR-8 (redundant always-loaded content removal). Affected: CLAUDE.md @-references.

## integration-first-tests

Outline for migrating subprocess-mocking tests to integration-first pattern. 939 tests, 117 files. 3 violation areas identified where git operations were mocked instead of using real git via init_repo fixture. Scoped but not executed — absorbed into test diamond migration task.

## runbook-fenced-blocks

Fix fenced code block handling in runbook processing. Test plan with 9 execution cycles, deliverable review. Affected: agent-core/bin/prepare-runbook.py.

## commit-cli-tool

Outline for commit CLI tool. 3 review rounds. Absorbed into handoff-cli-tool plan when commit, handoff, and status were unified into `_session` CLI group.

## ambient-awareness

Killed: scope absorbed into other work.

## commit-rca-fixes

Killed: fixes landed via other plans.

## hook-output-fix

Killed: fixes landed via hook-batch plan.

## memory-index-update

Killed: superseded by memory-index-recall and subsequent recall work.

## plan-skill-fast-paths

Killed: fast paths absorbed into runbook evolution.

## reflect-skill

Empty plan directory — never populated. Reflect skill exists independently (agent-core/skills/reflect/).

## remember-update

Killed: absorbed into remember-skill-update plan.

## workflow-controls

Killed: scope absorbed into workflow-fixes and error-handling plans.

## docs-to-skills

Early doc-to-skill refactoring. Structural change absorbed into domain-based doc reorganization.

## handoff-skill

Early handoff skill design. Predates current handoff infrastructure; superseded by handoff-lite-fixes and commit-unification.

## commit-context

Early commit-context skill. Absorbed into commit-unification plan.

## wt-merge-dirty-tree

Brief for dirty-tree handling during worktree merge. Absorbed into worktree-rm-safety.

## wt-merge-skill

Outline for worktree merge ceremony. Absorbed into worktree-skill plan.

## runbook (validation)

Runbook validation reports (lifecycle, model-tags, red-plausibility, test-counts). Intermediate work absorbed into runbook-quality-gates.

## continuation-prepend

Continuation passing protocol gaps: cooperative protocol compliance for skills receiving continuation chains. Deliverables: `plans/continuation-prepend/plan.md` (continuation prepend design), `plans/cooperative-protocol-gaps/` (protocol gap classification), integration tests for continuation passing. Reviewed via deliverable-review with fix cycle.

## execute-skill-dispatch

Skill dispatch routing for inline execution. Classification and requirements for how skills are invoked during task execution. Affected: agent-core/skills/.

## flatten-hook-tiers

Hook tier simplification. Flattened hook tier structure for cleaner matching. Affected: agent-core/hooks/.

## inline-tdd-dispatch

TDD delegation for inline tasks. When inline execution encounters TDD work, delegate to test-driver agent in fresh context to preserve RED/GREEN discipline. Affected: agent-core/skills/.

## recall-cli-integration

CLI integration for recall system. 30 tests, recall resolver wired into `claudeutils _recall` CLI. Outline, runbook, full execution. Affected: src/claudeutils/when/, tests/.

## recall-null

Null mode for recall — skip recall pass when no recall-artifact exists. Tier 2 execution with outline. Affected: agent-core/skills/.

## runbook-recall-expansion

Step agent and corrector recall during full orchestration. 7 FRs expanding recall passes to orchestrated execution contexts. Affected: agent-core/skills/orchestrate/, agent-core/agents/.

## task-classification

Two-section task list (In-tree Tasks / Worktree Tasks) with D-9 classification heuristic. Runbook with 7+ cycles. Regression: design D-4 conflated move semantics with post-merge hygiene, removing `_update_session_and_amend`. Affected: agent-core/fragments/execute-rule.md, agent-core/skills/handoff/.

## task-pattern-statuses

Task status notation patterns: `[!]` blocked, `[✗]` failed, `[–]` canceled markers for session.md task tracking. Affected: agent-core/fragments/execute-rule.md.

## userpromptsubmit-topic

UPS topic injection for contextual hook responses. Topic detection from user prompt, injected as additionalContext for agent-relevant decision recall. Outline, runbook, full execution. Affected: agent-core/hooks/userpromptsubmit-shortcuts.py.

## when-resolve-fix

Fix for when-resolve.py behavior. Brief-scoped bugfix. Affected: src/claudeutils/when/.

## wt-rm-dirty

Dirty tree handling during worktree rm. Restored `_update_session_and_amend` after task-classification regression, fixed lifecycle.md dirty-state bug (merge.py stages lifecycle before commit). Affected: src/claudeutils/worktree/cli.py, src/claudeutils/worktree/merge.py.

## merge-submodule-ordering

Submodule conflict check ordering bug in merge.py. Absorbed by merge-lifecycle-audit plan (state machine audit covers this as one of 3 phase-boundary bugs).

## fix-planstate-detector

Added `outlined` status to planstate inference. FR-1: outline.md without design.md → `outlined`. FR-2: next action `/runbook plans/{name}/outline.md`. FR-3: downstream enumeration sites updated. Affected: src/claudeutils/planstate/inference.py, agent-core/fragments/execute-rule.md.

## pushback-grounding

Claim verification + recall for `d:` discussion protocol. FRs 1-3 delivered to pushback.md (ground evaluation section with Read-before-assess pattern, topic-relevant recall resolution, integration before "Form your assessment"). FR-4 (hook expansion update) superseded by directive skill promotion task. Affected: agent-core/fragments/pushback.md.

## cooperative-protocol-gaps

Continuation protocol compliance gaps in /design, /runbook, /worktree, /commit. Superseded by "Retrofit skill pre-work" task which covers same scope (continuation frontmatter + §Continuation sections).

## complexity-routing

Grounding research on complexity classification model. 7 fix points identified, execution strategy decision file written, routing model applied to /design and /runbook skills. Inline execution. Affected: agents/decisions/execution-strategy.md, agent-core/skills/design/, agent-core/skills/runbook/.

## fix-wt-parallel-restart

Remove restart disqualification from worktree skill parallel grouping (Mode B) and execute-rule.md. Prose edit. Affected: agent-core/skills/worktree/SKILL.md, agent-core/fragments/execute-rule.md.

## phase-scoped-agents

Per-phase agent generation with crew-<plan>-p<N> naming scheme. Concrete approach for phase-scoped baselines in orchestration. Outline, runbook, full execution. Affected: agent-core/skills/orchestrate/, agent-core/bin/prepare-runbook.py.

## runbook-generation-fixes

3 root causes in prepare-runbook.py producing 10 defects. Absorbed into parsing-fixes-batch execution. Affected: agent-core/bin/prepare-runbook.py.

## task-lifecycle

Task lifecycle awareness for STATUS and handoff. Unified task command source (planstate vs session.md), session-level continuation guidance. Inline execution. Affected: agent-core/fragments/execute-rule.md, agent-core/skills/handoff/SKILL.md.

## update-grounding-skill

Ground skill redesign: unified brainstorm/explore modes, parallelize branch agents via scout, remove conditional delete logic. Affected: agent-core/skills/ground/SKILL.md, agent-core/skills/ground/references/.

## worktree-rm-error-ux

Remove --confirm gate from worktree rm, improve git error messaging. Two phases (TDD + general). Affected: src/claudeutils/worktree/cli.py.
