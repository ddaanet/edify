# RCA: General-Step Detection Gap in Review Axes

**Date:** 2026-02-13
**Incident:** Worktree-update-recovery runbook had vacuous steps and density issues caught only by manual review. plan-reviewer agent checks TDD discipline but lacks equivalent detection criteria for general-step phases.

---

## Executive Summary

Detection criteria in `agents/decisions/runbook-review.md` are TDD-specific (RED/GREEN/cycles terminology). General steps have equivalent failure modes (vacuity, density, dependency ordering) but no documented detection criteria. The review pipeline has two bypass paths: outline review (Phase 0.75) checks only general-step LLM failure modes, and fast-path (Phase 0.95) skips outline review entirely.

**Root cause:** Documentation-driven review approach without enforcement of type-agnostic LLM failure mode detection at both outline and expanded levels.

**Impact:** General-step runbooks can pass plan-reviewer with vacuous steps, density issues, and ordering violations because review criteria only apply to TDD phases.

---

## 1. Root Cause

**Primary cause:** Detection criteria in `agents/decisions/runbook-review.md` are TDD-specific.

**Evidence:**

From `agents/decisions/runbook-review.md`:

```markdown
### Vacuous Cycles

Cycles where RED tests don't constrain implementation. Haiku satisfies them with degenerate GREEN (structurally correct, behaviorally meaningless).

**Detection — a cycle is vacuous when any of:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- Cycle tests presentation format (output shape) rather than semantic correctness
```

All four detection criteria use TDD-specific language (RED/GREEN/cycles). General steps have equivalent failure modes:
- General vacuity: Step only creates scaffolding without functional outcome
- General density: Adjacent steps with <1 branch point difference
- General ordering: Step N depends on structure from step N+k

**Why this is the root cause:**

The review pipeline is documentation-driven. plan-reviewer agent (lines 63-86 in `agent-core/agents/plan-reviewer.md`) loads review-plan skill, which references `agents/decisions/runbook-review.md` as the source of detection criteria. If criteria don't cover general steps, the agent cannot detect issues.

---

## 2. Contributing Factors

### 2.1 Outline Review Scope Gap

**Location:** `agent-core/agents/runbook-outline-review-agent.md` lines 116-137

The outline review agent checks LLM failure modes (vacuity, intra-phase ordering, density, checkpoint spacing) and includes general-step language:

```markdown
**Vacuity:**
- Each step/cycle must test a branch point or produce a functional outcome
- Flag steps where RED can be satisfied by `import X; assert callable(X)` (TDD) or where the step only creates scaffolding without behavior (adhoc)
```

**However:** Outline review happens at Phase 0.75, before expansion. LLM failure modes can be introduced during expansion (Phase 1) when the planner elaborates steps. No re-validation of LLM failure modes occurs after expansion for general-step phases.

**Contrast with TDD:** plan-reviewer checks TDD discipline (prescriptive code, RED/GREEN sequencing) which catches some expansion-time degradation. General-step phases have no equivalent post-expansion check.

### 2.2 Fast-Path Bypass

**Location:** `agent-core/skills/runbook/SKILL.md` lines 326-348 (Phase 0.95)

Phase 0.95 "Outline Sufficiency Check" promotes outlines directly to runbooks when:
- Every item specifies target files/locations
- Every item has concrete action
- Every item has verification criteria
- No unresolved design decisions

**If sufficient → promote outline to runbook:**
- Skip to Phase 4 (prepare artifacts and handoff)
- **Bypasses:** Phase 1 (per-phase expansion), Phase 3 (final holistic review)

**Impact:** Outline review is the ONLY quality gate when fast-path activates. If outline review doesn't catch general-step issues, no downstream review will.

**Evidence from session:** Worktree-update-recovery runbook was Tier 3 (simplified), used Tier 2 fast-path route (user noted "originally 6 steps, now 4 after density/vacuity fixes"). Manual review detected:
- 2 Medium: density (Steps 1.3+1.4 same file), vacuity (Step 1.2 echo stub)
- 2 Low: dependency metadata inaccuracy, checkpoint spacing

### 2.3 1:1 Finding-to-Step Heuristic

**Location:** Implicit heuristic in review reasoning

When expansion creates 1:1 mapping between outline items and expanded steps, density analysis is skipped. The heuristic assumes "outline reviewed = expansion safe." But expansion can introduce verbosity and structural issues not present in compact outline form.

**Example:** Outline says "Fix C2 and C3." Expansion creates Step 1.1 (fix C2) and Step 1.2 (fix C3). If both touch same file and C3 depends on C2, this is density + ordering violation. But 1:1 mapping masks the issue because outline-level consolidation check passed.

