# Deliverable Review: handoff-cli-tool (RC9)

**Date:** 2026-03-24
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1738 | -95 | +1643 |
| Test | 20 | +3529 | -59 | +3470 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5278** | **-162** | **+5116** |

### RC8 Finding Verification

| RC8 Finding | Status | Evidence |
|-------------|--------|----------|
| m-1: Bare `pytest.raises` without match (test_session_commit.py:101) | FIXED | test_session_commit.py:101 — `pytest.raises(CommitInputError, match="no-edit contradicts")` |
| m-2: Heading not verified in handoff parse test (test_session_handoff.py:47) | FIXED | test_session_handoff.py:47 — `assert any("**Handoff CLI tool design" in line ...)` |
| m-3: Empty `## Files` section not rejected (commit.py) | FIXED | commit.py:116-118 — `if not files: raise CommitInputError("## Files section is empty")` after `files is None` check |
| m-4: `ci.message or ""` fallback masks unreachable state (commit_pipeline.py:334) | FIXED | commit_pipeline.py:334 — `assert ci.message is not None or no_edit` replaces `or ""` |
| m-5: `_strip_hints` fragile continuation detection (commit_pipeline.py:203-208) | FIXED | commit_pipeline.py:203-208 — single-space passes through, `prev_was_hint` stays True for subsequent filtering |
| m-6: `ParsedTask` import from wrong module in render.py:7 | FIXED | render.py:7 — `from claudeutils.session.parse import ParsedTask` |

6 of 6 RC8 findings verified fixed.

## Critical Findings

None.

## Major Findings

**M-1: `vet_check` path existence checked against process cwd, not `cwd` parameter** — commit_gate.py:159
- Axis: robustness (code)
- `matched_paths = [Path(f) for f in matched if Path(f).exists()]` resolves relative paths against the process working directory, not the `cwd` parameter passed to `vet_check`. The same `cwd` is correctly threaded to `_load_review_patterns(cwd)`, `_find_reports(cwd)`, and `_dirty_files(cwd)` — line 159 is the exception.
- Impact: When `cwd` differs from process cwd (test fixtures, submodule contexts), `matched_paths` may be empty — `vet_check` returns `passed=True`, silently bypassing the freshness check. Fix: `(Path(cwd or ".") / f).exists()`.
- Layer 2 confirmation: `commit_pipeline.py:176` calls `vet_check(ci.files, cwd=cwd)` with `cwd` propagated from the pipeline entry point — the bug is in the gate, not the caller.

## Minor Findings

### Test Specificity

1. **m-1: Bare `pytest.raises(CleanFileError)` without match** (tests/test_session_commit.py:257, specificity)
   - `test_validate_files_amend` second raises block uses `pytest.raises(CleanFileError)` without `match=`. Passes on any CleanFileError — does not distinguish the "amend but not in HEAD" variant from the standard clean-file variant.

2. **m-2: Bare `pytest.raises(SessionFileError)` without match** (tests/test_session_parser.py:147, specificity)
   - `test_parse_session_missing_file` catches any `SessionFileError`. A `match="not found"` or similar would pin the expected failure reason.

3. **m-3: Bare `pytest.raises(subprocess.CalledProcessError)` without match** (tests/test_commit_pipeline_errors.py:26, specificity)
   - `test_git_commit_raises_on_failure` catches any `CalledProcessError`. Exit code check or returncode match would tighten the expected failure mode.

### Test Vacuity

4. **m-4: Redundant `len(...) > 0` assertion** (tests/test_session_handoff.py:45, vacuity)
   - `assert len(result.completed_lines) > 0` is redundant — the `any(...)` assertions on lines 46-47 already imply non-empty.

5. **m-5: Redundant `len(...) > 0` assertion** (tests/test_session_parser.py:57, vacuity)
   - Same pattern as m-4. The `any("Extracted git helpers" ...)` assertion on line 58 already implies non-empty.

### Test Conformance

6. **m-6: Handoff fixture uses bold-colon format, not `### ` headings** (tests/test_session_handoff.py:31, conformance)
   - `HANDOFF_INPUT_FIXTURE` line 31 uses `**Handoff CLI tool design (Phase A):**` (bold-colon). outline.md:75 specifies "Completed entries use `### ` headings (standard markdown nesting), not bold-colon format." The primary fixture should match the specified canonical input format.

### Code Robustness

7. **m-7: `step_reached` stored but never read during resume** (src/claudeutils/session/handoff/pipeline.py:20, conformance H-4)
   - Carried from RC8 m-2. `HandoffState.step_reached` is set but the resume path re-runs the full pipeline regardless. Functionally safe (writes are idempotent), but the field is vestigial. Either honor it or remove it.

8. **m-8: `_AGENT_CORE_PATTERNS` hardcoded submodule name** (src/claudeutils/session/commit_gate.py:138, modularity)
   - Hardcoded `["agent-core/bin/**", "agent-core/skills/**/*.sh"]` breaks if submodule is renamed. outline.md C-1 explicitly defers config model for submodule patterns — carried forward as acknowledged.

9. **m-9: `_git_output` lacks porcelain-safety docstring warning** (src/claudeutils/session/commit_gate.py:31-43, robustness)
   - `_git_output` strips stdout like `git.py:_git`, but unlike `_git` has no warning that `.strip()` destroys porcelain format. Currently safe (only used for `diff-tree`), but the omission invites misuse.

10. **m-10: `format_commit_output` unconditional parent append** (src/claudeutils/session/commit_pipeline.py:234, functional correctness)
    - `parts.append(_strip_hints(parent_output))` appends unconditionally. If `parent_output` is empty (edge case — parent commit normally produces output), a trailing empty element joins with a spurious newline. Low-probability but defensive guard would be cleaner.

### Carried Forward (not counted)

- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation)
- `SESSION_FIXTURE` defined after first usage in test_session_status.py (pre-existing style issue)
- Pipeline ordering: staging before precommit (RC5 m-3, accepted — required for precommit to see staged state)
- Skill integration "(future)" for _commit/_handoff/_status (tracked as separate worktree task "Skill-CLI integration")

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit 0/1/2 |
| S-4: Session.md parser | Covered | parse.py |
| S-5: Git changes utility | Covered | git_cli.py with submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Uniform overwrite |
| H-3: Diagnostic output | Covered | Unconditional after writes |
| H-4: State caching | Covered | step_reached vestigial but safe |
| C-1: Scripted vet check | Partial | Patterns + reports — cwd bug in freshness check (M-1) |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| C-Message: EOF semantics | Covered | in_message flag |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill Step 7 precommit gate |

## Summary

| Severity | Count | Delta from RC8 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 1 | +1 |
| Minor | 10 | +4 (RC8: 6m resolved, 10 new m) |

**RC8 fixes:** 6 of 6 findings verified fixed.

**New major:** vet_check path existence bug (M-1) — cwd not used for `Path(f).exists()` at commit_gate.py:159. Silently bypasses freshness check when process cwd differs from repo cwd.

**New minors:** 3 bare `pytest.raises` without `match=` (same class as prior rounds), 2 redundant `len > 0` assertions, 1 fixture format/spec mismatch, 4 code robustness items.

**Trend:** RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/6m → RC8 0C/0M/6m → RC9 0C/1M/10m. The M-1 vet_check cwd bug is a regression — the similar cwd threading pattern exists correctly in every other call site in commit_gate.py.
