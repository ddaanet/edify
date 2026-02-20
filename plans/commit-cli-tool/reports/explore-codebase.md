# Codebase Exploration: Commit CLI Tool

## Summary

The repo is the `claudeutils` Python package (v0.0.2) with a `claudeutils` Click CLI entry point. It has an `agent-core` git submodule containing all agent skills, fragments, and bin scripts. The pending task is to add a commit CLI command that handles `precommit → gate → stage → commit` across both the main repo and the `agent-core` submodule — absorbing what the `/commit` skill currently does as an LLM procedure into a scriptable CLI command.

---

## 1. Project Structure

**Root:** `/Users/david/code/claudeutils-wt/commit-cli-tool/`

```
agent-core/         Git submodule — skills, agents, fragments, bin scripts
agents/             Session context (session.md, learnings.md, decisions/)
bin/                last-output script (extracts latest Claude session output)
plans/              Runbooks and execution artifacts
scripts/            check_line_limits.sh, scrape-validation.py
src/claudeutils/    Python source (the actual CLI tool)
tests/              Pytest suite
justfile            All recipes (precommit, test, format, wt-*, release, etc.)
pyproject.toml      Project metadata and tooling config
```

**Python module layout (`src/claudeutils/`):**

```
cli.py              Main Click group — entry point (main = cli)
account/cli.py      account subcommand group
compose.py          Markdown composition from YAML config
discovery.py        Session listing
exceptions.py       Custom exceptions
extraction.py       Feedback extraction
filtering.py        Feedback filtering/categorization
markdown*.py        Markdown processing pipeline
model/cli.py        model subcommand group
models.py           Pydantic models (FeedbackItem etc.)
parsing.py          Parsing utilities
paths.py            Path resolution (project history dir, etc.)
planstate/          Plan state tracking module (aggregation, inference, models, vet)
recall/cli.py       recall subcommand group
statusline/cli.py   statusline subcommand group
tokens_cli.py       Token counting via Anthropic API
tokens.py           Token utilities
validation/cli.py   validate subcommand group
when/cli.py         when subcommand group
worktree/           Worktree management (cli.py, merge.py, merge_state.py, resolve.py, session.py, utils.py)
```

---

## 2. pyproject.toml Entry Points

**File:** `/Users/david/code/claudeutils-wt/commit-cli-tool/pyproject.toml`

```toml
[project]
name = "claudeutils"
version = "0.0.2"
requires-python = ">=3.14"

[project.scripts]
claudeutils = "claudeutils.cli:main"
```

Single entry point: `claudeutils` CLI → `claudeutils.cli:main` (alias for `cli` Click group, line 394 of `cli.py`).

**Dependencies:** `click>=8.3.1`, `anthropic>=0.75.0`, `pydantic>=2.0`, `pyyaml>=6.0`, `platformdirs>=4.5.1`, `socksio>=1.0.0`.

**Tooling:** ruff (strict, `select=["ALL"]`), mypy (strict), docformatter, pytest. `agent-core/` excluded from ruff via `exclude = ["agent-core", ...]`.

---

## 3. Existing CLI Modules

**File:** `/Users/david/code/claudeutils-wt/commit-cli-tool/src/claudeutils/cli.py`

Top-level `cli` Click group. Sub-commands:

| Subcommand | Source | Description |
|---|---|---|
| `list` | inline | List top-level sessions |
| `extract` | inline | Extract feedback from session by prefix |
| `collect` | inline | Batch collect from all sessions |
| `analyze` | inline | Filter/categorize feedback |
| `rules` | inline | Extract rule-worthy items |
| `tokens` | inline | Count tokens via Anthropic API |
| `compose` | inline | Compose markdown from YAML config |
| `markdown` | inline | Process markdown files from stdin |
| `account` | `account/cli.py` | Account subcommands |
| `model` | `model/cli.py` | Model subcommands |
| `recall` | `recall/cli.py` | Recall subcommands |
| `statusline` | `statusline/cli.py` | Statusline subcommands |
| `validate` | `validation/cli.py` | Validation subcommands |
| `when` | `when/cli.py` | When subcommands |
| `_worktree` | `worktree/cli.py` | Worktree management (internal, underscore-prefixed) |

