# Worktree Merge From Main — Runbook Outline

## Requirements Mapping

| Requirement | Phase | Items | Notes |
|-------------|-------|-------|-------|
| FR-1 session.md keep-ours | Phase 2 | 2.1, 2.2 | resolve + remerge both adapted |
| FR-2 learnings theirs-base + ours delta | Phase 3 | 3.1, 3.2 | ours/theirs inversion in diff3 |
| FR-3 accept main's structural changes | Phase 2 | 2.3, 2.4 | Delete/modify auto-resolution |
| FR-4 sandbox bypass | Phase 4 (inline) | Mode D documentation | Sandbox note in Mode D skill text |
| FR-5 idempotent resume | Phase 1 | (shared) | `merge_state.py` already direction-agnostic: `_is_branch_merged("main")` + `_recover_untracked_file_collision` work for both directions |
| NFR-1 minimal output | All phases | Output discipline in each function | Consistent with existing merge output style |
| NFR-2 no data loss | Phase 2, 3 | Verified by E2E tests (2.4, 3.4) | session.md, learnings.md, uncommitted changes |
| C-1 unify with existing merge infra | Phase 1 | 1.1-1.2 | Direction param through shared pipeline |
| C-2 requires clean tree | Phase 1 | 1.2 | Reuses `_check_clean_for_merge` |
| C-3 worktree skill integration | Phase 3, 4 | 3.3, 3.4, Phase 4 | CLI flag + Mode D skill |

## Key Decisions

- **Direction threading:** Single `from_main: bool` parameter threads through `merge()` → all phases. When `from_main=True`, target branch is always `"main"`. Resolution policies select based on this flag.
- **Slug semantics:** `merge(slug, from_main)` — when `from_main=True`, slug is `"main"` (set by CLI layer). All internal functions receive slug as before; behavior varies by `from_main` flag.
- **Resolution inversion:** Session.md: from-main keeps ours entirely (vs additive for worktree→main). Learnings.md: from-main swaps ours/theirs in diff3 (main is base, branch additions are delta). Delete/modify: from-main accepts theirs (main's deletion wins over branch's stale modification).
- **CLI contract:** `_worktree merge <slug>` (existing) vs `_worktree merge --from-main` (new). Mutually exclusive: `--from-main` with slug is an error.

## Phase Structure

### Phase 1: Direction-aware merge pipeline (type: tdd)

Foundation: thread `from_main` through shared phases, adapt each phase's behavior.

- Cycle 1.1: `merge()` function signature — add `from_main: bool = False` parameter, thread to phase functions
  - Files: `src/claudeutils/worktree/merge.py`
  - Test: call `merge("main", from_main=True)` on already-merged state → succeeds without error
  - Depends on: nothing (foundation)

- Cycle 1.2: Batch `from_main` adaptation of 4 independent merge.py functions — each adds a `from_main` conditional branch
  - Files: `src/claudeutils/worktree/merge.py`
  - Functions and tests:
    - `_phase1_validate_clean_trees`: skip `wt_path` check for from-main, validate current branch is not main. Test: from-main on main branch → exit code 2 with "cannot merge main into itself"; from-main on worktree branch → passes validation
    - `_phase4_merge_commit_and_precommit`: skip `_append_lifecycle_delivered` for from-main, pass `from_main` to remerge functions. Test: from-main merge does not append lifecycle "delivered" entries
    - `_format_conflict_report`: hint command shows `--from-main` when appropriate. Test: from-main conflict report contains `merge --from-main` hint, not `merge main`
    - `_phase3_merge_parent`: merge target is `main` (not slug), merge message reflects direction. Test: from-main merge creates commit with message "Merge main into <branch>"; worktree→main merge message unchanged
  - Depends on: Cycle 1.1

**Checkpoint:** `just precommit` — all existing tests pass (no regressions), new direction parameter accepted.

### Phase 2: Direction-aware session.md and structural resolution (type: tdd)

