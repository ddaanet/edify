# Runbook Outline: Session CLI Tool

**Design:** `plans/handoff-cli-tool/outline.md`
**Recall:** `plans/handoff-cli-tool/recall-artifact.md`

## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Notes |
|---|---|---|---|
| S-1: Package structure + CLI registration | 1 | 1.2 | `_session` group + `_git` group in main cli.py |
| S-2: `_git()` extraction + submodule discovery | 1 | 1.1 | Move from worktree/git_ops.py, add discover_submodules() |
| S-3: Output/error conventions | 1, all | 1.1 | `_fail()` + `_git_ok()` — conventions applied cross-cutting |
| S-4: Session.md parser | 2 | 2.1–2.2 | Extends existing worktree/session.py + validation/task_parsing.py |
| S-5: Git status/diff utility | 1 | 1.3 | `_git` CLI group with status/diff subcommands |
| H-1: Domain boundaries | 4 | — | Design constraint, not a deliverable step |
| H-2: Committed detection | 4 | 4.3 | Diff-based three-mode write |
| H-3: Diagnostics | 4 | 4.6 | Git status/diff (always) |
| H-4: State caching | 4 | 4.4 | tmp/.handoff-state.json with step_reached resume |
| C-1: Scripted vet check | 5 | 5.3 | pyproject.toml patterns, report freshness |
| C-2: Submodule coordination | 6 | 6.2 | Per-submodule partition + commit + stage pointer |
| C-3: Input validation | 5 | 5.2 | Clean-files check with STOP directive |
| C-4: Validation levels | 6 | 6.4 | Orthogonal: just-lint, no-vet, amend |
| C-5: Amend semantics | 6 | 6.3 | HEAD file check + submodule amend propagation |
| ST-0: Worktree-destined tasks | 3 | 3.1 | Skip `→ slug` and `→ wt` in Next selection |
| ST-1: Parallel group detection | 3 | 3.3 | First eligible consecutive group, cap 5 |
| ST-2: Preconditions + degradation | 2, 3 | 2.2, 3.4 | Missing session.md → exit 2; old format → defaults |
| Integration tests | 7 | 7.1–7.4 | E2E with real git repos via tmp_path |

## Key Decisions

- All output to stdout as structured markdown, exit code carries signal (S-3)
- Existing `worktree/session.py` provides `TaskBlock`, `extract_task_blocks()`, `find_section_bounds()`, `ParsedTask` — new session parser extends/adapts, does not duplicate
- `_git()` extracted from `worktree/git_ops.py` to `claudeutils/git.py`, worktree imports updated
- CliRunner + real git repos via `tmp_path` for all tests
- `_fail()` pattern with `Never` return type for error termination
- Submodule discovery via `git submodule status` / `.gitmodules`, not hardcoded names

---

### Phase 1: Shared infrastructure (type: general)

Extract git utilities and establish package structure. Foundation for all subcommands.

- Step 1.1: Extract git helpers to `claudeutils/git.py`
  - Move `_git()` and `_is_submodule_dirty()` from `worktree/git_ops.py`
  - Add `discover_submodules()` (parse `git submodule status`)
  - Generalize `_is_submodule_dirty()` to accept path parameter instead of hardcoded `"agent-core"`
  - Add `_git_ok(*args) -> bool` (returncode == 0, no exception)
  - Add `_fail(msg, code=1) -> Never` (click.echo to stdout + raise SystemExit)
  - Update all imports in `worktree/git_ops.py`, `worktree/cli.py`, `worktree/merge.py`, `worktree/merge_state.py`, `worktree/resolve.py`
  - Verification: `just precommit` passes, unit tests for `_git_ok()` and `_fail()`

- Step 1.2: Create `claudeutils/session/` package structure
  - `__init__.py`, `cli.py` (Click group), empty subpackages (`handoff/`, `commit/`, `status/`)
  - Register `_session` group in main `cli.py` (hidden=True, underscore prefix)
  - Verification: `claudeutils _session --help` works

- Step 1.3: Add `claudeutils _git status` and `claudeutils _git diff` subcommands
  - Discover submodules, iterate each for status/diff, return structured markdown
  - Output: parent section + per-submodule sections with path prefix labels
  - Register `_git` group in main `cli.py` (hidden=True)
  - Verification: manual test in repo with submodule, unit tests with tmp_path git repo

**Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.

---

### Phase 2: Session.md parser (type: tdd)

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

- Cycle 2.1: Parse all session.md sections with parametrized tests
  - Status line (text between `# Session Handoff:` and first `##`)
  - Completed section (under `## Completed This Session`)
  - Pending tasks with full metadata (model, command, restart, plan directory, `→` markers)
  - Worktree tasks section (same task format, `## Worktree Tasks` section name)
  - Depends on: existing `find_section_bounds()` in `worktree/session.py`
  - Reuses `ParsedTask` from `validation/task_parsing.py`, extends with plan directory extraction
  - Parametrized tests: one case per section type, edge cases for missing/malformed sections

