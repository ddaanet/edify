# Commit CLI Tool — Design Outline

## Approach

Create `claudeutils commit` — the sole commit path (direct `git add`/`git commit` sandbox-blacklisted). Reads structured markdown on stdin, produces structured markdown on stdout. The `/commit` skill handles LLM-specific work (session freshness, message drafting, gitmoji) and pipes to this CLI for mechanical execution.

**Pipeline:** validate input → gate → precommit → stage → submodule commit → parent commit.

## Key Decisions

### D-1: Structured markdown I/O

**Rationale:** The caller is exclusively an LLM agent. Traditional CLI flags exist for human ergonomics (tab completion, `--help`, short options). An LLM's native format is markdown — no quoting/escaping errors, natural multiline, extensible without code changes.

**Input (stdin):**

```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- tests/test_commit_gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet

## Submodule Message
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference
> - Remove ambient rule for commit-time vet check

## Message
> ✨ Add commit CLI with scripted vet gate
>
> - Structured markdown I/O (stdin/stdout)
> - Gate B file classification from pyproject.toml patterns
> - Submodule-aware commit pipeline
> - 4 new modules: git.py, commit/cli.py, gate.py, parse.py
```

**Sections:**
- `## Files` — required. Bulleted list of paths to stage. Handles modifications, additions, and deletions (no distinction needed — `git add` handles all). Placed first (primary input, determines pipeline behavior).
- `## Options` — optional. Bulleted list:
  - `no-vet` — skip Gate B (vet report check). For WIP commits and first commits in new plans.
  - `just-lint` — run `just lint` instead of `just precommit`. For TDD GREEN WIP commits.
- `## Submodule Message` — conditionally required (see D-4). Blockquoted content — protects message body from parser interference when it contains `## ` lines.
- `## Message` — required. Blockquoted content. Placed last — everything from `## Message` to EOF is message content, providing maximum safety for free-form content containing markdown headers.

**Output (stdout):**

Success:
```markdown
## Result
commit: a7f38c2

## Gate
status: passed

## Precommit
status: passed
```

Gate failure (non-zero exit, `## Result` omitted) — two subtypes:

Missing-report failure:
```markdown
## Gate
status: failed
unvetted:
- src/auth.py
- tests/test_auth.py
```

Stale-report failure (see D-3 for details):
```markdown
## Gate
status: failed
reason: stale-report
newest-change: src/auth.py (2026-02-20 14:32)
newest-report: plans/commit-cli-tool/reports/vet-review.md (2026-02-20 12:15)
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

Clean-files error (listed files have no uncommitted changes):
```markdown
## Error
type: clean-files
files:
- src/config.py

STOP: Listed files have no uncommitted changes. Do not remove files and retry. Report this error to the user.
```

Warning (commit proceeds, discrepancy surfaced):
```markdown
## Warning
type: orphaned-submodule-message
detail: Submodule message provided but no agent-core changes found. Section ignored.

## Result
commit: a7f38c2

## Gate
status: passed

## Precommit
status: passed
```

**Error taxonomy:**
- **Stop** (non-zero exit, no commit): clean-files, missing submodule message, gate failure, precommit failure. Unrecoverable or possible data loss.
- **Warning + proceed** (zero exit, commit succeeds): orphaned submodule message. Recoverable, CLI handles it, surfaces discrepancy.

**Parsing rules:** Sections identified by `## ` prefix, matched against known section names (`Files`, `Options`, `Submodule Message`, `Message`). Only known names trigger section boundaries — unknown `## ` lines within blockquoted content are treated as message body. Forward-compatible: new section names can be added in code.

**Unknown options:** Unrecognized values in `## Options` → error (exit non-zero). Fail-fast prevents silent misconfiguration from typos (e.g., `just_lint` vs `just-lint`).

### D-2: Shared `_git()` helper

Extract `_git()` from `worktree/utils.py` to `claudeutils/git.py`. Also move `_is_submodule_dirty()` (used by both modules). Keep worktree-specific utilities in `worktree/utils.py`. Update worktree imports.

**Submodule operations:** The existing codebase uses `-C agent-core` as args to `_git()` for submodule context (see `_probe_registrations`, `_remove_worktrees` in `worktree/utils.py`). The commit module uses the same pattern — pass `"-C", "agent-core"` as leading args, no signature change needed.

### D-3: Gate B — scripted vet check

File classification by path pattern from project configuration. Mechanical, no LLM judgment.

**Configuration in `pyproject.toml`:**

```toml
[tool.claudeutils.commit]
require-review = [
    "src/**/*.py",
    "tests/**/*.py",
    "scripts/**",
    "bin/**",
]
```

No patterns configured → gate passes (opt-in). Each project defines what "production artifact" means for its own structure. No hardcoded knowledge of submodule internals — agent-core's gate concerns belong to agent-core, not the parent CLI.