**No existing `commit` subcommand.** The worktree CLI is the closest structural analog.

---

## 4. Existing Precommit: `just precommit`

**File:** `/Users/david/code/claudeutils-wt/commit-cli-tool/justfile` (lines 18-27)

```bash
precommit:
    sync                          # uv sync (skipped in Claude Code sandbox: [ -w /tmp ])
    run-checks                    # ruff check, docformatter -c, mypy
    pytest_output=$(safe pytest 2>&1)
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped"; fi
    run-line-limits               # scripts/check_line_limits.sh
    report-end-safe "Precommit"
```

**`run-checks`** (bash_prolog helper):
```bash
run-checks() {
    report "ruff check" ruff check -q
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}
```

**`scripts/check_line_limits.sh`:** Python files in `src/` and `tests/`: max 400 lines. Markdown files in `agents/decisions/`: max 400 lines.

**Key property:** `just precommit` only runs Python code quality checks. It does NOT handle git staging or commits.

**Sandbox skip:** `sync()` checks `[ -w /tmp ]` — if in Claude Code sandbox (no `/tmp` write), uv sync is skipped. This means `just precommit` works in sandbox.

---

## 5. `/commit` Skill — Full Details

**File:** `/Users/david/code/claudeutils-wt/commit-cli-tool/agent-core/skills/commit/SKILL.md`

The commit skill is an LLM skill, invoked as `/commit`. It is not a script.

### Flags
- `--context` — skip git discovery (use conversation context)
- `--test` — use `just test` instead of `just precommit` (TDD WIP commits)
- `--lint` — use `just lint` instead
- `--no-gitmoji` — skip gitmoji selection

### Gate A — Session freshness
Read `agents/session.md`. If stale (completed work not recorded, new tasks not recorded), invoke `/handoff --commit` which tail-calls back to `/commit`. If current, proceed.

### Gate B — Vet checkpoint
List changed files via git. For each production artifact (code, scripts, plans, skills, agents), check for vet report in `plans/*/reports/` or `tmp/`. No vet report → delegate to `vet-fix-agent` first. UNFIXABLE vet issues → escalate to user.

### Step 1 — Validation + discovery
```bash
exec 2>&1
set -xeuo pipefail
just precommit   # (or: just test / just lint based on flags)
git status -vv
```

### Step 1b — Submodule check
If `git status` shows modified `agent-core` submodule:
1. `(cd agent-core && git status)` — check if submodule has uncommitted changes
2. If dirty: `(cd agent-core && git add <files> && git commit -m "...")`
3. Stage pointer: `git add agent-core`
4. Continue with parent commit

Uses subshell pattern `(cd submodule && ...)` to avoid changing main session cwd.

### Step 2 — Draft commit message
Format: imperative title (50-72 chars) + blank line + bullet details (WHAT + WHY, quantifiable).

### Step 3 — Gitmoji selection
Read `skills/commit/references/gitmoji-index.txt` (~78 entries). Analyze commit semantics → select most specific emoji → prefix title.

### Step 4 — Stage and commit
```bash
exec 2>&1
set -xeuo pipefail
git add file1.txt file2.txt   # specific files only, not git add -A
git commit -m "$(cat <<'EOF'
🐛 Fix bug title

- Detail 1
- Detail 2
EOF
)"
git status
```

### Post-commit
Display STATUS (next pending task, pending list).

---

## 6. Agent-Core Submodule

**Path:** `/Users/david/code/claudeutils-wt/commit-cli-tool/agent-core/`
**Branch on this worktree:** `commit-cli-tool`
**Pointer commit:** `192101ff06941cce9d15a3c18d47f9af42cfa60f`

**Relationship:** Agent-core is a git submodule. Parent repo contains a pointer commit. Changes to agent-core must be committed inside the submodule first, then the pointer staged/committed in the parent.

