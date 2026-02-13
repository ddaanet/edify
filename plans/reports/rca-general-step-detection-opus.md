# RCA: General-Step Detection Gap in Runbook Review Pipeline

**Date:** 2026-02-13
**Analyst:** Opus
**Incident:** Worktree-update-recovery runbook (general steps) passed plan-reviewer automated review with vacuity and density issues. Manual review against the same `runbook-review.md` axes caught 2 Medium and 2 Low findings, collapsing 6 steps to 4.

---

## 1. Root Cause

**`agents/decisions/runbook-review.md` was created 4.5 hours before per-phase typing shipped and was never updated afterward. The feature's artifact inventory treated it as a read-only reference rather than a semantic consumer requiring update. The TDD-specific language is not an intentional design choice — it is a creation-timing artifact.**

The document has four axes (Vacuous Cycles, Dependency Ordering, Cycle Density, Checkpoint Spacing). Every heading, every detection bullet, and every example uses TDD terminology: "RED tests", "GREEN adds ≤3 lines", "cycles", "RED can be satisfied by `assert callable(X)`". General-step phases have identical failure modes (scaffolding-only steps, same-file density, forward dependencies) but zero documented detection patterns.

This is a **downstream consumer update gap**, not an asymmetric specification. The review-plan skill (`agent-core/skills/review-plan/SKILL.md` Section 11) already declares type-agnostic intent:

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

---

## Deepening

Three additional axes of investigation, prompted by the parallel sonnet RCA's timeline finding.

### D1. Timeline Verification

**Claim to verify:** `runbook-review.md` was created before per-phase typing was designed, making the root cause a downstream consumer update gap rather than a TDD-centric authorial choice.

**Evidence from git history:**

| Event | Commit | Timestamp | Delta |
|-------|--------|-----------|-------|
| `runbook-review.md` created | `2d29fc8` | 2026-02-12 11:00:05 +0100 | T+0h |
| workflow-fixes design (per-phase typing begins) | `ca5eb5c` | 2026-02-12 13:49:26 +0100 | T+2h49m |
| Unified /plan design complete | `b8b560d` | 2026-02-12 14:51:33 +0100 | T+3h51m |
| Unification shipped (per-phase typing live) | `6d753f9` | 2026-02-12 15:24:24 +0100 | T+4h24m |

**Confirmed.** `runbook-review.md` was created 4h24m before per-phase typing shipped. The file has exactly one commit in its entire history — the creation commit. It was never modified after per-phase typing was introduced.

**Root cause revision:** The original Section 1 diagnosis ("TDD-specific language") is the proximate cause but not the root cause. The file was written in a TDD-only world — per-phase typing did not yet exist. When per-phase typing shipped 4.5 hours later, the workflow-fixes design (`plans/workflow-fixes/outline.md`) listed 10 artifacts to update but treated `runbook-review.md` as a read-only reference source, not as an artifact requiring update:

- Line 20: "Add LLM failure mode detection criteria to review-tdd-plan skill (*reference* `agents/decisions/runbook-review.md` four-axis methodology)"
- Line 82: "verify criteria completeness *against* `agents/decisions/runbook-review.md`"

The design used `runbook-review.md` as a stable foundation to build upon, never questioning whether the foundation itself needed updating to match the new type model. The review-plan skill's Section 11 was written during workflow-fixes to add general-step bullets — but the authoritative source it references was never updated to match.

**Corrected root cause:** This is a **downstream consumer update gap**. When per-phase typing shipped, the feature's artifact inventory treated `runbook-review.md` as immutable reference rather than a semantic consumer that needed updating. The TDD-specific language is not an intentional design choice — it is an artifact of creation timing.

### D2. Fix Shape Reconsideration

**Observation:** Manual review succeeded by mentally translating TDD terminology to general equivalents. This proves the four axes are conceptually type-agnostic — "vacuity" applies to any item that doesn't constrain implementation, regardless of whether the item is a TDD cycle or a general step.

**Revised Fix 1 structure:** Instead of dual side-by-side sections, restructure each axis as:

1. **Type-agnostic concept** (the axis definition, using "item" not "cycle")
2. **TDD detection bullets** (existing content, anchored by `**TDD:**`)
3. **General detection bullets** (new content, anchored by `**General:**`)

This is simpler and more maintainable than the originally proposed structure for three reasons:

- **Single definition per axis.** The conceptual definition ("items that don't constrain implementation") is written once, not duplicated across TDD and general sections. This prevents drift between parallel definitions.
- **Additive change.** The existing TDD bullets remain verbatim under a `**TDD:**` label. Adding general support is purely additive — no existing content is rewritten, only relabeled and extended.
- **Natural extension point.** If a third phase type is ever introduced (e.g., `type: integration`), detection bullets add under a new label within the same axis structure. No structural refactoring needed.