- Cycle 2.2: Full session.md parse — `SessionData` dataclass combining all sections
  - Missing session.md → raise specific error (ST-2: fatal, not degradation)
  - Old format (no metadata) → defaults

**Checkpoint:** All parser tests pass, `just precommit` clean.

---

### Phase 3: Status subcommand (type: tdd)

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

- Cycle 3.1: Render Next task (first pending task without `→` marker, with command and model)
  - Skips `→ slug` (branched) and `→ wt` (destined for worktree)

- Cycle 3.2: Render list sections with parametrized tests
  - Pending section: in-tree tasks with plan status from `_worktree ls` (CLI output, not ad-hoc Python)
  - Worktree section: worktree tasks with slug annotations
  - Unscheduled Plans section: plans with no associated pending task, excluding `delivered`, sorted alphabetically
  - Parametrized tests: one case per section type, empty-section omission for each

- Cycle 3.3: Parallel group detection (ST-1)
  - Independent when: no shared plan directory, no logical dependency
  - First eligible consecutive group, cap 5, omit section if none

- Cycle 3.4: CLI wiring — `claudeutils _session status` Click command
  - Parse session.md, call `_worktree ls`, render output, exit 0
  - Missing session.md → exit 2 (ST-2)
  - Empty sections omitted
  - Depends on: Phase 2 (SessionData parser), Phase 1 (package structure)

**Checkpoint:** `just precommit` — status subcommand fully functional.

---

### Phase 4: Handoff pipeline (type: tdd)

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

- Cycle 4.1: Parse handoff stdin (status marker + completed heading)
  - Validation: `**Status:**` line required, `## Completed This Session` heading required
  - Missing → exit 2

- Cycle 4.2: Status line overwrite in session.md
  - Locate status line between `# Session Handoff:` and first `##`, replace content

- Cycle 4.3: Completed section write with committed detection (H-2)
  - Diff completed section against HEAD via `git diff HEAD -- agents/session.md`
  - Three modes: overwrite (no diff), append (old removed), auto-strip committed content

- Cycle 4.4: State caching (H-4)
  - Cache to `tmp/.handoff-state.json` before first mutation
  - Contents: input_markdown, timestamp, step_reached
  - Resume mode: no stdin → load from state file, re-execute from step_reached

- Cycle 4.6: Diagnostic output (H-3)
  - Git status/diff (always after session.md writes)

- Cycle 4.7: CLI wiring — `claudeutils _session handoff` with fresh/resume modes
  - Fresh: stdin has content → full pipeline
  - Resume: no stdin + state file exists → resume from step_reached
  - Depends on: Phase 2 (SessionData parser for session.md read/locate)

**Checkpoint:** `just precommit` — handoff subcommand fully functional.

- Step 4.8: Update handoff skill — add pre-handoff precommit gate (type: general, model: opus)
  - Add `just precommit` gate to `agent-core/skills/handoff/SKILL.md` after all writes, before STATUS display
  - Coupled deliverable: without this, precommit drops out of handoff flow

---

### Phase 5: Commit parser + vet check (type: tdd)

Markdown stdin parser (commit-specific format) and scripted vet check.

- Cycle 5.1: Parse commit markdown stdin — all sections with parametrized tests
  - `## Files` section (required, bulleted paths)
  - `## Options` section (optional: no-vet, just-lint, amend; unknown options → exit 2)
  - `## Submodule <path>` sections (repeatable, blockquoted; path matches `git submodule status`)
  - `## Message` section (required, blockquoted, everything to EOF; `## ` within blockquotes treated as body)
  - Parametrized tests: one case per section type, plus edge cases (missing required, unknown options, blockquote nesting)

- Cycle 5.2: Input validation — clean files check (C-3)
  - Each path in Files checked against `git status --porcelain`
  - Clean files → exit 2 with STOP directive
  - Amend mode: also check `git diff-tree --no-commit-id --name-only HEAD`

- Cycle 5.3: Scripted vet check (C-1)
  - File classification from `[tool.claudeutils.commit].require-review` patterns in pyproject.toml
  - No patterns → pass (opt-in)
  - Report discovery: `plans/*/reports/` matching `*vet*` or `*review*`
  - Freshness: mtime of newest production artifact vs newest report
  - Stale → exit 1

**Checkpoint:** `just precommit` — parser and vet check tests pass.

---

### Phase 6: Commit pipeline + output (type: tdd)

Staging, submodule coordination, amend semantics, structured output.

- Cycle 6.1: Parent-only commit pipeline (no submodules)
  - Stage files → precommit → git commit → stdout passthrough
  - Success: raw git output, exit 0
  - Precommit failure: diagnostic output, exit 1

- Cycle 6.2: Submodule coordination (C-2)
  - Partition files by submodule path prefix
  - Per-submodule: stage files → commit with submodule message → stage pointer
  - Validation: submodule files without message → exit 1 (stop)
  - Warning: message provided but no submodule changes → warning + proceed

- Cycle 6.3: Amend semantics (C-5)
  - `--amend` flag to git commit
  - Amend validation: files in HEAD commit OR in `git status --porcelain`
  - Submodule amend: amend submodule → re-stage pointer → amend parent

