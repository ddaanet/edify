# Deliverable Review: Code — handoff-cli-tool

**Reviewer:** Opus 4.6 (Layer 1)
**Design reference:** `plans/handoff-cli-tool/outline.md`

## Critical

### CR-1: `_git_commit` ignores non-zero exit code

- **File:** `src/claudeutils/session/commit_pipeline.py:77-84`
- **Axis:** Robustness, error signaling
- **Description:** `_git_commit()` uses `check=False` and returns `result.stdout.strip()` without inspecting `result.returncode`. The calling code in `commit_pipeline()` (line 281-289) unconditionally returns `CommitResult(success=True, ...)`. If `git commit` fails (e.g., nothing staged after validation, hook rejection, lock contention), the pipeline reports success with empty or error-containing output. Same issue in `_commit_submodule()` (line 134-148) — submodule commit failure is silently treated as success.

### CR-2: Submodule committed before validation gate

- **File:** `src/claudeutils/session/commit_pipeline.py:254-273`
- **Axis:** Conformance, robustness
- **Description:** The outline specifies pipeline order: "validate → vet check → precommit → stage → submodule commit → parent commit." The implementation commits submodules (line 256-264) and stages parent files (line 267-268) before running the validation gate (line 271). If precommit or vet check fails after submodule commit, the submodule has an irrevocable commit but the parent doesn't, leaving an inconsistent state. The submodule commit cannot be rolled back without explicit `--amend` or reset.

## Major

### MJ-1: Status command missing session continuation header

- **File:** `src/claudeutils/session/status/cli.py`, `src/claudeutils/session/status/render.py`
- **Axis:** Functional completeness (conformance)
- **Description:** The outline specifies: "Session continuation header: When git tree is dirty, prepend `Session: uncommitted changes — /handoff, /commit`. If any plan-associated task has status review-pending, append `/deliverable-review plans/<name>`." This feature is entirely absent from the implementation. The status command never checks git dirty state and never renders the session continuation header.

### MJ-2: Status command does not query plan lifecycle states

- **File:** `src/claudeutils/session/status/cli.py:31-34`
- **Axis:** Functional completeness (conformance)
- **Description:** The outline pipeline step 2 says: "claudeutils _worktree ls for plan states and worktree info." The implementation populates `plan_states` with empty strings (line 34: `plan_states.setdefault(task.plan_dir, "")`) and passes an empty dict for unscheduled plan discovery (line 60: `render_unscheduled({}, task_plan_dirs)`). Rendered output shows `Plan: <dir> | Status: ` (blank status). Plan lifecycle states are never read from the filesystem.

### MJ-3: Status output format deviates from outline

- **File:** `src/claudeutils/session/status/render.py:8-31`
- **Axis:** Conformance
- **Description:** The outline specifies the first in-tree task should use `▶` marker with command, model, and restart metadata inline, suppressing the separate `Next:` section for single-task cases. The implementation renders a separate `Next:` section (always, even for single-task) using `Next: <name>` format without `▶`. The `render_pending` function renders all in-tree tasks identically with `- <name>` prefix, without distinguishing the first task.

### MJ-4: Dead code — `handoff/context.py` unused

- **File:** `src/claudeutils/session/handoff/context.py`
- **Axis:** Excess, vacuity
- **Description:** `PrecommitResult` and `format_diagnostics()` are defined (45 lines) but never imported or used by the handoff CLI pipeline. The handoff CLI (`cli.py`) runs git status/diff inline (lines 57-72) and formats output directly. These were written for an earlier design where the CLI ran precommit internally, which was removed during checkpoint-4 review. Tests exist for this dead code (`test_session_handoff.py:291-330`) adding to the maintenance burden.

### MJ-5: `git_status()` corrupts first line of porcelain output

- **File:** `src/claudeutils/git.py:84-98`
- **Axis:** Robustness, functional correctness
- **Description:** `git_status()` returns `result.stdout.strip()`. For `git status --porcelain`, the first line may start with a space (e.g., ` M file.py` for unstaged modification). `strip()` removes the leading space, corrupting the XY status code of the first line from ` M` to `M`. Downstream consumer `_prefix_status_lines()` in `git_cli.py` parses `line[:3]` as the status code — the corrupted first line yields `M f` instead of ` M ` plus `file.py`. This is the same class of bug documented in learnings.md ("When parsing git status porcelain format"). The `commit_gate.py:_dirty_files()` correctly avoids this by using raw `result.stdout.splitlines()`.

## Minor

### MN-1: Uncaught `CalledProcessError` from `_stage_files`

- **File:** `src/claudeutils/session/commit_pipeline.py:52-59, 267-268`
- **Axis:** Robustness, error signaling
- **Description:** `_stage_files()` uses `check=True`, so it raises `subprocess.CalledProcessError` on failure. This exception is not caught in `commit_pipeline()`, producing an unhandled traceback rather than a structured `CommitResult` with exit code 1 per S-3. Same issue for `_commit_submodule()` line 121-126 which uses `check=True` for `git add`.

### MN-2: `_fail` duplication across modules

- **File:** `src/claudeutils/git.py:33-39`, `src/claudeutils/worktree/cli.py:66-68`
- **Axis:** Modularity
- **Description:** `_fail()` is defined in `git.py` and duplicated identically in `worktree/cli.py`. The session commands correctly import from `git.py`, but the worktree module retains its local copy. Pre-existing issue, not introduced by this deliverable, but the extraction to `git.py` was an opportunity to remove the duplicate.

### MN-3: `_strip_hints` only filters `hint:` prefix

- **File:** `src/claudeutils/session/commit_pipeline.py:187-189`
- **Axis:** Robustness
- **Description:** The docstring says "Remove git hint/advice lines" but the filter only checks `line.startswith("hint:")`. While git primarily uses the `hint:` prefix, some configurations may produce differently-prefixed advice lines. Low risk since the existing filter covers the common case.

### MN-4: Status `render_pending` omits restart metadata

- **File:** `src/claudeutils/session/status/render.py:34-57`
- **Axis:** Conformance
- **Description:** The outline format shows `Restart: <yes/no>` for in-tree tasks. The `render_pending` function only renders model in parentheses; restart flag is only shown in the separate `Next:` section (via `render_next`). The in-tree listing omits restart information for all tasks except the first.

### MN-5: Plan status line renders with empty value

- **File:** `src/claudeutils/session/status/render.py:54-56`
- **Axis:** Robustness
- **Description:** When `plan_states[task.plan_dir]` is empty string (always, per MJ-2), the output reads `Plan: <dir> | Status: ` with trailing empty value. If plan discovery is deferred, the status should be omitted or show a placeholder.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 5 |
| Minor | 5 |

The core parsing (commit input, handoff input, session.md) and git extraction (S-2, S-5) are well-implemented. The commit gate logic (C-1, C-3, C-5) is solid. The handoff pipeline (H-1 through H-4) works correctly. The critical issues are both in the commit pipeline's error handling — silent success on git commit failure and ordering violation with submodule commits before validation. The major issues are concentrated in the status subcommand, which is missing several outline-specified features.
