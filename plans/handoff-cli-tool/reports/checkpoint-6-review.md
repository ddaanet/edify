# Review: Phase 6 Checkpoint — Commit Pipeline

**Scope**: Cycles 6.1–6.6: staging, submodule coordination, amend semantics, validation levels, output formatting, CLI wiring
**Date**: 2026-03-21
**Mode**: review + fix

## Summary

Phase 6 delivers the full commit pipeline with submodule coordination, amend semantics, validation levels, and CLI wiring. Tests pass (19/19) pre-fix; all 19 pass post-fix with full suite at 1751/1752 (1 xfail). Five correctness issues found: `validate_files` (C-3) never called from the pipeline; `format_commit_output` defined and tested but bypassed; `_dirty_files` used bare `--porcelain` (collapses untracked directories, masking individual file paths); vet failure output used wrong header and omitted file list; orphan-submodule warning text didn't match the design spec.

**Overall Assessment**: Needs Minor Changes (post-fix: Ready)

## Issues Found

### Critical Issues

1. **`validate_files` (C-3) not called from `commit_pipeline`**
   - Location: `src/claudeutils/session/commit_pipeline.py`, `commit_pipeline()`
   - Problem: `validate_files` is implemented in `commit_gate.py` and tested in `test_session_commit.py`, but never imported or called from `commit_pipeline`. The pipeline stages and commits clean (unmodified) files without error, bypassing the STOP directive for caller-model divergence.
   - Fix: Import and call `validate_files` after submodule partitioning — parent files against parent cwd, submodule files against each submodule's cwd. Submodule files must be validated in the submodule repo context because `git status --porcelain -u` in the parent shows the submodule pointer, not individual files within it.
   - **Status**: FIXED

2. **`_dirty_files` uses bare `--porcelain` (untracked directories collapse individual files)**
   - Location: `src/claudeutils/session/commit_gate.py`, `_dirty_files()`
   - Problem: `git status --porcelain` reports untracked files as `?? dir/` (the directory), not `?? dir/file.py`. `validate_files(["dir/file.py"])` then fails to find the file in the dirty set, incorrectly raising `CleanFileError` for new untracked files.
   - Fix: Use `git status --porcelain -u` to list individual untracked files instead of parent directories.
   - **Status**: FIXED

3. **`format_commit_output` not used in `commit_pipeline`**
   - Location: `src/claudeutils/session/commit_pipeline.py`, `commit_pipeline()`
   - Problem: `format_commit_output` is defined (line 186) and tested (Cycle 6.5), but `commit_pipeline` assembles output manually with a raw `output_parts` list. This bypasses hint-stripping on the parent commit output and produces inconsistent formatting.
   - Fix: Replace the manual `output_parts` assembly with a call to `format_commit_output(submodule_outputs=..., parent_output=..., warnings=...)`.
   - **Status**: FIXED

### Major Issues

1. **Vet failure output format doesn't match design**
   - Location: `src/claudeutils/session/commit_pipeline.py`, `_validate()`, lines 171-176
   - Problem: Design specifies `**Vet check:** unreviewed files\n- src/auth.py` and `**Vet check:** stale report`. Implementation outputs `**Vet:** <detail>` — wrong header (`Vet` vs `Vet check`), and the unreviewed case doesn't include the file list.
   - Suggestion: Use `**Vet check:**` header. For `reason == "unreviewed"`, append the file list. For `reason == "stale"`, use `stale report` label with `stale_info` detail lines.
   - **Status**: FIXED

2. **Orphan-submodule warning text doesn't match design**
   - Location: `src/claudeutils/session/commit_pipeline.py`, lines 228-232
   - Problem: Warning message is `## Submodule {path} has no matching files` — embeds a markdown heading in the warning body. Design specifies: `Submodule message provided but no changes found for: {path}. Ignored.`
   - Suggestion: Change to match design output spec.
   - **Status**: FIXED

### Minor Issues

_None._

## Fixes Applied

- `src/claudeutils/session/commit_gate.py:44` — changed `git status --porcelain` to `git status --porcelain -u` so untracked files are listed individually rather than collapsed to directory entries
- `src/claudeutils/session/commit_pipeline.py:11` — added `CleanFileError, validate_files` to import from `commit_gate`
- `src/claudeutils/session/commit_pipeline.py:227–236` — added submodule-aware `validate_files` call after partitioning: parent files validated in parent cwd, each submodule's files in their submodule cwd
- `src/claudeutils/session/commit_pipeline.py:169–182` — fixed vet failure output: `**Vet check:**` header (was `**Vet:**`), unreviewed case includes file list, stale case uses `stale report` label
- `src/claudeutils/session/commit_pipeline.py:248–252` — fixed orphan warning message to match design spec (`Submodule message provided but no changes found for: {path}. Ignored.`)
- `src/claudeutils/session/commit_pipeline.py:254–289` — refactored output assembly: `submodule_outputs` dict fed to `format_commit_output` instead of raw `output_parts` list; parent output, submodule outputs, and warnings all routed through `format_commit_output` for hint-stripping and consistent structure

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| C-1: Scripted vet check | Satisfied | `vet_check()` called in `_validate()` |
| C-2: Submodule coordination (4-cell matrix) | Satisfied | `_partition_by_submodule`, `_commit_submodule`, warning for orphan, error for missing message |
| C-3: Input validation (clean files) | Satisfied (post-fix) | `validate_files` called after partition, per-repo |
| C-4: Validation levels (just-lint/no-vet) | Satisfied | `_validate()` branches on `just-lint` option |
| C-5: Amend semantics | Satisfied | `--amend` passed through; `validate_files(amend=amend)` propagated |
| S-3: Structured stdout output | Satisfied | `commit_pipeline` returns `CommitResult.output` |
| S-3: Vet check output format | Satisfied (post-fix) | `**Vet check:**` header with file list |
| S-3: Warning format | Satisfied (post-fix) | Matches design warning template |
| `_dirty_files` untracked files | Satisfied (post-fix) | `-u` flag lists individual files, not directories |
| CLI registration (`_commit`) | Satisfied | `cli.py:156` `cli.add_command(commit_cmd, "_commit")` |

---

## Positive Observations

- `_partition_by_submodule` cleanly handles the four-cell submodule matrix
- `_commit_submodule` correctly stages the submodule pointer in the parent after committing
- `_strip_hints` is well-targeted — filters only `hint:`-prefixed lines
- `test_commit_amend_validation` directly tests the amend-accepts-HEAD-files contract
- Test helper `_init_repo_with_submodule` is thorough: origin repo, parent, submodule add, and per-repo git identity setup
- Validation levels (just-lint, no-vet, combined) tested with mock call-count assertions — verifies routing, not just success
