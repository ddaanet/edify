## 2026-02-21: Evidence from hook-batch pre-execution review

### Source evidence

Full review: `plans/hook-batch/reports/runbook-pre-execution-review.md` (updated version on hook-batch branch, commit `ea706dca`). Original review found 2C/3M/3m, updated review found 3C/4M/3m after deeper analysis of context loss.

### prepare-runbook.py issues

**Model propagation (C1, M3, m3):** Step files get `Execution Model: haiku` from agent's base model, ignoring phase-level `model:` frontmatter. 7 of 16 step files had wrong model. Phase 1 is behavioral changes to an 839-line script — haiku rationalizing test failures is a documented failure mode (learnings: "When haiku rationalizes test failures").

**Phase numbering (C2, M1):** Phases 3-5 step files had wrong Phase metadata (off-by-one). Root cause: prepare-runbook.py counted PHASE_BOUNDARY markers sequentially instead of reading actual phase numbers from source files. 9 of 16 step files affected.

**Phase context not extracted to step files (C3, M5):** Phase-level prerequisites, constraints, and completion validation sections are NOT propagated into step files. Phase 2 lost: test helper replication guidance, NOT-patterns constraint (python3 denied), completion validation with `git merge-base` false positive warning. All 5 phases lost completion validation sections.

**Single agent generation (M4):** Generated one `hook-batch-task.md` agent embedding only Phase 1 context. Phases 2-5 agents received Phase 1's key decisions (D-7 additive directives, Tier 1/2/3 structure) which are irrelevant and confusing for those phases.

**Unjustified interleaving (M2):** Orchestrator plan interleaved Phase 2 and 3 steps (step-2-1, step-3-1, step-2-2, step-3-2) despite no cross-phase dependency. Mixed model tiers within a phase boundary. Caused the phase numbering off-by-one.

### Phase expansion issues (outline → runbook-phase-*.md)

Phase file expansion introduced defects caught by per-phase reviews:
- Phase 2: `startswith('git merge')` without trailing space → false positive on `git merge-base` (critical, same risk the stop conditions documented)
- Phase 3: Non-existent file reference in validation test
- Phase 4: `--summary` placement contradicted prerequisite note; `set -euo pipefail` bug
- Phase 5: Sandbox note missing from validation commands; placement ambiguity; cross-step atomic write discrepancy

Every phase required review+fix pass. The expansion agent produces phase files with bugs that a review agent then catches. The defect introduction rate suggests the expansion prompt or process needs improvement, not just better review.

### Fix applied during hook-batch execution

Commit `ea706dca`: Replaced single agent with 5 per-phase agents (hb-p1 through hb-p5), created per-phase context files (`plans/hook-batch/context/phase-{1-5}.md`), fixed model tags in 8 step files, fixed phase numbers in 9 step files, de-interleaved phases 2+3, fixed boundary labels. Manual patch — not a tooling fix.

### Scope for this task

Two categories:
1. **prepare-runbook.py fixes** — model propagation, phase numbering, context extraction, per-phase agent generation. These are code bugs with clear reproduction.
2. **Phase expansion quality** — expansion agent introduces defects during outline→phase generation. This is a prompt/process quality issue, harder to fix mechanically. May need prompt improvements, additional validation steps, or structural changes to how expansion works.
