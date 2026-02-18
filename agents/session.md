# Session: Worktree — Design runbook evolution

**Status:** Design complete, ready for direct execution of prose edits.

## Completed This Session

**Design skill complexity gates:**
- Entry gate: artifact-aware triage reads plan directory before classification — existing outline can skip ceremony
- Mid-stream gate: post-outline re-check downgrades complexity when outline reveals simpler work
- File: `agent-core/skills/design/SKILL.md` (+21 lines)

**Outline review (A.6) + user discussion (B):**
- Outline-review-agent found FR-2a anti-pattern gap, FR-3c "mocked I/O" contradiction — fixes applied to outline
- User decisions: rewrite existing anti-pattern entry (not append), leave xfail checkpoint unchanged
- Report: `plans/runbook-evolution/reports/outline-review.md`

**Design skill execution readiness gate:**
- Missing gate: `/design` always routed to `/runbook` after sufficiency gate, even when execution was simple
- Fix: execution readiness criteria inline in Outline Sufficiency Gate section — ≤3 files, prose/additive, insertion points identified, no cross-file coordination
- C.5 references gate by heading name (not positional)
- File: `agent-core/skills/design/SKILL.md`

**Prototype:** `plans/prototypes/recover-agent-writes.py` — extracts Write calls from agent session logs

**Design runbook evolution — design phase complete:**
- `/design plans/runbook-evolution/` invoked → entry gate → sufficiency gate passed → execution readiness passed
- Outline IS the design (no design.md needed)

## Pending Tasks

- [ ] **Execute runbook evolution edits** — direct execution of outline.md prose edits | opus
  - Design: `plans/runbook-evolution/outline.md` (outline = design, sufficiency gate passed)
  - Requirements: `plans/runbook-evolution/requirements.md` (5 FRs)
  - Scope: `agent-core/skills/runbook/SKILL.md` + `agent-core/skills/runbook/references/anti-patterns.md`
  - Insertion points: lines 253 (Phase 0.75), 535 (TDD Cycle Planning), 791 (Testing Strategy section)
  - User decisions: rewrite existing anti-pattern entry (not append), leave xfail checkpoint unchanged
  - Execute edits → vet-fix-agent → `/handoff --commit`

## Blockers / Gotchas

**learnings.md at 207 lines (soft limit 80):**
- No entries ≥7 active days — consolidation batch insufficient
- Size trigger fires but nothing eligible for `/remember`

## Next Steps

Execute prose edits per outline.md in opus session. Read SKILL.md, make 3 insertions + anti-patterns.md edits, then vet.
