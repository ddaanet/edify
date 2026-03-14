# Brief: Runbook integration-first generation constraint

## 2026-03-14: Outline generation must enforce integration-first

**Problem:** handoff-cli-tool runbook had Phase 7 as separate integration tests — deferred-integration anti-pattern. Cycles 7.1-7.3 tested paths already built in CLI wiring cycles (3.4, 4.7, 6.6). Killed during proof, absorbed into wiring cycles.

**Root cause:** `/runbook` skill Phase 0.75 outline generation doesn't enforce integration-first principle from `tdd-cycle-planning.md` at phase structure level. This is a generation constraint (applied during creation), not a review constraint (the outline doesn't exist yet to review).

**Corrector side:** General anti-pattern: phases where all cycles only exercise production paths built in earlier phases. Not specific to "CLI wiring" — any deferred-integration phase.

**Relation:** Addendum to `plans/runbook-quality-directives/brief.md` — existing plan covers corrector detection but not generation prevention.
