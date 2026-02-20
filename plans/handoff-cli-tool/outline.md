# Session CLI Tool — Design Outline

**Task:** `claudeutils _session` command group — mechanical CLI for handoff, commit, and status operations. Internal (underscore prefix, hidden from `--help`). Skills remain the user interface; CLI handles writes, validation, subprocess orchestration.

## Approach

Three subcommands under `_session`: `handoff` (session.md writes + diagnostics), `commit` (sole commit path, sandbox-blacklisted alternatives), `status` (pure data transformation for STATUS display). Each reads structured markdown, performs mechanical operations, returns markdown output. LLM judgment stays in skills.

## Shared Infrastructure

### S-1: Package structure

```
src/claudeutils/
  git.py              NEW — shared git helpers (_git, _is_submodule_dirty)
  session/
    __init__.py
    cli.py            Click group registered as `_session` in parent cli.py
    parse.py          Session.md parser (shared: handoff writes, status reads)
    handoff/
      __init__.py
      cli.py          Subcommand
      pipeline.py     Pipeline + state caching
      context.py      Diagnostic gathering
    commit/
      __init__.py
      cli.py          Subcommand
      gate.py         Vet gate (pyproject.toml patterns + report discovery)
      parse.py        Markdown stdin parser (commit-specific format)
    status/
      __init__.py
      cli.py          Subcommand
      render.py       STATUS output formatting
```

Registration: `cli.add_command(session_group)` in main `cli.py`, same pattern as worktree.

### S-2: `_git()` extraction

Move `_git()` and `_is_submodule_dirty()` from `worktree/utils.py` to `claudeutils/git.py`. Update worktree imports. Submodule operations: `"-C", "agent-core"` as leading args (existing codebase pattern).

### S-3: Error conventions

All subcommands:
- stdout: structured markdown (diagnostics, results)
- stderr: errors (agent sees directly)
- Exit codes: 0=success, 1=pipeline error (runtime failure), 2=input validation (malformed caller input)

### S-4: Session.md parser

Shared parser for session.md structure:
- Status line (between `# Session Handoff:` and first `##`)
- Completed section (under `## Completed This Session`)
- Pending tasks with metadata (model, command, restart, plan directory)
- Worktree tasks section
- Plan directory associations

Used by handoff (locate write targets) and status (read + format).

---

## `_session handoff`

Two modes — fresh (stdin has content) and resume (no stdin, reads state file).

### Input

```markdown
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
```

Required: `**Status:**` line marker and `## Completed This Session` heading.

### Pipeline

**Fresh:**
1. Parse stdin for status marker and completed heading
2. Cache input to state file (before first mutation — enables retry)
3. Overwrite status line in session.md
4. Write completed section (committed detection — see H-2)
5. `just precommit`
   - Failure: output precommit result + learnings age + worktree ls, leave state file, exit 1
6. Output diagnostics (conditional — see H-3)
7. Delete state file

**Resume** (no stdin): load from state file, re-execute from `step_reached`. Agent calls `claudeutils _session handoff` directly on retry.

### H-1: Domain boundaries

| Owner | Responsibility |
|-------|---------------|
| Handoff CLI | Session.md mechanical writes (status overwrite, completed section) + precommit + diagnostics + state caching |
| Worktree CLI | `→ slug` markers |
| Agent (Edit/Write) | Pending task mutations, learnings append + invalidation, blockers, reference files |

Learnings flow: agent writes learnings (Edit) → reviews for invalidation → calls CLI. Manual append before invalidation improves conflict detection via spatial proximity.

### H-2: Completed section write mode

Diff completed section against HEAD (`git diff HEAD -- agents/session.md`, extract section from both):

| Prior state | Behavior |
|---|---|
| No diff (first handoff or content committed) | Overwrite |
| Old removed, new present (agent cleared old) | Append |
| Old preserved with additions | Auto-strip committed content, keep new additions |

Session.md write targets: status line and completed section only. All other sections agent-owned.

### H-3: Diagnostic output

| Diagnostic | Condition |
|-----------|-----------|
| Precommit result | Always |
| Git status/diff | Precommit passed |
| Learnings age | Any entries ≥7 active days (summary line only) |
| Worktree ls | Worktrees exist |

### H-4: State caching

- Location: `<project-root>/tmp/.handoff-state.json`
- Contents: `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}`
- `step_reached`: `"write_session"` | `"precommit"` | `"diagnostics"`
- Created at step 2 (before mutation), deleted on success

---

## `_session commit`

Sole commit path. Reads structured markdown on stdin, produces structured markdown on stdout.

Pipeline: validate → gate → precommit → stage → submodule commit → parent commit.

### Input

```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet

## Submodule Message
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet gate
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
```

**Sections:**
- `## Files` — required, first. Bulleted paths to stage (modifications, additions, deletions — `git add` handles all).
- `## Options` — optional. `no-vet` (skip Gate B), `just-lint` (lint only). Unknown options → error (fail-fast).
- `## Submodule Message` — conditionally required (see C-2). Blockquoted.
- `## Message` — required, last. Blockquoted. Everything from `## Message` to EOF is message body — safe for content containing `## ` lines.

Parsing: `## ` prefix matched against known section names. Unknown `## ` within blockquotes treated as message body.

### Output

Success:
```markdown
## Result
commit: a7f38c2

## Gate
status: passed

## Precommit
status: passed
```

