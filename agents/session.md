# Session Handoff: 2026-02-17

**Status:** RCA completed on CLI tool usage deviation. Deliverable code findings still pending.

## Completed This Session

**RCA: failure to use CLI for project state queries:**
- Deviation: ad-hoc `python3 -c` scripts to call `list_plans()` instead of `claudeutils _worktree ls`
- Root cause: execute-rule.md used Python function syntax → agent followed literally, skipping project-tooling check
- Deeper cause: specific procedural instructions suppress cross-cutting operational rules (same class as "shortcuts bypass upstream steps")
- Fix: execute-rule.md updated to reference CLI command, prohibit ad-hoc Python (uncommitted)
- Learning added to `agents/learnings.md`: "When querying project state"

## Pending Tasks

- [ ] **Fix deliverable code findings** — M-4/M-5/M-6/M-7 code + test gaps | sonnet
  - M-4: Implement full gate priority chain in inference.py (4 gate types per D-7)
  - M-5: Dynamic phase discovery in vet.py (replace hardcoded map)
  - M-6: Populate TreeInfo with design-specified fields, remove display.py duplication
  - M-7: Add tests for outline-only, problem-only, VetStatus.any_stale
  - Note: apply testing diamond — integration tests for wiring (M-4 gate wiring, M-6 display path), unit for combinatorial (M-4 gate types)
  - Reports: `deliverable-review-code.md`, `deliverable-review-test.md`

- [ ] **Design runbook evolution** — `/design plans/runbook-evolution/` | opus | restart
  - Requirements at `plans/runbook-evolution/requirements.md`
  - Outline exists at `plans/runbook-evolution/outline.md` — resume from Phase A.6 (outline review)
  - Scope: runbook SKILL.md generation directives only

- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution
  - Different scope and execution profile

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)

## Blockers / Gotchas

**test_submodule_safety failures from main:**
- 4 tests failing: cd-and-single, cd-and-chain, cd-and-pytest, dquote-and
- From merged main content, not workwoods changes
- Precommit passes (1026/1027, 1 xfail)

**learnings.md at 139 lines (soft limit 80):**
- No entries at ≥7 active days — consolidation trigger not met

**Gate wiring incomplete in display path:**
- `list_plans()` → `infer_state()` never passes `vet_status_func`, so `PlanState.gate` is always None in production
- Addressed by M-4 but wiring through aggregate_trees → list_plans → infer_state is separate

**`_task_summary` not wired to display:**
- Function exists and is tested (4 tests) but not called from `format_rich_ls`
- Addressed by M-6 (TreeInfo enrichment)

## Next Steps

Fix deliverable code findings (M-4/M-5/M-6/M-7). Deliverable fixes before pipeline improvements.

---
*Handoff by Sonnet. RCA on CLI usage, deliverable code fixes next.*
