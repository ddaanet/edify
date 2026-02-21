# Agent Naming Brainstorm — 2026-02-21

## Problem

Three agent categories use names describing manner or mechanism instead of function:
- `quiet-task` / `quiet-explore` — "quiet" describes output pattern, not role
- `*-task` suffix — "task" is generic, doesn't convey fixed-role executor
- Several agents retain `-agent` suffix (runbook-simplification-agent, test-hooks)

## Constraints (accumulated across 3 rounds)

- **Nouns** for standalone agents (like corrector, not correct)
- **Prefix** for plan-specific executors (clusters in ls/autocomplete)
- **Discoverable:** cold reader understands the role without documentation
- **Easy to spell:** no obscure Latin, archaic English, or ambiguous words
- **Distinct:** three categories must not overlap semantically
- **No collision** with existing names: corrector, reviewer, auditor, refactor

## Category 1: Bespoke Deliverable Agent (quiet-task)

Receives custom prompt per invocation. Produces concrete deliverables (files, scripts, configs), not reports. Returns filepath, terse to orchestrator.

**Semantic territories explored:**
- Latin/construction (faber, mason, forge, smith, wright, mint) — edify root connection but cryptic
- Messenger/delegation (envoy, legate, errand, sortie) — wrong emphasis on fetching vs building
- Guild/production (artisan, maker, crafter, producer) — bespoke maker signal
- Writing (scribe, clerk, author) — too narrow (recording vs creating)

**Decision: artisan** — "skilled maker of bespoke things." Universally known, captures custom-prompted + concrete-deliverable pattern. 7 chars. Phonetic echo of "ArtifactAgent" concept name.

Runners-up: smith (5, strong artifact signal but narrow metallurgy connotation), maker (5, too generic — doesn't distinguish from exploration).

## Category 2: Bespoke Exploration Agent (quiet-explore)

Receives custom prompt per invocation. Produces research findings, analysis, exploration results written to files. Output is knowledge, not concrete deliverable.

**Decision: scout** — "goes out, explores territory, reports back findings." 5 chars, universally known, no spelling ambiguity. Distinct from artisan (scouts don't build things).

Runners-up: surveyor (8, too long), analyst (7, doesn't connote exploration).

## Category 3: Plan-Specific Executors (*-task)

Fixed system prompt per agent type. Executes steps from runbooks. Named after plan or specialty.

**Convention: crew- prefix** — `crew-quality-infra-reform`, `crew-plugin-migration`. "Crew member with fixed role on a named project." Clusters in directory listings. 4-char prefix.

Evaluated alternatives: -hand suffix (4, good but doesn't cluster), -runner suffix (6, generic + long), bare names (0, loses categorical signal), -op (2, too terse/ambiguous).

**Note:** crew- applies to generated plan-specific agents (prepare-runbook output), not manually maintained agents.

## Category 4: TDD Executor (tdd-task)

Standalone TDD cycle executor (RED/GREEN/REFACTOR). Also template for crew-* generation. NOT plan-specific itself — used for custom TDD iterations.

**Decision: test-driver** — "drives tests" via TDD discipline. "Driver" is the D in "Test-Driven Development." 11 chars (longer than ideal but typed infrequently as template agent). Self-documenting, no ambiguity.

Runners-up: driver (6, device-driver ambiguity), prover (6, mathematical connotation), cycler (6, awkward person-noun).

## Additional Renames (consistency)

| Current | New | Rationale |
|---------|-----|-----------|
| runbook-simplification-agent | runbook-simplifier | Noun, drop `-agent` |
| test-hooks | hooks-tester | Noun role-name |

## Deletions

8 plan-specific agent files in `.claude/agents/*-task.md` — detritus from past plans, replaced by crew- convention.

## Process Notes

- 3 rounds of opus brainstorming with progressive constraint refinement
- Round 1: broad exploration (Latin roots, construction metaphors, military, guild, theater)
- Round 2: filtered for discoverability and transparency
- Round 3: focused on tdd-task with brainstorm-name agent (fell back to general-purpose — agent not registered as subagent_type)
