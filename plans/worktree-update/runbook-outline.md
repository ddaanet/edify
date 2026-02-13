# Worktree Update TDD Runbook: Outline

**Design:** `plans/worktree-update/design.md`
**Type:** TDD
**Model:** haiku (execution), sonnet (checkpoints)

---

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: Sibling directory paths (`<repo>-wt/<slug>`) | Phase 1: `wt_path()` | Container detection, path construction |
| FR-2: Worktree-based submodule (shared object store) | Phase 5: `new` command | Replace `--reference` with worktree add |
| FR-3: Sandbox permission registration | Phase 2: `add_sandbox_dir()` + Phase 5 | JSON manipulation, both settings files |
| FR-4: Existing branch reuse | Phase 5: `new` command | Branch detection before creation |
| FR-5: Submodule removal ordering | Phase 6: `rm` command | Submodule first, then parent |
| FR-6: Graceful branch deletion (`-d` with fallback) | Phase 6: `rm` command | Safe delete, warn on unmerged |
| FR-7: 4-phase merge ceremony | Phase 7: `merge` command | Clean tree, submodule, parent, precommit |
| FR-8: Focused session generation | Phase 4: `focus_session()` + Phase 5 | Task extraction, context filtering |
| FR-9: Task-based mode (`--task`) | Phase 5: `new` command | Combines slug + session + creation |
| FR-10: Justfile independence | Phase 8 (non-TDD) | Native bash for wt-ls, both-sides clean for wt-merge |

---

## Phase Structure

### Phase 1: Path Computation (`wt_path()`)

**Complexity:** Medium (4 cycles)
**Files:** `src/claudeutils/cli.py`, `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Register CLI group and extract path computation logic into testable function

**Cycles:**
- 1.1: `wt_path()` basic path construction with CLI group registration
- 1.2: Container detection and sibling paths
- 1.3: Container creation — directory materialization
- 1.4: Edge cases (special characters, root directory, deep nesting)

---

### Phase 2: Sandbox Registration (`add_sandbox_dir()`)

**Complexity:** Medium (4 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_sandbox_registration.py`
**Description:** JSON manipulation for sandbox permissions

**Cycles:**
- 2.1: Create `add_sandbox_dir()` function — basic JSON read/write with nested key path (happy path)
- 2.2: Missing file handling (create from scratch with `{}`)
- 2.3: Nested key creation (`permissions.additionalDirectories` when keys absent)
- 2.4: Deduplication logic (avoid adding existing paths)

**Depends on:** Phase 1 (needs `wt_path()` for container determination)

**Checkpoint:** Post-Phase 2 checkpoint (fix + vet) — JSON manipulation validated before proceeding

---

### Phase 3: Slug Derivation (`derive_slug()`)

**Complexity:** Low (1 cycle)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Fix edge cases in existing `derive_slug()` function

**Cycles:**
- 3.1: Edge case handling (special chars, truncation with trailing hyphen removal, empty/whitespace input)

**Depends on:** Phase 1 (function already exists, verifying behavior)

---

### Phase 4: Focused Session Generation (`focus_session()`)

