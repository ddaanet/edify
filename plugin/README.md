# edify plugin

A [Claude Code][claude-code] bundle of framework-agnostic skills and agents,
built around a `requirements → design → runbook → orchestrate` planning and
execution pipeline.

The pipeline was torn down in 2026-05, when the ecosystem (superpowers, native
memory) was judged to have caught up, and revived in 2026-08. On revival it was
rewired off the subsystems that did not come back: recall reads
`memory/MEMORY.md` and the memory files it indexes instead of the removed
`edify _recall` CLI, `/commit` and `/handoff` defer to the `commit-commands`
and `handoff` plugins, and the session task frame is `.claude/handoff-task.md`.

A plain subdirectory of the `edify` repo (previously a git submodule). Skills
are invoked as slash commands.

## Skills

Slash-command procedures that inject instructions into the current
conversation. Each lives in `skills/<name>/SKILL.md`.

**Pipeline** — run in sequence; each stage hands to the next via continuation.

| Skill | Purpose |
|-------|---------|
| `/requirements` | Capture and document requirements for design and planning |
| `/design` | Triage complexity, then design the approach; routes simple work straight to `/inline` |
| `/runbook` | Decompose a design into a runbook of typed items (tdd slices, general, inline) |
| `/orchestrate` | Execute a runbook by composing dispatch prompts per item, with verification gates |
| `/inline` | Sequence inline execution — pre-work, execute, post-work — for work without a runbook |
| `/review` | Review in-progress changes for quality and correctness |

**Standalone** — usable on their own, no pipeline required.

| Skill | Purpose |
|-------|---------|
| `/proof` | Item-by-item structured user validation of an artifact before it ships |
| `/deliverable-review` | Post-execution artifact review, severity-classified against ISO 25010 / IEEE 1012 |
| `/ground` | Ground a methodology in external research before asserting it (diverge–converge) |
| `/formalize` | Verify a Python function against intent via an icontract contract checked with `edify check` (CrossHair) |
| `/recall` | Select and Read relevant memory-index entries for the current task or a given topic |

## Agents

Subagent definitions in `agents/`, dispatched by the pipeline skills.

| Agent | Role |
|-------|------|
| `scout` | Open-ended codebase exploration; writes findings to a report file |
| `artisan` | General implementation work for a dispatched runbook item |
| `test-driver` | Executes one TDD slice dispatch in RED or GREEN mode |
| `tdd-auditor` | Audits TDD discipline after execution |
| `refactor` | Applies deslop directives; escalates what needs a stronger model |
| `corrector` | Reviews produced artifacts against domain criteria |
| `design-corrector` | Corrector specialized for design documents |
| `outline-corrector` | Corrector specialized for design outlines |
| `runbook-corrector` | Corrector specialized for runbooks |
| `runbook-simplifier` | Consolidates redundant patterns in a runbook before `/proof` |
| `brainstorm-name` | Generates and scores candidate names |

## Scripts

Utility scripts in `bin/` (Python 3):

| Script | Purpose |
|--------|---------|
| `bootstrap-venv.sh` | SessionStart hook: provision a venv with the version-matched `edify-cli` via uv |
| `bump-plugin-version.py` | Bump the plugin manifest version |
| `check-version-consistency.py` | Verify plugin and package versions agree |
| `triage-feedback.sh` | Compare predicted against actual complexity after execution |

Plus `skills/orchestrate/scripts/verify-step.sh`, the clean-tree and precommit
gate `/orchestrate` runs after each dispatch.

## Recipes

`just precommit` runs the plugin's own checks. See `justfile` and
`portable.just`.

[claude-code]: https://docs.claude.com/en/docs/claude-code/overview
