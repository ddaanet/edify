## Runbook Review: hook-batch

**Artifacts reviewed:** orchestrator-plan.md, runbook-outline.md, outline.md, 5 phase files, 16 step files, hook-batch-task.md agent

---

### Critical Issues (3)

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

**C3: Phase 2 content loss — phase-level prerequisites and constraints missing from step files**

Phase 2 (runbook-phase-2.md) has phase-level prerequisites and key decisions that are NOT in step-2-1 or step-2-2:

Lost prerequisites:
- "Read `userpromptsubmit-shortcuts.py` main() — understand hook output JSON structure" — agent executing Cycle 2.1 won't know to study the output format it needs to replicate
- "Read `test_userpromptsubmit_shortcuts.py` lines 1-35 — understand `call_hook()` helper pattern. Replicate this pattern for the new test file." — the instruction to replicate the existing test helper pattern is absent
- "Verify `pretooluse-recipe-redirect.py` does NOT exist yet"

Lost constraints:
- "NOT patterns: `python3` and `python` commands are denied in settings.json but have no project recipe equivalent — do NOT add redirect for these" — step-2-2 has `python3 script.py` in a passthrough test assertion, but the rationale and explicit prohibition are missing. A haiku agent could add python3 as a redirect pattern.

Lost completion validation:
- Phase 2 completion validation section (lines 222-240) including `git merge-base` false positive warning and stop conditions — not in any step file

**Impact:** Phase 2 is a new file with a new test file. The prerequisite to study the existing test helper pattern and replicate it is critical — without it, the agent may invent a different test pattern instead of following the established `call_hook()` convention.

---

### Major Issues (4)

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

**M4: Agent file embeds Phase 1 only — misleading context for Phases 2-5**

hook-batch-task.md embeds Phase 1 content (prerequisites, key decisions, D-7 additive directives, Tier 1/2/3 structure). Steps from Phases 2-5 receive this Phase 1 context, which is irrelevant and potentially confusing — the agent "knows" about Phase 1's scan_for_directive refactor when executing Phase 4's health scripts or Phase 2's recipe-redirect.

Phase 2-5 key decisions and prerequisites are neither in the agent's Common Context nor in the step files. Each phase has its own design decisions (D-1 through D-8) that guide implementation — the executing agent only sees Phase 1's.

**M5: Completion validation sections lost from all phase files**

Each phase file ends with success criteria and stop conditions that aren't extracted into any step file or the orchestrator plan. The orchestrator would need to read phase files at PHASE_BOUNDARY checkpoints, but the orchestrator plan doesn't reference them.

Lost per phase:
- Phase 1: line count check, stop conditions (RED fails to fail, GREEN passes without implementation, TestAnyLineMatching update)
- Phase 2: success criteria, stop conditions (`git merge-base` false positive warning)
- Phase 3: success criteria (execute permissions, edge case handling)
- Phase 4: success criteria (flag file coordination verification)
- Phase 5: success criteria (idempotency, existing hooks preserved, restart note)

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

### Content Loss Summary: Phase Files vs Step Files

| Phase | Step content self-contained? | Phase-level content lost |
|-------|------------------------------|--------------------------|
| 1 | Yes — embedded in agent | N/A (agent has Phase 1 context) |
| 2 | **No** — prerequisites, NOT-patterns constraint, completion validation missing | Critical — new file needs pattern replication guidance |
| 3 | Mostly yes — step prerequisites capture phase decisions | Framing only (key decision rationale) |
| 4 | Mostly yes — step content includes flag file logic, health checks | Framing only (D-4 dual delivery rationale) |
| 5 | Mostly yes — step prerequisites capture sandbox/dedup constraints | Phase-level "verify all 5 scripts exist" checklist |

---

### Assessment

**NEEDS_REVISION** — 3 critical, 5 major issues. C1 (wrong models) and C3 (Phase 2 content loss) are the highest-risk items. Dispatching haiku for Phase 1/2 TDD cycles will produce documented failure modes. Phase 2 step agents lacking the call_hook() replication prerequisite may invent incompatible test patterns.

**Fix approach:** Source phase files are correct. Issues are in generated artifacts (step files, orchestrator plan, agent file).

Options:
- **Regenerate:** Fix prepare-runbook.py's phase numbering and model propagation, re-run. Addresses C1, C2, M1 structurally. Does NOT address C3, M4, M5 (prepare-runbook.py's extraction design doesn't inject phase-level context into steps).
- **Manual patch:** Update 16 step files (model + phase fields), fix orchestrator plan (de-interleave, renumber boundaries), inject Phase 2 prerequisites into step-2-1. Addresses all issues but is error-prone.
- **Hybrid:** Fix prepare-runbook.py for C1/C2/M1, manually inject Phase 2 prerequisites into step-2-1 for C3, add phase file references to orchestrator plan PHASE_BOUNDARY comments for M5.
