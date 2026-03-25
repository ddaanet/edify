# Code Review: handoff-cli-tool (RC11)

## Summary

Full-scope review of 26 code files (+1751/-96 lines) against outline.md design specification. Evaluated on all code-specific axes: conformance, functional correctness, functional completeness, vacuity, excess, robustness, modularity, testability, idempotency, error signaling.

## Critical Findings

None.

## Major Findings

**M-1** `session/handoff/pipeline.py:89-100` — conformance, functional completeness — H-2 committed detection not implemented. Design specifies three write modes based on `git diff HEAD -- agents/session.md`:
- No diff -> Overwrite
- Old removed, new present -> Append
- Old preserved with additions -> Auto-strip committed content, keep new additions

Implementation collapses all three into unconditional overwrite via `_write_completed_section`. The docstring acknowledges the three modes exist but claims they all produce the same result. This is incorrect: append mode should preserve existing uncommitted content and add new content; auto-strip should keep new additions while stripping committed content. Only the overwrite case matches the current behavior.

**M-2** `session/handoff/pipeline.py:14-19` — conformance, functional completeness — H-4 `step_reached` field missing from `HandoffState`. Design specifies state file contents as `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}` with values `"write_session"` | `"diagnostics"`. Implementation stores only `input_markdown` and `timestamp`. The resume path (cli.py:52) re-executes from the beginning rather than resuming from `step_reached`. If a crash occurs after `overwrite_status` but before `write_completed`, resume will re-overwrite the status (idempotent) but also re-write completed (safe since it's an overwrite). If crash occurs after `write_completed` but before diagnostics, resume re-executes both writes (idempotent since both are overwrites). While functionally safe given the current overwrite-only behavior, this deviates from the design specification.

## Minor Findings

### Conformance

**m-1** `validation/task_parsing.py:21` — S-4/ST-0 `→ wt` marker not parseable. `WORKTREE_MARKER_PATTERN` matches only `` → `slug` `` (backtick-wrapped alphanumeric slug). The design specifies `→ wt` (no backticks) as a distinct marker for tasks destined for worktree but not yet branched. Tasks with `→ wt` in session.md will have `worktree_marker = None`, causing them to appear as regular tasks in status output and be eligible for `Next:` selection — violating ST-0.

**m-2** `session/commit_pipeline.py:276-282` — S-3 exit code semantics — Missing submodule message (C-2 "files in Files, no Submodule section") returns `CommitResult(success=False)` which exits 1 (pipeline error). Per S-3, this is input validation (malformed caller input) and should exit 2. The caller provided submodule-prefixed files without the corresponding `## Submodule` section.

**m-3** `session/commit_pipeline.py:263-267` — error signaling — `_validate_inputs` returns `CommitResult(success=False, output="**Error:** No commit message provided")` for missing message, yielding exit 1. The parser (`commit.py:129-131`) already catches this case with `CommitInputError("Missing required section: ## Message")` yielding exit 2. Redundant check that would only trigger if `parse_commit_input` is bypassed. If kept, should exit 2 (validation error).

### Robustness

**m-4** `session/commit_pipeline.py:193-213` — `_strip_hints` continuation logic has a dead branch. Lines 206-208: when `prev_was_hint` is True and a line starts with a single space followed by a non-space, the code sets `prev_was_hint = True` and appends the line. The comment says "single-space: pass through but keep hint context" but this means a single-space-indented line after a hint is both kept in output AND treated as a hint continuation (subsequent continuation lines after it would also be filtered). The intent is ambiguous.

**m-5** `session/commit_gate.py:51-68` — `_dirty_files` uses `-u` flag for untracked file expansion. On repositories with many untracked files, this could be slow. Not a correctness issue but a performance consideration.

**m-6** `session/handoff/cli.py:60-61` — `git_changes()` is called for diagnostics output even when the tree is clean. The function always runs `git status --porcelain` and `git diff HEAD` for parent and each submodule. Minor unnecessary work when everything is committed.

### Functional Correctness

**m-7** `session/status/render.py:105-127` — `_build_dependency_edges` uses text-search in concatenated blocker content. If a task name like "Fix" appears as a substring in unrelated blocker text (e.g., "Fixed in prior session"), two tasks sharing common words would be falsely linked. Overly conservative (prevents safe parallelism) but never incorrectly enables unsafe parallelism.

**m-8** `session/status/cli.py:67` — `list_plans(Path("plans"))` uses relative path. If process cwd differs from project root, resolves to wrong directory. Consistent with other relative-path assumptions in the status command but not defensively coded.

### Testability

**m-9** `session/commit_pipeline.py:22-37,40-55` — `_run_precommit` and `_run_lint` have comment "Patchable in tests" but use module-level functions. Test patching works via `monkeypatch.setattr` but the design note suggests these were intended to be more formally patchable (e.g., via dependency injection or protocol). Minor — current approach works.

### Style

**m-10** `session/commit_gate.py:31-48` — `_git_output` duplicates `git.py:_git()` functionality. Both run a git command and return stripped stdout. The commit_gate module defines its own local version to avoid importing from `git.py`. This creates two functions with identical semantics that could drift independently.

## Notes

- S-1 package structure conforms to design — `session/` subpackage with `cli.py`, `parse.py`, `commit.py`, `commit_gate.py`, `commit_pipeline.py`, `handoff/`, `status/`. Minor deviation: `handoff.py` is a subpackage (`handoff/`) rather than a single module, and `status.py` is similarly split into `status/cli.py` + `status/render.py`. Reasonable modularity improvement over the flat design.
- S-2 `_git()` extraction to `git.py` is complete. Worktree module imports from `claudeutils.git`. Submodule discovery via `git submodule status` is properly dynamic.
- S-3 output conventions are correctly followed: all session subcommands output to stdout, exit codes are semantic (0/1/2), no stderr usage.
- S-5 `_git changes` utility is implemented and registered. Clean tree output is "Tree is clean." rather than the design's phrasing "output says so" (implementation choice, conformant).
- C-1 vet check correctly loads patterns from `pyproject.toml`, includes `_AGENT_CORE_PATTERNS` hardcoded (deferred per outline), discovers reports via glob.
- C-2 four-state submodule matrix is implemented: files+message -> commit submodule first; files only -> stop (needs message); message only -> warning (ignored); neither -> parent-only.
- C-3 input validation with STOP directive is correctly implemented via `CleanFileError`.
- C-4 validation levels are orthogonal: `just-lint` and `no-vet` options work independently and in combination.
- C-5 amend semantics correctly use `diff-tree` for HEAD file check, propagate `--amend` to both submodule and parent when submodule files present, enforce `no-edit` requires `amend`.
- ST-2 missing session.md and old format both produce fatal error exit 2, conformant.
- Error messages follow cli.md conventions: facts only, STOP for data-loss risk, no suggestions.
- `tests/pytest_helpers.py` provides well-structured test infrastructure with `init_repo_at`, `init_repo_minimal`, `create_submodule_origin`, `add_submodule`.
- `planstate/aggregation.py` and `recall_cli/cli.py` changes are correctly scoped: aggregation removes duplicated `_is_dirty` and uses `extract_plan_order`; recall_cli imports `_fail` from new location.
- Worktree module files correctly updated imports to `claudeutils.git`.

## Severity Summary

0 Critical, 2 Major, 10 Minor
