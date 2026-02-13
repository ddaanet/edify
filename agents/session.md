# Session Handoff: 2026-02-13

**Status:** Deliverable review round 2 complete. 1 critical, 2 major, 3 minor findings require fixes before merge.

## Completed This Session

**Deliverable review round 2:**
- Full review per `agents/decisions/deliverable-review.md` process
- Inventory: 41 deliverables (14 code, 10 test, 3 agentic prose, 14 documentation)
- Gap analysis: All 12 design steps delivered, no missing or unjustified excess
- Report: `plans/when-recall/reports/deliverable-review-2.md`
- Go/no-go: Fix C-1 and M-1 before merge, M-2 cleanup deferrable

## Pending Tasks

- [ ] **Fix when-recall review round 2 findings** — `/design plans/when-recall/reports/deliverable-review-2.md` | sonnet
  - C-1: `cli.py` replaced worktree import/registration with when_cmd — must restore both
  - M-1: `resolver.py:150` `_handle_no_match()` hardcodes `/when` — needs operator param, fix "how to" candidate parsing
  - M-2: Duplicate `check_orphan_entries`, `check_entry_placement`, `check_structural_entries` in both `memory_index_checks.py` and `memory_index_helpers.py` — facade uses helpers (exact match), checks versions (fuzzy) are dead code
  - N-1: `_build_heading()` `capitalize()` degrades acronyms (TDD→Tdd) — confirmed in `workflow-core.md:40`
  - N-2: `_get_suggestions()` reimplements fuzzy matching (error path only, low impact)
  - N-3: `navigation.py` HeadingInfo uses dataclass not Pydantic (minor convention)

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

- [ ] **Consolidate learnings** — learnings.md at 349+ lines | sonnet
  - Blocked on: memory redesign

- [ ] **Remove duplicate memory index entries on precommit** | sonnet
  - Blocked on: memory redesign

- [ ] **Update design skill** — TDD non-code steps + Phase C density checkpoint | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** | sonnet

- [ ] **Commit skill optimizations** | sonnet
  - Blocked on: worktree-update delivery

## Blockers / Gotchas

**Learnings.md over soft limit:** 349 lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

**C-1 merge hazard:** `cli.py` lines 26 and 148 will conflict on merge to main — both worktree and when_cmd must be present.

## Reference Files

- `plans/when-recall/reports/deliverable-review-2.md` — Round 2 findings (this session)
- `plans/when-recall/reports/deliverable-review.md` — Round 1 findings (2026-02-13 morning)
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `src/claudeutils/when/resolver.py` — M-1 at line 150, N-1 at line 272
- `src/claudeutils/cli.py` — C-1 at lines 26, 148
- `src/claudeutils/validation/memory_index_checks.py` — M-2 dead code at lines 137, 222, 274
