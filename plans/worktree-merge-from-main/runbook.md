# Worktree Merge From Main — Runbook

name: worktree-merge-from-main
model: sonnet

## Common Context

**Requirements:** `plans/worktree-merge-from-main/requirements.md` — 5 FRs, 3 constraints, Q-1 resolved.

**Design decisions:**
- Direction threading: `from_main: bool` threads through `merge()` → all phases
- Slug semantics: when `from_main=True`, slug is `"main"` (set by CLI layer)
- Resolution inversion: session.md keeps ours; learnings.md swaps ours/theirs in diff3; delete/modify accepts theirs
- CLI contract: `_worktree merge --from-main` (mutually exclusive with slug arg)

**Key source files:**
- `src/claudeutils/worktree/merge.py` — 4-phase merge pipeline, `merge()` orchestrator
- `src/claudeutils/worktree/resolve.py` — `resolve_session_md`, `resolve_learnings_md`, `diff3_merge_segments`
- `src/claudeutils/worktree/remerge.py` — `remerge_session_md`, `remerge_learnings_md` (phase 4 all-paths)
- `src/claudeutils/worktree/merge_state.py` — `_detect_merge_state` (direction-agnostic, no changes needed)
- `src/claudeutils/worktree/cli.py` — Click CLI, `merge` subcommand
- `agent-core/skills/worktree/SKILL.md` — Modes A-C, skill documentation

**Test conventions:**
- E2E with real git repos via `tmp_path` (no subprocess mocks except error injection)
- Click CliRunner for CLI tests
- Branch as merged parent in test fixtures (amend preserves parents)
- Verify BOTH directions in resolution tests (regression preservation)

**Recall artifact:** `plans/worktree-merge-from-main/recall-artifact.md`

### Phase 1: Direction-aware merge pipeline (type: tdd, model: sonnet)

## Cycle 1.1: `merge()` function signature

Add `from_main: bool = False` parameter to `merge()` and thread to all phase functions.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** Test that `merge("main", from_main=True)` is accepted on an already-merged state (main is ancestor of HEAD). Create a real git repo with a branch, merge the branch, then call `merge("main", from_main=True)`. Assert: no error (exit code 0), function returns normally.

**GREEN:** Add `from_main` parameter to `merge()` signature. Thread to `_phase1_validate_clean_trees`, `_phase2_resolve_submodule`, `_phase3_merge_parent`, `_phase4_merge_commit_and_precommit`. Each phase function adds the parameter but does not yet branch on it (pass-through). Existing behavior unchanged.

**Dependencies:** None (foundation cycle)

**Stop/Error Conditions:**
- RED passes without implementation → parameter may already exist, check merge.py
- Existing tests break after GREEN → parameter threading changed a signature incorrectly

## Cycle 1.2: Batch `from_main` adaptation of merge.py phase functions

Adapt 4 independent functions in merge.py to branch on `from_main`:

1. `_phase1_validate_clean_trees(slug, from_main)`: skip `wt_path(slug)` check when from_main. Validate current branch is not main: `git symbolic-ref --short HEAD` ≠ "main".
2. `_phase4_merge_commit_and_precommit(slug, from_main)`: skip `_append_lifecycle_delivered` when from_main. Pass `from_main` to `remerge_learnings_md` and `remerge_session_md`.
3. `_format_conflict_report(conflicts, slug, from_main)`: when from_main, hint says `claudeutils _worktree merge --from-main` instead of `claudeutils _worktree merge {slug}`.
4. `_phase3_merge_parent(slug, from_main)`: pass `from_main` to `_auto_resolve_known_conflicts`.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** 4 tests, one per function:
- `_phase1_validate_clean_trees("main", from_main=True)` on main branch → `SystemExit(2)` with "cannot merge main into itself"; on non-main branch → passes
- `_phase4_merge_commit_and_precommit` with from_main → no lifecycle "delivered" entries appended
- `_format_conflict_report(["some/file"], "main", from_main=True)` → output contains `merge --from-main`
- After `_phase3_merge_parent("main", from_main=True)` merge, commit message reflects direction

**GREEN:** Add `from_main` conditionals to each function. `_auto_resolve_known_conflicts` gains `from_main` parameter (pass-through for now — policies in Phase 2).

**Dependencies:** Cycle 1.1

**Stop/Error Conditions:**
- RED passes before implementation → function may already branch on from_main
- Existing worktree→main tests break → from_main=False default not preserving existing behavior
- "cannot merge main into itself" test passes on wrong branch → verify git symbolic-ref detection

**Checkpoint:** `just precommit` — all existing tests pass, new direction parameter accepted.

### Phase 2: Direction-aware session.md and structural resolution (type: tdd, model: sonnet)

## Cycle 2.1: `resolve_session_md` from-main policy (FR-1)

When `from_main=True`, keep ours entirely — no additive merge. Checkout --ours, git add.

**Files:** `src/claudeutils/worktree/resolve.py`