**Worktree handling:** Both parent and submodule get parallel worktrees when `just wt-new` or `claudeutils _worktree new` is called. Merging: `just wt-merge` handles submodule resolution (Phase 2) before parent merge (Phase 3).

**Agent-core structure:**
```
agents/          LLM agent definitions (.md files with YAML frontmatter)
bin/             Python/bash scripts used by skills and orchestration
configs/         Shared tool configs (mypy-base.toml, ruff-base.toml, docformatter-base.toml)
docs/
fragments/       Behavioral rules loaded via @-references in CLAUDE.md
hooks/           Claude Code hook scripts (pretooluse-*.sh, submodule-safety.py, etc.)
justfile         sync-to-parent recipe (creates symlinks in .claude/)
plans/           Agent-core's own runbooks
scripts/         Update and maintenance scripts
skills/          LLM skill definitions (/commit, /gitmoji, /handoff, /design, /runbook, etc.)
templates/       Templates for runbook generation
```

**Syncing to parent:** `just sync-to-parent` (in `agent-core/`) creates relative symlinks:
- `.claude/skills/<name>` → `../../agent-core/skills/<name>`
- `.claude/agents/<name>.md` → `../../agent-core/agents/<name>.md`
- `.claude/hooks/<name>` → `../../agent-core/hooks/<name>`

---

## 7. agent-core/bin/ Scripts

**Directory:** `/Users/david/code/claudeutils-wt/commit-cli-tool/agent-core/bin/`

| Script | Description |
|---|---|
| `prepare-runbook.py` | Transforms runbook.md → plan-specific agent file + step files + orchestrator-plan.md. Supports general/TDD/mixed/phase-grouped runbooks. The main orchestration setup tool. |
| `task-context.sh` | Recovers session.md from git history for a task name. Uses `git log -S "<task-name>"` to find the introduction commit. |
| `add-learning.py` | Appends entries to learnings.md |
| `assemble-runbook.py` | Assembles phase-grouped runbook files into a single runbook |
| `batch-edit.py` | Applies batch edits to multiple files |
| `compress-key.py` | Compresses session/learning content |
| `focus-session.py` | Generates focused session.md for worktree creation |
| `learning-ages.py` | Reports ages of learning entries |
| `when-resolve.py` | Resolves `/when` memory index queries |

