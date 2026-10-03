# edify plugin

A [Claude Code][claude-code] bundle of skills and agents built around a
`requirements → design → runbook → build` planning and execution pipeline.

The pipeline was torn down in 2026-05, when the ecosystem (superpowers, native
memory) was judged to have caught up, and revived in 2026-08. On revival it was
rewired off the subsystems that did not come back: recall reads
`memory/MEMORY.md` and the memory files it indexes instead of the removed
`edify _recall` CLI, `/commit` and `/handoff` defer to the `commit-commands` and
`handoff` plugins, and the session task frame is `.claude/handoff-task.md`.

A plain subdirectory of the `edify` repo (previously a git submodule). Skills
are invoked as slash commands.

## Skills

Slash-command procedures that inject instructions into the current conversation.
Each lives in `skills/<name>/SKILL.md`.

**Pipeline** — run in sequence; each stage names the next command and stops
there.

| Skill | Purpose |
|-------|---------|
| `/requirements` | Capture and document requirements for design and planning |
| `/design` | Triage complexity, then design the approach; routes simple work straight to `/build` |
| `/runbook` | Decompose a design into a runbook of typed items (tdd slices, general) |
| `/build` | Execute planned work — a runbook, or a design with none — composing a dispatch prompt per item, with verification gates |
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

Utility scripts in `bin/` (POSIX shell and Python 3):

| Script | Purpose |
|--------|---------|
| `bootstrap-venv.sh` | SessionStart hook: provision a venv with the version-matched `edify-cli` via uv |
| `bump-plugin-version.py` | Bump the plugin manifest version |
| `check-version-consistency.py` | Verify plugin and package versions agree |
| `triage-feedback.sh` | Compare predicted against actual complexity after execution |

Plus three in `skills/build/scripts/`, used by `/build`:

- `verify-step.sh` — the clean-tree and precommit gate. `/build` runs it at its
  entry gate and after every committing step: a slice's GREEN and its
  code-review commit, a delegated general item, a review item, an item done in
  session (`/build` §4.1), the phase-boundary commit, the review gate and the
  run's closing commit (`skills/build/references/finishing.md` §3). Never after
  a RED or a test review, whose tests are uncommitted by design.
- `changed-files.sh` — prints the run's base as `BASE:`, then the files the run
  changed: the committed diff from that base to `HEAD`, minus the exempt paths
  and the job's own `plans/<job>/` record. `--phase` takes the current phase's
  base instead. The phase-boundary and review-gate scopes and the triage base
  come from it.
- `exempt-paths.sh` — sourced by the other two, never run: the one definition of
  the three paths dirty by convention (`memory`, `.claude/handoff-*.md`,
  `inbox/*.md`), which the gate tolerates and the changed-files list drops.

## Recipes

`just precommit` runs the plugin's own checks. See `justfile` and
`portable.just`.

[claude-code]: https://docs.claude.com/en/docs/claude-code/overview
