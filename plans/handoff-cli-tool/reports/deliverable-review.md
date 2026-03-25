# Deliverable Review: handoff-cli-tool (RC13)

**Date:** 2026-03-25
**Methodology:** agents/decisions/deliverable-review.md
**Review type:** Full-scope (no delta-scoping per learnings)
**Layers:** L1 (3 opus agents: code, test, prose+config) + L2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1900 | -97 | +1803 |
| Test | 21 | +3901 | -60 | +3841 |
| Agentic prose | 2 | +10 | -10 | +0 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **51** | **+5813** | **-169** | **+5644** |

### RC12 Critical Verification

| RC12 Finding | Status | Evidence |
|-------------|--------|----------|
| C-1: CommitInputError uncaught in commit_cmd | **FIXED** | cli.py:33-34 catches CommitInputError; test_commit_cli_submodule_missing_message_exits_2 exercises full path |

C-1 fix satisfies S-3 on all three axes:
- **Output channel:** `_fail()` → `click.echo` → stdout
- **Output format:** `f"**Error:** {e}"` — structured markdown
- **Exit code:** `code=2` — input validation

Propagation path verified: `_validate_inputs` (commit_pipeline.py:267,277) raises `CommitInputError` → `commit_pipeline()` does not catch → `commit_cmd` except at line 33 catches → `_fail()` exits 2. Test uses real git submodule setup, exercises full CLI pipeline, asserts exit code + output format + error message content.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

All 22 minors carried from RC12. No new findings.

### Code (7)

**m-1** `handoff/pipeline.py:203,228` — functional correctness — Append and autostrip modes strip blank lines (`if line.strip()`) from current section. Loses inter-group markdown spacing.

**m-2** `handoff/pipeline.py:206-219` — modularity — Autostrip re-executes `_find_repo_root` + `git show HEAD:` already done in `_detect_write_mode`.

**m-3** `status/cli.py:60-65` — robustness — Old-format detection compares raw task line count against parsed count. Malformed lines produce misleading "Old-format" error.

**m-4** `commit_gate.py:66` — functional correctness — `len(line) > 3` guard in `_dirty_files()`. No practical impact (git never produces empty paths).

**m-5** `handoff/pipeline.py:173-178` — robustness — `_detect_write_mode` stripped-line comparison. Different indentation → false match after `.strip()`. Edge case.

**m-6** `handoff/cli.py:70` — functional correctness — Empty `git_changes()` produces empty fenced code block in diagnostics.

**m-7** `handoff/pipeline.py:115-140,170` — robustness — `splitlines(keepends=True)` preserves trailing newlines but mode detection uses `==` (newline-sensitive) while writers use `.splitlines()` (newline-insensitive).

### Test (10)

**m-8** `test_session_status.py:280` — conformance — SESSION_FIXTURE defined after first usage (line 253).

**m-9** `test_session_commit_pipeline.py:108-125` — specificity — Generic assertion words ("continuation", "other line").

**m-10** `test_planstate_aggregation.py:102-197` — independence — Conflates positive/negative paths in one function.

**m-11** `test_session_handoff.py:217-248` — independence — Two tests exercise same `_write_completed_section` path.

**m-12** `test_session_commit_pipeline.py:157-212` / `test_session_commit_pipeline_ext.py:22-35` — conformance — Inconsistent submodule setup helpers.

**m-13** `test_session_handoff_committed.py:99-100` — functional correctness — Comment describes agent behavior, not mode-detection rationale.

**m-14** `test_session_handoff_committed.py` — coverage — Autostrip error fallback path has no dedicated test.

**m-15** `test_session_handoff_cli.py` — coverage — No test for resume from `step_reached="write_session"`.

**m-16** `test_session_handoff.py:217` — excess — Pre-H-2 accumulated content test redundant with committed detection tests.

**m-17** `test_session_handoff_committed.py` — coverage — No direct `_detect_write_mode` unit test.

### Prose+Config (5)

**m-18** handoff/SKILL.md:146 — actionability — "STOP — fix issues and retry" competes with communication rule 1.

**m-19** handoff/SKILL.md:27 — constraint precision — H-2 reference identifier unresolvable by agents.

**m-20** design/SKILL.md:135-142 — scope — Changes are standalone bugfix, not handoff-cli-tool deliverable.

**m-21** .claude/settings.local.json — vacuity — Trailing newline change only.

**m-22** .gitignore:17 — scope — `.vscode/` → `.vscode` broadening unrelated to plan scope.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | session/ subpackage with handoff/ and status/ |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py; worktree imports updated |
| S-3: Output and error conventions | Covered | C-1 regression closed |
| S-4: Session.md parser | Covered | session/parse.py |
| S-5: Git changes utility | Covered | git_cli.py |
| H-1: Domain boundaries | Covered | CLI: status + completed writes |
| H-2: Committed detection | Covered | Three modes in pipeline.py |
| H-3: Diagnostic output | Covered | git_changes() after writes |
| H-4: State caching + step_reached | Covered | HandoffState + resume logic |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + report freshness |
| C-2: Submodule coordination | Covered | 4-state matrix; error path S-3 compliant |
| C-3: Input validation + STOP | Covered | CleanFileError |
| C-4: Validation levels | Covered | Orthogonal options |
| C-5: Amend semantics | Covered | diff-tree, directional propagation |
| ST-0: Worktree-destined tasks | Covered | Marker skip in Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | Lines 155-158 |
| Coupled skill update | Covered | Handoff SKILL.md Step 7 |

## Cross-Cutting Analysis (Layer 2)

- **Path consistency:** `CLAUDEUTILS_SESSION_FILE` env var consistent between handoff and status ✓
- **API contract alignment:** All exception types (CommitInputError, CleanFileError, HandoffInputError) properly caught at CLI boundaries ✓
- **Naming uniformity:** Error classes, data classes, private functions — consistent patterns ✓
- **`_fail()` consolidation:** Single definition in `git.py`, all subcommands import ✓
- **Import chain (S-2):** All worktree modules updated to import from `claudeutils.git` ✓
- **Fragment convention:** Skill changes follow established patterns ✓
- **State file coverage:** `tmp/.handoff-state.json` covered by existing `/tmp/` gitignore entry ✓
- **Coupled skill update:** Precommit gate delivered (SKILL.md Step 7). CLI composition deferred to skill-cli-integration plan ✓
- **RC12 C-1 closure:** L1 code agent, L1 test agent, and L2 all independently verified fix correctness ✓

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 22 (all carried from RC12) |

**RC12 C-1 closure confirmed.** The `except CommitInputError` clause at `session/cli.py:33-34` closes the regression. S-3 compliance restored. CLI-level test exercises full propagation path with real git submodule setup.

**No new findings.** Three independent L1 agents (code, test, prose+config) and L2 cross-cutting review produced zero new findings above RC12 baseline.

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m → RC12 1C/0M/22m → RC13 0C/0M/22m. Both original majors resolved (RC12). Critical regression from fix introduced and closed (RC12→RC13). Minor count stable — all 22 are edge cases, style items, and scope notes with no functional impact.
