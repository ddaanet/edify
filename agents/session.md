# Session Handoff: 2026-02-13

**Status:** Phases 1-8 complete. Precommit passing clean (all warnings resolved).

## Completed This Session

**Complexity refactoring:**
- `parse_memory_index()`: Extracted `_parse_new_format_line()` and `_parse_old_format_line()` helpers
- `check_collisions()`: Extracted `_resolve_entry_heading()` helper, merged two entry loops
- All C901/PLR0912/PLR0915 warnings resolved, `just precommit` passes

**Remember skill update:**
- Updated `agent-core/skills/remember/SKILL.md` Step 4a to generate `/when` or `/how` format entries
- Added trigger naming guidelines: plain prose, 2-5 words, optimize for discovery
- Added operator selection guidance: `/when` for behavioral, `/how` for procedural
- Includes key compression tool verification step
- Implements FR-5 from when-recall design

## Pending Tasks

- [x] **Update remember skill** | haiku
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

**Operator→prefix mapping:** `/when` → "When", `/how` → "How to". Both `_extract_entry_key` and `_build_heading` must use same mapping. Test both operators in every TDD cycle.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/reports/deliverable-review.md` — Findings that drove TDD cycles
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `agent-core/skills/remember/SKILL.md` — Updated to generate `/when` or `/how` format entries
- `src/claudeutils/validation/memory_index_helpers.py` — Contains `_strip_operator_prefix` helper and autofix logic needing update
- `src/claudeutils/recall/index_parser.py` — Refactored: helpers extracted
- `src/claudeutils/validation/memory_index_checks.py` — Refactored: helper extracted
