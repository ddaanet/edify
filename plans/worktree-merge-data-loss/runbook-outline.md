# Worktree Merge Data Loss — Runbook Outline

## Requirements Mapping

| Requirement | Implementation Phase | Items |
|-------------|---------------------|-------|
| FR-1: `rm` classifies branch (merged/focused-only/unmerged) | Phase 1 | Cycles 1.1-1.3 |
| FR-2: `rm` refuses removal when unmerged real history (exit 1) | Phase 1 | Cycles 1.4-1.5 |
| FR-3: `rm` allows focused-session-only removal | Phase 1 | Cycle 1.6 |
| FR-4: `rm` exit codes (0/1/2) | Phase 1 | Cycles 1.4-1.6 |
| FR-5: CLI never suggests destructive commands | Phase 1 | Cycles 1.7-1.8 |
| FR-6: Phase 4 refuses single-parent when merge expected | Phase 1 | Cycles 1.9, 1.11 |
| FR-7: Post-merge ancestry validation | Phase 1 | Cycle 1.12 |
| FR-8: `rm` reports removal type in success message | Phase 1 | Cycles 1.5-1.6 |
| FR-9: Skill Mode C handles `rm` exit 1 | Phase 2 | Step 2.1 |

## Phase Structure

### Phase 1: Core Implementation (type: tdd)

**Scope:** Track 1 (removal guard), Track 2 (merge correctness), shared helpers

**Complexity:** 13 TDD cycles, 3 implementation files + 2 test files

**Model:** haiku

**Cycles:**

#### Track 1: Removal Guard (cli.py)

- Cycle 1.1: Shared helper — `_is_branch_merged(slug)` in utils.py
- Cycle 1.2: Branch classification — `_classify_branch(slug)` returns count and focused flag
- Cycle 1.3: Classification edge case — orphan branch (merge-base failure)
- Cycle 1.4: Guard refuses unmerged real history (exit 1, stderr message with count)
- Cycle 1.5: Guard allows merged branch removal (exit 0, `git branch -d`, "Removed {slug}")
- Cycle 1.6: Guard allows focused-session-only removal (exit 0, `git branch -D`, "Removed {slug} (focused session only)")
- Cycle 1.7: Guard integration — cli.py rm() calls guard before all destructive operations
- Cycle 1.8: No `git branch -D` in output — verify no destructive suggestions in stderr/stdout

#### Track 2: Merge Correctness (merge.py)

- Cycle 1.9: MERGE_HEAD checkpoint — Phase 4 refuses single-parent commit when branch unmerged (exit 2, "merge state lost" message)
- Cycle 1.10: Already-merged idempotency — Phase 4 allows commit when branch already merged (exit 0)
- Cycle 1.11: No MERGE_HEAD + no staged changes — exit 2 if branch unmerged, skip if merged
- Cycle 1.12: Post-merge ancestry validation — `_validate_merge_result(slug)` called after commit, verifies slug is ancestor of HEAD (exit 2 if not)
- Cycle 1.13: Parent repo file preservation — end-to-end test: branch with parent + submodule changes → merge → verify all files present in HEAD

**Checkpoint:** After Cycle 1.13 — Light checkpoint (Fix + Functional)

### Phase 2: Skill Update (type: general)

**Scope:** Track 3 (SKILL.md Mode C documentation)

**Complexity:** ~1 prose edit

**Model:** haiku

**Steps:**

- Step 2.1: Update SKILL.md Mode C step 3 — add `rm` exit 1 handling and escalation guidance

## Key Design Decisions

- **D-1:** Focused session detection via marker text `"Focused session for {slug}"` (cli.py:175)
- **D-2:** `rm` exit codes — 0 (removed), 1 (refused: unmerged), 2 (error)
- **D-3:** No destructive CLI output — report problem, not workaround
- **D-4:** MERGE_HEAD checkpoint — Phase 4 refuses single-parent for unmerged branches
- **D-5:** Ancestry validation — `merge-base --is-ancestor` verifies merge completeness
- **D-6:** Guard before destruction — classification and refusal before ANY removal
- **D-7:** `_is_branch_merged` in utils.py — shared by cli.py and merge.py

## Complexity per Phase

### Phase 1 (TDD)
- **Files:** 3 implementation (cli.py, merge.py, utils.py), 2 test files (test_worktree_rm_guard.py, test_worktree_merge_correctness.py)
- **LOC delta:** ~70 total (~35 cli.py, ~25 merge.py, ~8 utils.py, 2 imports)
- **Dependencies:** Cycles 1.1-1.8 (Track 1) and 1.9-1.13 (Track 2) are independent until checkpoint. Cycle 1.1 (`_is_branch_merged`) is prerequisite for both tracks.
- **Model:** haiku (execution, straightforward git operations)

### Phase 2 (General)
- **Files:** 1 skill doc (agent-core/skills/worktree/SKILL.md)
- **LOC delta:** ~6 lines (prose addition to Mode C step 3)
- **Dependencies:** Requires Phase 1 complete (rm exit 1 behavior exists)
- **Model:** haiku (prose edit)

## Expansion Guidance

**Track independence:** Track 1 (cycles 1.1-1.8) and Track 2 (cycles 1.9-1.13) can be developed in parallel during expansion. Both track test files can be created concurrently. Only the checkpoint requires both tracks complete.

**Shared dependency ordering:** Cycle 1.1 (`_is_branch_merged` in utils.py) must complete before Track 1 cycles 1.4-1.6 and Track 2 cycles 1.9-1.11. This is a foundation cycle for both tracks.

**Test file split:** Two test files for clarity:
- `test_worktree_rm_guard.py` — Track 1 (removal guard, classification, exit codes, messaging)
- `test_worktree_merge_correctness.py` — Track 2 (MERGE_HEAD checkpoint, ancestry validation, parent file preservation)

**Cycle 1.7 integration note:** This cycle integrates guard logic into cli.py rm() function. Implementation must call guard before existing operations (probe, warn, remove_session_task, remove_worktrees, branch deletion, rmtree). Guard refusal (exit 1) must prevent ALL downstream operations.

**Cycle 1.13 end-to-end scope:** This regression test validates the original incident scenario. Create branch in worktree with both parent repo changes (e.g., new file in parent) and submodule changes. Merge via Phase 4. Verify parent repo file exists in HEAD after merge. Test may pass without fixes if bug was environment-specific — defensive checks still valuable.

**Phase 2 sufficiency:** SKILL.md update is straightforward prose — outline detail sufficient, may skip full expansion.
