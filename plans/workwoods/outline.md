# Workwoods — Design Outline

## Approach

Replace manual plan tracking (jobs.md) with filesystem-inferred plan state. Build cross-tree status aggregation that reads session.md, git history, and plan directories across all worktrees. Upgrade `wt-ls` to display computed live status. Make worktree merge non-destructive (bidirectional). Extend merge with explicit per-section merge strategies for session.md.

**Core insight:** Plan state is already encoded in filesystem artifacts (which files exist in `plans/<name>/`). Vet validity is encoded in mtime relationships. Work count is encoded in git log. All three can be computed on demand — no manual tracking file needed.

**Requirements coverage:**
- FR-1: Phase 3 (cross-tree aggregation) + Phase 4 (upgraded wt-ls CLI)
- FR-2: Phase 2 (vet staleness detection via mtime)
- FR-3: Phase 1 (plan state inference module with workflow gates)
- FR-4: Phase 5 (worktree skill update for non-destructive merge)
- FR-5: Phase 5 (per-section merge strategies: additive tasks, Blockers evaluation, snippet squash)
- FR-6: Phase 6 (jobs.md elimination — direct replacement, no transition)
- NFR-1: All phases — computed on demand, no stored state
- NFR-2: All phases — read-only aggregation, no shared state
- NFR-3: All phases — git-versioned or computed from git
- C-1: Phase 2 (filesystem mtime for vet staleness)
- C-2: Phase 3 (git commit hash for work counting)
- C-3: No action needed (already satisfied)

## Key Decisions

**D-1: New module, not worktree extension.** Plan state inference (`planstate/`) is conceptually independent of worktree operations. Cross-tree status aggregation composes planstate + worktree discovery + git queries. Keeps worktree module focused on lifecycle operations.

**D-2: Upgrade existing `_worktree ls`, don't create new command.** Same entry point, richer output. Backward-compatible: old tab-separated format becomes a `--porcelain` flag; default output becomes the rich status display.

**D-3: Direct jobs.md replacement, no transition.** jobs.md is manually maintained and already drifts — validating planstate against an unreliable source adds complexity for no value. Phase 1 builds inference, Phase 5 adopts it, Phase 6 removes jobs.md. The phases themselves are the migration.

**D-4: Bidirectional merge = skill update only.** The `merge` CLI command already doesn't delete worktrees — that's the skill's Mode C calling `rm` afterward. Update skill to make `rm` a separate user decision, not automatic post-merge.

**D-5: FR-5 requires new code for Blockers evaluation.** Additive task merge exists (`_resolve_session_md_conflict()`). But the merge needs explicit per-section strategies: squash volatile sections (Status, Completed This Session, Next Steps, Reference Files), additive merge for tasks, and evaluate-then-merge for Blockers/Gotchas. Blockers evaluation is new — extract from worktree, flag for relevance review.

**D-6: worktree-merge-data-loss is execution dependency.** Its Track 1 (removal guard) and Track 2 (merge correctness) must be deployed before workwoods FR-4 execution. Design proceeds independently.

**D-7: Workflow gates as advisory preconditions.** Planstate returns `(state, next_action, gate_condition)` tuples. Gates are preconditions on state transitions (e.g., "vet stale — re-vet before planning"). Advisory, not blocking — shown in STATUS display. Natural completion of FR-3's next-action computation.

**D-8: Plan archive loaded at workflow gates, not always in context.** Completed plans move from jobs.md to `agents/plan-archive.md` with paragraph summaries (deliverables, key decisions, affected modules). Loaded on demand at design skill Phase A.1 and diagnostic/RCA sessions. Not in CLAUDE.md @-references. On-demand loading makes richer entries affordable.

## Scope

**In scope:**
- Plan state inference module with workflow gates (FR-3, FR-6 foundation) — Phase 1
- Vet staleness detection via mtime (FR-2, C-1) — Phase 2
- Cross-tree status aggregation (FR-1, C-2, NFR-1) — Phase 3
- Upgraded `wt-ls` CLI (FR-1) — Phase 4
- Per-section session.md merge strategies (FR-5) — Phase 5
- Worktree skill update for bidirectional merge (FR-4) — Phase 5
- jobs.md elimination and plan archive migration (FR-6) — Phase 6
- Validation updates (planstate replaces jobs.py validator) — Phase 6
- Design skill A.1 gate for archive loading — Phase 6
- Documentation updates (execute-rule.md STATUS section) — Phase 5

**Out of scope:**
- worktree-merge-data-loss implementation (separate plan, execution dependency per D-6)
- Separate tasks.md extraction (requirements explicitly deferred)
- Model tier changes (requirements: out of scope)
- Handoff review agent (requirements: out of scope)

## Open Questions (Resolved)

- **Q-1 (status snippet format):** Use session.md — already structured, parsed by session.py. No new file format.
- **Q-2 (wt-ls interaction):** Upgrade existing command. Rich output by default, `--porcelain` for old format.
- **Q-3 (worktree-update R1 overlap):** Additive task merge already satisfied by existing `_resolve_session_md_conflict()`. Blockers evaluation is new work.
- **Q-4 (jobs.md transition):** Direct replacement, no transition validation. Phases are the migration.
- **Q-5 (session snippet squash):** Per-section merge strategies defined — squash volatile sections, additive tasks, evaluate Blockers/Gotchas.

## Dependencies