**RED:** Set up merge with conflicting session.md (main has full task list, branch has focused session). Call `resolve_session_md(conflicts, slug="main", from_main=True)`. Assert: session.md content matches branch's original session exactly; main's tasks not injected.

**GREEN:** Add `from_main: bool = False` to `resolve_session_md`. When from_main: `git checkout --ours agents/session.md`, `git add agents/session.md`, return filtered conflicts. Skip `_merge_session_contents` entirely.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → session.md may not be in conflicts list; verify test fixture creates actual conflict
- Branch session content changes after resolution → checkout --ours not working correctly

## Cycle 2.2: `remerge_session_md` from-main policy (FR-1)

When `from_main=True`, keep ours entirely in phase 4 remerge (skip structural merge, just git add current working tree version).

**Files:** `src/claudeutils/worktree/remerge.py`

**RED:** Two tests:
1. from_main=True: set up MERGE_HEAD state. Call `remerge_session_md(slug="main", from_main=True)`. Assert: session.md content is the worktree's version, main's tasks not injected.
2. Regression: from_main=False (default): existing behavior unchanged — structural merge via `_merge_session_contents` still runs.

**GREEN:** Add `from_main: bool = False` to `remerge_session_md`. When from_main: `git add agents/session.md` (current working tree version is already the branch's content). Skip `_merge_session_contents` call.

**Dependencies:** Cycle 2.1

**Stop/Error Conditions:**
- RED passes before implementation → remerge may not be called in test fixture; verify MERGE_HEAD state exists
- Regression test fails → from_main=False default not preserving existing structural merge behavior

## Cycle 2.3: Delete/modify conflict auto-resolution (FR-3)

When `from_main=True`, auto-resolve delete/modify conflicts by accepting theirs (main's deletion). Detect via `git status --porcelain`: DU = deleted by theirs, UD = deleted by us.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** Two tests:
1. from_main with DU conflict (main deleted file, branch modified it): call `_auto_resolve_known_conflicts` with from_main=True. Assert: file resolved (accepted deletion), removed from conflicts list.
2. Regression: same DU conflict without from_main → remains in conflicts list (not auto-resolved).

**GREEN:** In `_auto_resolve_known_conflicts(conflicts, slug, from_main)`: when from_main, detect DU conflicts via `git status --porcelain`, resolve each by `git rm <file>` + `git add <file>`, remove from conflicts list. Report resolved files via `click.echo`.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → DU conflict may not be in test fixture; verify delete/modify scenario creates proper conflict markers
- `git status --porcelain` shows unexpected markers → verify merge state is active (MERGE_HEAD exists)
- Regression test (worktree→main) changes behavior → from_main guard not gating correctly

## Cycle 2.4: E2E integration — session.md + structural resolution

End-to-end test with real git repos verifying FR-1 and FR-3 together.

**Files:** new test file `tests/test_worktree_merge_from_main.py`

**RED:** Create real git repo: initial commit, create branch, diverge both (main deletes a file + adds tasks to session.md, branch modifies deleted file + has focused session). Call `merge("main", from_main=True)`. Assert: session.md is branch's version (ours), deleted file is gone (theirs accepted), merge succeeds (exit 0), main is ancestor of HEAD.

**GREEN:** Should already pass from Cycles 2.1-2.3. If not, debug the integration gap.

**Dependencies:** Cycles 2.1, 2.2, 2.3

**Stop/Error Conditions:**
- RED passes before all prior cycles implemented → test fixture may not exercise the right code paths
- Integration fails despite unit cycles passing → wiring issue between merge pipeline and resolution functions
- Session.md content differs from branch's original → resolve or remerge not keeping ours

**Checkpoint:** `just precommit` — session.md and structural resolution verified for both directions.

### Phase 3: Direction-aware learnings.md resolution and CLI (type: tdd, model: sonnet)

## Cycle 3.1: `resolve_learnings_md` from-main policy (FR-2)

When `from_main=True`, invert ours/theirs in diff3: main (theirs) is base, branch (ours) additions are delta.

**Files:** `src/claudeutils/worktree/resolve.py`

**RED:** Set up merge with conflicting learnings.md. Main has consolidated learnings (fewer entries), branch has original + new entries. Call `resolve_learnings_md(conflicts, from_main=True)`. Assert: result uses main's entries as base, branch-only entries appended, entries in both not doubled.

**GREEN:** Add `from_main: bool = False` to `resolve_learnings_md`. When from_main: swap ours/theirs when calling `diff3_merge_segments` — pass theirs_segs as ours and ours_segs as theirs. The diff3 merge then treats main as the authoritative base and branch entries as additions.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → conflict fixture may not include learnings.md; verify index stages :1:/:2:/:3: exist
- Entries doubled in result → ours/theirs swap logic incorrect; check which side is base vs delta
- Branch-only entries missing → diff3 treating branch entries as deletions instead of additions

## Cycle 3.2: `remerge_learnings_md` from-main policy (FR-2)

When `from_main=True`, invert ours/theirs in the phase 4 all-paths learnings merge.

**Files:** `src/claudeutils/worktree/remerge.py`

**RED:** Two tests:
1. from_main=True: MERGE_HEAD state with divergent learnings. Call `remerge_learnings_md(from_main=True)`. Assert: produces main-base + branch delta content.
2. Regression: from_main=False (default): existing behavior unchanged — ours as base.

**GREEN:** Add `from_main: bool = False` to `remerge_learnings_md`. When from_main: swap ours_segs/theirs_segs in `diff3_merge_segments` call, and swap role in statistics output.

**Dependencies:** Cycle 3.1

**Stop/Error Conditions:**
- RED passes before implementation → verify MERGE_HEAD exists in test fixture
- Regression test fails → from_main=False default not preserving existing ours-base behavior
- Statistics output wrong → ours/theirs labels swapped but counts not adjusted

## Cycle 3.3: CLI `--from-main` flag (C-3)

Add Click `--from-main` flag to merge command. Mutually exclusive with slug argument.

**Files:** `src/claudeutils/worktree/cli.py`

**RED (CliRunner):**
1. `merge --from-main` on a branch where main is ancestor → exit 0
2. `merge --from-main some-slug` → exit 1 with error message
3. `merge` (no args, no flag) → exit 1/2 with usage error

**GREEN:** Make slug optional (`required=False`). Add `--from-main` flag. Validation: if from_main and slug → error; if not from_main and not slug → error. When from_main: call `merge_impl("main", from_main=True)`.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → CliRunner may be catching exceptions differently; verify exit codes
- Click argument parsing conflicts → optional slug + flag may need callback-based validation
- Existing `merge <slug>` tests break → slug must remain positional and functional when --from-main absent

## Cycle 3.4: Full E2E — `--from-main` merge happy path

End-to-end via CliRunner with real git repos exercising all FRs.

**Files:** `tests/test_worktree_merge_from_main.py` (extend from Cycle 2.4)

**RED:** Create real git repo with main + worktree branch, diverge both (main modifies learnings + deletes file, branch has focused session + new learnings + modified deleted file). Invoke via CliRunner: `merge --from-main`. Assert: session ours, learnings main-base + branch delta, deleted file gone, main ancestor of HEAD, exit 0.

**GREEN:** Should already pass from all prior cycles. If not, debug integration gap.

**Dependencies:** Cycles 3.1, 3.2, 3.3, Phase 2

**Stop/Error Conditions:**
- RED passes before all prior cycles → test fixture may not exercise all code paths
- CliRunner exit code non-zero → check stderr output for specific error
- Learnings content wrong → verify diff3 inversion producing main-base + branch delta
- Session content wrong → verify ours-keep policy active in full pipeline

**Checkpoint:** `just precommit` — all FRs verified, CLI working, full E2E passing.

### Phase 4: Skill and documentation updates (type: inline, model: opus)

## Step 4.1: Add Mode D to SKILL.md and update enumeration sites

Add Mode D (Sync from main) to `agent-core/skills/worktree/SKILL.md` following Mode C structure.

**Mode D content:**
- Invocation: `wt sync` or `wt from-main`, maps to `claudeutils _worktree merge --from-main`
- Sandbox bypass required (same as Mode C)
- Exit code handling parallels Mode C (0=success, 3=conflicts, 1=precommit failure, 2=fatal)
- Key differences from Mode C: session.md keeps ours (worktree focus preserved), learnings.md uses main as base with branch delta appended, delete/modify conflicts auto-resolved (main's structural changes accepted)

**Enumeration sites:** Grep SKILL.md for "merge", "Mode C", "slug" references. Update:
- Principles section: "Merge is idempotent" applies to both directions
- Mode list (if any): add Mode D entry
- Any Mode C references that should mention bidirectional awareness

**Checkpoint:** `just precommit` — skill file validates, all tests pass.

## Weak Orchestrator Metadata

**Total Steps**: 11 (10 TDD cycles + 1 inline step)

**Execution Model**:
- Cycles 1.1-3.4: Sonnet (standard implementation, behavioral code)
- Step 4.1: Opus (agentic prose — skill file editing)

**Step Dependencies**: Phase 1 → Phase 2 + Phase 3 (partially parallel: 2.1-2.3 and 3.1-3.3 independent) → Phase 4

**Error Escalation**:
- Sonnet → User: test failures that persist after GREEN implementation, design ambiguity
- Opus → User: skill wording disputes

**Report Locations**: `plans/worktree-merge-from-main/reports/`

**Success Criteria**: All 5 FRs verified by E2E tests, `just precommit` passes, no regressions in existing 35+ worktree test files.

**Prerequisites**:
- Clean git tree (verified via `git status --porcelain`)
- worktree-merge-resilience plan delivered (provides diff3 infrastructure used by this plan)
