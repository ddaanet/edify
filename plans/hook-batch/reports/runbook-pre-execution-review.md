The data confirms systematic issues. Here's my review.

---

## Runbook Review: hook-batch

**Artifacts reviewed:** orchestrator-plan.md, runbook-outline.md, outline.md, 5 phase files, 16 step files, hook-batch-task.md agent

---

### Critical Issues (2)

**C1: All Phase 1 and Phase 2 step files have wrong execution model (haiku instead of sonnet)**

Every step file has `**Execution Model**: haiku` at line 4 — prepare-runbook.py defaulted to the agent's base model. Phase 1 (`model: sonnet` in frontmatter, High complexity) and Phase 2 (`model: sonnet`) need sonnet.

Phase 1 is behavioral changes to an 839-line script with additive scanning refactors, section scoping, and regex pattern guards. The learnings explicitly document haiku rationalizing test failures on this exact class of work (Cycle 1.2 of worktree-update: haiku committed with 3 failing regression tests, required sonnet escalation).

**Affected:** step-1-1 through step-1-5, step-2-1, step-2-2 (7 files)

**C2: Step file Phase metadata systematically off-by-one for Phases 3-5**

| Step files | Phase in file | Correct Phase |
|-----------|---------------|---------------|
| step-3-1, step-3-2 | 2 | 3 |
| step-4-1, step-4-2, step-4-3 | 3 | 4 |
| step-5-1, step-5-2, step-5-3, step-5-4 | 4 | 5 |

9 of 16 step files have wrong Phase metadata. An orchestrator reading Phase metadata to determine context (which phase file to reference) would load the wrong phase.

**Root cause:** Orchestrator plan interleaves Phase 2 and 3 steps, and prepare-runbook.py counted phase boundaries rather than using actual phase numbers from the source files.

---

### Major Issues (3)

**M1: Orchestrator plan PHASE_BOUNDARY labels misnumbered**

| Step | Boundary label | Actually ends |
|------|---------------|--------------|
| step-1-5 | "phase 1" | Phase 1 ✓ |
| step-3-2 | "phase 2" | Phases 2+3 ✗ |
| step-4-3 | "phase 3" | Phase 4 ✗ |
| step-5-4 | "phase 4" | Phase 5 ✗ |

The orchestrator uses PHASE_BOUNDARY to insert review checkpoints. If it applies the Phase 2 checkpoint criteria (TDD) at the step-3-2 boundary, it reviews Phase 3 general work with TDD criteria.

**M2: Phase 2+3 interleaving with no dependency justification**

Orchestrator plan orders: step-2-1, **step-3-1**, step-2-2, step-3-2. Phase 3 (PostToolUse auto-format, haiku) is interleaved with Phase 2 (PreToolUse recipe-redirect, sonnet TDD). The cross-phase dependencies section in runbook-outline.md states no dependency between Phase 2 and Phase 3. Unjustified interleaving:
- Mixes model tiers within a phase boundary (sonnet TDD + haiku general)
- Caused the systematic Phase metadata off-by-one (C2)
- Confuses checkpoint placement (M1)

**M3: Step 5-3 model contradiction — header says haiku, body says sonnet**

step-5-3.md line 4: `**Execution Model**: haiku`
step-5-3.md line 15: `**Execution Model:** Sonnet`
Phase 5 prerequisites: "Step 5.3 requires Sonnet model (justfile edit requires careful placement and context)"

If orchestrator reads line 4 (generated header), it dispatches haiku for a justfile edit that the phase author explicitly flagged as needing sonnet.

---

### Minor Issues (3)

**m1: Growth projection understates risk**

Outline says 839→~980 lines is "well within limits." The 400-line module limit (project-config.md) is already exceeded by 2x at 839 lines. Growth to ~980 doesn't change compliance status (already non-compliant), but "well within limits" is misleading — it implies the limit doesn't apply. Should state explicitly whether hook scripts are exempt or acknowledge pre-existing limit exceedance.

**m2: Step 3.2 is a validation-only step**

Step 3.2 runs the same commands already listed in Step 3.1's Validation section. It creates no artifact and modifies no files. Could be merged into Step 3.1. The expansion guidance noted this: "If expansion adds no substance beyond what Step Detail already specifies, keep the phase compact."

**m3: Agent file has conflicting model in frontmatter vs embedded phase content**

hook-batch-task.md frontmatter: `model: haiku`
Embedded at line 149: `model: sonnet` (from Phase 1 content)

The agent's base model (haiku) contradicts the embedded phase requirement (sonnet). The orchestrator must override with the step-level model, but the step-level model is also wrong (C1).

---

### Assessment

**NEEDS_REVISION** — C1 and C2 must be fixed before execution. Dispatching haiku for Phase 1/2 TDD cycles on an 839-line behavioral script will produce the failure mode documented in learnings (haiku rationalizing test failures). The Phase metadata errors (C2) and boundary misnumbering (M1, M2) will cause wrong checkpoint criteria and context loading.

**Fix approach:** The source phase files are correct. The issues are all in generated artifacts (step files, orchestrator plan). Fixing the generation source won't help since prepare-runbook.py has already run. Options:
- Regenerate: fix prepare-runbook.py's phase numbering and model propagation, re-run
- Manual patch: update the 16 step files' Execution Model and Phase fields, fix orchestrator plan boundaries, de-interleave Phase 2/3