**Top-level bin/** (`/Users/david/code/claudeutils-wt/commit-cli-tool/bin/`):
- `last-output` — Python script extracting the latest assistant output from Claude session JSONL files. Has a full `argparse` CLI with `-n` (position), `-o` (output file), `-d` (directory) options.

---

## 8. Gitmoji Integration

**Two index copies:**
1. `/Users/david/code/claudeutils-wt/commit-cli-tool/agent-core/skills/gitmoji/cache/gitmojis.txt` — used by standalone gitmoji skill
2. `/Users/david/code/claudeutils-wt/commit-cli-tool/agent-core/skills/commit/references/gitmoji-index.txt` — used inline by `/commit` skill in Step 3

Both are identical format: `emoji - name - description` (78 entries each).

**Selection protocol (commit skill, Step 3):**
- Read entire index (never grep/search — read all 78 entries)
- Analyze commit semantics: type (bug fix, feature, docs, refactor, etc.), scope, impact
- Select most specific matching emoji
- Prefer specific over generic (e.g., 🐛 not 🔧 for bugs)
- Return emoji character only — not `:bug:` format

**Custom additions beyond standard gitmoji.dev set:**
- `🗜️ - compress` — Reducing file size, condensing content, or optimizing for brevity
- `🤖 - robot` — Add or update agent skills, instructions, or guidance

**Gitmoji skill** (`agent-core/skills/gitmoji/SKILL.md`): Standalone invocable skill for on-demand gitmoji selection. Has `scripts/update-gitmoji-index.sh` to refresh from gitmoji.dev. Scope boundary: this skill does NOT analyze git diffs — caller's responsibility.

---

## 9. Git Workflow: Commits Across Main + Submodule

**Current flow (via `/commit` skill — LLM procedure):**

1. Run `just precommit` (validation gate)
2. `git status -vv` to discover changes + staging state
3. Check for modified submodules in output
4. If `agent-core` shows as modified (`M agent-core`):
   - `(cd agent-core && git status)` — check if submodule has uncommitted changes
   - If dirty: `(cd agent-core && git add <files> && git commit -m "message")`
   - `git add agent-core` — stage the pointer update
5. `git add <specific parent files>` — no `-A`
6. `git commit -m "$(cat <<'EOF' ... EOF)"` — heredoc for multiline messages
7. `git status` — verify clean tree

**Worktree merge flow (`just wt-merge`):**

Phase 2 (submodule resolution):
- Compare wt submodule commit vs local HEAD
- If different and not ancestor: `git -C agent-core merge --no-edit $wt_commit`
- `git add agent-core` + `git commit -m "🔀 Merge agent-core from $slug"`

Phase 3 (parent merge):
- `git merge --no-commit --no-ff $branch`
- Conflict resolution: agent-core keeps ours (Phase 2 already handled), session files get special treatment
- `git commit -m "🔀 Merge $slug"`

Post-merge: runs `just precommit` as a gate.

**Python worktree CLI** (`src/claudeutils/worktree/`): Full Python reimplementation of the justfile worktree recipes. Module breakdown:
- `cli.py` — Click commands (new, rm, ls, merge, clean-tree, add-commit)
- `merge.py` — merge logic
- `merge_state.py` — merge state detection and recovery
- `resolve.py` — resolve session.md and learnings.md conflicts
- `session.py` — session.md manipulation (move task to worktree, remove worktree task)
- `utils.py` — `_git()` helper, `wt_path()`, various predicates

---

## 10. Worktree CLI as Structural Template

**File:** `/Users/david/code/claudeutils-wt/commit-cli-tool/src/claudeutils/worktree/cli.py`

The `_worktree` sub-group is the closest structural analog for the new commit CLI. Key patterns:

**Sub-group registration pattern:**
```python
# In worktree/cli.py:
@click.group(name="_worktree")
def worktree() -> None:
    """Worktree commands."""

# In cli.py:
from claudeutils.worktree.cli import worktree
cli.add_command(worktree)
```

**`_git()` helper** (`utils.py`): All git subprocess calls route through this. It captures stdout, raises `CalledProcessError` on failure, handles `env=` and `cwd=` overrides. Reusable for the commit module.

**`add-commit` primitive** (lines 243-251 of worktree/cli.py):
```python
@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files, commit with stdin message."""
    _git("add", *list(files))
    try:
        _git("diff", "--quiet", "--cached")
    except subprocess.CalledProcessError:
        click.echo(_git("commit", "-m", click.get_text_stream("stdin").read()))
```

This is a minimal commit primitive (no validation, no gitmoji, no submodule awareness). The new commit command is a richer version.

---

## Gaps / Open Questions

- **No commit CLI module exists** in `src/claudeutils/`. Will need `src/claudeutils/commit/` with `cli.py` (and supporting modules if needed).
- **Gate A (session freshness)** is inherently LLM-specific (requires reading conversation context). Almost certainly out of scope for a scripted CLI.
- **Gate B (vet checkpoint)** is LLM-specific in the skill, but session.md says "absorbs: Script commit vet gate (Gate B → scripted check)" — this is the core design question for the new tool.
- **Gitmoji selection** requires semantic LLM judgment. A scripted CLI would need to either: (a) accept emoji as an argument, (b) skip it entirely, or (c) call the Anthropic API for selection.
- **The task description** says "Single command: precommit → gate → stage → commit in main + agent-core submodule" — the "gate" is the key design choice.
- **`just precommit` vs subprocess** — the CLI can call `just precommit` as a subprocess (simplest) or replicate its checks in Python (more flexible but duplicates logic).
- **Submodule cwd pattern** — Python equivalent of bash subshell is `subprocess.run(..., cwd="agent-core")`. The `_git()` helper in `utils.py` supports a `cwd` or `-C` argument pattern already.
