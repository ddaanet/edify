# Deliverable Review: handoff-cli-tool (Round 2)

**Date:** 2026-03-22
**Methodology:** agents/decisions/deliverable-review.md
**Scope:** Rework delta only (778+/196- across 16 files, commits `2611ceff..c2f7bd75`)

## Rework Delta Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 8 | +156 | -131 | +25 |
| Test | 7 | +622 | -55 | +567 |
| Agentic prose | 1 | +1 | -1 | +0 |
| Deleted | 1 | +0 | -45 | -45 |
| **Total** | **16** | **+778** | **-196** | **+547** |

## Fix Verification

All 18 addressed findings verified against rework delta:

| Finding | Severity | Status | Evidence |
|---------|----------|--------|----------|
| C#1 | Critical | ✅ FIXED | SKILL.md: `Bash(just:*,wc:*,git:*)` |
| C#2 | Critical | ⚠️ PARTIAL | `_git_commit` fixed (`check=True`); `_commit_submodule` NOT fixed — see Critical #1 below |
| C#3 | Critical | ✅ FIXED | Pipeline reordered: `_validate_inputs` → stage → `_validate` → submodule commits |
| C#4 | Critical | ✅ FIXED | CLI catches `CleanFileError`, calls `_fail(str(e), code=2)` |
| C#5 | Critical | ✅ FIXED | `test_commit_amend_no_edit` in `test_commit_pipeline_errors.py:155-188` |
| MN-1 | Minor | ✅ FIXED | `_error()` helper + try/except in pipeline for staging and commit |
| M#6 | Major | ✅ FIXED | `handoff/context.py` deleted, tests removed |
| M#7 | Major | ✅ FIXED | `list_plans(Path("plans"))` populates real states |
| M#8 | Major | ✅ FIXED | `render_continuation()` added, checks `_is_dirty()` |
| M#9 | Major | ✅ FIXED | `▶` marker in `render_pending`, `render_next` call removed from CLI |
| M#10 | Major | ✅ FIXED | `git_status()` uses `.rstrip("\n")` |
| M#11 | Major | ✅ FIXED | Handoff CLI imports and uses `git_changes()` |
| M#12 | Major | ✅ FIXED | `_count_raw_tasks()` validation, exit 2 on mismatch |
| M#13 | Major | ✅ FIXED | Renamed + `test_commit_skips_vet_when_no_vet` added |
| M#14 | Major | ✅ FIXED | `or` → two separate `assert` statements |
| M#15 | Major | ✅ FIXED | `test_write_completed_overwrites_not_appends` added |
| M#16 | Major | ✅ FIXED | `test_validate_stale_vet_failure` + `test_validate_unknown_vet_reason` |
| m-4 | Minor | ✅ FIXED | `or` → two separate `assert` statements |

## Critical Findings

### 1. `_commit_submodule` git commit still uses `check=False` without returncode check

- **File:** `src/claudeutils/session/commit_pipeline.py:134-148`
- **Axis:** Robustness, error signaling
- **Design req:** S-3 — exit code carries semantic signal; C#2 original finding explicitly stated "Same issue in `_commit_submodule()` (line 134-148)"
- **Impact:** `_commit_submodule()` runs `subprocess.run(cmd, ..., check=False)` for the git commit (line 134-139) and returns `result.stdout.strip()` without checking `result.returncode` (line 148). The pipeline's `try/except CalledProcessError` at lines 297-306 only catches errors from the two `git add` calls (which use `check=True`), not from the git commit. If submodule commit fails (hook rejection, nothing staged), the function silently returns empty/error text, pipeline treats it as success, stages unchanged pointer, and proceeds to parent commit. Submodule changes silently lost.
- **Rework gap:** Cycle 1.1 runbook specified `_commit_submodule returns tuple[bool, str] with same pattern`. Implementation changed `_git_commit` to `check=True` but did not apply the equivalent fix to `_commit_submodule`.

## Major Findings

### 2. SKILL.md missing `Bash(claudeutils:*)` in allowed-tools

- **File:** `agent-core/skills/handoff/SKILL.md:4` vs `:77`
- **Axis:** Functional correctness
- **Impact:** Line 77 instructs "Run `Bash: claudeutils _worktree ls`" for command derivation. Allowed-tools `Bash(just:*,wc:*,git:*)` does not include `claudeutils`. The skill agent cannot execute this command — plan state discovery for command derivation is blocked.
- **Source:** Prose Layer 1

## Minor Findings

**Code (3):**

- **`render_next` is dead code** — `render.py:24-47`. Function no longer imported or called after M#9 fix merged next-task display into `render_pending`. Same class as M#6 (dead code).

- **▶ selection doesn't skip worktree-marked tasks** — `render.py:64-70`. Design ST-0: "Tasks with any `→` marker skipped for Next: selection." `render_pending` doesn't check `task.worktree_marker` before assigning `▶`. Low risk — in-tree tasks normally lack worktree markers. Dead `render_next` (line 36-37) had this check.

- **`_is_dirty()` uses `_git()` which `.strip()`s — same bug class as M#10** — `git.py:128` calls `_git("status", "--porcelain")` which returns `r.stdout.strip()` (line 24). First status line's leading space stripped → `line[3:]` off-by-one for first line only. Error direction: false-positive (over-reports dirty), so safe but inconsistent with the M#10 fix applied to `git_status()`.

- **`step_reached` field is dead data** — `handoff/pipeline.py:21`. Saved but never read during resume. Resume path (`handoff/cli.py:46-52`) re-executes all steps unconditionally. Acceptable (operations are idempotent) but misleading — suggests partial-resume capability that doesn't exist. Source: Code Layer 1.

- **Old section name `## Pending Tasks` not detected** — `status/cli.py:22-34`. If session.md uses old section name, both `_count_raw_tasks("In-tree Tasks")` and `parse_tasks("In-tree Tasks")` return 0. Validation `0 != 0` passes silently → "No in-tree tasks" instead of exit 2. Source: Code Layer 1.

**Test (1):**

- **`test_status_rejects_old_format` uses weak `or` assertion** — `test_status_rework.py:143`. Same weak disjunction pattern that M#14 and m-4 fixed in other test files.

## Gap Analysis

| Round 1 Finding | Round 2 Status |
|-----------------|----------------|
| C#1 SKILL.md | Fixed |
| C#2 git commit returncode | Partial — parent fixed, submodule NOT fixed (Critical #1) |
| C#3 pipeline ordering | Fixed |
| C#4 exit code semantics | Fixed |
| C#5 amend+no-edit test | Fixed |
| M#6 dead code | Fixed (new dead code introduced: `render_next`) |
| M#7 plan discovery | Fixed |
| M#8 continuation header | Fixed |
| M#9 output format | Fixed |
| M#10 strip bug | Fixed (same class persists in `_is_dirty`) |
| M#11 handoff git changes | Fixed |
| M#12 old format enforcement | Fixed |
| M#13 no-vet test direction | Fixed |
| M#14 weak assertion | Fixed (same pattern introduced in new test) |
| M#15 H-2 append test | Fixed |
| M#16 validate edge cases | Fixed |
| MN-1 uncaught exception | Fixed |
| m-4 weak CLI assertion | Fixed |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 1 |
| Minor | 6 |

17 of 18 findings fully fixed. One Critical remains: `_commit_submodule` git commit returncode not checked — same bug class as C#2, explicitly called out in round 1 but missed during rework. One Major: SKILL.md allowed-tools blocks `claudeutils _worktree ls` command derivation. Six minor issues (dead `render_next`, worktree-marker skip, `_is_dirty` strip, dead `step_reached`, old section name bypass, weak test assertion).
