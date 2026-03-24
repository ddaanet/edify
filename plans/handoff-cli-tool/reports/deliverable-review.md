# Deliverable Review: handoff-cli-tool (RC7)

**Date:** 2026-03-24
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1733 | -95 | +1638 |
| Test | 20 | +3486 | -59 | +3427 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5230** | **-162** | **+5068** |

### RC6 Finding Verification

| RC6 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1 (`_split_sections` `in_message` test) | FIXED | test_session_commit.py:142-159 — asserts section names `== ["Files", "Message"]` and `## Not a section` in Message body |
| m-1 (`git log` confirmation) | FIXED | test_session_commit_cli.py:39-46 — `subprocess.run(["git", "log", "--oneline", "-1"])` |
| m-2 (submodule assertion tightened) | FIXED | test_session_handoff_cli.py:234 — `"## Submodule: agent-core"` |
| m-3 (multi-submodule order test) | FIXED | test_session_commit_pipeline_ext.py:332-393 — alpha/beta submodules |
| m-4 (redundant checkbox removed) | FIXED | render.py:45 — condition is `first_eligible and task.worktree_marker is None` |
| m-5 (`ParsedTask` import aligned) | FIXED | test_session_status.py:11 — `from claudeutils.session.parse import ParsedTask` |

6 of 6 RC6 findings verified fixed.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Test Quality

1. **m-1: Format test vacuous disjunction** (test_session_commit_format.py:21, vacuity)
   - `assert ":" not in output.split("\n")[0] or "a7f38c2]" in output` — second disjunct is always true by construction (fixture includes that hash). Intended check (no submodule label prefix on first line) is masked.

2. **m-2: Parametrize over shared fixture** (test_session_commit.py:50-75, excess)
   - Four parametrize cases all parse the same `COMMIT_INPUT_FIXTURE`, each checking one field. A single test asserting all fields would be equivalent. Parametrization suggests independence that doesn't exist.

3. **m-3: `ParsedTask` import path inconsistency** (test_status_rework.py:13, consistency)
   - Imports from `claudeutils.validation.task_parsing` while test_session_status.py:11 and test_session_parser.py:7 use `claudeutils.session.parse` (the S-4 public interface). Residual from RC6 m-5 fix scope.

4. **m-4: No test for `just-lint` + `no-vet` combination** (test_session_commit_validation.py, completeness)
   - Design C-4 specifies orthogonal options including combined `just-lint` + `no-vet`. Individual option tests exist; the specific combination has no dedicated test. Implicit coverage via orthogonality.

5. **m-5: Imprecise "clean" assertion** (test_git_cli.py:83, specificity)
   - `assert "clean" in result.output.lower()` matches any output containing "clean." Implementation emits `"Tree is clean."` — a pinned assertion would catch format regressions.

6. **m-6: Imprecise "Git status" assertion** (test_session_handoff_cli.py:90, specificity)
   - `assert "Git status" in result.output` — substring of actual `"**Git status:**"`. Adequate but not pinned.

### Carried Forward (not counted)

- `step_reached` vestigial (RC5 m-2, accepted — idempotent replay is safe)
- Pipeline ordering deviation: staging before precommit (RC5 m-3, accepted — required for precommit to see staged state)
- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation)
- `SESSION_FIXTURE` defined after first usage (pre-existing quality issue)

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit 0/1/2 |
| S-4: Session.md parser | Covered | parse.py composes existing functions |
| S-5: Git changes utility | Covered | git_cli.py with submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Uniform overwrite |
| H-3: Diagnostic output | Covered | Unconditional after RC5 fix |
| H-4: State caching | Covered | step_reached vestigial but safe |
| C-1: Scripted vet check | Covered | Patterns + reports with cwd propagation |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| C-Message: EOF semantics | Covered | in_message flag with regression test |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill Step 7 precommit gate |

## Summary

| Severity | Count | Delta from RC6 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 0 | -1 (RC6 M-1 resolved) |
| Minor | 6 | +1 (RC6: 5m resolved, 6 new m) |

**RC6 fixes:** 6 of 6 findings verified fixed. All Majors resolved.

**New minors:** Test specificity (m-1, m-5, m-6), style (m-2, m-3), and one design-combination gap (m-4). All are at the test-quality level — no code or behavioral issues found.

**Trend:** RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/6m. Zero Critical and Major findings across two consecutive rounds. Minor count stable at test-quality level.
