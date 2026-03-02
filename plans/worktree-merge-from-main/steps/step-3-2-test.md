# Cycle 3.2

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.2: `remerge_learnings_md` from-main policy (FR-2)

When `from_main=True`, invert ours/theirs in the phase 4 all-paths learnings merge.

**Files:** `src/claudeutils/worktree/remerge.py`

**RED:** Two tests:
1. from_main=True: MERGE_HEAD state with divergent learnings. Call `remerge_learnings_md(from_main=True)`. Assert: produces main-base + branch delta content.
2. Regression: from_main=False (default): existing behavior unchanged — ours as base.

**GREEN:** Add `from_main: bool = False` to `remerge_learnings_md`. When from_main: swap ours_segs/theirs_segs in `diff3_merge_segments` call, and swap role in statistics output.

**Dependencies:** Cycle 3.1

**Stop/Error Conditions:**
- RED passes before implementation → verify MERGE_HEAD exists in test fixture
- Regression test fails → from_main=False default not preserving existing ours-base behavior
- Statistics output wrong → ours/theirs labels swapped but counts not adjusted
