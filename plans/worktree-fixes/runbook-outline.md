# Worktree Fixes — Runbook Outline

**Design:** `plans/worktree-fixes/design.md`
**Created:** 2026-02-14

---

## Requirements Mapping

| Requirement | Phases | Implementation Element |
|-------------|--------|------------------------|
| FR-1: Task name constraints (`[a-zA-Z0-9 .\-]`, max 25 chars, lossless slugs) | Phase 0 | `validate_task_name_format()` in `validation/tasks.py`, `derive_slug()` fail-fast in `cli.py` |
| FR-2: Precommit task name validation | Phase 0 | Integration in `validation/tasks.py::validate()` |
| FR-4: Session merge preserves full task blocks | Phase 1 | `extract_task_blocks()` in new `session.py`, `_resolve_session_md_conflict()` uses blocks |
| FR-5: Merge commit always created | Phase 1 | MERGE_HEAD detection in `merge.py::_phase4_merge_commit_and_precommit()` |
| FR-6: Automate session.md task movement | Phase 2 | `move_task_to_worktree()`, `remove_worktree_task()` in `session.py`, wire into `new`/`rm` |

---

## Phase Structure

### Phase 0: Task name constraints (type: tdd)

**Scope:** FR-1, FR-2 — validation infrastructure
**Complexity:** Low
**Model:** haiku

**Cycles:**

- Cycle 0.1: `validate_task_name_format()` valid names (alphanumeric/space/dot/hyphen)
- Cycle 0.2: `validate_task_name_format()` invalid characters rejected
- Cycle 0.3: `validate_task_name_format()` length constraint (max 25 chars)
- Cycle 0.4: `derive_slug()` fail-fast with format validation
- Cycle 0.5: `derive_slug()` lossless transformation (no truncation)
- Cycle 0.6: Precommit integration in `validate()` function

### Phase 1: Merge fixes (type: tdd)

**Scope:** FR-4, FR-5 — shared session.py module + merge logic fixes
**Complexity:** Moderate
**Model:** haiku

**Cycles:**

- Cycle 1.1: `extract_task_blocks()` and `find_section_bounds()` in new `session.py` (single-line tasks, section boundaries)
- Cycle 1.2: `extract_task_blocks()` multi-line tasks with continuation lines
- Cycle 1.3: `extract_task_blocks()` section filter (Pending vs Worktree)
- Cycle 1.4: `_resolve_session_md_conflict()` block-based comparison preserving continuation lines
- Cycle 1.5: `_resolve_session_md_conflict()` insertion point via `find_section_bounds()`
- Cycle 1.6: `_phase4` MERGE_HEAD detection logic
- Cycle 1.7: `_phase4` always commits when merge in progress (`--allow-empty`)
- Cycle 1.8: `_phase4` empty-diff merge creates commit, branch deletable via `git branch -d`
- Cycle 1.9: `focus_session()` uses `extract_task_blocks()` preserving continuation lines

### Phase 2: Session automation (type: tdd)

**Scope:** FR-6 — automated task movement
**Complexity:** Moderate
**Model:** haiku

**Cycles:**

- Cycle 2.1: `move_task_to_worktree()` moves single-line task
- Cycle 2.2: `move_task_to_worktree()` appends `→ <slug>` marker
- Cycle 2.3: `move_task_to_worktree()` creates Worktree Tasks section if missing
- Cycle 2.4: `move_task_to_worktree()` preserves multi-line task blocks
- Cycle 2.5: `remove_worktree_task()` reads worktree branch state
- Cycle 2.6: `remove_worktree_task()` removes completed tasks
- Cycle 2.7: `remove_worktree_task()` keeps incomplete tasks
- Cycle 2.8: `new --task` E2E calls `move_task_to_worktree()`
- Cycle 2.9: `rm` command reordering (check state before branch deletion)
- Cycle 2.10: `rm` E2E calls `remove_worktree_task()`

### Phase 3: Skill update (type: general)

**Scope:** Documentation update
**Complexity:** Low
**Model:** opus

**Steps:**

- Step 3.1: Remove manual session.md editing from Mode A step 4
- Step 3.2: Remove manual session.md editing from Mode B step 4
- Step 3.3: Simplify Mode C step 3 removal instructions
- Step 3.4: Document automated task movement behavior

---

## Key Decisions Reference

**From design.md:**

1. **TaskBlock as lines, not parsed fields** — Task blocks are arbitrary metadata in continuation lines. Parsing into structured fields adds complexity. Merge/movement copy blocks intact.

2. **Section-aware extraction** — `extract_task_blocks()` accepts section filter. Same task name can appear in Pending and Worktree during transitions.

3. **Branch check for rm, not merge-result check** — At `rm` time, merged session.md has Worktree Tasks from "ours" (unchanged). Check worktree branch via `git show branch:agents/session.md` for ground truth.

