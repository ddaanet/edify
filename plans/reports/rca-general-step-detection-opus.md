# RCA: General-Step Detection Gap in Runbook Review Pipeline

**Date:** 2026-02-13
**Analyst:** Opus
**Incident:** Worktree-update-recovery runbook (general steps) passed plan-reviewer automated review with vacuity and density issues. Manual review against the same `runbook-review.md` axes caught 2 Medium and 2 Low findings, collapsing 6 steps to 4.

---

## 1. Root Cause

**The authoritative detection methodology document (`agents/decisions/runbook-review.md`) provides detection criteria exclusively in TDD terms. The review pipeline is documentation-driven: agents follow what the document says. Since the document says nothing about general steps, general-step defects pass undetected.**

The document has four axes (Vacuous Cycles, Dependency Ordering, Cycle Density, Checkpoint Spacing). Every heading, every detection bullet, and every example uses TDD terminology: "RED tests", "GREEN adds ≤3 lines", "cycles", "RED can be satisfied by `assert callable(X)`". General-step phases have identical failure modes (scaffolding-only steps, same-file density, forward dependencies) but zero documented detection patterns.

This is not a missing feature — it is an asymmetric specification. The review-plan skill (`agent-core/skills/review-plan/SKILL.md` Section 11) already declares type-agnostic intent:

```
### 11. LLM Failure Modes (CRITICAL) — all phases
Criteria from agents/decisions/runbook-review.md (four axes). Apply regardless of phase type.
```