### 2.4 Type-Agnostic Criteria Not Propagated to Phase Review

**Location:** `agent-core/agents/plan-reviewer.md` lines 79-83

```markdown
**All phases (LLM failure modes):**
- Vacuity: Items that don't constrain implementation (merge into behavioral items)
- Dependency ordering: Foundation-first within phases (reorder or UNFIXABLE if cross-phase)
- Density: Adjacent items with <1 branch point difference (collapse)
- Checkpoint spacing: Gaps >10 items or >2 phases without checkpoint
```

This section correctly states type-agnostic criteria. However:
1. Detection methodology lives in `agents/decisions/runbook-review.md` (TDD-specific language)
2. review-plan skill (lines 259-283) references the TDD-specific criteria file
3. No parallel detection methodology exists for general steps

**Gap:** Plan-reviewer declares intent to check LLM failure modes for all phases, but implements TDD-specific detection only.

---

## 3. Evidence

### 3.1 Worktree-Update-Recovery Manual Findings

From session.md:

```
**Runbook review (manual, against runbook-review.md axes):**
- 2 Medium: density (Steps 1.3+1.4 same file), vacuity (Step 1.2 echo stub)
- 2 Low: dependency metadata inaccuracy (parallel claim), checkpoint spacing
- Collapsed 6 steps → 4: merged 1.1+1.2 (justfile edits), merged 1.3+1.4 (cli.py fixes)
- Fixed dependency metadata (was "all parallel", now notes same-file and ordering constraints)
```

**Significance:** Manual review used `agents/decisions/runbook-review.md` as reference (session note: "manual, against runbook-review.md axes") and found issues plan-reviewer missed. This proves the criteria exist but the automated review doesn't apply them to general steps.

### 3.2 Detection Criteria Format in runbook-review.md

All four axes use TDD-centric language:
- **Vacuous Cycles** (line 9): "Cycles where RED tests don't constrain implementation"
- **Dependency Ordering** (line 23): "Cycles that reference structures not yet created"
- **Cycle Density** (line 36): "Unnecessary cycles that dilute expansion quality"
- **Checkpoint Spacing** (line 50): Uses "cycles" throughout

**General steps equivalent:**
- Vacuous steps: Create scaffolding without functional outcome
- Dependency ordering: Step N tests behavior depending on structure from step N+k
- Step density: Adjacent steps with <1 branch point difference
- Checkpoint spacing: (same as TDD — this one is truly type-agnostic)

### 3.3 Outline Review Has General-Step Detection

From `agent-core/agents/runbook-outline-review-agent.md` line 118:

```markdown
- Flag steps where RED can be satisfied by `import X; assert callable(X)` (TDD) or where the step only creates scaffolding without behavior (adhoc)
```

Proof that general-step detection criteria exist in outline review, but not in post-expansion phase review.

### 3.4 review-plan Skill References TDD-Specific Criteria

From `agent-core/skills/review-plan/SKILL.md` line 260:

```markdown
### 11. LLM Failure Modes (CRITICAL) — all phases

Criteria from `agents/decisions/runbook-review.md` (four axes). Apply regardless of phase type.
```

The skill directs agents to `runbook-review.md` for detection methodology, but that file only provides TDD-specific detection patterns.

---

## 4. Proposed Fixes

### Fix 1: Add General-Step Detection Section to runbook-review.md

**File:** `agents/decisions/runbook-review.md`

**Action:** Add section "General-Step Equivalents" after the four TDD axes:

```markdown
## .General-Step Detection Equivalents

The four axes apply to general-step phases with adapted detection criteria.

### Vacuous Steps

Steps that only create scaffolding without functional outcome. Haiku satisfies them with directory creation, echo statements, or structural changes that don't affect behavior.

**Detection — a step is vacuous when any of:**
- Step creates files/directories without adding functional content
- Step output is template text or echo statements (no computation)
- Step tests integration wiring (A calls B) when called function already verified
- Step describes presentation changes (formatting, layout) without semantic effect

**Action:** Merge into nearest behavioral step or elevate preamble.

### Dependency Ordering (General)

Steps that reference structures not yet created. Executing agent must either create them ad-hoc (scope creep) or assume their existence (coupling to future work).

**Detection — ordering problem exists when:**
- Step N modifies/extends structure created in step N+k (k>0)
- Step N's implementation assumes data shape that later step establishes
- Step references "newly created file" that doesn't exist until later step

**Action:** Reorder foundation-first. If cross-phase: UNFIXABLE (outline revision needed).

### Step Density

Unnecessary steps that dilute focus and increase context pressure.

**Detection — steps should collapse when:**
- Two adjacent steps modify same file with <1 branch point difference in logic
- Step adds single constant or trivial config change (≤5 lines)
- Step exists solely for formatting/presentation separable from behavior
- Entire phase has ≤3 steps, all Low complexity, modifying function that already exists

**Action:** Collapse into adjacent step. For single-change steps, inline as preamble.

### Checkpoint Spacing (applies to both)

[Existing content unchanged — this criterion is already type-agnostic]
```

