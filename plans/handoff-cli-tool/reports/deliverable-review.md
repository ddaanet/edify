# Deliverable Review: handoff-cli-tool (RC11)

**Date:** 2026-03-25
**Methodology:** agents/decisions/deliverable-review.md
**Review type:** Full-scope (no delta-scoping per learnings)
**Layers:** L1 (3 opus agents: code, test, prose+config) + L2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1751 | -96 | +1655 |
| Test | 20 | +3665 | -60 | +3605 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5427** | **-164** | **+5263** |

### RC10 Finding Verification

| RC10 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1: `load_state()` backward compat | FIXED | pipeline.py:45-47 — filters `data` to `HandoffState.__dataclass_fields__` |
| M-2: Handoff CLI error handling | FIXED | cli.py:54-58 — try/except `(OSError, ValueError)` around pipeline calls |
| m-1: Submodule CleanFileError paths | VERIFIED | Regression test confirms paths include submodule prefix |
| m-2: `overwrite_status` regex backreference | FIXED | pipeline.py:77-80 — function callback replacement |
| m-3: `_build_repo_section` blank line | FIXED | git_cli.py:32 |
| m-6: Redundant `len > 0` | FIXED | test_session_parser.py:138 |
| m-7: Bare `pytest.raises` (test_session_commit.py) | FIXED | match="no uncommitted changes" |
| m-8: Bare `pytest.raises` (test_worktree_merge_errors.py) | FIXED | match="non-zero exit" |
| m-9: Ambiguous assertion string | CARRIED | m-12 below — same finding at same location |
| m-10: Disjunctive assertion | FIXED | test_session_status.py:263 — specific `"In-tree:"` |
| m-11: Integration test plan dir | FIXED | test_session_integration.py:37-39 — creates `plans/widget/` |
| m-12: Un-parenthesized except (PEP 758) | DISMISSED | Python 3.14 canonical form per PEP 758 |
| m-13: Dead `return None` | FIXED | worktree/cli.py:264 — removed, `noqa: RET503` added |

11 of 13 RC10 findings fixed. m-9 carried (same location). m-12 dismissed (PEP 758).

## Critical Findings

None.

## Major Findings

**M-1** `session/handoff/pipeline.py:89-100` — conformance, functional completeness
H-2 committed detection not implemented in CLI. Design specifies three write modes based on `git diff HEAD -- agents/session.md`:
- No diff → Overwrite
- Old removed, new present → Append
- Old preserved with additions → Auto-strip committed content, keep new additions

Implementation collapses all three into unconditional overwrite. Docstring acknowledges simplification. Risk mitigated: handoff skill's Step 1 handles uncommitted-prior-handoff detection, and CLI is internal-only (hidden, skill-called). Design allocated this to CLI.

**M-2** `session/handoff/pipeline.py:14-19` — conformance, functional completeness
H-4 `step_reached` field missing from `HandoffState`. Design specifies `step_reached: "write_session" | "diagnostics"` for granular resume. Implementation replays full pipeline on resume. Functionally safe — all writes idempotent (overwrite). Related to M-1: if committed detection were implemented, idempotency would not hold, making step_reached necessary.

## Minor Findings

### Code (10)

**m-1** `validation/task_parsing.py:21` — conformance — `WORKTREE_MARKER_PATTERN` requires backtick-wrapped slug. Design's `→ wt` marker (ST-0, no backticks) won't match. Practical impact low: `→ wt` tasks belong in Worktree Tasks section (rendered separately).

**m-2** `session/commit_pipeline.py:276-282` — conformance — Missing submodule message returns exit 1 (pipeline error). Per S-3, malformed caller input → exit 2.

**m-3** `session/commit_pipeline.py:263-267` — error signaling — Redundant missing-message check yields exit 1. Parser already catches this with exit 2. If kept, should exit 2.

**m-4** `session/commit_pipeline.py:193-213` — robustness — `_strip_hints` single-space continuation logic: line both kept in output AND treated as hint context. Intent ambiguous.

**m-5** `session/commit_gate.py:51-68` — robustness — `_dirty_files` uses `-u` flag. Performance concern with many untracked files.

