# claudeutils

Workflow infrastructure for [Claude Code][claude-code]. Two parts: a Python CLI
for working with session data and project structure, and a framework of skills,
agents, hooks, and instruction fragments that give Claude Code agents structured
workflows — design, planning, TDD, orchestration, review, and handoff.

Not on PyPI. Install from source:

```bash
git clone https://github.com/ddaanet/claudeutils
cd claudeutils
uv tool install .
```

Requires Python 3.14+ and [uv].

## Agent Framework

The `agent-core/` submodule provides workflow infrastructure for Claude Code
projects. Currently installed as a git submodule with symlinks
(`just sync-to-parent`); converting to a Claude Code plugin.

It ships 18 skills, 14 specialized sub-agents, 23 instruction fragments, and
hooks — but the two things that matter most are structured workflow and memory
management.

### Structured Workflow

Without structure, agent work drifts: incomplete implementations, skipped
reviews, scope creep, no handoff between sessions. The framework imposes a
pipeline:

```
/design → /runbook → [plan-reviewer] → /orchestrate → [vet-fix-agent] → /handoff
```

`/design` triages complexity — simple tasks execute directly, moderate tasks
skip to planning, complex tasks get full Opus architectural design. `/runbook`
produces step-by-step execution plans with per-phase typing (TDD cycles or
general steps). `/orchestrate` dispatches each step to a sub-agent in isolated
context. Vet review follows every production artifact. `/handoff` captures what
happened for the next session.

The pipeline is not mandatory. You can invoke any skill independently. But the
full sequence is what prevents the "works on my prompt" failure mode where a
task succeeds in one session and leaves wreckage for the next.

### Memory Management

Claude Code sessions are stateless — each conversation starts fresh. The
framework maintains persistent project memory across sessions:

- **session.md** — pending tasks, in-progress work, blockers. The handoff
  document between sessions. Agents read it at startup, update it at `/handoff`
- **learnings.md** — institutional knowledge accumulated from mistakes and
  discoveries. Append-only, consolidated via `/remember` when it grows large
- **memory-index.md** — keyword-rich catalog pointing to detailed documentation
  in `decisions/`. Agents scan the index to decide what to load on demand,
  instead of pre-loading everything
- **decisions/** — architectural and implementation decisions, one heading per
  topic. The permanent record that learnings graduate into
- **jobs.md** — plan lifecycle tracking (`requirements` → `designed` → `planned`
  → `complete`)

`claudeutils validate` enforces consistency across these files — cross-reference
integrity, format conventions, key uniqueness.

The memory system solves the "agent amnesia" problem: without it, every session
rediscovers the same decisions, repeats the same mistakes, and loses context
from prior work.

## CLI Commands

### Feedback pipeline

Claude Code stores session data in `~/.claude/projects/`. These commands parse
the JSONL to extract your messages — what you actually said to your agents,
across all sessions.

```bash
# List conversation sessions
claudeutils list

# Extract feedback from a session (prefix match on UUID)
claudeutils extract e12d203f

# Full pipeline: collect all → filter noise → extract rules
claudeutils collect | claudeutils analyze -
claudeutils collect | claudeutils rules --input -
```

`collect` gathers feedback from every session. `analyze` categorizes it
(instructions, corrections, process, code review, preferences) and filters
noise — command output, system messages, single-character responses. `rules`
applies stricter filters and deduplicates for actionable items.

### Markdown cleanup

Claude generates markdown with structural issues that formatters can't handle:
consecutive emoji lines that should be lists, nested code blocks inside
markdown fences, metadata labels with dangling lists. The preprocessor fixes
the structure in place, then you run [dprint] for consistent formatting.

```bash
# Fix files changed in working tree
git status --short | cut -c4- | claudeutils markdown
```

Reads file paths from stdin, modifies files in place.

### Token counting

Count tokens using the Anthropic API. Requires `ANTHROPIC_API_KEY`.

```bash
claudeutils tokens sonnet prompt.md
claudeutils tokens opus file1.md file2.md
claudeutils tokens haiku prompt.md --json
```

Aliases (`haiku`, `sonnet`, `opus`) resolve to the latest model version. Full
model IDs also work.

### Account and model management

Switch between API providers and plan modes. Manage default model overrides.

```bash
claudeutils account status
claudeutils account api
claudeutils account plan

claudeutils model list
claudeutils model set claude-sonnet-4-5-20250929
claudeutils model reset
```

### Composition

Assemble a single markdown file from modular fragments. Used to build agent
definitions and system prompts from reusable pieces.

```yaml
# compose.yaml
output: agents/system-prompt.md
fragments:
  - fragments/core-rules.md
  - fragments/tool-usage.md
  - fragments/project-specific.md
```

```bash
claudeutils compose compose.yaml --validate strict
claudeutils compose compose.yaml --dry-run
```

### Validation

Validate project structure and conventions — memory index consistency, decision
file formatting, job tracking, learnings format, task key uniqueness.

```bash
claudeutils validate                    # all validators
claudeutils validate memory-index       # specific validator
claudeutils validate decisions
claudeutils validate jobs
claudeutils validate learnings
claudeutils validate tasks
```

### Recall analysis

Measure whether agents actually consult relevant memory index entries when
working on related topics. Runs against local session history.

```bash
claudeutils recall --index agents/memory-index.md
claudeutils recall --index agents/memory-index.md --sessions 50 --output report.md
```

### Statusline

Reads the JSON that Claude Code pipes to statusline hooks and formats a
two-line display: model, directory, git status, cost, and context usage on
line one; account mode and usage limits on line two.

Configured as a Claude Code statusline hook — not typically invoked directly.

## Development

```bash
just dev        # format + check + test
just test       # tests only
just check      # lint + type check
just precommit  # all checks (CI equivalent)
```

Python 3.14+ with full type annotations ([mypy] strict). [Pydantic] for data
validation. [pytest] for testing. [ruff] for linting. [uv] for dependency
management. [just] for task running.

## License

MIT

[claude-code]: https://github.com/anthropics/claude-code
[dprint]: https://dprint.dev
[mypy]: https://mypy.readthedocs.io
[pydantic]: https://docs.pydantic.dev
[pytest]: https://pytest.org
[ruff]: https://docs.astral.sh/ruff
[uv]: https://docs.astral.sh/uv
[just]: https://just.systems
