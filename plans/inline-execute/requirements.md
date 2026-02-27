# Inline Execution Skill

## Requirements

### Functional Requirements

**FR-1: Classification persistence**
During /design Phase 0 triage, write the classification block to `plans/<job>/classification.md`. Contains: classification, implementation certainty, requirement stability, behavioral code check, work type, artifact destination, evidence summary. Acceptance: file exists after Phase 0 completes; content matches the visible output block format.

**FR-2: Pre-work — task context loading**
On cold-start task pickup (new session, not chaining from /design or /runbook), load task context before execution:
- Run `agent-core/bin/task-context.sh '<task-name>'` to recover origin session
- Read `plans/<job>/brief.md` if present (cross-tree context)
- Read `plans/<job>/recall-artifact.md` if present; batch-resolve via `when-resolve.py`
- If no recall artifact exists, perform lightweight recall: read memory-index, resolve domain-relevant entries

Skip pre-work when chaining directly from /design or /runbook (context already loaded). The chain signal is mechanically detectable: classification.md or outline.md was written in the current conversation.

Acceptance: on cold start, recall artifact entries are resolved into context before any edits. On chain, pre-work is skipped without tool calls.

**FR-3: Execute work**
Execute the implementation — edits, TDD cycles for behavioral code, prose changes. The skill does not prescribe how to implement; it provides the lifecycle wrapper. For behavioral code: RED test → GREEN → verify per cycle (existing Tier 1 pattern).

Acceptance: implementation complete, all edits applied.

**FR-4: Post-work — corrector dispatch**
After implementation, delegate to corrector agent. Include review-relevant entries from recall artifact in corrector prompt (failure modes, quality anti-patterns). Standard corrector scope: changed files, requirements/design context, IN/OUT boundaries.

This replaces ad-hoc corrector/vet dispatch currently scattered across /design Phase B, /design Phase C.5, and /runbook Tier 1. Single corrector dispatch pattern, one place.

Acceptance: corrector runs with recall context; report written to `plans/<job>/reports/`.

**FR-5: Post-work — execution evidence collection**
After corrector completes, collect three evidence signals:
- Files changed: `git diff --stat` against pre-work baseline
- Agent count: count of execution-phase report files in `plans/<job>/reports/` (exclude design-review, outline-review)
- Behavioral code: grep for new function/class definitions in `git diff` output

Acceptance: evidence collection produces structured result with all three signals.

**FR-6: Post-work — triage feedback comparison**
Read `plans/<job>/classification.md`. Compare prediction to collected evidence (FR-5). Apply divergence heuristics:
- Predicted Simple, evidence shows behavioral code or agents → underclassified
- Predicted Complex, evidence shows ≤2 files + 0 agents + no new functions → overclassified
- Match when evidence pattern aligns with prediction

If classification.md absent (no /design ran), skip comparison silently. The Read is the gate — file absence is the negative path.

Acceptance: comparison produces verdict (match / overclassified / underclassified) with evidence summary, or silent skip when no classification file.

**FR-7: Post-work — triage feedback log**
Append comparison result (FR-6) to `plans/reports/triage-feedback-log.md`. Entry format: date, job name, predicted classification, evidence summary, verdict. On divergence, surface inline message: "Triage: predicted [X], evidence suggests [Y] ([summary])." Silent on match.

Acceptance: log grows by one entry per comparison; inline message only on divergence.

**FR-8: Post-work — deliverable-review chaining**
After corrector and evidence collection, set up `/deliverable-review plans/<job>` as the next lifecycle step. Chain via `/handoff [CONTINUATION: /commit]` with deliverable-review as next pending task for the following session.

Acceptance: handoff writes deliverable-review task to session.md pending list. Next session's `s` (status) shows it.

**FR-9: Lifecycle integration — /design exit path**
Replace the current direct-execution sequences in /design Phase B (sufficiency gate) and Phase C.5 (execution readiness) with invocation of this skill. /design determines execution-readiness; this skill handles execution + post-work.

Current pattern (replace):
```
1. Execute edits in current session
2. Delegate to corrector
3. /handoff [CONTINUATION: /commit]
```

New pattern:
```
1. /inline-execute (or equivalent invocation)
   — handles: execute, corrector, evidence, triage feedback, deliverable-review chain, handoff
```

Acceptance: /design sufficiency and execution-readiness gates route to this skill instead of inline steps.

