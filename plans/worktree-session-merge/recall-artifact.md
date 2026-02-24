# Recall Artifact — worktree-session-merge

## When Resolving Session.md Conflicts During Merge

**Source:** `agents/decisions/operational-tooling.md`
**Relevance:** Existing conflict resolution pattern — the fix extends this to non-conflict paths.

Anti-pattern: `git checkout main -- agents/session.md` discards branch-side data. Correct: compare against known task list, verify no tasks dropped.

## When Tracking Worktree Tasks In Session.md

**Source:** `agents/decisions/operational-tooling.md`
**Relevance:** WT section is being phased out (inline markers planned). Fix must handle current format.

Anti-pattern: Separate WT section with move semantics. Correct: tasks stay in Pending with inline `→ slug` marker. Current code still uses the section — fix must preserve it until migration.

## When Merging Worktree With Consolidated Learnings

**Source:** `agents/decisions/operational-tooling.md`
**Relevance:** Same bug class — merge favoring longer/different branch version over main's consolidated version.

After merging a branch that diverged before consolidation, verify file content. Only delta (new entries added on branch) should be appended.

## When Tests Simulate Merge Workflows

**Source:** `agents/decisions/testing.md`
**Relevance:** Test setup pattern for merge scenarios.

Test should make worktree branch the one that gets merged. Its tip becomes parent of merge commit, preserved through amend.

## When Preferring E2E Over Mocked Subprocess

**Source:** `agents/decisions/testing.md`
**Relevance:** Test approach constraint — real git repos via tmp_path, no subprocess mocking.

Git with tmp_path is fast (milliseconds). Mock subprocess only for error injection.

## When Placing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** Post-merge validation pattern for future session.md precommit check (out of scope but informs design).

Gate at chokepoint (commit). Scripted check blocks mechanically. No judgment at the gate.

## When Adding A New Variant To An Enumerated System

**Source:** `agents/decisions/workflow-planning.md`
**Relevance:** After adding `remerge_session_md()`, grep for all callers of `_phase4_merge_commit_and_precommit` to verify slug threading.

After updating authoritative definition, grep all affected files for existing variant names and update every enumeration site.

## Merge Artifact Diagnostic

**Source:** `plans/worktree-merge-resilience/diagnostic.md`
**Relevance:** Documents the general class of merge artifacts. Session.md is a specific instance.

Reproduction conditions: branch diverges, main receives merges, branch modifies in-place + adds at tail, ort strategy produces clean-but-wrong result.

## Learnings.md Merge Resilience Outline

**Source:** `plans/worktree-merge-resilience/outline.md`
**Relevance:** Establishes the `remerge_*` pattern. Session.md fix follows same integration pattern (phase 4 insertion point) but different merge algorithm.

Key pattern: resolver runs on ALL merge paths, not just conflicts. Phase 4 is the convergence point for all 5 state machine paths.
