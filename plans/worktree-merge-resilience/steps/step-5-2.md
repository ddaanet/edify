# Step 5.2

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.2: Migrate all `click.echo(..., err=True)` to stdout (D-8, C-2)

**Objective:** All merge-related output goes to stdout. Exit code carries the semantic signal. Eliminates need for `2>&1` at call sites.

**Script Evaluation:** Haiku — mechanical substitution.

**Execution Model:** Haiku (mechanical substitution, enumerate call sites with grep).

**Scope boundary:** Only `merge.py` and the `merge` command function in `cli.py` (the `@worktree.command() def merge(slug)` function and its exception handler). Do NOT modify other CLI commands (`new`, `rm`, `ls`, etc.) or their error output.

**Implementation:**
1. Run: `grep -n "err=True" src/claudeutils/worktree/merge.py src/claudeutils/worktree/cli.py`
2. For `merge.py` matches: remove `err=True` from every match
3. For `cli.py` matches: remove `err=True` only from the `merge` command function (the `except subprocess.CalledProcessError` handler in `def merge(slug)`); skip all other functions
4. Verify no `err=True` remains in scope: `grep -n "err=True" src/claudeutils/worktree/merge.py` returns no matches; `grep -n "err=True" src/claudeutils/worktree/cli.py` returns only lines in non-merge functions (new, rm, etc.)

**Expected Outcome:** Zero `err=True` occurrences in merge.py and cli.py merge handler. All output visible via stdout only.

**Error Conditions:**
- `err=True` in a non-merge context (e.g., `new.py`, `rm.py`) — do NOT change those; scope is merge only
- Multiple `err=True` on same line → remove argument, preserve other arguments

**Validation:**
- `grep -n "err=True" src/claudeutils/worktree/merge.py` — zero matches
- `grep -n "err=True" src/claudeutils/worktree/cli.py` — only lines in non-merge functions (verify no match is inside `def merge(slug)`)
- `just precommit` passes

---