FR-1 (session.md keep-ours) and FR-3 (accept main's structural changes).

- Cycle 2.1: `resolve_session_md` from-main policy — keep ours entirely (checkout --ours, git add) instead of additive merge
  - Files: `src/claudeutils/worktree/resolve.py`
  - Test: from-main with conflicting session.md → worktree session preserved unchanged, main's session discarded
  - Depends on: Phase 1

- Cycle 2.2: `remerge_session_md` from-main policy — add `from_main: bool = False` parameter, keep ours entirely (skip structural merge, just git add current)
  - Files: `src/claudeutils/worktree/remerge.py`
  - Test: from-main remerge keeps worktree session.md content, does not inject main's tasks; worktree→main remerge behavior unchanged
  - Depends on: Cycle 2.1

- Cycle 2.3: Delete/modify conflict auto-resolution — detect delete/modify conflicts via `git status` conflict markers (UD/DU), accept theirs (main's deletion) when from-main. Extends `_auto_resolve_known_conflicts` with `from_main` parameter.
  - Files: `src/claudeutils/worktree/merge.py`
  - Test: file deleted on main, modified on branch → from-main resolves as deleted (theirs wins); same scenario in worktree→main → remains unresolved conflict
  - Depends on: Phase 1

- Cycle 2.4: Integration test — E2E from-main merge with session.md conflict and file deletion on main
  - Files: new test file or extend existing
  - Test: real git repos, branch diverges from main, main deletes file + modifies session, merge from main → session preserved, file deleted, merge succeeds
  - Depends on: Cycles 2.1, 2.2, 2.3

**Checkpoint:** `just precommit` — session.md and structural resolution verified for both directions.

### Phase 3: Direction-aware learnings.md resolution and CLI (type: tdd)

FR-2 (learnings inversion) and C-3 (CLI integration).

- Cycle 3.1: `resolve_learnings_md` from-main policy — invert ours/theirs in diff3 (theirs = main is base, ours = branch additions are delta)
  - Files: `src/claudeutils/worktree/resolve.py`
  - Test: from-main with conflicting learnings → main entries as base, branch-only entries appended, no duplication
  - Depends on: Phase 1

- Cycle 3.2: `remerge_learnings_md` from-main policy — add `from_main: bool = False` parameter, invert ours/theirs in diff3 (main = base, branch additions = delta)
  - Files: `src/claudeutils/worktree/remerge.py`
  - Test: from-main remerge produces main-base + branch delta content; worktree→main remerge behavior unchanged
  - Depends on: Cycle 3.1

- Cycle 3.3: CLI `--from-main` flag — Click option, mutual exclusivity with slug, target validation
  - Files: `src/claudeutils/worktree/cli.py`
  - Test (CliRunner): `merge --from-main` succeeds; `merge --from-main some-slug` errors; `merge` (no args, no flag) errors
  - Depends on: Phase 1

- Cycle 3.4: Full E2E test — `--from-main` merge happy path via CliRunner with real git repos
  - Files: new test file
  - Test: create main + worktree branch, diverge both, `merge --from-main` → session ours, learnings inverted, main ancestor of HEAD, exit 0
  - Depends on: Cycles 3.1, 3.2, 3.3, Phase 2

**Checkpoint:** `just precommit` — all FRs verified, CLI working, full E2E passing.

### Phase 4: Skill and documentation updates (type: inline)

- Step 4.1: Add Mode D (Sync from main) to SKILL.md and update all enumeration sites
  - Files: `agent-core/skills/worktree/SKILL.md`
  - Mode D section:
    - Invocation: `wt sync` or `wt from-main` in skill, maps to `claudeutils _worktree merge --from-main`
    - Same sandbox bypass requirement as Mode C
    - Exit code handling parallels Mode C (0=success, 3=conflicts, 1=precommit failure, 2=fatal)
    - Key behavioral differences: resolution policies documented (session ours, learnings inverted, structural theirs)
  - Enumeration sites: Principles section ("Merge is idempotent"), Continuation section, and any "Mode C" references that need parallel Mode D mentions. Grep for "merge", "Mode C", "slug" references that need updating for bidirectional awareness

**Checkpoint:** `just precommit` — skill file validates, all tests pass.

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Test infrastructure:**
- Phase 1-3 cycles share test infrastructure: real git repos via `tmp_path`, branch setup helper creating main + worktree branch with divergent commits. Extract shared fixture across phases. Per recall ("when preferring e2e over mocked subprocess"): real git repos only, mock only for error injection.
- Per recall ("when tests simulate merge workflows"): test branch must be the merged parent, not a branch created at the merge commit SHA. Amend preserves merge parents.
- Phase 2-3 resolution tests should verify BOTH directions in each test (from-main and worktree→main) to prevent regressions.

**Cycle expansion:**
- Delete/modify conflict detection (Cycle 2.3): detect via `git status --porcelain` conflict markers (UD = deleted by us, DU = deleted by theirs). For from-main, DU conflicts (deleted by theirs/main) are auto-resolved by accepting deletion. Do NOT use `git diff --diff-filter` during active merge conflict state.
- CLI test (Cycle 3.3): use `click.testing.CliRunner` per testing conventions. Note `merge` subcommand already takes `slug` as argument — `--from-main` is a flag that makes slug optional.
- `merge_state.py` functions (`_detect_merge_state`, `_recover_untracked_file_collision`) are already direction-agnostic: `_is_branch_merged("main")` checks if main is ancestor of HEAD (correct for from-main "already up to date"). No adaptation needed — verified by code review.

**Regression preservation:**
- Existing worktree→main behavior (session.md additive merge, learnings ours-base, completed task filtering per recall "when merging completed tasks from branch") must remain unchanged. All new `from_main` code paths gate on the flag.
- `_auto_resolve_known_conflicts` currently takes `(conflicts, slug)`. Adding `from_main` parameter requires updating existing call site in `_phase3_merge_parent`.

**Checkpoint guidance:**
- Phase 1 checkpoint verifies no regressions in existing 35+ worktree test files.
- Phase 2 checkpoint: session.md and structural resolution verified for both directions.
- Phase 3 checkpoint: full E2E via CLI, all FRs verified.
- Phase 4 checkpoint: SKILL.md enumeration sites complete.

**Growth projection:**
- `merge.py`: 387 current + ~50 (2 cycles, ~10 lines each for 5 function adaptations) = ~437. Above 400-line threshold — consider extracting direction-specific helpers or a `_from_main_overrides()` helper to keep file manageable.
- `resolve.py`: 358 current + ~20 (from_main guard in 2 functions) = ~378. Under threshold.
- `remerge.py`: 99 current + ~20 (from_main parameter + conditional in 2 functions) = ~119. Under threshold.
- `cli.py`: 362 current + ~15 (--from-main flag + validation) = ~377. Under threshold.
- `SKILL.md`: 139 current + ~40 (Mode D section) = ~179. Under threshold.

**Enumeration sites (recall: "when adding new variant"):**
- Phase 4 Step 4.1 must grep SKILL.md for all references to merge behavior, Mode C, slug-based merge, and update for bidirectional awareness. Key sections: Mode C description, Principles ("Merge is idempotent", "Parallel execution requires individual merge"), Continuation section.