**Revised example for Vacuity:**

```markdown
### Vacuity

Items that don't constrain implementation. The executing agent satisfies them with
degenerate output (structurally present, behaviorally meaningless).

**Detection — an item is vacuous when any of:**

**TDD:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- Cycle tests presentation format (output shape) rather than semantic correctness

**General:**
- Step creates scaffolding without functional outcome (mkdir, echo, touch, stub recipe)
- Step output is template text or stub with no computation or state transformation
- Step modifies config/metadata without behavioral effect on execution
- Step tests integration wiring when called function already verified in prior step

**Action:** Eliminate, or merge into nearest behavioral item.
```

**Key differences from original Fix 1:**
- Heading stays "### Vacuity" (not "### Vacuous Cycles" — normalize to concept)
- Opening paragraph is type-agnostic (uses "items" and "executing agent")
- TDD and General bullets are labeled subsections within one axis, not parallel sections
- Action uses "item" not "cycle/step"

This structure makes it mechanically impossible to check TDD criteria without also seeing the General criteria — they share the same heading and detection section.

### D3. Meta Root Cause: Systemic Propagation Gap

**Question:** Is the `runbook-review.md` gap an isolated incident or part of a pattern?

**Evidence of systemic propagation failures:**

| Feature | Shipped | Propagation Gap | Discovery |
|---------|---------|----------------|-----------|
| Per-phase typing (workflow-fixes) | `6d753f9` 2026-02-12 15:24 | `runbook-review.md` not updated | Manual review, 2026-02-13 |
| Workflow unification (same plan) | `6d753f9` 2026-02-12 15:24 | Docs still reference `plan-tdd`, `plan-adhoc`, `tdd-plan-reviewer` | Separate commit `fe9c324` 2026-02-12 15:31 (7 min later, 20 name updates across 3 files) |
| `implementation-notes.md` move | `5b9ea8a` 2026-02-04 17:03 | 9 files with stale path references | Follow-up commit, same session |

**Pattern:** Features ship with an artifact inventory scoped to *producers* (skills, agents, configs that implement the feature) but not *semantic consumers* (documentation, methodology files, reference materials that assume the old semantics). The design phase identifies "what to build" and "what to update" but doesn't systematically identify "what references the old behavior."

**Why this happens:** The design-to-runbook pipeline has no propagation analysis step. The workflow-fixes outline (commit `ca5eb5c`) lists "Fixes by Artifact" — 10 artifacts identified through exploration reports and known issues. But the exploration searched for *artifacts with problems*, not *artifacts that reference changed semantics*. `runbook-review.md` had no problems in isolation — its content was correct for TDD. The problem only emerged when per-phase typing changed the semantic context around it.

**Analogy:** This is the documentation equivalent of a broken interface contract. The feature (per-phase typing) changed the "interface" (what phase types exist), but the "consumer" (`runbook-review.md`) was never notified. In code, a compiler catches this. In documentation, nothing catches it.

**Proposed fix: Semantic consumer checklist**

Add a propagation verification step to the design workflow (`/design` skill or `/runbook` skill Phase 0.75):

**When a feature changes terminology, type systems, or behavioral semantics:**

1. **Grep for old terminology** in `agents/decisions/`, `agent-core/skills/`, `agent-core/agents/`, and `agent-core/fragments/`
2. **For each file referencing old terms:** Classify as producer (needs rewrite) or consumer (needs update)
3. **Add consumers to artifact inventory** with explicit "update to new semantics" scope
4. **Verify at review:** Outline review checks that all grep hits are covered in artifact list

**Placement:** This belongs in the runbook outline review criteria (`agent-core/agents/runbook-outline-review-agent.md`) as a new check under "Execution Readiness":

```markdown
**Semantic propagation completeness** — When design introduces new terminology, type
systems, or behavioral semantics: verify artifact inventory includes all files that
reference old semantics. Use Grep to find references. Classify as producer (rewrite)
or consumer (update). Flag missing consumers as Major issue.
```

**Scope note:** This check only applies to features that change shared semantics (new type systems, renamed concepts, changed interfaces). Purely additive features (new skill, new agent) don't require propagation analysis.

**Cost-benefit:** The grep step adds ~2 minutes to outline review. The alternative is discovering stale consumers in production (this RCA) or in follow-up cleanup commits (`fe9c324`, `5b9ea8a`). The grep is cheaper.