**External:**
- worktree-merge-data-loss Track 1 (removal guard) and Track 2 (merge correctness) must be deployed before Phase 5 execution (D-6)

**Internal phase dependencies:**
- Phase 2 depends on Phase 1 (planstate module integration)
- Phase 3 depends on Phase 1 and Phase 2 (aggregates planstate + vet status)
- Phase 4 depends on Phase 3 (CLI consumes aggregation)
- Phase 5 depends on Phase 1 (execute-rule.md uses planstate inference)
- Phase 6 depends on Phase 1 and Phase 5 (completes jobs.md elimination after planstate adoption)

## Risks

**R-1: Vet naming convention assumptions**
- Phase 2 assumes naming convention (outline.md → reports/design-vet.md, etc.)
- Mitigation: Encode conventions as configuration or constants; test coverage for convention validation

**R-2: Filesystem mtime reliability**
- C-1 uses filesystem mtime which can be manipulated (touch, checkout, restore)
- Mitigation: Document limitation; mtime is "good enough" for normal workflows, not adversarial cases

**R-3: Blockers evaluation complexity**
- Extracting Blockers/Gotchas from worktree and evaluating continued relevance may require agent judgment at merge time
- Mitigation: Extract and flag — present to agent/user for decision rather than auto-resolving

## Phase Structure

**Phase 1: Plan state inference** (TDD) — FR-3, FR-6 foundation
- Artifact detection: scan `plans/<name>/` for requirements.md, outline.md, design.md, runbook-phase-*.md, steps/, orchestrator-plan.md
- State mapping: artifact set → status (requirements/designed/planned/ready)
- Next action computation: status → command string
- Workflow gates: preconditions on state transitions (e.g., vet stale → re-vet first). Returns `(state, next_action, gate_condition)` tuples (D-7)
- Module: `src/claudeutils/planstate/`
- Test coverage: artifact presence/absence combinations, state transitions, next action derivation, gate conditions

**Phase 2: Vet staleness detection** (TDD) — FR-2, C-1
- Vet chain definition: source artifact → expected vet report (naming convention: outline.md → reports/design-vet.md, runbook-phase-N.md → reports/checkpoint-N.md)
- Mtime comparison: source mtime > report mtime = stale (C-1: filesystem mtime, not git timestamps)
- Per-plan vet summary: which artifacts need re-vet
- Feeds Phase 1 gate conditions (stale vet = gate on next transition)
- Integrates with planstate module
- Test coverage: mtime edge cases (equal, source newer, report newer), missing reports, naming convention validation

**Phase 3: Cross-tree status aggregation** (TDD) — FR-1, C-2, NFR-1
- Tree discovery: `git worktree list` → paths
- Per-tree data: session.md task status, commit count since last handoff (C-2: `git log -1 --format=%H -- agents/session.md` as anchor), latest commit subject, clean/dirty state (`git status --porcelain`), recency (last commit timestamp)
- Aggregation: combine planstate + vet status + tree status
- Sort by most recently committed
- Computed on demand (NFR-1: no stored state)
- Test coverage: multiple worktrees, main tree, empty trees, dirty vs clean states, commit count edge cases (no handoff yet, multiple commits)

**Phase 4: Upgraded wt-ls CLI** (TDD) — FR-1
- Rich output format (default): human-readable multi-line per tree (worktree name, plan, status, gate conditions, commits since handoff, latest commit subject, vet chain status, clean/dirty)
- Porcelain output (--porcelain): backward-compatible tab-separated (D-2)
- Integration with planstate + vet + tree status from Phase 3
- Include main tree in output (not just worktrees)
- Sort by most recently committed first (FR-1)
- Test coverage: output formatting, porcelain mode, sorting, main tree inclusion, gate display

**Phase 5: Merge strategies + skill update** (mixed: TDD for merge code, general for skill/docs) — FR-4, FR-5
- Per-section session.md merge strategies (D-5):

  | Section | Strategy |
  |---------|----------|
  | Status line | Squash (discard worktree's) |
  | Completed This Session | Squash (session-local) |
  | Pending Tasks | Additive (existing behavior) |
  | Worktree Tasks | Preserve main's |
  | Blockers/Gotchas | Evaluate — extract from worktree, flag for relevance review |
  | Reference Files | Squash (paths may not apply to main) |
  | Next Steps | Squash (session-local) |

- Implement Blockers/Gotchas extraction in `_resolve_session_md_conflict()` (TDD)
- Worktree skill Mode C: remove auto-rm, make `wt-rm` separate user decision (D-4, general)
- execute-rule.md STATUS: update to use planstate inference instead of jobs.md reads (general)
- Dependencies: worktree-merge-data-loss Track 1 + Track 2 must be deployed first (D-6)
- Test coverage: per-section merge behavior, Blockers extraction and flagging

**Phase 6: jobs.md elimination + archive** (mixed: TDD for validation, general for skill/doc updates) — FR-6
- New planstate validator: replaces validation/jobs.py (TDD)
- Plan archive: migrate jobs.md "Complete (Archived)" → `agents/plan-archive.md` with paragraph summaries (D-8)
- Design skill A.1: add archive loading gate — load plan-archive.md during documentation checkpoint
- Handoff skill update: on plan completion, append paragraph summary to plan-archive.md; stop writing jobs.md plan table
- Remove jobs.md from session file exemptions in merge
- Remove validation/jobs.py and precommit integration
- Remove jobs.md @-reference from CLAUDE.md
- Test coverage: planstate validator correctness, archive format validation
