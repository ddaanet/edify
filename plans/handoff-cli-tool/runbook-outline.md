# Runbook Outline: Session CLI Tool

**Design:** `plans/handoff-cli-tool/outline.md`
**Recall:** `plans/handoff-cli-tool/recall-artifact.md`

## Requirements Mapping

| Requirement | Phase |
|---|---|
| S-1: Package structure + CLI registration | 1 |
| S-2: `_git()` extraction + submodule discovery | 1 |
| S-5: Git status/diff utility | 1 |
| S-3: Output/error conventions | 1 (shared `_fail()`) |
| S-4: Session.md parser | 2 |
| Status subcommand (ST-0, ST-1, ST-2) | 3 |
| Handoff pipeline (H-1..H-4) | 4 |
| Commit parser + input validation (C-3) | 5 |
| Commit scripted vet check (C-1) | 5 |
| Commit submodule coordination (C-2) | 6 |
| Commit pipeline + output (C-4, C-5) | 6 |
| Integration tests | 7 |

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

- Step 1.1: Extract `_git()` and `_is_submodule_dirty()` from `worktree/git_ops.py` to `claudeutils/git.py`
  - Move functions, add `discover_submodules()` (parse `git submodule status`)
  - Generalize `_is_submodule_dirty()` to accept path parameter instead of hardcoded `"agent-core"`
  - Update all imports in `worktree/git_ops.py`, `worktree/cli.py`, `worktree/merge.py`, `worktree/merge_state.py`, `worktree/resolve.py`
  - Verification: `just precommit` passes, no broken imports

- Step 1.2: Add `_git_ok()` boolean helper and `_fail()` error termination to `claudeutils/git.py`
  - `_git_ok(*args) -> bool` — returncode == 0, no exception
  - `_fail(msg, code=1) -> Never` — click.echo to stdout + raise SystemExit
  - Verification: unit tests for both helpers

- Step 1.3: Create `claudeutils/session/` package structure
  - `__init__.py`, `cli.py` (Click group), empty subpackages (`handoff/`, `commit/`, `status/`)
  - Register `_session` group in main `cli.py` (hidden=True, underscore prefix)
  - Verification: `claudeutils _session --help` works

- Step 1.4: Add `claudeutils _git status` and `claudeutils _git diff` subcommands
  - Discover submodules, iterate each for status/diff, return structured markdown
  - Output: parent section + per-submodule sections with path prefix labels
  - Register `_git` group in main `cli.py` (hidden=True)
  - Verification: manual test in repo with submodule, unit tests with tmp_path git repo

**Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.

---

### Phase 2: Session.md parser (type: tdd)

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

- Cycle 2.1: Parse status line (text between `# Session Handoff:` and first `##`)
  - Depends on: existing `find_section_bounds()` in `worktree/session.py`

- Cycle 2.2: Parse completed section (under `## Completed This Session`)

- Cycle 2.3: Parse pending tasks with full metadata (model, command, restart, plan directory, `→` markers)
  - Reuses `ParsedTask` from `validation/task_parsing.py`
  - Extends with plan directory extraction (existing `_extract_plan_from_block()`)

- Cycle 2.4: Parse worktree tasks section (same structure, different section name)

- Cycle 2.5: Full session.md parse — `SessionData` dataclass combining all sections
  - Missing session.md → raise specific error (ST-2: fatal, not degradation)
  - Old format (no metadata) → defaults

**Checkpoint:** All parser tests pass, `just precommit` clean.

---

### Phase 3: Status subcommand (type: tdd)

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

- Cycle 3.1: Render Next task (first pending task without `→` marker, with command and model)
  - Skips `→ slug` (branched) and `→ wt` (destined for worktree)

- Cycle 3.2: Render Pending section (in-tree tasks with plan status from `_worktree ls`)
  - Cross-reference plan directories with `claudeutils _worktree ls` output
  - Plan status derived from CLI output, not ad-hoc Python

- Cycle 3.3: Render Worktree section (worktree tasks with slug annotations)

- Cycle 3.4: Render Unscheduled Plans section
  - Plans with no associated pending task, excluding `delivered` status
  - Sorted alphabetically

- Cycle 3.5: Parallel group detection (ST-1)
  - Independent when: no shared plan directory, no logical dependency
  - Largest group only, omit section if none

- Cycle 3.6: CLI wiring — `claudeutils _session status` Click command
  - Parse session.md, call `_worktree ls`, render output, exit 0
  - Missing session.md → exit 2 (ST-2)
  - Empty sections omitted

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

- Cycle 4.5: Precommit integration
  - Run `just precommit` after session.md writes
  - Failure: output precommit result + learnings age, leave state file, exit 1

- Cycle 4.6: Diagnostic output (H-3)
  - Precommit result (always), git status/diff (on pass), learnings age (≥7 active days)
  - Diagnostics conditional on precommit success

- Cycle 4.7: CLI wiring — `claudeutils _session handoff` with fresh/resume modes
  - Fresh: stdin has content → full pipeline
  - Resume: no stdin + state file exists → resume from step_reached

**Checkpoint:** `just precommit` — handoff subcommand fully functional.

---

### Phase 5: Commit parser + vet check (type: tdd)

Markdown stdin parser (commit-specific format) and scripted vet check.

- Cycle 5.1: Parse `## Files` section (required, bulleted paths)

- Cycle 5.2: Parse `## Options` section (optional: no-vet, just-lint, amend)
  - Unknown options → exit 2

- Cycle 5.3: Parse `## Submodule <path>` sections (repeatable, blockquoted message)
  - Path matches submodule directory name from `git submodule status`

- Cycle 5.4: Parse `## Message` section (required, blockquoted, everything to EOF)
  - `## ` within blockquotes treated as message body

- Cycle 5.5: Input validation — clean files check (C-3)
  - Each path in Files checked against `git status --porcelain`
  - Clean files → exit 2 with STOP directive
  - Amend mode: also check `git diff-tree --no-commit-id --name-only HEAD`

- Cycle 5.6: Scripted vet check (C-1)
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

- **Phase 1** is general (infrastructure extraction, no TDD cycles needed — verification is "imports work, precommit passes")
- **Phases 2-7** are TDD — each cycle gets RED/GREEN expansion
- **Existing code reuse:** Phase 2 should import from `validation/task_parsing.py` and `worktree/session.py`, not duplicate. New parser wraps existing functions into a unified `SessionData` model
- **Subprocess in tests:** Use real git repos via `tmp_path`, mock only for error injection (lock files, permission errors)
- **`_worktree ls` dependency:** Status subcommand calls CLI, not internal Python functions. Tests should use CliRunner with a real plan directory structure
- **Submodule test setup:** Phases 5-7 need git repos with submodules in `tmp_path` — create a shared fixture