**Vet report discovery:** Search `plans/*/reports/` for files matching `*vet*` or `*review*`. Do NOT search `tmp/` (ephemeral, gitignored). If files matching `require-review` patterns are present and no vet report found → exit 1.

**Report freshness:** Compare mtime of newest production artifact against mtime of newest vet report. If newest artifact is newer than newest report → stale report → gate fails. Deleted files (no disk mtime) skip freshness check.

Stale-report failure output:
```markdown
## Gate
status: failed
reason: stale-report
newest-change: src/auth.py (2026-02-20 14:32)
newest-report: plans/commit-cli-tool/reports/vet-review.md (2026-02-20 12:15)
```

### D-4: Submodule coordination

**Symmetric validation — `## Files` content and git index must agree with `## Submodule Message` presence:**

| agent-core paths in `## Files` OR staged in index | `## Submodule Message` present | Result |
|---|---|---|
| Yes | Yes | Commit submodule |
| Yes | No | **Stop** — submodule changes need explicit message |
| No | Yes | **Warning + proceed** — section ignored, discrepancy surfaced in output |
| No | No | Parent-only commit |

**Commit sequence** (when submodule changes present):
1. Partition `## Files` paths into parent vs submodule sets
2. Stage + commit submodule: `_git("-C", "agent-core", "add", *submodule_files)` then `_git("-C", "agent-core", "commit", "-m", msg)`
3. Stage submodule pointer: `_git("add", "agent-core")`
4. Commit parent with remaining files + pointer

**Pre-staged agent-core changes:** If agent-core has already-staged changes not mentioned in `## Files`, they are committed as part of step 2 (stage includes them). This is correct behavior — the caller listed the explicit files but git staging is cumulative. The submodule message presence check (see table above) uses "agent-core paths in `## Files` OR staged in index" — so pre-staged agent-core content still requires `## Submodule Message`.

### D-5: Input validation

**File status check:** After parsing `## Files`, verify each listed path appears in `git status --porcelain` output (modified, staged, untracked, or deleted). Paths with no uncommitted changes → error with stop directive (see D-1 clean-files error output).

**Rationale:** A listed file with no changes means the caller's filesystem model doesn't match reality — hallucinated edit, silent write failure, or stale state. This must surface, not silently no-op.

### D-6: Validation levels

| Context | Validation | Option |
|---------|-----------|--------|
| Final commit / refactor | `just precommit` (lint + tests + line limits) | (default) |
| TDD GREEN WIP | `just lint` (ruff + docformatter + mypy) | `just-lint` |
| First commit in plan | Skip vet gate only | `no-vet` |
| TDD GREEN WIP + no vet | `just lint` + skip vet gate | `just-lint` + `no-vet` |

No option to skip validation entirely. Escape hatch is removing sandbox blacklist entries.

### D-7: Module structure

```
src/claudeutils/
  git.py              NEW — shared git helpers (_git, _is_submodule_dirty)
  commit/
    __init__.py       NEW — empty
    cli.py            NEW — Click command (reads stdin, writes stdout)
    gate.py           NEW — vet gate logic (classify from pyproject.toml, check reports)
    parse.py          NEW — markdown stdin parser
  worktree/
    utils.py          MODIFIED — import _git from git.py, remove local copy
```

Registration: `cli.add_command(commit)` in main `cli.py`, same pattern as worktree.

## Scope

**IN:**
- `claudeutils commit` CLI command with markdown I/O
- Stdin parser (markdown sections → structured data)
- Vet gate logic (file classification from pyproject.toml + report existence)
- Input validation (file status check, submodule message consistency)
- Submodule-aware commit pipeline
- Shared `_git()` extraction
- Tests (CliRunner + real git repos via tmp_path)

**OUT:**
- Gate A (session freshness) — stays in `/commit` skill (requires LLM)
- Commit message drafting — stays in skill
- Gitmoji selection — stays in skill
- Skill updates to use CLI — separate follow-up task

## Skill Integration (future)

After CLI exists, the `/commit` skill simplifies to:

1. Gate A (LLM — session freshness check)
2. Discovery: `git status -vv` (for message drafting)
3. Draft message + gitmoji (LLM)
4. Pipe structured markdown to `claudeutils commit`

Current skill steps (validation, gate B, submodule check, stage, commit) collapse into one CLI call.

## Phase Notes (for runbook planning)

- Phase 1: Extract `_git()` to shared module — **general** (refactor, no new behavior)
- Phase 2: Stdin parser + input validation — **TDD** (parsing, file status check, submodule message consistency)
- Phase 3: Vet gate — **TDD** (pyproject.toml pattern loading, file classification, report discovery)
- Phase 4: Commit pipeline + output — **TDD** (staging, submodule coordination, structured output)
- Phase 5: Integration tests — **TDD** (end-to-end with real git repos, full pipeline)

Consolidation deferred to runbook tier assessment. Unit tests embedded in TDD phases 2-4. Phase 5 integration tests are distinct (real git repos, full pipeline).