**m-6** `session/handoff/cli.py:60-61` — robustness — `git_changes()` called unconditionally for diagnostics. Minor unnecessary work when tree is clean (unlikely after writes).

**m-7** `session/status/render.py:105-127` — functional correctness — `_build_dependency_edges` uses substring matching in concatenated blocker text. False dependency links possible for common words. Conservative (prevents parallelism, never enables unsafe parallelism).

**m-8** `session/status/cli.py:67` — functional correctness — `list_plans(Path("plans"))` uses relative path. Matches other relative-path assumptions in CLI context.

**m-9** `session/commit_pipeline.py:22-37,40-55` — testability — `_run_precommit`/`_run_lint` comment "Patchable in tests" but are module-level functions. `monkeypatch.setattr` works.

**m-10** `session/commit_gate.py:31-48` — modularity — `_git_output` duplicates `git.py:_git()` but adds `cwd` parameter. Shared helper doesn't support `cwd`.

### Test (5)

**m-11** `test_session_status.py:280-298` — conformance — `SESSION_FIXTURE` defined after first usage. Forward reference works but unconventional.

**m-12** `test_session_commit_pipeline.py:121-134` — specificity — Hint-stripping assertion strings ("continuation", "single") are generic. Low risk with inline test data. Carried from RC10 m-9.

**m-13** `test_planstate_aggregation.py:102-197` — independence — `test_git_metadata_helpers` conflates positive and negative paths.

**m-14** `test_session_handoff.py:235-261` — conformance — Two tests exercise same `_write_completed_section` code path, differing only in initial state. Near-redundant.

**m-15** `test_session_commit_pipeline.py:157-212` — conformance — Inconsistent submodule setup helpers between test files.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | session/ subpackage |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | All stdout, exit codes 0/1/2 |
| S-4: Session.md parser | Covered | session/parse.py |
| S-5: Git changes utility | Covered | git_cli.py |
| H-1: Domain boundaries | Covered | CLI: status + completed writes |
| H-2: Committed detection | **Simplified** | All modes → overwrite (M-1) |
| H-3: Diagnostic output | Covered | git_changes() after writes |
| H-4: State caching | **Simplified** | No step_reached (M-2) |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + report freshness |
| C-2: Submodule coordination | Covered | 4-state matrix |
| C-3: Input validation + STOP | Covered | CleanFileError |
| C-4: Validation levels | Covered | Orthogonal options |
| C-5: Amend semantics | Covered | diff-tree, directional propagation |
| ST-0: Worktree-destined tasks | Covered | Marker skip in Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All commands registered |
| Coupled skill update | Covered | Handoff SKILL.md Step 7 |

## Cross-Cutting Analysis (Layer 2)

- **Path consistency:** `CLAUDEUTILS_SESSION_FILE` env var, consistent between handoff and status ✅
- **API contract alignment:** `ParsedTask` ↔ `render_pending()`, `CommitInput` ↔ `commit_pipeline()` ✅
- **Naming uniformity:** Error classes, data classes, private functions — consistent ✅
- **`_fail()` consolidation:** Single definition in `git.py`, all subcommands import ✅
- **Import chain (S-2):** All worktree modules correct ✅
- **Fragment convention:** Skill changes follow patterns ✅
- **RC10 test fixes:** All test-related fixes verified ✅

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 15 |

**RC10 fixes:** 11 of 13 fixed. 1 carried (m-12, generic assertion strings). 1 dismissed (PEP 758).

**Remaining Majors:** Both are design-spec conformance deviations, not functional defects. M-1 (H-2 committed detection) and M-2 (H-4 step_reached) are documented simplifications — the implementation is internally consistent and functionally safe. The handoff skill provides the detection logic that the design allocated to the CLI, and idempotent writes make step_reached unnecessary.

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m. Major count stable at 2 — same two design simplifications surfaced in RC10 and RC11 (M-1/M-2 are spec-level decisions, not code bugs). Minor count increased by 2 (5 new test minors, 3 code minors resolved from RC10 but replaced by different code minors from fresh full-scope review).