**Rationale:** Provides parallel detection methodology for general steps using same structure as TDD criteria.

### Fix 2: Update review-plan Skill to Use Type-Agnostic Criteria

**File:** `agent-core/skills/review-plan/SKILL.md` lines 259-283

**Action:** Expand section 11 with explicit detection patterns for both types:

```markdown
### 11. LLM Failure Modes (CRITICAL) — all phases

Criteria from `agents/decisions/runbook-review.md` (four axes). Apply regardless of phase type.

**11.1 Vacuity**

**TDD detection:**
- Cycles where RED can pass with `assert callable(X)` or `import X`
- GREEN adds ≤3 lines of non-branching code
- Cycle tests integration wiring (A calls B) when B already tested

**General detection:**
- Steps creating scaffolding without functional outcome (mkdir, touch, echo stub)
- Steps producing template text with no computation
- Steps testing presentation format not semantic correctness

**Fix:** Merge into nearest behavioral cycle/step

**11.2 Dependency Ordering**

[Apply same pattern — explicit TDD + General detection criteria]

**11.3 Density**

[Apply same pattern]

**11.4 Checkpoint Spacing**

[Existing content — already type-agnostic]
```

**Rationale:** Makes detection actionable for executing agents without requiring external reference lookup.

### Fix 3: Strengthen Outline Review Propagation

**File:** `agent-core/agents/runbook-outline-review-agent.md` lines 205-254

**Action:** Enhance Expansion Guidance section to explicitly transmit LLM failure mode findings:

```markdown
**LLM Failure Mode Reminders:**

During outline review, the following LLM failure mode candidates were identified:

- **Vacuity risk:** [Steps that need behavioral verification, not just structure]
- **Density risk:** [Adjacent items that should remain separate vs collapse]
- **Ordering constraints:** [Foundation-first dependencies to preserve]
- **Checkpoint placement:** [Recommended validation points]

These should be re-validated after expansion — expansion can introduce new failure modes not present in compact outline form.
```

**Rationale:** Outline review detects issues at sketch level. Expansion Guidance transmits findings forward, but agents also need to know "re-check these axes post-expansion."

### Fix 4: Mandate LLM Failure Mode Re-Check After Expansion

**File:** `agent-core/skills/runbook/SKILL.md` Phase 1 (line 352)

**Action:** Add explicit re-check step after each phase expansion:

```markdown
3. **Review phase content:**
   - Delegate to `plan-reviewer` (fix-all mode)
   - Agent applies type-aware criteria: TDD discipline for TDD phases, step quality for general phases, **LLM failure modes for ALL phases**
   - **Critical:** LLM failure modes (vacuity, ordering, density, checkpoints) MUST be re-validated post-expansion, even if outline review passed
   - Agent returns review report path
```

**Rationale:** Makes re-validation explicit. Outline review is sketch-level; expansion introduces detail where LLM failure modes manifest.

### Fix 5: Close Fast-Path Outline Review Gap

**File:** `agent-core/skills/runbook/SKILL.md` Phase 0.95 (line 338)

**Action:** Add LLM failure mode validation to sufficiency criteria:

```markdown
**If sufficient → validate LLM failure modes before promotion:**

0. **Pre-promotion validation:** Run LLM failure mode check on outline:
   - Vacuity: All items produce functional outcomes (not scaffolding-only)
   - Ordering: Foundation-first within phases (no forward dependencies)
   - Density: No adjacent items with <1 branch point difference
   - Checkpoints: Gaps ≤10 items between validation points

1. **If validation fails:** Fix issues, then promote outline to runbook
2. **If validation passes:** Promote outline to runbook [existing steps 1-7]
```

**Rationale:** Fast-path runbooks bypass Phase 1 expansion review and Phase 3 holistic review. Outline is the ONLY artifact reviewed. Must validate LLM failure modes before promotion.

---

## 5. Scope Assessment

### Affected Files

