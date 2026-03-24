# Code Deliverable Review: handoff-cli-tool (RC9)

## RC8 Finding Verification

| Finding | Status | Evidence |
|---------|--------|----------|
| m-3: Empty Files section not rejected | FIXED | commit.py:116-118 — `if not files: raise CommitInputError("## Files section is empty")` added after the `files is None` check |
| m-4: ci.message or "" fallback | FIXED | commit_pipeline.py:334 — `assert ci.message is not None or no_edit` replaces dead `or ""` fallback; upstream guard at line 262 returns error if `ci.message is None and not no_edit` |
| m-5: _strip_hints fragile detection | FIXED | commit_pipeline.py:203-208 — now distinguishes tab/double-space (continuation, filtered) from single-space (passes through via `result.append(line)`, `prev_was_hint` stays True so subsequent double-space lines still filtered) |
| m-6: ParsedTask import in render.py | FIXED | render.py:7 — `from claudeutils.session.parse import ParsedTask` (re-exported from parse.py:13,21 via `claudeutils.validation.task_parsing`) |

All 4 code-relevant RC8 findings verified fixed.

## New Findings

### Critical

None

### Major

**M-1: `vet_check` path existence checked against process cwd, not repo cwd** — commit_gate.py:159
- Axis: robustness
- `matched_paths = [Path(f) for f in matched if Path(f).exists()]` resolves relative to the process working directory, not the `cwd` parameter passed to `vet_check`. When `cwd` differs from process cwd (e.g., tests, submodule contexts), the existence check evaluates against the wrong directory. Should be `(Path(cwd or ".") / f).exists()`. The same `cwd` is correctly threaded to `_load_review_patterns(cwd)`, `_find_reports(cwd)`, and `_dirty_files(cwd)` — this line is the exception.
- Impact: When all matched files are relative paths that don't exist at process cwd, `matched_paths` becomes empty and `vet_check` returns `passed=True`, silently skipping the freshness check.

### Minor

**m-1: `step_reached` stored but never read during resume** — handoff/pipeline.py:20, handoff/cli.py:46-52
- Axis: conformance (H-4)
- Carried from RC8 m-2. `HandoffState.step_reached` is set to `"write_session"` but the resume path re-runs the full pipeline regardless. Functionally safe (writes are idempotent), but the field is vestigial — either honor it or remove it.

**m-2: `_AGENT_CORE_PATTERNS` hardcoded** — commit_gate.py:138
- Axis: modularity
- Carried from RC8 m-4 (reworded). Hardcoded `["agent-core/bin/**", "agent-core/skills/**/*.sh"]` will break if the submodule is renamed. Outline C-1 explicitly defers config model for submodule patterns.

**m-3: `_git_output` in commit_gate.py lacks porcelain warning** — commit_gate.py:31-43
- Axis: robustness
- `_git_output` strips stdout like `git.py:_git`, but unlike `_git` it has no docstring warning about porcelain format destruction. Currently only used for `diff-tree` (safe to strip), but the missing warning invites misuse.

**m-4: `format_commit_output` trailing element when parent_output is empty** — commit_pipeline.py:234
- Axis: functional correctness
- `parts.append(_strip_hints(parent_output))` unconditionally appends the parent output. When `parent_output` is empty string (which shouldn't happen in normal flow since parent commit always produces output), this appends an empty element, producing a trailing newline in the joined result.

## Summary

0 critical, 1 major, 4 minor
