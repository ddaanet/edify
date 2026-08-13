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
| `/runbook` | Decompose a design into executable steps, typed per phase (TDD cycles, general, inline) |
| `/orchestrate` | Execute a prepared runbook with plan-specific agents and mechanical verification gates (Tier 3) |
| `/inline` | Sequence inline execution — pre-work, execute, post-work (Tier 1/2) |
| `/review-plan` | Review runbook quality: TDD discipline, step clarity, LLM failure modes |
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
| `artisan` | General implementation work within a runbook step |
| `test-driver` | Drives TDD cycles (RED → GREEN) for a runbook phase |
| `tdd-auditor` | Audits TDD discipline after execution |
| `refactor` | Applies deslop directives; escalates what needs a stronger model |
| `corrector` | Reviews produced artifacts against domain criteria |
| `design-corrector` | Corrector specialized for design documents |
| `outline-corrector` | Corrector specialized for design outlines |
| `runbook-corrector` | Corrector specialized for runbooks |
| `runbook-outline-corrector` | Corrector specialized for runbook outlines |
| `runbook-simplifier` | Simplifies over-decomposed runbooks |
| `brainstorm-name` | Generates and scores candidate names |
| `hooks-tester` | Exercises Claude Code hook configurations |

## Documentation

Pipeline reference in `docs/`: `general-workflow.md` and `tdd-workflow.md` for
the two execution modes, `pattern-weak-orchestrator.md` and
`pattern-plan-specific-agent.md` for the orchestration patterns,
`@file-pattern.md` for the `@`-reference convention, `shortcuts.md` for the
slash-command index, and `migration-guide.md` for adopting the pipeline in
another project.

## Scripts

Utility scripts in `bin/` (Python 3):

| Script | Purpose |
|--------|---------|
| `bump-plugin-version.py` | Bump the plugin manifest version |
| `check-version-consistency.py` | Verify plugin and package versions agree |
| `deliverable-inventory.py` | Diff merge-base→HEAD, classify changed files, report counts |
| `prepare-runbook.py` | Expand a runbook into per-step files and plan-specific agent definitions |
| `validate-runbook.py` | Check a runbook's structure before execution |
| `assemble-runbook.py` | Reassemble a split runbook directory into a single document |
| `task-context.sh` | Recover the commit that introduced a named task from git history |
| `triage-feedback.sh` | Compare predicted against actual complexity after execution |

Plus `scripts/create-plan-agent.sh` and `scripts/split-execution-plan.py`,
used by `/runbook` during expansion.

## Recipes

`just precommit` runs the plugin's own checks. See `justfile` and
`portable.just`.

[claude-code]: https://docs.claude.com/en/docs/claude-code/overview
