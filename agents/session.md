# Session Handoff: 2026-02-13

**Status:** Phases 1-8 complete. Precommit passing (2 complexity warnings remain for opus to fix).

## Completed This Session

**Skill wrappers (Phase 8):**
- `agent-core/skills/when/SKILL.md` — behavioral knowledge recall, third-person triggers, three resolution modes
- `agent-core/skills/how/SKILL.md` — procedural knowledge recall, distinct triggers from /when
- `just sync-to-parent` — symlinks in `.claude/skills/`
- Skill-reviewer: both pass (no critical/major issues)
- Post-restart verification: skills discoverable, resolver invokes correctly (file mode returns content, trigger mode returns expected "no match" pre-migration)

**Precommit fixes:**
- Line-length fixes (E501): broke long lines in 6 files to fit 88-char limit
- Docstring fix (D205): added blank line in `test_recall_integration.py`
- Test file splits to meet 400-line limit:
  - `test_when_resolver.py` (443→157 lines) + `test_when_resolver_errors.py` (297 lines)
  - `test_validation_memory_index.py` (604→352 lines) + `test_validation_memory_index_formats.py` (277 lines)
- Removed noqa comments from complexity warnings (opus will refactor)

## Pending Tasks

- [ ] **Refactor complex parsing functions** — Reduce complexity in 2 functions | opus
  - `parse_memory_index()`: C901 (13>10), PLR0912 (14>12), PLR0915 (53>50)
  - `check_collisions()`: C901 (13>10), PLR0912 (13>12)
  - Both are parsing functions with inherent complexity
  - Gate: `just precommit` must pass

- [ ] **Migrate memory-index.md to /when format** — Depends on: refactoring | sonnet
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

**Complexity warnings remain:** Two functions need refactoring for opus:
- `parse_memory_index()` in `src/claudeutils/recall/index_parser.py` (C901, PLR0912, PLR0915)
- `check_collisions()` in `src/claudeutils/validation/memory_index_checks.py` (C901, PLR0912)
- All other precommit checks pass (tests, line limits, formatting)

**Operator→prefix mapping:** `/when` → "When", `/how` → "How to". Both `_extract_entry_key` and `_build_heading` must use same mapping. Test both operators in every TDD cycle.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/reports/deliverable-review.md` — Findings that drove TDD cycles
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `src/claudeutils/validation/memory_index_helpers.py` — Contains `_strip_operator_prefix` helper and autofix logic needing update
- `src/claudeutils/recall/index_parser.py` — `parse_memory_index()` needs complexity reduction
- `src/claudeutils/validation/memory_index_checks.py` — `check_collisions()` needs complexity reduction
