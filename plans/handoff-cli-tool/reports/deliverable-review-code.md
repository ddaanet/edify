# L1 Code Review: handoff-cli-tool (RC13)

**Date:** 2026-03-25
**Methodology:** Full-scope review of all 26 code files against outline.md
**Review type:** RC12 C-1 fix verification + full-scope rescan
**Prior:** RC12 deliverable-review.md (1C/0M/22m)

## RC12 Critical Verification

**C-1 (CommitInputError uncaught in commit_cmd): FIXED**

`session/cli.py:33-34` adds `except CommitInputError as e:` after the `CleanFileError` handler. The fix satisfies S-3 on all three axes:
- **Output channel:** `_fail()` writes to stdout (via `click.echo`)
- **Output format:** `f"**Error:** {e}"` — structured markdown
- **Exit code:** `code=2` — input validation

Propagation path verified: `_validate_inputs` (commit_pipeline.py:267,277) raises `CommitInputError` -> `commit_pipeline()` does not catch it -> `commit_cmd` except clause at line 33 catches it -> `_fail()` outputs structured markdown and exits 2.

## RC12 Code Minor Carry-Forward

| RC12 ID | Location | Status | Notes |
|---------|----------|--------|-------|
| m-1 | pipeline.py:203,228 | NOT FIXED | Blank line stripping in append/autostrip |
| m-2 | pipeline.py:206-219 | NOT FIXED | Autostrip re-executes _find_repo_root |
| m-3 | status/cli.py:60-65 | NOT FIXED | Old-format detection false trigger |
| m-4 | commit_gate.py:66 | NOT FIXED | `> 3` guard (no practical impact) |
| m-5 | pipeline.py:173-178 | NOT FIXED | Strip comparison edge case |
| m-6 | handoff/cli.py:70 | NOT FIXED | Empty git_changes diagnostic |
| m-7 | pipeline.py:115-140,170 | NOT FIXED | Newline sensitivity in mode detection |

All 7 code minors carried from RC12 remain unaddressed. None have functional impact in normal operation.

## Findings

No new Critical or Major findings. No new Minor findings beyond those carried from RC12.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | session/ with handoff/ and status/ sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py; all worktree modules import from claudeutils.git |
| S-3: Output and error conventions | Covered | C-1 regression closed |
| S-4: Session.md parser | Covered | session/parse.py composes existing parsers |
| S-5: Git changes utility | Covered | git_cli.py with submodule iteration |
| H-1: Domain boundaries | Covered | CLI handles status + completed writes only |
| H-2: Committed detection | Covered | Three modes in pipeline.py:143-233 |
| H-3: Diagnostic output | Covered | git_changes() after writes (cli.py:69-70) |
| H-4: State caching + step_reached | Covered | HandoffState dataclass + resume logic (cli.py:59) |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + report freshness |
| C-2: Submodule coordination | Covered | 4-state matrix; error path now S-3 compliant |
| C-3: Input validation + STOP | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint / no-vet options |
| C-5: Amend semantics | Covered | diff-tree for HEAD files, directional propagation |
| ST-0: Worktree-destined tasks | Covered | worktree_marker skip in Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5, dependency edges |
| ST-2: Preconditions | Covered | Missing file -> exit 2, old format -> exit 2 |
| Registration in cli.py | Covered | Lines 155-158 |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 7 (all carried from RC12) |

**RC12 C-1 closure confirmed.** The `except CommitInputError` clause at `session/cli.py:33-34` catches the exception from `commit_pipeline._validate_inputs` and routes it through `_fail()` with `**Error:**` format and exit code 2. S-3 compliance restored on all three axes.

**No new findings.** Full-scope rescan of all 26 code files produced no findings above those already documented in RC12.

**Carried minors:** All 7 code minors from RC12 are edge cases with no functional impact in normal operation (blank line stripping, off-by-one guard never triggered, empty diagnostic block, string comparison sensitivity). The `_git_output` duplication (commit_gate.py:41) has an in-code TODO for consolidation.

**Trend:** RC12 1C/0M/7m -> RC13 0C/0M/7m (code scope). Critical regression closed. Minor count stable.