Gate failure — missing report:
```markdown
## Gate
status: failed
unvetted:
- src/auth.py
```

Gate failure — stale report:
```markdown
## Gate
status: failed
reason: stale-report
newest-change: src/auth.py (2026-02-20 14:32)
newest-report: plans/foo/reports/vet-review.md (2026-02-20 12:15)
```

Precommit failure:
```markdown
## Gate
status: passed

## Precommit
status: failed
output: |
  ruff check: 2 errors
  ...
```

Clean-files error:
```markdown
## Error
type: clean-files
files:
- src/config.py

STOP: Listed files have no uncommitted changes. Do not remove files and retry.
```

Warning (commit proceeds, discrepancy surfaced):
```markdown
## Warning
type: orphaned-submodule-message
detail: Submodule message provided but no agent-core changes found. Section ignored.

## Result
commit: a7f38c2
```

Error taxonomy: **stop** (non-zero, no commit) for clean-files, missing submodule message, gate failure, precommit failure. **Warning + proceed** (zero exit) for orphaned submodule message.

### C-1: Gate B — scripted vet check

File classification by path pattern:
```toml
[tool.claudeutils.commit]
require-review = [
    "src/**/*.py",
    "tests/**/*.py",
    "scripts/**",
    "bin/**",
]
```

No patterns → gate passes (opt-in). Report discovery: `plans/*/reports/` matching `*vet*` or `*review*` (not `tmp/`). Freshness: mtime of newest production artifact vs newest report. Stale → fail.

### C-2: Submodule coordination

| agent-core in Files OR staged | Submodule Message present | Result |
|---|---|---|
| Yes | Yes | Commit submodule first |
| Yes | No | **Stop** — needs message |
| No | Yes | **Warning** — ignored |
| No | No | Parent-only commit |

Sequence: partition files → stage + commit submodule → stage pointer → commit parent.

### C-3: Input validation

Each path in Files must appear in `git status --porcelain`. Clean files → error with stop directive. A clean-listed file means the caller's model doesn't match reality (hallucinated edit, silent write failure).

### C-4: Validation levels

| Context | Validation | Option |
|---------|-----------|--------|
| Final commit | `just precommit` | (default) |
| TDD GREEN WIP | `just lint` | `just-lint` |
| First commit | Skip gate only | `no-vet` |
| Combined | `just lint` + skip gate | `just-lint` + `no-vet` |

No option to skip validation entirely.

---

## `_session status`

Pure data transformation. Reads session.md + filesystem state, produces formatted STATUS output. No mutations, no stdin.

### Pipeline

1. Parse session.md (S-4 parser)
2. `claudeutils _worktree ls` for plan states and worktree info
3. Cross-reference plans with pending tasks → find unscheduled plans
4. Detect parallel task groups
5. Render STATUS format to stdout

### Output

Matches execute-rule.md MODE 1 format:

```
Next: <first pending task>
  `<command>`
  Model: <model> | Restart: <yes/no>

Pending:
- <task> (<model if non-default>)
  - Plan: <dir> | Status: <status>

Worktree:
- <task> → <slug>

Unscheduled Plans:
- <plan> — <status>

Parallel (N tasks, independent):
  - task 1
  - task 2
  `wt` to set up worktrees
```

### ST-1: Parallel group detection

Independent when: no shared plan directory, no logical dependency (Blockers/Gotchas), compatible model tier, no restart requirement. Largest group only. Omit section if none.

### ST-2: Graceful degradation

Missing session.md → "No pending tasks." Old format (no metadata) → defaults. Empty sections omitted.

---

## Scope

**IN:**
- `_session` command group (handoff, commit, status)
- Shared session.md parser
- `_git()` extraction to `claudeutils/git.py`
- Handoff: stdin parsing, session.md writes, committed detection, diagnostics, state caching
- Commit: stdin parsing, vet gate (pyproject.toml), input validation, submodule pipeline, structured output
- Status: session.md parsing, plan cross-referencing, parallel detection, STATUS rendering
- Tests (CliRunner + real git repos via tmp_path)
- Registration in main `cli.py`

**OUT:**
- Gate A (session freshness) — `/commit` skill (LLM judgment)
- Commit message drafting, gitmoji selection — skill
- Skill modifications (handoff/commit/status skills updated separately)
- Pending task mutations, learnings, blockers, reference files — agent Edit
- Consolidation delegation — existing skill

**Skill integration (future):** After CLI exists, `/commit` skill simplifies to: Gate A (LLM) → discovery (`git status -vv`) → draft message + gitmoji → pipe to `_session commit`. Current skill steps collapse into one CLI call.

## Phase Notes

- Phase 1: `_git()` extraction + session.md parser — **general**
- Phase 2: Status subcommand — **TDD** (pure function: session.md + filesystem → formatted output)
- Phase 3: Handoff pipeline — **TDD** (stdin parsing, session.md writes, committed detection, state caching, diagnostics)
- Phase 4: Commit parser + input validation — **TDD** (markdown parsing, file status check, submodule message consistency)
- Phase 5: Commit vet gate — **TDD** (pyproject.toml patterns, file classification, report discovery + freshness)
- Phase 6: Commit pipeline + output — **TDD** (staging, submodule coordination, structured output)
- Phase 7: Integration tests — **TDD** (end-to-end across subcommands, real git repos)
