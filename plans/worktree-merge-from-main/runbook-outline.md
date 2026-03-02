# Worktree Merge From Main — Runbook Outline

## Requirements Mapping

| Requirement | Phase | Items |
|-------------|-------|-------|
| FR-1 session.md keep-ours | Phase 2 | 2.1, 2.2 |
| FR-2 learnings theirs-base + ours delta | Phase 3 | 3.1, 3.2 |
| FR-3 accept main's structural changes | Phase 2 | 2.3, 2.4 |
| FR-4 sandbox bypass | Phase 4 (inline) | Documented in Mode D |
| FR-5 idempotent resume | Phase 1 | 1.3; verified Phase 3 Cycle 3.3 |
| NFR-1 minimal output | All phases | Output discipline in each function |
| NFR-2 no data loss | Phase 2, 3 | Verified by E2E tests |
| C-1 unify with existing merge infra | Phase 1 | Direction param through shared pipeline |
| C-2 requires clean tree | Phase 1 | 1.2 reuses `_check_clean_for_merge` |
| C-3 worktree skill integration | Phase 3, 4 | CLI flag + Mode D |

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

- Cycle 1.2: `_phase1_validate_clean_trees` adaptation — skip `wt_path` check for from-main, validate current branch is not main
  - Files: `src/claudeutils/worktree/merge.py`
  - Test: from-main on main branch → exit code 2 with "cannot merge main into itself"; from-main on worktree branch → passes validation
  - Depends on: Cycle 1.1

- Cycle 1.3: `_phase4_merge_commit_and_precommit` adaptation — skip `_append_lifecycle_delivered` for from-main, pass `from_main` to remerge functions
  - Files: `src/claudeutils/worktree/merge.py`
  - Test: from-main merge does not append lifecycle "delivered" entries
  - Depends on: Cycle 1.1

- Cycle 1.4: `_format_conflict_report` adaptation — hint command shows `--from-main` when appropriate
  - Files: `src/claudeutils/worktree/merge.py`
  - Test: from-main conflict report contains `merge --from-main` hint, not `merge main`
  - Depends on: Cycle 1.1

**Checkpoint:** `just precommit` — all existing tests pass (no regressions), new direction parameter accepted.

### Phase 2: Direction-aware session.md and structural resolution (type: tdd)

FR-1 (session.md keep-ours) and FR-3 (accept main's structural changes).

- Cycle 2.1: `resolve_session_md` from-main policy — keep ours entirely (checkout --ours, git add) instead of additive merge
  - Files: `src/claudeutils/worktree/resolve.py`
  - Test: from-main with conflicting session.md → worktree session preserved unchanged, main's session discarded
  - Depends on: Phase 1

- Cycle 2.2: `remerge_session_md` from-main policy — keep ours entirely (skip structural merge, just git add current)
  - Files: `src/claudeutils/worktree/remerge.py`
  - Test: from-main remerge keeps worktree session.md content, does not inject main's tasks
  - Depends on: Cycle 2.1

- Cycle 2.3: Delete/modify conflict auto-resolution — new function detecting delete/modify conflicts, accepting theirs (main's deletion) when from-main
  - Files: `src/claudeutils/worktree/merge.py` (in `_auto_resolve_known_conflicts`)
  - Test: file deleted on main, modified on branch → from-main resolves as deleted (theirs wins); same scenario in worktree→main → remains conflict
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

- Cycle 3.2: `remerge_learnings_md` from-main policy — invert ours/theirs in diff3
  - Files: `src/claudeutils/worktree/remerge.py`
  - Test: from-main remerge produces main-base + branch delta content
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

- Add Mode D (Sync from main) to `agent-core/skills/worktree/SKILL.md` following Mode C structure
  - Invocation: `wt sync` or `wt from-main` in skill, maps to `claudeutils _worktree merge --from-main`
  - Same sandbox bypass requirement as Mode C
  - Exit code handling parallels Mode C (0=success, 3=conflicts, 1=precommit failure, 2=fatal)
  - Key behavioral differences: resolution policies documented (session ours, learnings inverted, structural theirs)

## Expansion Guidance

- Phase 1 cycles share test infrastructure: real git repos via `tmp_path`, branch setup helper creating main + worktree branch with divergent commits. Extract shared fixture across phases.
- Phase 2-3 resolution tests should verify BOTH directions in each test (from-main and worktree→main) to prevent regressions.
- Delete/modify conflict detection (Cycle 2.3): use `git diff --diff-filter=` to identify conflict types. Accept theirs via `git checkout --theirs <file> && git add <file>`.
- CLI test (Cycle 3.3): use `click.testing.CliRunner` per testing conventions.
- Inline Phase 4: Mode D parallels Mode C but with different resolution policies documented. Include the `--from-main` flag in the command invocation.
