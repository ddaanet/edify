# Deliverable Review: handoff-cli-tool (RC4)

**Date:** 2026-03-23
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1621 | -95 | +1526 |
| Test | 20 | +3381 | -16 | +3365 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5013** | **-119** | **+4894** |

### RC3 Finding Verification

| RC3 Finding | Status |
|-------------|--------|
| F-1 (M): Parallel detection ignores blockers | FIXED — `data.blockers` wired at cli.py:99 |
| F-2 (M): Stale vet lacks file detail | FIXED — `_newest_file` helper, per-file timestamps |
| F-3 (m): Duplicate `_fail` in worktree/cli.py | FIXED — removed, imports from git.py |
| F-4 (m): ▶ format deviates from design | Open — see m-3 |
| F-5 (m): Handoff parser strips blank lines | FIXED — both parsers preserve blanks |
| F-6 (m): Double read in status CLI | FIXED — content passed via kwarg |
| F-7 (m): Substring match for old section name | FIXED — uses `re.search` + `re.MULTILINE` |
| F-8 (m): `_strip_hints` incomplete | Open — see m-4 |

All RC3 Majors resolved. 2 of 6 RC3 Minors remain open.

## Critical Findings

None.

## Major Findings

1. **M-1: H-2 committed detection not tested against git state** (test_session_handoff.py, coverage)
   - Design H-2 specifies three write modes keyed on `git diff HEAD -- agents/session.md`. Implementation validly collapses to always-overwrite. No test verifies this invariant against committed state — all `write_completed` tests operate on bare files without a git repo. A single test that commits session.md, modifies it, then calls `write_completed` would confirm the simplification produces correct results.

2. **M-2: `_init_repo` duplicated across 6+ test files** (tests/test_session_*.py, excess)
   - Local `_init_repo` variants in test_session_commit.py, test_session_handoff.py, test_session_handoff_cli.py, test_session_integration.py, test_session_commit_pipeline_ext.py, test_session_commit_validation.py. `tests/pytest_helpers.py` exports `init_repo_at` which some files already use. Variants diverge (cwd vs -C, README vs empty commit). Maintenance hazard.

## Minor Findings

### Conformance

1. **m-1: HandoffState missing `step_reached` field** (session/handoff/pipeline.py:14-19)
   - Design H-4 specifies `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}` with values `"write_session"` | `"diagnostics"`. Implementation has only `input_markdown` and `timestamp`. The pipeline replays fully on resume (correct due to idempotent operations) but doesn't match spec.

2. **m-2: No ANSI color in `_status` output** (session/status/render.py)
   - Design says "ANSI-colored structured text." Implementation produces plain text only. Affects human usability for the direct invocation display path.

3. **m-3: ▶ line format deviates from design** (session/status/render.py:44)
   - Design: `▶ <task> (<model>) | Restart: <yes/no>` with command on separate indented line. Implementation: `▶ <task> — \`<cmd>\` | <model> | restart: <restart>` (inline, lowercase). Denser format, arguably better for terminal.

4. **m-4: `_strip_hints` only filters `hint:` and `advice:` prefixed lines** (session/commit_pipeline.py:187-189)
   - Git hint output includes indented continuation lines. Low impact — hints rare in commit output.

### Test Quality

5. **m-5: Parallel cap-at-5 untested** (test_session_status.py)
   - Design ST-1: "Cap at 5 concurrent sessions." No test creates 6+ independent tasks to verify.

6. **m-6: `or`-disjunction assertions weaken specificity** (test_session_commit_pipeline.py:40,75)
   - `assert "foo" in output or "1 file" in output` cannot distinguish which held. Pre-existing.

7. **m-7: Integration test `test_handoff_then_status` incomplete** (test_session_integration.py:60)
   - Verifies status shows pending task after handoff but does not check completed section or status line update.

### Scope

8. **m-8: `.gitignore` and `.claude/settings.local.json` outside design scope** (configuration)
   - Incidental cleanup attributed to this plan. Functionally correct, benign.

9. **m-9: worktree/cli.py:311 hardcodes "agent-core"** (worktree/cli.py:311)
   - Design S-2: "Replaces -C agent-core literals with iteration over discovered submodules." New session code uses `discover_submodules()`. Pre-existing worktree caller still hardcodes. Not a regression — pre-existing.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with all specified modules |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit codes, `**Header:** content` |
| S-4: Session.md parser | Covered | parse.py composes existing functions |
| S-5: Git changes utility | Covered | git_cli.py with `_git changes` command |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered (simplified) | Always-overwrite, test gap (M-1) |
| H-3: Diagnostic output | Covered | git_changes() after writes |
| H-4: State caching | Covered (partial) | Missing step_reached (m-1) |
| C-1: Scripted vet check | Covered | pyproject.toml patterns, report discovery |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | just-lint/no-vet orthogonal options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| ST-0: Worktree-destined tasks | Covered | ▶ skips worktree-marked tasks |
| ST-1: Parallel detection | Covered | Blockers wired, consecutive windows, cap |
| ST-2: Preconditions | Covered | Missing file=exit 2, old format=exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill has precommit gate (pre-existing) |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 9 |

**Delta from RC3:** RC3 had 2M+6m (code) + 5M+8m (test) + 0M+2m (prose). This round: 2M+9m total. All RC3 code Majors resolved. Test Majors reduced from 5 to 2. Remaining Majors are a test coverage gap (H-2 committed detection) and test helper duplication.