**FR-10: Lifecycle integration — /runbook Tier 1 and Tier 2 exit paths**
Replace the current Tier 1 direct implementation sequence and Tier 2 execution sequence in /runbook with invocation of this skill. /runbook retains tier assessment criteria and Tier 2 lightweight cycle planning, but routes execution to `/inline`.

Current Tier 1 pattern (replace):
```
1. Implement changes directly
2. Delegate to review agent
3. Apply fixes
4. /handoff --commit
```

Current Tier 2 execution pattern (replace):
```
1. For each cycle: delegate via Task (test-driver/artisan)
2. Intermediate checkpoints every 3-5 cycles
3. After delegation complete: delegate to review agent
4. Apply all fixes from review
5. Tail-call /handoff --commit
```

New pattern (both tiers):
```
1. /inline (with plan context already loaded from /runbook)
   — handles: execute (direct or delegated), corrector, evidence, triage feedback, deliverable-review chain, handoff
```

Acceptance: /runbook Tier 1 and Tier 2 assessments route to this skill instead of inline execution steps. /runbook retains Tier 2 criteria, planning, and design-constraint rules. Tier 3 unchanged.

### Non-Functional Requirements

**NFR-1: Lightweight when chaining**
When invoked directly after /design or /runbook (context loaded), pre-work is zero tool calls. Total overhead vs current pattern: evidence collection + triage comparison (3-4 tool calls) + deliverable-review chaining (in handoff).

**NFR-2: Mechanical detection, human correction**
Triage evidence collection (FR-5) and comparison (FR-6) are fully automated. Triage criteria updates remain human decisions.

**NFR-3: Single corrector pattern**
One corrector dispatch template used by this skill. Replaces 3+ ad-hoc corrector invocations across /design and /runbook. Corrector scope, recall context inclusion, and report location defined once.

### Constraints

**C-1: /design writes prediction, this skill reads it**
Classification persistence (FR-1) stays in /design Phase 0. This skill is downstream — it consumes the prediction, never writes it.

**C-2: Classification file format matches existing output block**
No new format — the visible Phase 0 output block IS the persistence format.

**C-3: Divergence heuristics are initial estimates**
Starting points. The feedback loop itself reveals whether they need refinement.

**C-4: Does not replace /orchestrate**
This skill handles Tier 1 (inline) execution. Tier 2/3 work still goes through /orchestrate. The /orchestrate Section 3.0 (inline phases within orchestrated work) is a separate concern — the orchestrator handles those directly.

### Out of Scope

- Automatic triage criteria modification — detection only, not correction
- JSONL transcript parsing — classification persisted to file (FR-1)
- Batch retrospective analysis — can be built later using the log (FR-7) as input
- Tier 2/3 execution — handled by /orchestrate
- /orchestrate Section 3.0 inline phases — orchestrator-direct, separate lifecycle
- Learning entry for patterns (FR-6 from prior version) — deferred; manual review of log sufficient initially

### Dependencies

- `/design` skill — Phase 0 writes classification.md (FR-1); Phase B/C.5 routes to this skill (FR-9)
- `/runbook` skill — Tier 1 routes to this skill (FR-10)
- `/handoff` skill — chained at end for session state + commit (FR-8)
- `corrector` agent — delegated for post-work review (FR-4)

### Open Questions

- Q-1: What git baseline for the diff? Last commit before execution? Branch point? Simplest: `git stash` or `git rev-parse HEAD` captured at skill entry.
- Q-2: Skill name — `/inline-execute`, `/execute`, `/run`? Needs to not collide with existing shortcuts (`x` = #execute from execute-rule.md).
- Q-3: Should the batch retrospective script be a follow-up task?

### References

- `plans/reports/design-skill-grounding.md` — Gap 7 grounding (GJP, AAR, ESI)
- `plans/triage-feedback/problem.md` — original problem statement
- `plans/prototypes/extract-design-metrics.py` — prototype JSONL extraction
- `plans/reports/design-session-empirical-data.md` — n=38 classification distribution
- `agent-core/skills/design/SKILL.md` — Phase B/C.5 direct execution (FR-9 replacement target)
- `agent-core/skills/runbook/SKILL.md` — Tier 1 direct implementation (FR-10 replacement target)
- `agent-core/skills/orchestrate/SKILL.md` — Section 3.0 inline execution (out of scope reference)

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` for new skill creation and modifications to /design and /runbook
