# Test Deliverable Review: handoff-cli-tool (RC4)

Reviewed 20 test files against `plans/handoff-cli-tool/outline.md`.

## Coverage Matrix

| Design Section | Test File(s) | Coverage Assessment |
|---|---|---|
| S-1: Package structure | test_session_commit_cli.py, test_git_cli.py, test_session_integration.py | Registration tested via CliRunner invocation of `_handoff`, `_commit`, `_status`, `_git changes`. Adequate. |
| S-2: `_git()` extraction + submodule discovery | test_git_helpers.py | `_git_ok`, `discover_submodules`, `_is_submodule_dirty`, `git_status` porcelain format, `_is_dirty` with exclude_path. Adequate. |
| S-3: Output and error conventions | test_session_commit_cli.py, test_session_commit_format.py, test_commit_pipeline_errors.py | Exit codes 0/1/2 tested. Structured markdown errors (`**Error:**`, `**Warning:**`), `STOP:` directive, hint stripping. Adequate. |
| S-4: Session.md parser | test_session_parser.py | Status line, completed section, in-tree tasks, worktree tasks, plan_dir extraction, `->` markers, blockers extraction, blank line preservation. Adequate. |
| S-5: Git changes utility | test_git_cli.py | Clean/dirty parent, dirty submodule with prefixed paths, clean submodule omitted. Adequate. |
| H-1: Domain boundaries | test_session_handoff.py, test_session_handoff_cli.py | Status overwrite, completed section write. Other sections preserved. Adequate. |
| H-2: Completed section write mode | test_session_handoff.py | Overwrite, replace accumulated content, empty section, idempotent. Gap: no git-diff-based mode detection tested. See M-1. |
| H-3: Diagnostic output | test_session_handoff_cli.py | Fresh handoff asserts diagnostics. Submodule diagnostics tested. Adequate. |
| H-4: State caching | test_session_handoff.py, test_session_handoff_cli.py | save/load/clear state, resume mode, no-stdin-no-state error. Adequate. |
| C-1: Scripted vet check | test_session_commit.py, test_session_commit_validation.py | No config passes, fresh report passes, unreviewed fails, stale fails with per-file detail. Adequate. |
| C-2: Submodule coordination | test_session_commit_pipeline_ext.py | Four-cell matrix fully covered. Adequate. |
| C-3: Input validation | test_session_commit.py, test_session_commit_cli.py | Clean file error with STOP, amend accepts HEAD files, CleanFileError exits 2. Adequate. |
| C-4: Validation levels | test_session_commit_validation.py | just-lint, no-vet, default calls vet, combined options. Adequate. |
| C-5: Amend semantics | test_session_commit_pipeline_ext.py, test_commit_pipeline_errors.py | Parent amend, submodule amend, amend validation, amend+no-edit. Adequate. |
| ST-0: Worktree-destined tasks | test_status_rework.py, test_session_status.py | Worktree-marked tasks skipped for Next. Both marker types rendered. Adequate. |
| ST-1: Parallel group detection | test_session_status.py, test_status_rework.py | Different plans, single task, shared plan, mixed consecutive, blocker exclusion at unit level. E2e blocker path tested. Adequate. |
| ST-2: Preconditions and degradation | test_session_status.py, test_status_rework.py | Missing session.md exits 2, old format exits 2, old section name rejected. Adequate. |

## Findings

### Critical

None.

### Major

1. **M-1: H-2 committed detection modes not tested through git diff** (test_session_handoff.py:208-268, coverage)
   - The outline (H-2) specifies three write modes keyed on `git diff HEAD -- agents/session.md`: overwrite, append, and auto-strip. All `write_completed` tests operate on bare files without a git repo. The `_init_repo` and `_commit_session` helpers exist in the file but are never used by `write_completed` tests. If the implementation collapses all modes to overwrite (a valid simplification), no test verifies the invariant that overwrite-always produces correct results when the file state differs from HEAD. A test that commits session.md, modifies it, then calls `write_completed` would close this gap.

2. **M-2: `_init_repo` duplicated across 6+ files instead of shared helper** (test_session_commit.py:163, test_session_handoff.py:175, test_session_handoff_cli.py:16, test_session_integration.py:14, test_session_commit_pipeline_ext.py:15, excess)
   - Eight test files define local `_init_repo` functions. `test_commit_pipeline_errors.py` and `test_git_helpers.py` already import from `tests.pytest_helpers.init_repo_at`. The local copies vary: some create and commit a README.md (pipeline_ext), others don't; some use `cwd=`, some use `-C`. Divergent repo initialization is a maintenance hazard and can mask test fragility.

### Minor

1. **m-1: `test_parse_commit_input` parametrized but shares single parse call** (test_session_commit.py:48-73, specificity)
   - Four parametrizations all parse the same fixture. If `parse_commit_input` raises, all four fail simultaneously. The parametrization suggests four independent tests but provides no isolation. A single test asserting all four sections would be more direct.

2. **m-2: Parallel detection cap-at-5 untested** (test_session_status.py, coverage)
   - ST-1 specifies "Cap at 5 concurrent sessions." No test creates 6+ independent tasks to verify the cap.

3. **m-3: `test_parse_commit_blockquote_stripping` incomplete** (test_session_commit.py:155, specificity)
   - Asserts no line starts with `"> "` (with space) but does not check bare `">"` lines. If implementation strips `"> "` but leaves bare `>`, this test passes incorrectly.

4. **m-4: `test_handoff_then_status` does not verify completed section or status line** (test_session_integration.py:60, coverage)
   - The integration test verifies status shows the pending task after handoff but does not verify the completed section was written or the status line updated. Round-trip verification is incomplete.

5. **m-5: `or`-disjunction assertions weaken specificity** (test_session_commit_pipeline.py:40,75, specificity)
   - `assert "foo" in result.output.lower() or "1 file" in result.output` and `assert "Precommit" in result.output or "failed" in result.output` cannot distinguish which condition held. Pre-existing from prior rounds; remains.

6. **m-6: `test_session_status_cli` fixture defined after usage** (test_session_status.py:235 vs :208, quality)
   - `SESSION_FIXTURE` is defined at line 235, 27 lines after the test that first references it. Harms readability.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 6 |

**Delta from RC3:** RC3 had 5M/8m. This round finds 2M/6m.
- RC3 M2 (blockers never passed to detect_parallel) resolved: `test_status_parallel_uses_blockers` now covers e2e path.
- RC3 M4 (SESSION_FIXTURE ordering) downgraded to m-6 (quality, not functional correctness).
- RC3 M5 (or-disjunction assertions) downgraded to m-5 (pre-existing, stable).
- RC3 m8 (worktree import changes) dropped: mechanical, verified correct, no finding.

**Remaining M-1** (H-2 committed detection) is the only substantive coverage gap. The design specifies three modes; tests exercise one. If the implementation correctly simplified to always-overwrite, a single test confirming correctness against committed state would close this.

**Remaining M-2** (_init_repo duplication) is a code quality issue affecting maintainability, not correctness.
