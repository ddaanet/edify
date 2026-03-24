# Code Review: handoff-cli-tool (RC7 Layer 1)

**Date:** 2026-03-24
**Reviewer:** Opus 4.6 [1M]
**Files reviewed:** 26 code files (1733 lines)
**Methodology:** Full-scope review against outline.md design specification

## RC6 Fix Verification

| RC6 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1: `_split_sections` `in_message` flag test | VERIFIED | `test_split_sections_in_message_preserves_headings` at test_session_commit.py:142-159 — asserts only `["Files", "Message"]` sections and `## Not a section` remains in Message body |
| m-1: `git log --oneline -1` confirmation | VERIFIED | test_session_commit_cli.py:39-46 — `subprocess.run(["git", "log", "--oneline", "-1"], ...)` confirms commit created |
| m-2: Submodule assertion tightened | VERIFIED | test_session_handoff_cli.py:234 — `assert "## Submodule: agent-core" in result.output` |
| m-3: Multi-submodule order test | VERIFIED | `test_commit_multi_submodule_order` at test_session_commit_pipeline_ext.py:332 — alpha/beta submodules both committed before parent |
| m-4: Redundant checkbox check removed | VERIFIED | render.py `checkbox` check at line 37 (filter) and line 152 (detect_parallel). No redundant inner-loop check remains in render_pending |
| m-5: `ParsedTask` import aligned | VERIFIED | test_session_status.py:11 — `from claudeutils.session.parse import ParsedTask` (canonical re-export path) |

All 6 RC6 findings verified fixed.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## Carried Forward (not counted)

- `step_reached` vestigial in HandoffState (RC5 m-2, accepted — idempotent replay is safe)
- Pipeline ordering deviation: staging before precommit (RC5 m-3, accepted — required for precommit to see staged state)
- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation, mitigated by section placement)

## Gap Analysis

| Design Requirement | Status |
|---|---|
| S-1: Package structure | Covered — session/ package with cli.py, parse.py, commit.py, commit_gate.py, commit_pipeline.py, handoff/, status/ |
| S-2: `_git()` extraction + submodule discovery | Covered — git.py with `_git`, `discover_submodules`, `_is_submodule_dirty`, `git_status`, `git_diff`, `_is_dirty` |
| S-3: Output and error conventions | Covered — all output to stdout, exit 0/1/2 semantics correct |
| S-4: Session.md parser | Covered — parse.py composes `extract_task_blocks`, `parse_task_line`, `find_section_bounds` |
| S-5: Git changes utility | Covered — git_cli.py with submodule-aware `git_changes()` and `_git changes` CLI |
| H-1: Domain boundaries | Covered — CLI writes status + completed only |
| H-2: Completed section write mode | Covered — uniform overwrite via `_write_completed_section` |
| H-3: Diagnostic output | Covered — unconditional `click.echo` at handoff/cli.py:58 |
| H-4: State caching | Covered — `tmp/.handoff-state.json` with save/load/clear lifecycle |
| C-1: Scripted vet check | Covered — pyproject.toml patterns + agent-core patterns + report discovery/freshness |
| C-2: Submodule coordination | Covered — partition, validate message presence, commit-first with pointer staging |
| C-3: Input validation | Covered — `CleanFileError` with STOP directive, amend-aware via `_head_files` |
| C-4: Validation levels | Covered — orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered — amend, no-edit, message validation, submodule propagation |
| C-Message: EOF semantics | Covered — `in_message` flag in `_split_sections` with regression test |
| ST-0: Worktree-destined tasks | Covered — `worktree_marker is None` check in Next selection |
| ST-1: Parallel detection | Covered — consecutive windows, dependency edges, cap at 5 |
| ST-2: Preconditions | Covered — missing file exit 2, old format exit 2, old section name exit 2 |
| Registration in cli.py | Covered — `_handoff`, `_commit`, `_status`, `_git` all registered (cli.py:155-158) |

## Summary

| Severity | Count | Delta from RC6 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 0 | -1 (RC6 M-1 resolved) |
| Minor | 0 | -5 (all RC6 minors resolved) |

RC6 fixes: 6 of 6 findings verified fixed. All code conforms to design specification. No new findings.

Trend: RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/0m. Clean.