4. **`--allow-empty` for merge commits** — `git merge --no-commit --no-ff` sets MERGE_HEAD. After conflict resolution, staged changes may be empty. `git commit --allow-empty` creates merge commit regardless, making branch an ancestor.

5. **Validation in derive_slug AND precommit** — Fail-fast at creation time (`derive_slug()`) + precommit catches manual edits. Defense in depth.

6. **Shared `validate_task_name_format()` function** — Both `derive_slug()` and precommit call same function. Single source of truth.

---

## Complexity Per Phase

| Phase | Cycles/Steps | Files Changed | Model |
|-------|--------------|---------------|-------|
| Phase 0 | 6 cycles | `cli.py`, `validation/tasks.py`, tests | haiku |
| Phase 1 | 9 cycles | `session.py` (new), `merge.py`, `cli.py`, tests | haiku |
| Phase 2 | 10 cycles | `cli.py`, `session.py`, tests | haiku |
| Phase 3 | 4 steps | `SKILL.md` | opus |

**Total:** 25 cycles + 4 steps across 4 phases

---

## Expansion Guidance

**Phase 0:**
- Parametrize valid/invalid character test cases aggressively (8+ cases: alphanumeric, space, period, hyphen, special chars, empty, whitespace-only, length boundary) — single parametrized test saves token overhead
- `derive_slug()` tests must verify ValueError raised with clear message
- Precommit integration test: create session.md with invalid task names, run validator, assert errors

**Phase 1:**
- Cycle 1.1 creates new module `src/claudeutils/worktree/session.py` with dataclass `TaskBlock` + both `extract_task_blocks()` and `find_section_bounds()` — consolidates existence checks for both utility functions (avoids vacuous scaffolding cycle for `find_section_bounds()`)
- `extract_task_blocks()` needs careful boundary detection: next `- [ ]`/`- [x]`/`- [>]` task, next `## `, or EOF
- Task block regex: `^- \[[ x>]\] \*\*(.+?)\*\*` (no em dash — unlike validation/tasks.py pattern, Worktree Tasks entries use `→ \`slug\`` not ` — `)
- Test with realistic multi-line blocks from actual session.md examples
- Cycles 1.6-1.8 (`_phase4`): Verify git state transitions explicitly (MERGE_HEAD presence/absence, branch ancestry via `git log --oneline`) not just function return values
- `_phase4` test must verify `git branch -d` succeeds after empty-diff merge (integration check)
- `focus_session()` test verifies full blocks preserved in output
- Cross-reference existing merge test pattern: `test_worktree_merge_conflicts.py::test_merge_conflict_session_md`

**Phase 2:**
- `move_task_to_worktree()` operates on main repo's session.md, not worktree copy
- `remove_worktree_task()` must run BEFORE `git branch -d` (reorder `rm` command operations)
- E2E tests verify session.md state after CLI commands complete
- Branch state check uses `git show {branch}:agents/session.md` (must parse output)

**Phase 3:**
- Prose editing, no test cycles needed
- Remove manual instructions, add note about CLI automation
- Cross-reference CLI commands in documentation

**All phases:**
- Use E2E tests with real git repos via `tmp_path` fixtures (per `agents/decisions/testing.md`)
- Follow existing test patterns in `tests/test_worktree_*.py` and `tests/test_validation_*.py`
- No subprocess mocking except for error injection cases
- Verify behavioral outcomes, not just structure (per TDD RED Phase guidance)
- Design Key Decisions (lines 92-107 in this outline) should propagate to relevant cycle GREEN phases (explain WHY implementation matches design choice)

**Checkpoints:**
- After Phase 0: Full checkpoint (fix + vet + functional) — validation infrastructure must work before Phase 1 depends on it
- After Phase 1: Full checkpoint (fix + vet + functional) — session.py and merge fixes are core logic
- After Phase 2: Full checkpoint (fix + vet + functional) — automation wiring completes behavior
- After Phase 3: Light checkpoint (fix + functional only) — documentation only

**Dependencies:**
- Phase 1 depends on Phase 0 completion (`derive_slug()` validation must be in place)
- Phase 2 depends on Phase 1 completion (uses `extract_task_blocks()` from session.py)
- Phase 3 is independent (documentation only)

---

## Success Criteria

**Overall:**
- All 5 FRs satisfied with passing tests
- No regressions in existing worktree tests
- Precommit validation passes
- Line limits maintained (no file >400 lines)

**Per-phase:**
- Phase 0: Invalid task names rejected at creation and precommit
- Phase 1: Multi-line task blocks preserved in merge, empty-diff merges create commits
- Phase 2: Task movement automated in `new --task` and `rm` commands
- Phase 3: Skill documentation updated with automation behavior