**Complexity:** Medium (3 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Parse session.md and generate focused content

**Cycles:**
- 4.1: Task extraction by name (with metadata, output formatting)
- 4.2: Section filtering — Blockers and Reference Files (relevant entries only)
- 4.3: Missing task error handling

**Depends on:** None

---

### Phase 5: Update `new` Command + Task Mode

**Complexity:** High (7 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_new.py`
**Description:** Refactor `new` command using extracted functions, add `--task` mode

**Cycles:**
- 5.1: Refactor to use `wt_path()` for sibling paths and existing branch detection/reuse
- 5.2: Worktree-based submodule creation with branch reuse (replace `--reference`)
- 5.3: Sandbox registration (both main and worktree settings files)
- 5.4: Environment initialization (`just setup` with warning on failure)
- 5.5: Add `--task` option with `--session-md` default
- 5.6: Task mode: slug derivation + focused session + tab-separated output (`<slug>\t<path>`)
- 5.7: Session file handling (warn and ignore `--session` when branch exists)

**Depends on:** Phases 1, 2, 4 (functions must exist)

**Checkpoint:** Post-Phase 5 checkpoint (fix + vet + functional) — Integration point validated before merge command

---

### Phase 6: Update `rm` Command

**Complexity:** Medium (5 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Refactor `rm` command with improved removal logic

**Cycles:**
- 6.1: Refactor to use `wt_path()` for path resolution and uncommitted changes warning
- 6.2: Worktree registration probing (parent and submodule)
- 6.3: Submodule-first removal ordering
- 6.4: Post-removal cleanup (orphaned directories and empty container)
- 6.5: Safe branch deletion (`-d` with fallback warning)

**Depends on:** Phase 1 (`wt_path()` function)

**Checkpoint:** Post-Phase 6 checkpoint (fix + functional) — Validates removal ordering correctness before large Phase 7 merge implementation

---

### Phase 7: Add `merge` Command (4-Phase Ceremony)

**Complexity:** High (13 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Implement 4-phase merge ceremony with auto-resolution

**Cycles:**
- 7.1: Phase 1 pre-checks — OURS clean tree (session exempt)
- 7.2: Phase 1 pre-checks — THEIRS clean tree (strict, no session exemption)
- 7.3: Phase 1 pre-checks — branch existence, worktree directory check
- 7.4: Phase 2 submodule resolution — ancestry check
- 7.5: Phase 2 submodule resolution — fetch if needed (with object check)
- 7.6: Phase 2 submodule resolution — merge and commit
- 7.7: Phase 3 parent merge — initiate merge
- 7.8: Phase 3 conflict handling — agent-core auto-resolve
- 7.9: Phase 3 conflict handling — session.md auto-resolve (task extraction)
- 7.10: Phase 3 conflict handling — learnings.md auto-resolve (append theirs-only)
- 7.11: Phase 3 conflict handling — jobs.md auto-resolve
- 7.12: Phase 3 conflict handling — source file abort
- 7.13: Phase 4 precommit validation — run and check exit code

**Depends on:** Phase 1 (`wt_path()` for directory resolution)

**Checkpoint:** Full checkpoint at end of Phase 7 (fix + vet + functional)

---

### Phase 8: Non-Code Artifacts

**Complexity:** Low (not TDD)
**Files:** `justfile`, `agent-core/justfile`, `agent-core/skills/worktree/SKILL.md`, `agent-core/fragments/execute-rule.md`
**Description:** Update justfile recipes, skill, and documentation

**Tasks (not cycles):**
- 8.1: Justfile `wt-ls` — native bash `git worktree list` parsing
- 8.2: Justfile `wt-merge` — add THEIRS clean tree check (strict)
- 8.3: Agent-core justfile — add `setup` recipe
- 8.4: Skill Mode A — use `new --task`, remove inline focus-session
- 8.5: Skill Mode C — use `merge` command
- 8.6: Execute-rule.md — update Worktree Tasks marker (slug-only, no `wt/` prefix)

---

### Phase 9: Interactive Refactoring

**Complexity:** N/A (opus interactive, not delegated)
**Files:** `justfile` (wt-* recipes)
**Description:** Reduce verbosity in justfile recipes, extract shared patterns, apply deslop

**Approach:** Opus interactive session (not TDD, not delegated). User-driven refactoring.

---

## Key Design Decisions Reference

Decision 1 (D1): Path computation — `wt_path(slug)` with container detection
Decision 2 (D2): Worktree-based submodule — `git -C agent-core worktree add`
Decision 3 (D3): Skill primary, recipes independent — zero coupling
Decision 4 (D4): Single implementation — no duplication for shared logic
Decision 5 (D5): Environment init warn only — `just setup` prerequisite
Decision 6 (D6): CLI hidden — `_worktree` prefix
Decision 7 (D7): Task mode — `new --task "<name>"` combines operations
Decision 8 (D8): Justfile independence — both Python merge and justfile check both sides

---

## Complexity Distribution

| Phase | Cycles | Complexity | Model |
|-------|--------|------------|-------|
| 1: Setup + wt_path() | 4 | Medium | haiku |
| 2: add_sandbox_dir() | 4 | Medium | haiku |
| 3: derive_slug() | 1 | Low | haiku |
| 4: focus_session() | 3 | Medium | haiku |
| 5: new command | 7 | High | haiku |
| 6: rm command | 5 | Medium | haiku |
| 7: merge command | 13 | High | haiku |
| 8: Non-code | N/A | Low | sonnet (direct) |
| 9: Refactoring | N/A | N/A | opus (interactive) |

**Total TDD cycles:** 37 (Phases 1-7)

---

## Expansion Guidance

**Phase-by-phase expansion:**
- Each phase generates cycle details with RED/GREEN/Stop Conditions
- Per-phase review by tdd-plan-reviewer (prescriptive code detection)
- Full review after all phases complete (cross-phase consistency)

**Investigation prerequisites:**
- Phase 5 and 7 modify existing `new` and `rm` commands — read current implementations before writing
- Phase 7 merge ceremony — read justfile `wt-merge` recipe (lines 200-310) for reference

**Conformance note:**
- Phase 7 merge command conforms to justfile prototype behavior
- Tests must include exact exit codes (0, 1, 2) and phase outcomes
- Session file auto-resolution strategies must match justfile patterns

**File size tracking:**
- `cli.py` currently ~386 lines
- Phase 5 adds ~100-150 lines (new command refactor + task mode)
- Phase 7 adds ~150-200 lines (merge ceremony)
- Estimate: ~636-736 lines after Phase 7 → split required in Phase 7 cleanup cycle

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Applied consolidations (from LLM failure mode analysis):**
- Phase 0 merged into Phase 1 cycle 1.1 (CLI registration + path computation)
- Phase 2 reordered for foundation-first dependency ordering (2.1→2.2→2.3→2.4)
- Phase 3 collapsed from 3 cycles to 1 (all edge cases in single behavioral cycle)
- Phase 4 cycle 4.5 merged into 4.1 (output formatting as part of extraction contract)
- Phase 5: removed vacuous cycles 5.1 and 5.6, merged 5.9 into 5.7/5.8
- Phase 6: removed vacuous 6.1, merged 6.5+6.6 into single cleanup cycle
- Added checkpoints after Phase 2 and Phase 5 per instruction-loss research

**Consolidation candidates (remaining):**
- Phase 8 tasks 8.1-8.3 (justfile changes) could be consolidated into single task if editing same recipe sections

**Cycle expansion:**
- Phase 1 cycle 1.1: Combine CLI registration with verification (`assert worktree` + help output check)
- Phase 5 cycle 5.2 (worktree-based submodule): Include shell line reference to justfile wt-new recipe (lines 150-180) for object store verification approach
- Phase 7 cycles 7.8-7.12 (conflict handling): Reference justfile wt-merge recipe conflict resolution section (lines 250-290) for auto-resolution patterns
- Phase 7 cycle 7.9 (session.md task extraction): Specify exact regex pattern from design (line 152): `- [ ] **<name>**`
- Phase 6 cycle 6.3 (removal ordering): Note git error message for detection: "fatal: 'remove' refusing to remove..." when order violated

**Checkpoint guidance:**
- Phase 2 checkpoint: Verify JSON manipulation correctness (nested keys, dedup, file creation) before building on it
- Phase 5 checkpoint: Verify `claudeutils _worktree new --task` creates worktree at sibling path and outputs tab-separated format
- Phase 7 checkpoint: Functional validation (create worktree, make conflicting changes, verify auto-resolution), exit code validation (0=success, 1=conflicts/precommit, 2=fatal)

**References to include:**
- Design lines 64-101 (new command update section) → expand into Phase 5 cycle details
- Design lines 123-172 (merge command 4-phase ceremony) → expand into Phase 7 cycle details
- Design lines 178-196 (focus_session function) → expand into Phase 4 cycle details
- Justfile lines 100-300 (wt-* recipes) → reference for conformance verification in test assertions

**Module split guidance (if cli.py >700 lines after Phase 7):**
- Extract functions to `src/claudeutils/worktree/core.py`: wt_path, add_sandbox_dir, derive_slug, focus_session
- Leave CLI commands in `cli.py` as thin wrappers calling core functions
- Update tests to import from core module for function-level tests, cli module for command-level tests
