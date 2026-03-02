# Cycle 3.4

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.4: Full E2E — `--from-main` merge happy path

End-to-end via CliRunner with real git repos exercising all FRs.

**Files:** `tests/test_worktree_merge_from_main.py` (extend from Cycle 2.4)

**RED:** Create real git repo with main + worktree branch, diverge both (main modifies learnings + deletes file, branch has focused session + new learnings + modified deleted file). Invoke via CliRunner: `merge --from-main`. Assert: session ours, learnings main-base + branch delta, deleted file gone, main ancestor of HEAD, exit 0.

**GREEN:** Should already pass from all prior cycles. If not, debug integration gap.

**Dependencies:** Cycles 3.1, 3.2, 3.3, Phase 2

**Stop/Error Conditions:**
- RED passes before all prior cycles → test fixture may not exercise all code paths
- CliRunner exit code non-zero → check stderr output for specific error
- Learnings content wrong → verify diff3 inversion producing main-base + branch delta
- Session content wrong → verify ours-keep policy active in full pipeline

**Checkpoint:** `just precommit` — all FRs verified, CLI working, full E2E passing.
