# Cycle 2.4

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.4: E2E integration — session.md + structural resolution

End-to-end test with real git repos verifying FR-1 and FR-3 together.

**Files:** new test file `tests/test_worktree_merge_from_main.py`

**RED:** Create real git repo: initial commit, create branch, diverge both (main deletes a file + adds tasks to session.md, branch modifies deleted file + has focused session). Call `merge("main", from_main=True)`. Assert: session.md is branch's version (ours), deleted file is gone (theirs accepted), merge succeeds (exit 0), main is ancestor of HEAD.

**GREEN:** Should already pass from Cycles 2.1-2.3. If not, debug the integration gap.

**Dependencies:** Cycles 2.1, 2.2, 2.3

**Stop/Error Conditions:**
- RED passes before all prior cycles implemented → test fixture may not exercise the right code paths
- Integration fails despite unit cycles passing → wiring issue between merge pipeline and resolution functions
- Session.md content differs from branch's original → resolve or remerge not keeping ours

**Checkpoint:** `just precommit` — session.md and structural resolution verified for both directions.
