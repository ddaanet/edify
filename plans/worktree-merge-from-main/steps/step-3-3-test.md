# Cycle 3.3

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.3: CLI `--from-main` flag (C-3)

Add Click `--from-main` flag to merge command. Mutually exclusive with slug argument.

**Files:** `src/claudeutils/worktree/cli.py`

**RED (CliRunner):**
1. `merge --from-main` on a branch where main is ancestor → exit 0
2. `merge --from-main some-slug` → exit 1 with error message
3. `merge` (no args, no flag) → exit 1/2 with usage error

**GREEN:** Make slug optional (`required=False`). Add `--from-main` flag. Validation: if from_main and slug → error; if not from_main and not slug → error. When from_main: call `merge_impl("main", from_main=True)`.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → CliRunner may be catching exceptions differently; verify exit codes
- Click argument parsing conflicts → optional slug + flag may need callback-based validation
- Existing `merge <slug>` tests break → slug must remain positional and functional when --from-main absent
