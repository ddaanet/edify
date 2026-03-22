# Code Review: handoff-cli-tool (Round 2)

**Reviewer:** Opus 4.6
**Design reference:** `plans/handoff-cli-tool/outline.md`

## Fix Verification

### C#2 (CR-1): `_git_commit` ignores non-zero exit code — PARTIALLY FIXED

- **Parent commit:** FIXED. `_git_commit()` now uses `check=True` (`commit_pipeline.py:82`), and the caller catches `CalledProcessError` at line 313.
- **Submodule commit:** NOT FIXED. `_commit_submodule()` still uses `check=False` for the `git commit` subprocess (`commit_pipeline.py:139`). If the submodule commit fails, the function silently proceeds to stage the (unchanged) submodule pointer in the parent (line 142-147) and returns whatever stdout was produced. The `CalledProcessError` catch at the call site (line 305) only fires from the `git add` calls (which use `check=True`), not from a failed commit.

### C#3 (CR-2): Submodule committed before validation gate — FIXED

- The pipeline now follows correct ordering: `_validate_inputs` (line 272) → `_stage_files` (line 285) → `_validate` precommit/vet (line 290) → submodule commits (line 296) → parent commit (line 310).
- Evidence: submodule commit loop at lines 296-307 is after validation gate at lines 289-292.

### C#4: Exit code 2 for CleanFileError — FIXED

- `session/cli.py:31-32` catches `CleanFileError` and calls `_fail(str(e), code=2)`.

### MN-1: Uncaught CalledProcessError from `_stage_files` — FIXED

- `commit_pipeline.py:283-287` wraps `_stage_files` in `try/except subprocess.CalledProcessError`, returning `_error("staging failed", e)`.

### M#10 (MJ-5): `git_status()` strip bug — FIXED

- `git.py:98` now uses `return result.stdout.rstrip("\n")` instead of `.strip()`.

### M#11: Handoff uses shared `git_changes()` — FIXED

- `handoff/cli.py:13` imports `git_changes` from `claudeutils.git_cli`.
- `handoff/cli.py:57` calls `git_changes()` and echoes the result.

### M#7 (MJ-2): Plan state discovery — FIXED

- `status/cli.py:11` imports `list_plans` from `claudeutils.planstate.inference`.
- `status/cli.py:54` builds `all_plans` dict from real lifecycle states via `list_plans(Path("plans"))`.
- `status/cli.py:58` populates `plan_states` from `all_plans.get(task.plan_dir, "")`.

### M#8 (MJ-1): Session continuation header — FIXED

- `status/cli.py:63` calls `render_continuation(is_dirty=_is_dirty(), plan_states=plan_states)`.
- `render.py:8-21` implements `render_continuation` — returns header when dirty, appends `/deliverable-review` for `review-pending` plans, returns empty string when clean.

### M#9 (MJ-3): Output format — FIXED

- `render.py:70` uses `▶` marker for the first eligible pending task.
- The `▶` task is rendered inline in the In-tree section with command, model, and restart metadata.
- No separate `Next:` section in the CLI output path (`status/cli.py` does not call `render_next`).

### M#12: Old format enforcement — FIXED

- `status/cli.py:48-52` compares `_count_raw_tasks(content)` against `len(data.in_tree_tasks)`. Mismatch exits with code 2: "Old-format tasks missing metadata."

## New Findings

### N-1: `_commit_submodule` silently ignores submodule commit failure

- **File:** `src/claudeutils/session/commit_pipeline.py:134-148`
- **Axis:** Robustness, error signaling
- **Severity:** Major
- **Description:** This is the remaining half of the original C#2 finding. The submodule `git commit` at line 134-140 uses `check=False` without inspecting `result.returncode`. If the commit fails (empty commit, hook rejection, lock contention), the function proceeds to stage the submodule pointer in the parent and returns potentially empty or error-containing stdout. The caller's `CalledProcessError` catch (line 305) never fires for this failure mode. Fix: either use `check=True` (and let the existing catch handle it) or inspect `result.returncode` and raise on failure.

### N-2: `render_next` is dead code

- **File:** `src/claudeutils/session/status/render.py:24-47`
- **Axis:** Excess
- **Severity:** Minor
- **Description:** `render_next()` is defined and tested (10 tests in `test_session_status.py`) but never called from production code. The `▶` integration in `render_pending` replaced its purpose. The function and its tests add maintenance burden without contributing to the production path.

### N-3: `step_reached` field is unused in handoff resume

- **File:** `src/claudeutils/session/handoff/pipeline.py:21`, `src/claudeutils/session/handoff/cli.py:46-52`
- **Axis:** Vacuity
- **Severity:** Minor
- **Description:** `HandoffState.step_reached` is saved (line 29-35 of `pipeline.py`) but never read during resume. The resume path at `cli.py:46-52` loads the state file and re-parses `input_markdown`, then unconditionally re-executes all pipeline steps. The field is dead data. This is acceptable because the operations are idempotent (overwrite, not append), but the dead field adds misleading complexity suggesting partial-resume capability.

### N-4: `_count_raw_tasks` does not detect old section name

- **File:** `src/claudeutils/session/status/cli.py:22-34, 47-52`
- **Axis:** Robustness
- **Severity:** Minor
- **Description:** If session.md uses the old section name `## Pending Tasks` instead of `## In-tree Tasks`, both `_count_raw_tasks` and `parse_tasks` return 0 (neither finds the section). The validation `0 != 0` is false, so the check passes silently. Status output shows "No in-tree tasks" instead of the intended exit-2 error. The old-format enforcement only catches metadata-format issues within the correct section name, not the section name itself.

### N-5: Redundant `task.checkbox == " "` check in `render_pending`

- **File:** `src/claudeutils/session/status/render.py:67`
- **Axis:** Excess
- **Severity:** Trivial
- **Description:** Line 67 checks `task.checkbox == " "` but `pending` is already filtered to `checkbox == " "` at line 59. The condition is always true. Harmless but adds noise.

## Summary

| Category | Count |
|----------|-------|
| Fix verifications | 10 |
| FIXED | 9 |
| PARTIALLY FIXED | 1 (C#2 — parent path fixed, submodule path not) |
| New findings | 5 (1 Major, 3 Minor, 1 Trivial) |

The rework addressed the majority of round 1 findings. The one remaining issue is N-1 (submodule commit failure not checked), which is the other half of the original C#2 that was fixed for the parent commit path but missed for the submodule commit path. The new minor findings are dead code (`render_next`, `step_reached`) and edge-case robustness gaps.
