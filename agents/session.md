# Session Handoff: 2026-02-13

**Status:** TDD Cycles 1-5 complete (6 commits). All 24 validation tests passing. Precommit blocked on memory-index.md migration (Phase 9).

## Completed This Session

**TDD code fixes (Cycles 1-4):**
- Cycle 1 (e935321): `_extract_entry_key` includes operator prefix — `/when X` → "when x", `/how X` → "how to x"
- Cycle 2 (d11e279): Wire `operator` through `resolve()` signature — query includes operator for fuzzy matching
- Cycle 3 (80f744e): Wire operator from CLI to resolver — removed `# noqa: ARG001`, CLI passes operator
- Cycle 4 (2ade5c3): Extend section mode to H3+ headings — `_resolve_section` now matches all heading levels
- Cycle 5: Autofix function operator prefix handling — `_build_file_entries_map` now includes operator prefix in keys, matches `_extract_entry_key` logic

**Key insight (Cycle 5):**
- Headers dict keys include operator prefix (from heading text "When X")
- Entry dict keys include operator prefix (from `_extract_entry_key`)
- Structural set has NO operator prefix (just title text)
- Solution: Compare headers and entries directly (both have prefix), strip only for structural comparison

## Pending Tasks

- [ ] **Create bin wrapper** — `agent-core/bin/when-resolve.py` | haiku
  - Thin wrapper calling `claudeutils.when.cli.when_cmd()` directly
  - Usage: `when-resolve.py {when|how} <query...>`
  - Shebang: `#!/usr/bin/env python3`
  - Import: `from claudeutils.when.cli import when_cmd`
  - Call: `when_cmd()` (Click handles sys.argv parsing)
  - Make executable: `chmod +x agent-core/bin/when-resolve.py`
  - Reference: Similar to add-learning.py but simpler (no arg parsing, Click handles it)
  - See: plans/when-recall/design.md §Skills Implementation (lines 278-302)

- [ ] **Author skill wrappers** — Phase 8 agentic prose | opus | restart
  - `agent-core/skills/when/SKILL.md` — frontmatter in design.md, body needs authoring
  - `agent-core/skills/how/SKILL.md` — frontmatter in design.md, body needs authoring
  - Run `just sync-to-parent` after creating skills

- [ ] **Migrate memory-index.md to /when format** — Depends on: code fixes | sonnet
  - 152 entries: `Key — description` → `/when key` or `/how key`
  - Heading renames in agents/decisions/*.md: add When/How to prefix
  - Update preamble with consumption header from design spec
  - Migration script: `tmp/migrate-index.py` (has 152-entry operator mapping)
  - Atomic: entries + headings + header in single commit
  - Gate: `just precommit` must pass

- [ ] **Update remember skill** — Depends on: migration | haiku
  - Generate `/when` or `/how` entries with trigger naming guidelines
  - Design spec: §Remember Skill Update

- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Update plan-tdd skill** — Document background phase review agent pattern | sonnet

- [ ] **Execute worktree-update runbook** — `/orchestrate worktree-update` | haiku | restart
  - Plan: plans/worktree-update
  - 40 TDD cycles, 7 phases

- [ ] **Agentic process review and prose RCA** | opus
  - Scope: worktree-skill execution process

- [ ] **Workflow fixes** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **Consolidate learnings** — learnings.md at 319+ lines | sonnet
  - Blocked on: memory redesign

- [ ] **Remove duplicate memory index entries on precommit** | sonnet
  - Blocked on: memory redesign

- [ ] **Update design skill** — TDD non-code steps + Phase C density checkpoint | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** | sonnet

- [ ] **Commit skill optimizations** | sonnet
  - Blocked on: worktree-update delivery

## Blockers / Gotchas

**Autofix functions need updating:** `autofix_index` removes all entries instead of just structural ones. Root cause: autofix logic doesn't account for operator-prefixed keys. Need to strip operator prefix when comparing against structural set, but preserve full key for header matching.

**Precommit broken:** Phase 6 validator enforces /when format but Phase 9 migration not yet executed. 152+ entries fail `check_trigger_format`. Precommit will stay broken until migration completes. Currently 20/24 validation tests pass (4 autofix tests fail).

**Operator→prefix mapping:** `/when` → "When", `/how` → "How to". Both `_extract_entry_key` and `_build_heading` must use same mapping. Test both operators in every TDD cycle.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/reports/deliverable-review.md` — Findings that drove TDD cycles
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `src/claudeutils/validation/memory_index_helpers.py` — Contains `_strip_operator_prefix` helper and autofix logic needing update
- `tests/test_validation_memory_index.py` — 20/24 passing, 4 autofix tests failing
