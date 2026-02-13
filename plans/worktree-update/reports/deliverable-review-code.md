# Deliverable Review: worktree-update Code Artifacts

**Reviewer:** Opus 4.6
**Date:** 2026-02-13
**Scope:** `cli.py` (370 lines), `merge.py` (291 lines), `utils.py` (21 lines), `__init__.py` (1 line)
**Design reference:** `plans/worktree-update/design.md`

---

## Findings

### F1. `_git()` helper duplicated across cli.py and merge.py

- **File:** `src/claudeutils/worktree/cli.py:17-31` and `src/claudeutils/worktree/merge.py:11-25`
- **Axis:** Modularity
- **Severity:** Minor
- **Description:** Identical `_git()` function defined in both modules. The design says "extract logic into functions" and decision D4 says "single implementation for shared logic." This helper is a natural candidate for `utils.py`. The duplication means bug fixes or signature changes must be applied in two places.

### F2. `_filter_section` discards non-bullet continuation lines

- **File:** `src/claudeutils/worktree/cli.py:55-60`
- **Axis:** Functional correctness
- **Severity:** Major
- **Description:** The filtering logic in `_filter_section` iterates lines and keeps bullet lines (`- `) that are relevant, plus "non-bullet lines that have content" (line 59: `not line.startswith("- ") and line.strip()`). This means ALL non-bullet non-empty lines are kept regardless of relevance, and continuation lines of irrelevant bullets (indented lines under a `- ` entry) are included even when the parent bullet was filtered out. For example, if `Blockers / Gotchas` has:

  ```
  - Unrelated issue: GPU memory constraints
    - Sub-detail about GPU
  - Task X depends on Y
  ```

  The `Sub-detail about GPU` line would be included (it doesn't start with `- ` and has content), even though the parent bullet was irrelevant. The design says "relevant entries only" for filtered sections. Continuation lines (indented sub-bullets, additional metadata) should track the relevance of their parent bullet.

### F3. `focus_session` task regex doesn't capture multi-line metadata

- **File:** `src/claudeutils/worktree/cli.py:67`
- **Axis:** Functional correctness
- **Severity:** Major
- **Description:** The regex `r"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"` uses `re.DOTALL` so `.` matches newlines. The `(.+?)` is lazy, so it stops at the first `\n-` or `\n## `. However, real session.md task entries have continuation lines:

  ```
  - [ ] **Task Name** -- `command` | sonnet
    - Plan: plans/test-plan
    - Notes: additional context
  ```

  The `(?=\n-)` lookahead will match at the start of the `  - Plan:` continuation line (it starts with `\n` then `-` after spaces... wait, the continuation is `\n  - `, which has `\n` followed by spaces then `-`). Actually `\n-` requires newline immediately followed by `-`. Continuation lines are indented (`  - `), so `\n  - ` would not match `\n-`. This means the regex *does* capture continuation lines correctly -- they're consumed by `(.+?)` until a non-indented `\n-` or `\n## ` is found.

  **Correction:** After closer analysis, this works correctly for indented continuation lines. The lazy quantifier stops at `\n-` (top-level bullet) or `\n## ` (section header), both of which are unindented. Continuation lines starting with `  - ` don't trigger the lookahead. **Reclassified as non-issue.**

### F4. Phase 1 THEIRS clean check runs on non-existent directory

- **File:** `src/claudeutils/worktree/merge.py:166-178`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** When the worktree directory doesn't exist (line 167 prints a warning), the code still calls `_check_clean_for_merge(path=wt_path(slug), label="worktree")` on line 178. This runs `git -C <nonexistent-path> status --porcelain` which fails with a non-zero exit and empty stdout. Due to `check=False`, the function silently succeeds (no dirty lines found). The behavior is correct by accident -- a missing worktree is "clean" -- but relies on git's error behavior rather than explicit handling. An explicit `if worktree_dir.exists():` guard would make the intent clear.

### F5. `_phase3_merge_parent` returns early on clean merge, skipping commit

- **File:** `src/claudeutils/worktree/merge.py:233-234`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Description:** When `git merge --no-commit --no-ff` returns 0 (clean merge, no conflicts), the function returns immediately. The staged changes from the `--no-commit` merge are then committed in Phase 4 (`_phase4_merge_commit_and_precommit`), which checks for staged changes. This is correct -- Phase 4 handles the commit regardless. The early return is appropriate because it skips conflict resolution which isn't needed. **Not a bug, design is correct.**

### F6. `_resolve_learnings_md_conflict` line-level dedup can lose ordering context

- **File:** `src/claudeutils/worktree/merge.py:123-130`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Description:** The learnings merge uses set-based line deduplication: `ours_lines = set(ours_content.split("\n"))` then filters theirs lines not in ours. This has two minor issues:
  1. Lines that are identical but appear in different semantic contexts (e.g., `---` separator lines, blank lines) may be incorrectly deduplicated.
  2. The appended theirs-only content preserves theirs ordering but may result in structurally awkward placement (e.g., section headers without their content if some content lines matched ours).

  The design says "Find theirs-only lines (lines in :3 not in :2), append to ours." The implementation matches the design literally. The structural edge cases are acceptable for an automated merge that will be reviewed.

### F7. `_probe_registrations` uses string containment instead of path matching

- **File:** `src/claudeutils/worktree/cli.py:308-309`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** The registration probing checks `str(worktree_path) in parent_list`. This is a substring match on the entire porcelain output. If a path is a prefix of another (e.g., `/tmp/repo-wt/a` and `/tmp/repo-wt/abc`), a check for `/tmp/repo-wt/a` would match both entries. The design says "Use path matching, not grep (more reliable parsing)." The `_parse_worktree_list` function exists and does proper porcelain parsing, but `_probe_registrations` uses raw string containment instead.

### F8. `_check_clean_for_merge` exempt_paths uses substring matching

- **File:** `src/claudeutils/worktree/merge.py:47-49`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** The exemption check `any(p in line for p in exempt_paths)` uses substring matching. For example, `"agents/session.md"` being in `exempt_paths` would also exempt a hypothetical file like `xagents/session.md` or `agents/session.md.bak`. Additionally, `"agent-core"` as an exempt path would match any line containing "agent-core" as a substring, including files like `update-agent-core.py`. In practice these false positives are unlikely given the project structure, but the pattern is fragile.

### F9. `clean_tree` command parses combined output differently from `_check_clean_for_merge`

- **File:** `src/claudeutils/worktree/cli.py:244-259` vs `src/claudeutils/worktree/merge.py:28-71`
- **Axis:** Modularity
- **Severity:** Minor
- **Description:** The `clean_tree` CLI command and `_check_clean_for_merge` in merge.py both implement "check if tree is clean with exemptions" but use different parsing strategies. `clean_tree` concatenates parent + submodule porcelain output and filters on filename suffix, while `_check_clean_for_merge` checks parent and submodule separately with substring matching. The design says shared logic should have single implementations (D4), but these are intentionally different -- `clean_tree` is the general-purpose CLI command, while `_check_clean_for_merge` is merge-specific with the THEIRS strict mode distinction.

### F10. `add_sandbox_dir` writes trailing newline inconsistently

- **File:** `src/claudeutils/worktree/cli.py:98`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Description:** `json.dumps(settings, indent=2, ensure_ascii=False)` does not add a trailing newline. The design doesn't specify this, but it means the settings file won't have a trailing newline, which may trigger linter warnings if settings.local.json is ever linted. This is cosmetic since settings.local.json is gitignored.

### F11. `initialize_environment` silently returns when `just` is not available

- **File:** `src/claudeutils/worktree/cli.py:101-116`
- **Axis:** Conformance (D5)
- **Severity:** Minor
- **Description:** The design (D5) says "If recipe missing: warn, do not fall back." When `just --version` fails (line 105), the function returns silently without printing a warning. The warning is only printed when `just setup` fails (line 115). A user without `just` installed gets no feedback that environment initialization was skipped. The function should print a warning when `just` is not available.

### F12. No test for `focus_session` with continuation-line metadata (plan directory)

- **File:** Tests: `tests/test_worktree_utils.py:163-220`
- **Axis:** Testability / Functional completeness
- **Severity:** Minor
- **Description:** The `focus_session` function extracts `plan_dir` from a `plan:\s*(\S+)` regex in the task metadata (line 73). The test `test_focus_session_section_filtering` includes `plan: plans/feature-x/` in the task entry but the plan directory is on the same line as the task. There's no test verifying that plan directory extraction works when it appears on a continuation line (indented below the task), which is the actual format in real session.md files:
  ```
  - [ ] **Task** -- `command` | sonnet
    - Plan: plans/feature-x/
  ```
  Looking at the regex on line 67, the metadata capture group spans continuation lines. However, `plan:\s*(\S+)` on line 73 would match `Plan: plans/feature-x/` (case-insensitive? No -- `plan:` is lowercase, `Plan:` has uppercase P). **This is a bug**: the regex `r"plan:\s*(\S+)"` won't match `Plan:` in continuation lines where the convention uses title case.

### F13. `plan_dir` regex is case-sensitive but session.md uses title case

- **File:** `src/claudeutils/worktree/cli.py:73`
- **Axis:** Functional correctness
- **Severity:** Major
- **Description:** Line 73: `m := re.search(r"plan:\s*(\S+)", metadata)` searches for lowercase `plan:`. Real session.md entries use `Plan:` with title case (visible in `agents/session.md` and test fixtures like `test_focus_session_section_filtering` line 188: `plan: plans/feature-x/`). The test uses lowercase to match the implementation, but real sessions use `- Plan:` (title case). If the plan directory line is indented (`  - Plan: plans/feature-x/`), the regex won't match because `P` is uppercase. This means `_filter_section` receives `plan_dir=None`, and section filtering falls back to task-name-only matching, potentially missing entries that reference the plan directory but not the task name.

### F14. `_phase4_merge_commit_and_precommit` exit code doesn't distinguish precommit failure from fatal error

- **File:** `src/claudeutils/worktree/merge.py:280-282`
- **Axis:** Error signaling / Conformance
- **Severity:** Minor
- **Description:** The design specifies exit code 1 for "Conflicts unresolved OR precommit failure" and exit code 2 for "Fatal error (branch not found, submodule failure)." The implementation uses `raise SystemExit(1)` for precommit failure, which matches the design. However, if the `just precommit` command itself is not found (FileNotFoundError), the subprocess.run would raise an exception that propagates as an unhandled error, not a controlled exit code 2. The design doesn't explicitly address this case, but it could be considered a fatal error deserving exit code 2.

### F15. `_phase3_merge_parent` calls `git clean -fd` after abort, which may remove unrelated files

- **File:** `src/claudeutils/worktree/merge.py:250`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** After `git merge --abort`, the code runs `git clean -fd` to remove merge debris. The `-fd` flag removes untracked files and directories. If the user happened to have untracked files in the working tree before the merge (which shouldn't happen since Phase 1 checks for clean tree, but only tracked files via `--untracked-files=no`), those files would also be removed. The design specifies this behavior: "Abort: `git merge --abort`, clean debris: `git clean -fd`." The `--untracked-files=no` flag in clean tree checks means untracked files are not blocked at Phase 1, making this a potential data loss path.

### F16. Merge clean tree check uses `--untracked-files=no` — untracked files not blocked

- **File:** `src/claudeutils/worktree/merge.py:41`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** `_check_clean_for_merge` includes `--untracked-files=no` in the git status command, meaning untracked files don't trigger the clean tree gate. Combined with F15's `git clean -fd` on conflict abort, untracked files in the worktree could be silently deleted. The design says "Clean tree validation on BOTH sides" and "Check parent tree + submodule tree are clean" without specifying `--untracked-files=no`. The `clean_tree` CLI command (line 244) does not use this flag, creating an inconsistency between the two clean-tree checks.

### F17. No test for precommit failure path in merge

- **File:** Tests
- **Axis:** Testability
- **Severity:** Minor
- **Description:** `test_merge_precommit_validation` uses `mock_precommit` fixture that always returns success. There is no test verifying that merge exits 1 with "Precommit failed after merge" when precommit fails. The behavior is straightforward (check returncode, print message, exit 1), but the path is untested.

### F18. `_create_session_commit` tempfile context manager misuse

- **File:** `src/claudeutils/worktree/cli.py:154-156`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** The `with` statement on line 154-155 creates a NamedTemporaryFile and immediately exits the context manager (line 156 is outside the `with` block due to indentation). The `delete=False` flag prevents deletion on close, so the file persists. But the `with` statement opens the file, then the context manager closes it immediately, then the code on line 157 uses only `tmp.name` for the `GIT_INDEX_FILE` environment variable. The file is empty at this point (it was never written to) and git's `read-tree` writes to it. This works but the `with` block is misleading -- it looks like the temp file creation should encompass the `try` block. The actual cleanup in `finally` (line 176) is correct.

### F19. `rm` command submodule branch not deleted

- **File:** `src/claudeutils/worktree/cli.py:339-370`
- **Axis:** Functional completeness
- **Severity:** Minor
- **Description:** The `rm` command deletes the parent branch with `git branch -d <slug>` (line 358) but does not delete the corresponding submodule branch. After `_remove_worktrees` removes the submodule worktree, the branch `<slug>` still exists in the agent-core repository. The design says "Branch deletion: Use `-d` flag" but doesn't explicitly address submodule branch cleanup. Over time, this accumulates stale branches in the submodule.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major    | 2 |
| Minor    | 14 |

| Axis | Count |
|------|-------|
| Functional correctness | 4 (F2, F6, F10, F13) |
| Robustness | 4 (F4, F7, F8, F15) |
| Modularity | 2 (F1, F9) |
| Conformance | 2 (F11, F14) |
| Testability | 2 (F12, F17) |
| Functional completeness | 1 (F19) |
| Error signaling | 1 (F16) |

### Major findings requiring attention:

1. **F2** (`_filter_section` continuation line handling): Non-bullet continuation lines of irrelevant entries leak into filtered output. Blocker/Gotcha sections with structured sub-entries will produce incorrect focused sessions.

2. **F13** (`plan_dir` case-sensitive regex): The `plan:\s*` regex won't match title-case `Plan:` used in real session.md entries. This degrades section filtering to task-name-only, potentially missing plan-directory-referenced entries.

### Overall assessment:

The implementation satisfies the design spec at the structural level: sibling container paths (D1), worktree-based submodule (D2), skill-primary architecture (D3), shared utility functions (D4), warn-only env init (D5, with F11 gap), hidden CLI (D6), and task-based mode (D7). The 4-phase merge ceremony is complete and tested. Exit codes conform to spec. Test coverage is thorough across 12 test files.

The two major findings (F2, F13) affect `focus_session` quality -- the focused session may include irrelevant blocker sub-entries and miss plan-directory-referenced entries. These are correctness issues in the filtering logic, not architectural gaps.
