# Plan Archive

Completed plans with summaries. Loaded on demand during design research (Phase A.1)
and diagnostic/RCA sessions.

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

Learnings consolidation infrastructure. 7 steps, 4 phases. Automated consolidation of learnings.md into permanent documentation. Affected: agent-core/skills/remember/, agent-core/bin/.

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

## worktree-error-output

Migrated all `_worktree` CLI error output from stderr to stdout per LLM-native CLI convention. Added `_fail(msg, code) -> Never` helper consolidating `click.echo + raise SystemExit` pairs, caught `derive_slug` ValueError in `new()` with clean exit 2, removed `err=True` from 12 sites (8 error+exit converted to `_fail()`, 4 warning-only stripped). 5 steps across 3 phases (TDD × 2, general × 1), 13 commits. TDD audit: 50% compliance — Cycle 1.1 broken GREEN (lint not run before commit). Affected: `src/claudeutils/worktree/cli.py`, `tests/test_worktree_utils.py`, `tests/test_worktree_new_creation.py`.

## quality-infrastructure

3 FRs delivered: FR-3 renamed 11 agents (vet-fix-agent→corrector, quiet-task→artisan, tdd-task→test-driver, etc.) + deleted vet-agent + embedded vet-taxonomy in corrector + deleted 8 plan-specific detritus + propagated across ~45 files including prepare-runbook.py code paths. FR-1 split deslop.md into communication.md (prose rules, ambient) and project-conventions skill (code rules, injected). FR-2 added 5 grounded code density entries to cli.md + memory-index triggers. Affected: agent-core/agents/ (11 renames, 3 deletions), agent-core/skills/ (vet→review dir rename, 11 skill files updated), agent-core/fragments/ (vet-requirement→review-requirement, deslop deleted), agents/decisions/ (9 files), ~15 other files.