| File | Change Type | Complexity |
|------|-------------|------------|
| `agents/decisions/runbook-review.md` | Add section | Low — parallel structure to existing TDD axes |
| `agent-core/skills/review-plan/SKILL.md` | Expand criteria | Medium — 4 detection patterns × 2 types |
| `agent-core/agents/runbook-outline-review-agent.md` | Enhance guidance | Low — append to existing section |
| `agent-core/skills/runbook/SKILL.md` | Add validation step | Low — 2-line addition to Phase 1, 5-line addition to Phase 0.95 |
| `agent-core/agents/plan-reviewer.md` | Update references | Trivial — documentation pointer update |

**Estimated effort:** 2-3 cycles (1 documentation update cycle, 1 skill update cycle, 1 validation cycle).

### Testing Strategy

**Validation approach:**
1. Apply Fix 1 (runbook-review.md general-step criteria)
2. Create test general-step runbook with known vacuity/density/ordering issues
3. Delegate to plan-reviewer, verify detection
4. Apply Fix 2 (review-plan skill criteria expansion)
5. Re-test, verify improved detection
6. Apply Fixes 3-5 (outline review, fast-path validation)
7. Test fast-path promotion with LLM failure mode issues, verify rejection

**Success criteria:**
- plan-reviewer detects vacuous general steps with same fidelity as vacuous TDD cycles
- plan-reviewer detects density in general-step phases
- Outline review propagates LLM failure mode findings to expansion via Expansion Guidance
- Fast-path promotion rejects outlines with LLM failure mode issues

### Rollout Considerations

**No breaking changes:** Additions only, no removals or semantics changes.

**Backward compatibility:** Existing TDD-specific detection unchanged. General-step detection is additive.

**Migration path:** None needed — documentation updates are immediately active.

---

## 6. Validation

**Test case 1: Vacuous general step**

```markdown
### Step 1.1: Create directory structure

**Objective:** Set up project directories

**Implementation:**
- `mkdir -p src/`
- `mkdir -p tests/`

**Expected Outcome:** Directories exist
```

**Expected detection:** Vacuous (scaffolding without functional outcome). Should merge with Step 1.2 if it populates directories.

**Test case 2: Density violation**

```markdown
### Step 2.1: Update CLI help text

**Implementation:** Edit `src/cli.py` line 47, change "Process files" to "Process input files"

### Step 2.2: Update CLI description

**Implementation:** Edit `src/cli.py` line 53, change "Description" to "Command description"
```

**Expected detection:** Density (adjacent steps, same file, <1 branch point). Should collapse.

**Test case 3: Ordering violation**

```markdown
### Step 3.1: Add validation to parse_config()

**Implementation:** Extend `parse_config()` (created in Step 3.2) to validate required fields

### Step 3.2: Create parse_config() function

**Implementation:** Add `parse_config()` to `src/config.py`
```

**Expected detection:** Ordering violation (3.1 depends on 3.2). Should reorder or mark UNFIXABLE if cross-phase.

---

## 7. Related Work

**Expansion re-introduces outline-level defects (learning):**

From `agents/learnings.md`:

```
## Expansion re-introduces outline-level defects
- Anti-pattern: Outline review catches vacuous cycles and density issues, but phase expansion re-introduces them without re-validation
- Correct pattern: LLM failure mode checks (vacuity, dependency ordering, density, checkpoint spacing) must run at BOTH outline AND expanded phase levels
```

This RCA addresses the root cause of that learning: detection criteria exist only for TDD, and re-validation isn't enforced.

**Vet agents over-escalate alignment issues (learning):**

Related but distinct issue. Vet over-escalation is judgment calibration (treating pattern-matching as design decisions). This RCA is detection gap (lack of general-step criteria).

---

## 8. Conclusion

General-step detection gap is a **documentation-driven review pipeline issue**. Detection criteria exist (proven by manual review success and outline review general-step language) but are documented only in TDD-specific format. Review agents follow documentation literally, so TDD-specific criteria → no general-step detection.

**Fixes are low-risk:** All are documentation/skill updates with no code changes. Parallel structure to existing TDD criteria minimizes implementation complexity.

**Highest impact fix:** Fix 1 (add general-step detection to runbook-review.md). This is the authoritative source plan-reviewer references. Other fixes are transmission mechanisms for the criteria.

**Fast-path is critical path:** Phase 0.95 bypass is the highest-risk gap. When outline promotes directly to runbook, it bypasses ALL downstream review. Outline review MUST validate LLM failure modes before promotion.

---

**Next steps:**
1. Implement Fix 1 (runbook-review.md general-step criteria)
2. Test against known-bad general-step runbook
3. Implement Fix 2 (review-plan skill expansion)
4. Re-test for improved detection fidelity
5. Implement Fixes 3-5 (outline review, fast-path validation)
6. Full pipeline test (outline → expansion → review for general-step phases)