- Cycle 6.4: Validation levels (C-4)
  - `just-lint` option: `just lint` instead of `just precommit`
  - `no-vet` option: skip vet check
  - Options are orthogonal, combinable with amend

- Cycle 6.5: Output formatting
  - Success: git CLI output verbatim (parent unlabeled, submodule labeled `<path>:`)
  - Warning + success: warning prepended to git output
  - Failure: gate-specific diagnostic

- Cycle 6.6: CLI wiring — `claudeutils _session commit` reading stdin, full pipeline
  - Stdin → parse → validate → vet → precommit → stage → commit → stdout
  - Depends on: Phase 5 (parser + vet check), Phase 1 (git helpers, package structure)

**Checkpoint:** `just precommit` — commit subcommand fully functional.

---

### Phase 7: Integration tests (type: tdd)

End-to-end tests with real git repos via `tmp_path`.

- Cycle 7.1: Status integration — real session.md + real plan directories + worktree ls
  - Verify full STATUS output format

- Cycle 7.2: Handoff integration — stdin → session.md mutation → diagnostics
  - Fresh mode with precommit
  - Resume mode from state file

- Cycle 7.3: Commit integration — full pipeline with real git repo
  - Parent-only commit
  - Submodule commit (tmp_path repo with submodule)
  - Amend

- Cycle 7.4: Cross-subcommand — handoff then status reads updated session.md
  - Verifies parser consistency across write (handoff) and read (status) paths

**Checkpoint:** `just precommit` — all tests pass, full suite green.

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Phase type:**
- **Phase 1** is general (infrastructure extraction, no TDD cycles needed — verification is "imports work, precommit passes")
- **Phases 2-7** are TDD — each cycle gets RED/GREEN expansion

**Applied consolidations (simplification pass):**
- Steps 1.1+1.2 merged: all `claudeutils/git.py` functions in single step (same-module, no inter-dependency)
- Cycles 2.1-2.4 merged into 2.1: parametrized section parser (identical pattern, sequential additions to SessionData)
- Cycles 3.2-3.4 merged into 3.2: parametrized list section renderer (identical render pattern)
- Cycles 5.1-5.4 merged into 5.1: parametrized commit stdin parser (identical section-parse pattern)
- See `plans/handoff-cli-tool/reports/simplification-report.md` for full rationale

**Existing code reuse:**
- Phase 2 should import from `validation/task_parsing.py` (`ParsedTask`, `parse_task_line`, `TASK_PATTERN`) and `worktree/session.py` (`find_section_bounds`, `extract_task_blocks`, `_extract_plan_from_block`), not duplicate
- New parser wraps existing functions into a unified `SessionData` model
- `_is_submodule_dirty()` in `worktree/git_ops.py` (line 100-112) hardcodes "agent-core" — Step 1.1 must generalize to accept path parameter

**Checkpoint guidance:**
- Phase 4 (handoff) has 6 cycles (4.5 killed) — consider mid-phase checkpoint after Cycle 4.4 (state caching) before diagnostics integration (4.6). State caching is a natural boundary: mutations + recovery established before diagnostic output
- Each phase checkpoint is `just precommit`

**Cycle expansion:**
- Step 1.1: Import update scope is 5 files (`worktree/git_ops.py`, `worktree/cli.py`, `worktree/merge.py`, `worktree/merge_state.py`, `worktree/resolve.py`) — verify no other consumers via grep before extraction. Now also includes `_git_ok()` and `_fail()` (consolidated from former Step 1.2)
- Step 1.3 (`_git` CLI group): Design specifies `claudeutils _git status` and `claudeutils _git diff` as separate subcommands under a new `_git` group — distinct from `_session` group
- Cycle 4.3 (committed detection): Three modes based on `git diff HEAD` — test each mode explicitly. Design reference: H-2 table in outline.md
- Cycle 5.2 (clean-files + amend): Amend mode adds `git diff-tree` check — design reference C-5 in outline.md
- Cycle 6.2 (submodule coordination): Four-cell matrix from C-2 in design — each cell is a test case

**Subprocess in tests:**
- Use real git repos via `tmp_path`, mock only for error injection (lock files, permission errors)
- `_worktree ls` dependency: status subcommand calls CLI, not internal Python functions. Tests should use CliRunner with a real plan directory structure

**Shared test fixtures:**
- Phases 5-7 need git repos with submodules in `tmp_path` — create a shared conftest fixture
- Phase 4 needs a session.md fixture with realistic structure (both task sections, metadata, blockers)

**References to include:**
- `worktree/git_ops.py` lines 9-23 (`_git()` implementation) and lines 100-112 (`_is_submodule_dirty()`) for extraction scope
- `validation/task_parsing.py` lines 30-42 (`ParsedTask` dataclass) for reuse interface
- `worktree/session.py` lines 120-150 (`find_section_bounds`) and lines 225-245 (`_extract_plan_from_block`) for parser reuse
- `cli.py` line 152 (`cli.add_command(worktree)`) for registration pattern
