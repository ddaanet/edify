# Deliverable Review: wt-blocker-merge-fix

**Date:** 2026-02-21
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines | Change |
|------|------|-------|--------|
| Code | `src/claudeutils/worktree/resolve.py` | 163 | +53/−25 |
| Test | `tests/test_worktree_merge_blocker_fixes.py` | 147 | New file |

Conformance baseline: session.md completed-work description (no formal design document).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Correctness edge case

1. **Dedup fragility with previously-tagged blockers** — resolve.py:27-28, axis: robustness
   - If a prior merge tagged an ours blocker (`- Blocker [from: old-slug]`), theirs' untagged `- Blocker` won't match the first-line comparison. Produces cosmetic duplicate.
   - Low probability (same blocker independently authored in multiple worktrees). No data loss — worst case is a duplicate entry.

### Test coverage

2. **Missing test: both Reference Files and Next Steps present** — axis: coverage
   - Three positioning tests cover Reference Files only, Next Steps only, and neither. The `min(sb[0])` earliest-section selection (resolve.py:50) is unexercised when both exist.

3. **Missing test: continuation lines on shared blocker** — axis: coverage
   - Dedup tests use single-line blockers only. A shared blocker with differing continuation lines would confirm `b[0]` first-line-only matching is intentional. Vet report minor #2 also noted this.

### Code quality (pre-existing)

4. **Raw subprocess in `_task_is_in_pending_section`** — session.py:239-245, axis: modularity
   - 6-line `subprocess.run` call for `git show` when `_git` helper exists in `worktree/git_ops.py`. Same module's sibling `resolve.py` uses `_git` for identical operations (lines 112-113). Documented pattern: "24 calls replaced, 477→336 lines" (operational-tooling.md).
   - Pre-existing, not introduced by this branch. In the deliverable's dependency chain.

### Audit trail

5. **Vet report references stale code** — tmp/vet-blocker-merge.md, axis: accuracy
   - Scope says "tests/test_worktree_merge_strategies.py" — actual new tests are in test_worktree_merge_blocker_fixes.py.
   - Minor #1 references `result_so_far` pattern at resolve.py:72-79 — eliminated by the `_merge_blockers` extraction. Vet reviewed pre-extraction snapshot.

## Gap Analysis

| Specified deliverable | Status |
|---|---|
| Section positioning (before Reference Files / Next Steps) | Covered — resolve.py:46-60, tests 1-3 |
| Deduplication (ours blockers not re-appended) | Covered — resolve.py:27-29, tests 4-5 |
| `_merge_blockers()` helper extraction | Covered — resolve.py:16-60 |
| 5 new tests | Covered — 3 positioning + 2 dedup |

No missing deliverables. No unspecified deliverables.

## Summary

- Critical: 0
- Major: 0
- Minor: 5 (1 edge case, 2 coverage, 1 code quality, 1 audit trail)
