# Deliverable Review: worktree-merge-resilience

**Date:** 2026-02-18
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines | Changes |
|------|------|------:|---------|
| Code | src/claudeutils/worktree/merge.py | 341 | +117 (state machine, conflict report, Phase 3 rewrite) |
| Code | src/claudeutils/worktree/merge_state.py | 138 | New (extracted state detection + untracked recovery) |
| Code | src/claudeutils/worktree/cli.py | 398 | +1/-1 (err=True removal on merge handler) |
| Test | tests/test_worktree_merge_routing.py | 299 | New (5 state routing tests) |
| Test | tests/test_worktree_merge_submodule.py | 397 | +256 (conflict + resume tests) |
| Test | tests/test_worktree_merge_conflicts.py | 360 | +72 (conflict output) |
| Test | tests/test_worktree_merge_errors.py | 293 | +91 (error paths + untracked recovery) |
| Test | tests/test_worktree_merge_merge_head.py | 169 | +76 (MERGE_HEAD handling) |
| Test | tests/test_worktree_merge_correctness.py | 294 | +6 (exit code adjustments) |
| Test | tests/test_worktree_merge_validation.py | 190 | +10 (idempotency) |
| Prose | agent-core/skills/worktree/SKILL.md | 128 | Mode C rewrite (exit code 3, resume instructions) |

**Total:** 3007 lines across 11 files, +955/-112 net changes.

**Design conformance:** All design-specified files produced. No missing deliverables. No excess artifacts outside scope.

## Critical Findings

None.

## Major Findings

### 1. `parent_conflicts` resume skips auto-resolution
**File:** merge.py:327-333
**Axis:** Functional completeness (FR-5)
**Design ref:** FR-2, FR-5

When an agent resolves some conflicts but not all, re-running merge detects `parent_conflicts` and immediately reports + exits 3. It does NOT run `resolve_session_md`, `resolve_learnings_md`, or `checkout --ours agent-core`. If session.md or learnings.md are among the remaining unresolved conflicts, they appear in the report as requiring manual resolution when they could be auto-resolved.

The `_phase3_merge_parent` path (lines 225-238) correctly runs auto-resolution. The `parent_conflicts` resume path bypasses it entirely.

**Impact:** Agent gets stuck on auto-resolvable files after partial conflict resolution.

### 2. Precommit failure drops stdout diagnostics
**File:** merge.py:312-313
**Axis:** Conformance (D-8, C-2)
**Design ref:** D-8

Phase 4 echoes `precommit_result.stderr` on precommit failure but drops `precommit_result.stdout`. Many lint tools (ruff, mypy) write diagnostics to stdout. The agent sees "Precommit failed after merge" plus whatever was on stderr, missing the primary diagnostic output.

SKILL.md step 5 instructs "Review the failed precommit checks in stdout" — the contract assumes complete output.

### 3. Submodule MERGE_HEAD persists after successful parent merge
**File:** merge.py:131-181, merge_state.py:26-33
**Axis:** Robustness (cross-cutting: state machine + submodule lifecycle)
**Design ref:** D-2, FR-1

When Phase 2 submodule merge fails (MERGE_HEAD left in agent-core), the pipeline continues to Phase 3 (parent merge). If no parent source conflicts exist, Phase 3+4 succeed and exit 0. The agent-core MERGE_HEAD is never cleaned up.

On re-run, state is "merged" → Phase 1+2+4 → Phase 2 tries `git merge` in agent-core → fails ("You have not concluded your merge") → returns → Phase 4 sees branch merged → exits 0 again. The submodule MERGE_HEAD persists indefinitely, breaking `git -C agent-core` operations until manually resolved.

**Impact:** Submodule-only conflicts (no parent source conflicts) silently orphan MERGE_HEAD. Exit 0 gives no signal that cleanup is needed. D-2 says "Agent resolves submodule + parent conflicts in one pass" — but exit 0 doesn't prompt the agent.

### 4. resolve.py `err=True` in merge code path
**File:** resolve.py:98-106
**Axis:** Conformance (D-8)
**Design ref:** D-8

`resolve_session_md` (called from merge.py:233 during Phase 3) has two `click.echo(..., err=True)` calls in error-recovery paths. These execute during merge and send output to stderr, violating D-8's "single output stream" contract.