And even includes one general-step criterion inline (11.1: "General: Steps that only create scaffolding without functional outcome"). But this inline expansion is incomplete (only vacuity has a general detection bullet; density, ordering, and checkpoints don't) and contradicts the authority structure: the skill says "criteria from `runbook-review.md`" while `runbook-review.md` provides no general criteria to reference.

**Why this causes failure in practice:** The plan-reviewer agent reads `runbook-review.md` for detection methodology. When reviewing general-step phases, it finds no applicable patterns. It falls back to the review-plan skill's generic one-liners (11.1-11.4), which are insufficiently specific to distinguish vacuous steps from legitimate scaffolding or density issues from properly decomposed work. The agent checks the boxes ("Steps produce functional outcomes" — `PASS`) without the detection rigor that TDD criteria force (no "RED can be satisfied by import" equivalent for general steps).

---

## 2. Contributing Factors

### 2.1 Fast-Path Bypass Eliminates Downstream Review Entirely

**Location:** `agent-core/skills/runbook/SKILL.md` Phase 0.95 (lines 326-348)

When the outline sufficiency check passes, the outline promotes directly to runbook. This bypasses Phase 1 (per-phase expansion + review), Phase 2.5 (consolidation gate), and Phase 3 (holistic review). The outline review at Phase 0.75 becomes the *only* quality gate.

The outline review agent (`runbook-outline-review-agent.md`) does include general-step language in its vacuity check (line 118: "flag steps where... the step only creates scaffolding without behavior (adhoc)"). But outline-level items are compact descriptions — vacuity and density manifest more clearly in expanded form. A 1-line outline bullet "Add setup recipe to agent-core" becomes a 20-line expanded step that reveals itself as an echo stub. Fast-path promotion never reaches the expanded form.

**Severity:** High. This is the highest-risk bypass path. For small general-step runbooks (the common case for recovery work, migrations, infrastructure), fast-path activation is likely, and outline review is the weakest detection point.

### 2.2 1:1 Finding-to-Step Mapping Overrides Density Analysis

**Evidence from session.md:**

> Contributing: 1:1 finding-to-step mapping heuristic overrides density analysis

The worktree-update-recovery runbook mapped each deliverable review finding to exactly one step. This 1:1 mapping creates an implicit justification for step count: "6 findings → 6 steps → each step addresses exactly one finding." Density analysis asks "should adjacent steps collapse?" but the 1:1 mapping provides a counter-argument: "each step has a distinct finding as justification."

The manual review detected that Steps 1.1+1.2 both modified `justfile` (same file, related fixes) and Steps 1.3+1.4 both modified `cli.py` (same file, related fixes). The finding-level decomposition (C2, C3, M1, M2) is the wrong granularity for step decomposition — step granularity should optimize for execution efficiency (minimize file context switches), not for finding traceability.

**Why the automated review missed this:** The plan-reviewer's density check (Section 11.3) looks for "adjacent items testing same function with <1 branch point difference." But the steps addressed *different findings* in the same file. The TDD framing ("testing same function") doesn't map to the general-step equivalent ("modifying same file with independent changes"). The reviewer saw "different objectives → not density" when the correct analysis was "same file, same module, composable changes → density."

### 2.3 General-Step Section 10 Checks Structure, Not LLM Failure Modes

**Location:** `agent-core/skills/review-plan/SKILL.md` Section 10 (lines 237-256)

The review-plan skill has a dedicated "General Phase Step Quality" section (10.1-10.4) covering prerequisite validation, script evaluation, step clarity, and conformance validation. These check *structural* quality (does the step have an Objective? Is the size classification correct?), not *semantic* quality (does the step produce meaningful behavioral change? Is it dense with adjacent steps?).

Section 11 (LLM Failure Modes) is supposed to bridge this gap for all phases, but as established, its general-step detection criteria are underspecified. The result: general phases get structural review (Section 10) but weak semantic review (Section 11 with incomplete general criteria), while TDD phases get both structural (Sections 1-9) and semantic (Section 11 with full TDD detection patterns) review.

### 2.4 Reference Files Are TDD-Only

All four reference files in `agent-core/skills/runbook/references/` are TDD-specific:

- `patterns.md`: "TDD Runbook Patterns" — granularity criteria, numbering, dependencies for cycles
- `anti-patterns.md`: "Common mistakes in TDD runbook creation"
- `examples.md`: "TDD Runbook Examples" — complete cycle example with RED/GREEN/Stop
- `error-handling.md`: "Error Handling and Edge Cases" — TDD cycle generation errors

No reference file provides general-step expansion guidance, anti-patterns, or examples. When the planner (during Phase 1 expansion) or the reviewer (during Phase 1 review) needs to understand "what does a well-formed general step look like?", there is no reference material to consult.

### 2.5 `runbook-review.md` Process Section Hardcodes TDD Terminology

**Location:** `agents/decisions/runbook-review.md` lines 63-69

```
1. Read runbook outline (phase structure, cycle descriptions, dependency declarations)
2. For each cycle, evaluate against vacuity and dependency ordering axes
3. For each phase, evaluate cycle density and identify collapse candidates
4. Check checkpoint spacing across full runbook
```

The process uses "cycle" exclusively. A reviewing agent following this process for a general-step phase has no anchor — step 2 says "for each cycle" but there are no cycles in a general phase, only steps. The agent must infer that "cycle" means "step" in general context, an inference that degrades detection fidelity.

---

## 3. Evidence

### 3.1 Automated Review False Negatives

The plan-reviewer's report (`plans/worktree-update/reports/runbook-review.md` lines 105-115) passed all four LLM failure mode axes:

```
### Vacuity
**Status**: Pass — All steps produce functional outcomes (code fixes, config additions, test additions).

### Density
**Status**: Pass — Step scope appropriate. No single-line fixes inflated to full steps.
```

The manual review found:

| Finding | Severity | Detection | Automated Result |
|---------|----------|-----------|-----------------|
| Step 1.2 echo stub (vacuity) | Medium | Step only adds echo recipe — no functional outcome | Pass |
| Steps 1.3+1.4 same file (density) | Medium | Adjacent steps modifying `cli.py` with composable changes | Pass |
| Metadata "all parallel" (ordering) | Low | Steps 1.3-1.4 have implicit ordering (same file) | Pass |
| Checkpoint spacing | Low | 6 steps without checkpoint | Pass |

The vacuity finding is particularly revealing: Step 1.2 added a `setup` recipe to `agent-core/justfile` that was essentially `echo "No package dependencies"`. This is a textbook vacuous step — it produces no functional outcome. The TDD detection criterion ("RED can be satisfied by `assert callable(X)`") has no equivalent for general steps, so the reviewer categorized the step as "functional outcome: config addition" when it was actually a no-op stub.

### 3.2 Asymmetry Between Outline and Phase Review

The outline review agent (`runbook-outline-review-agent.md`) includes dual-type detection for vacuity (line 118):

```
Flag steps where RED can be satisfied by `import X; assert callable(X)` (TDD) or where
the step only creates scaffolding without behavior (adhoc)
```

The phase review (review-plan skill Section 11.1) also includes a general bullet:

```
General: Steps that only create scaffolding without functional outcome
```

But the phase review's density check (11.3) has no general equivalent:

```
Adjacent items testing same function with <1 branch point difference
```

"Testing same function" is TDD-specific. The general equivalent is "modifying same file/module with composable changes." This asymmetry means vacuity has partial general coverage but density has none.

### 3.3 Worktree-Update-Recovery Runbook Was General-Step

The entire recovery runbook used `## Step` headers, not `## Cycle` headers. Phase type was general (non-TDD). The plan-reviewer report confirmed: "Phase types: General (non-TDD)". This is the exact scenario where general-step detection criteria are needed.

---

## 4. Proposed Fixes

### Fix 1: Restructure `runbook-review.md` as Type-Agnostic with Type-Specific Examples

**File:** `agents/decisions/runbook-review.md`

**Current structure:** Four axes, each with TDD-only detection, action, and grounding.

**Proposed structure:** Each axis gets a type-neutral definition, then TDD-specific and general-specific detection bullets side by side.

Example for Vacuity:

```markdown
### Vacuity

Items that don't constrain implementation. The executing agent satisfies them with
degenerate output (structurally present, behaviorally meaningless).

**Detection — an item is vacuous when any of:**

**TDD cycles:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)

**General steps:**
- Step creates scaffolding without functional outcome (mkdir, echo, touch)
- Step output is stub/template text with no computation or state transformation
- Step modifies config/metadata without behavioral effect
- Step tests integration wiring when called function already verified

**Action:** Eliminate, or merge into nearest behavioral item.
```

Apply the same pattern to Dependency Ordering, Density, and Checkpoint Spacing.

**Also update Process section** (lines 63-69): Replace "cycle" with "item" or "cycle/step" to be type-neutral.

**Rationale:** This is the highest-impact fix. `runbook-review.md` is the authoritative source referenced by both the review-plan skill and plan-reviewer agent. Restructuring it as type-agnostic eliminates the root cause without changing any downstream consumers.

### Fix 2: Add General-Step Detection Examples to `review-plan/SKILL.md` Section 11

**File:** `agent-core/skills/review-plan/SKILL.md`

**Current state:** Section 11.1 has one general bullet. Sections 11.2-11.3 are TDD-only.

**Action:** Expand each subsection with explicit general detection patterns:

- **11.1 Vacuity (general):** "Steps creating only scaffolding (mkdir, touch, echo stub). Steps producing template text with no computation. Steps modifying config without behavioral effect."
- **11.2 Ordering (general):** "Step N modifies/extends artifact created in step N+k. Step N's implementation assumes state established by later step."
- **11.3 Density (general):** "Adjacent steps modifying same file with composable changes. Step adds single constant or trivial config (≤5 lines). Entire phase has ≤3 steps, all Low complexity, on same file."

**Rationale:** Even though Fix 1 addresses the authoritative source, inline criteria in the skill file provide immediate detection guidance without requiring the agent to load and parse `runbook-review.md`.

### Fix 3: Add General-Step References

**File:** `agent-core/skills/runbook/references/` (new or existing files)

**Action:** Add general-step content to the reference files:

- `patterns.md`: Add "General Step Patterns" section with granularity criteria for steps (similar to cycle granularity criteria: 1 behavioral outcome per step, too granular = single-line change, too coarse = multiple modules)
- `anti-patterns.md`: Add general-step anti-patterns (stub steps, same-file density, ordering violations)
- `examples.md`: Add a complete general-step runbook example showing proper structure

**Rationale:** Reference files are loaded by planners during Phase 1 expansion. Without general-step guidance, planners default to TDD patterns or invent ad-hoc structure.

### Fix 4: Add LLM Failure Mode Gate to Phase 0.95 Fast-Path

**File:** `agent-core/skills/runbook/SKILL.md` Phase 0.95 (lines 330-348)

**Action:** Add a pre-promotion validation step:

```markdown
**If sufficient → validate LLM failure modes before promotion:**

Before reformatting and writing, run inline LLM failure mode check:
- Vacuity: Every item produces a functional (not scaffolding) outcome
- Ordering: Foundation-first within phases, no forward references
- Density: No adjacent items modifying same file with <1 branch-point difference
- Checkpoints: Gaps ≤10 items between quality gates

If issues found: fix inline, then proceed with promotion.
```

**Rationale:** Fast-path is the highest-risk bypass. When it activates, outline review is the only prior gate, and it operates on compact items where defects are harder to detect. A lightweight inline check at promotion time catches defects that emerge only when examining items in sequence.

### Fix 5: Make Process Section Type-Neutral

**File:** `agents/decisions/runbook-review.md` lines 63-69

**Action:** Replace:

```
1. Read runbook outline (phase structure, cycle descriptions, dependency declarations)
2. For each cycle, evaluate against vacuity and dependency ordering axes
3. For each phase, evaluate cycle density and identify collapse candidates
```

With:

```
1. Read runbook (phase structure, item descriptions, dependency declarations)
2. For each item (cycle or step), evaluate against vacuity and dependency ordering axes
3. For each phase, evaluate item density and identify collapse candidates
```

**Rationale:** Process language guides agent behavior. "For each cycle" provides no procedural anchor for general-step review.

---

## 5. Scope Assessment

| File | Change | Effort |
|------|--------|--------|
| `agents/decisions/runbook-review.md` | Restructure 4 axes as dual-type, update process section | Medium (core fix) |
| `agent-core/skills/review-plan/SKILL.md` | Expand Section 11 with general detection patterns | Low |
| `agent-core/skills/runbook/references/patterns.md` | Add general-step granularity section | Low |
| `agent-core/skills/runbook/references/anti-patterns.md` | Add general-step anti-patterns | Low |
| `agent-core/skills/runbook/references/examples.md` | Add general-step example runbook | Medium |
| `agent-core/skills/runbook/SKILL.md` | Add Phase 0.95 LLM failure mode gate | Low |

**Total:** ~5 changes, no code, documentation/skill updates only. No test infrastructure required — validation through pipeline execution on next general-step runbook.

**Priority ordering:**
1. Fix 1 (runbook-review.md restructure) — root cause, highest impact
2. Fix 5 (process section) — part of same file, do together
3. Fix 2 (review-plan skill expansion) — immediate agent consumption
4. Fix 4 (fast-path gate) — closes highest-risk bypass
5. Fix 3 (reference files) — expansion quality improvement, lower urgency

---

## 6. Comparison with Prior RCA

An existing RCA exists at `plans/reports/rca-general-step-detection.md`. This opus analysis confirms and extends that report:

**Confirmed findings:**
- Root cause (TDD-specific detection criteria in authoritative source) — identical diagnosis
- Fast-path bypass (Phase 0.95) as high-risk contributing factor
- 1:1 finding-to-step heuristic overriding density analysis
- Type-agnostic intent declared but not implemented (plan-reviewer lines 79-83)

**Additional findings in this analysis:**
- **2.3 Section 10 vs 11 structural/semantic split:** General steps get structural review (Section 10) but weak semantic review (Section 11), while TDD gets both. This is a structural gap in the review-plan skill, not just a documentation gap in `runbook-review.md`
- **2.4 Reference files TDD-only:** No general-step expansion guidance, anti-patterns, or examples exist. Planners have no reference material for general steps
- **2.5 Process section hardcodes TDD terminology:** The procedural guidance in `runbook-review.md` says "for each cycle" — no procedural anchor for general-step review
- **Density detection gap is deeper than vacuity:** Vacuity has partial general coverage (outline review + review-plan 11.1). Density has zero general coverage — "testing same function" doesn't map to "modifying same file"
- **Fix 3 (reference files) and Fix 5 (process section):** Not proposed in prior RCA

**Differing emphasis:**
- Prior RCA proposes 5 fixes weighted toward transmission mechanisms (outline guidance propagation, runbook skill annotations). This analysis weights toward authoritative source restructuring (Fix 1 as dual-type with inline examples) and reference material (Fix 3)
- Prior RCA's Fix 3 (strengthen outline review propagation) addresses a real gap but is a band-aid — the root fix is making detection criteria available at every review point, not propagating findings forward from outline review
