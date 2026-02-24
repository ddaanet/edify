# Recall Artifact: Planstate Delivered

Recalled 12 decision files across 4 passes (mode: all). Topic: planstate lifecycle, merge integration, skill/prose updates.

## Decisions Directly Affecting This Plan

**When Adding A New Variant To An Enumerated System** (workflow-planning.md)
- After updating authoritative definition, grep ALL downstream enumeration sites
- Applied: Phase 3 must update execute-rule.md status values AND prioritize/SKILL.md plan status list

**When Selecting Model For Prose Artifact Edits** (pipeline-contracts.md)
- Skills, fragments, agent definitions, design documents → opus
- Applied: Phase 3 model corrected from sonnet to opus

**When Design Resolves To Simple Execution** (workflow-optimization.md)
- All-prose phases with no feedback loop → execute inline from design outline
- Applied: Phase 3 changed from general runbook to inline execution

**When Preferring E2E Over Mocked Subprocess** (testing.md)
- E2E with real git repos (tmp_path), mock only for error injection
- Applied: Phase 2 merge tests should use real git repos, not mock lifecycle.md parsing

**When Tests Simulate Merge Workflows** (testing.md)
- Test should make worktree branch the one that gets merged (parent of merge commit)
- Applied: Phase 2 tests creating merge scenarios must set up realistic branch topology

**When Tracking Worktree Tasks In Session.md** (operational-tooling.md)
- Tasks stay in Pending with inline marker; #status renders worktree section from `_worktree ls`
- Applied: D-6 delivered filtering is agent-side (execute-rule.md instruction), not code-side

## Decisions Constraining Implementation

**_parse_lifecycle_status() already exists** (inference.py lines 37-61)
- Phase 2 imports and reuses this; no shared utility extraction needed

**merge() state machine has 5 paths** (merge.py)
- clean, merged, parent_resolved, parent_conflicts, submodule_conflicts
- All converge through `_phase4_merge_commit_and_precommit`
- Single insertion point after _phase4 covers all paths

**merge.py is 364 lines** (project-config.md: 400-line limit)
- Adding ~25 lines for lifecycle scan stays within limit

**GREEN verification must include lint** (testing.md)
- Phase 2 TDD: `just check && just test`, not just pytest

## Tangential Context (loaded, no direct impact)

- defense-in-depth.md — quality gate layering (lifecycle entries at chokepoints is consistent)
- prompt-structure-research.md — rule formatting (Phase 3 adds values, doesn't restructure)
- project-config.md — agent composition, skill discovery (not applicable)
- workflow-core.md — checkpoint patterns (standard orchestration, no special handling)
- orchestration-execution.md — delegation patterns (standard, no special handling)
- implementation-notes.md — source-not-generated, edit preconditions (standard)