The outline excludes "Changes to resolve.py session/learnings strategies" from scope, but D-8 is a cross-cutting output concern. These paths are rare (triggered when `git add agents/session.md` fails) but when they fire, output goes to stderr while everything else goes to stdout.

## Minor Findings

### Code clarity
- `_parse_untracked_files` name misleading: function handles both untracked-file and local-changes-overwritten errors (merge_state.py:53-71)
- Duplicated conflict-listing pattern: `_git("diff", "--name-only", "--diff-filter=U").split("\n")` + filter appears identically at merge.py:225-226 and merge.py:328-331
- Conflict report divergence label ambiguous: "Branch: N commits ahead, Main: M commits ahead" — both say "ahead" (merge.py:53-55)
- No guard for absent agent-core directory in `_detect_merge_state` — git emits spurious stderr when agent-core doesn't exist (merge_state.py:26-30)

### Test specificity
- Submodule conflict tests accept `exit_code in (0, 3)` non-deterministically where scenario should produce deterministic `0` (test_worktree_merge_submodule.py:310, :349)
- `test_conflict_output_contains_all_fields` checks `any(code in output for code in ["UU", ...])` instead of asserting specific status code for the scenario (test_worktree_merge_conflicts.py:344)
- `test_merge_idempotency` accepts exit code 2 (fatal) as valid idempotency outcome (test_worktree_merge_validation.py:171)
- `_detect_merge_state()` directly unit-tested for only 2 of 5 states (merged, clean); parent_resolved, parent_conflicts, submodule_conflicts tested only indirectly through merge()
- Merged state test name claims Phase 1+2+4 routing but doesn't verify phase execution (test_worktree_merge_routing.py:59-86)
- No test for delete/modify conflict type in FR-4 output (only both-modified tested)
- Test name `test_merge_aborts_cleanly_when_untracked_file_blocks` contradicts NFR-2 — test validates recovery, not abort

### Design document
- outline.md D-5 says `merged → Phase 4 (precommit only)` but implementation routes Phase 1+2+4. This was an intentional fix from Cycle 1.2 escalation (session.md documents it). Design not updated.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| FR-1: Submodule conflict pass-through | Covered | merge.py:165-171 |
| FR-2: Parent merge preservation | Covered | merge.py:236-238 |
| FR-3: Untracked file collision handling | Covered | merge.py:202-220, merge_state.py:100-138 |
| FR-4: Conflict context output | Covered | merge.py:31-62 |
| FR-5: Idempotent resume | **Partial** | parent_conflicts route skips auto-resolution (Major #1) |
| NFR-1: Exit code 3 | Covered | merge.py:238, :333 |
| NFR-2: No data loss | Covered | Full audit: no abort/clean in any path |
| C-1: Skill contract | Covered | SKILL.md Mode C rewrite |
| C-2: Non-interactive resolution | Covered | No interactive prompts |
| D-1: Exit codes 0/1/2/3 | Covered | All 14 SystemExit calls correctly classified |
| D-2: Submodule pass-through | **Partial** | Works for initial run; dangling MERGE_HEAD on re-run (Major #3) |
| D-3: No merge abort | Covered | Zero instances of merge --abort or clean -fd |
| D-4: Untracked files git-add-retry | Covered | merge_state.py:100-138 |
| D-5: State machine routing | Covered | 5 states detected + routed correctly |
| D-6: _git check=False for conflicts | Covered | All conflict-path _git calls use check=False |
| D-7: No data loss invariant | Covered | Full audit in Layer 1 code report |
| D-8: All output to stdout | **Partial** | merge.py clean; resolve.py has 2 err=True in merge path (Major #4) |

## Summary

| Severity | Count |
|----------|------:|
| Critical | 0 |
| Major | 4 |
| Minor | 12 |

**Assessment:** Implementation is solid — state machine, exit codes, and no-data-loss invariant are all correct. The four Major findings are:
- Two functional gaps (parent_conflicts auto-resolution, submodule MERGE_HEAD cleanup)
- Two output gaps (precommit stdout dropped, resolve.py err=True)

None are data-loss risks. All are addressable as follow-up fixes.

## Layer 1 Reports

- `plans/worktree-merge-resilience/reports/deliverable-review-code.md`
- `plans/worktree-merge-resilience/reports/deliverable-review-tests.md`
- `plans/worktree-merge-resilience/reports/deliverable-review-prose.md`
