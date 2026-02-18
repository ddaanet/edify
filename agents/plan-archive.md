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

Unified /runbook skill, plan-reviewer agent, review-plan skill, pipeline-contracts. Consolidated fragmented workflow tooling into coherent pipeline. Affected: agent-core/skills/runbook/, agent-core/agents/.

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
