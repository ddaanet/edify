# RCA: General-Step Detection Gap in Review Axes

**Date:** 2026-02-13
**Incident:** Worktree-update-recovery runbook had vacuous steps and density issues caught only by manual review. plan-reviewer agent checks TDD discipline but lacks equivalent detection criteria for general-step phases.

---

## Executive Summary

Detection criteria in `agents/decisions/runbook-review.md` are TDD-specific (RED/GREEN/cycles terminology). General steps have equivalent failure modes (vacuity, density, dependency ordering) but no documented detection criteria. The review pipeline has two bypass paths: outline review (Phase 0.75) checks only general-step LLM failure modes, and fast-path (Phase 0.95) skips outline review entirely.

**Three-level root cause:**
1. **Immediate:** runbook-review.md uses TDD-specific language
2. **Proximate:** Per-phase typing introduced 4.5 hours after review criteria were created; downstream consumer update gap
3. **Systemic:** No feature propagation checklist to ensure semantic consumers are updated when capabilities change

**Key insight:** Manual review succeeded using TDD-specific axes by mentally translating terminology. This proves the axes ARE conceptually type-agnostic — they need language normalization, not parallel sections.

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

### Fix 1: Normalize runbook-review.md to Type-Agnostic Language (REVISED)

**File:** `agents/decisions/runbook-review.md`

**Action:** Rewrite the four axes using type-agnostic language with type-specific detection patterns.

**Pattern:** Lead with conceptual description (applies to both), then provide type-specific detection bullets using prefixes:
- `**TDD:**` — TDD-specific detection pattern
- `**General:**` — General-step-specific detection pattern
- `**Both:**` — Universally applicable detection pattern

**Example transformation:**

**Before (TDD-specific):**
```markdown
### Vacuous Cycles

Cycles where RED tests don't constrain implementation. Haiku satisfies them with degenerate GREEN (structurally correct, behaviorally meaningless).

**Detection — a cycle is vacuous when any of:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- Cycle tests presentation format (output shape) rather than semantic correctness
```

**After (type-agnostic):**
```markdown
### Vacuity

Items where tests or implementation don't constrain behavior. Haiku satisfies them with structural correctness without semantic meaning.

**Detection — an item is vacuous when any of:**
- **TDD:** RED can be satisfied by `import X; assert callable(X)` or structural assertion
- **TDD:** GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- **General:** Step creates scaffolding without functional content (mkdir, touch, echo stub)
- **General:** Step produces template text with no computation
- **Both:** Tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- **Both:** Tests presentation format (output shape) rather than semantic correctness

**Action:** Eliminate or merge into nearest behavioral item.
```

Apply same pattern to:
- **Dependency Ordering** → rewrite with TDD/General/Both patterns
- **Cycle Density** → rename to "Density", rewrite with patterns
- **Checkpoint Spacing** → already type-agnostic, minor rewording only

Update document title and intro:
- "Pre-execution review of TDD runbook outlines" → "Pre-execution review of runbook outlines (TDD and general)"

**Rationale:**
- Simpler than parallel sections (one definition, not two)
- More maintainable (updates apply to both types)
- Conceptually accurate (axes ARE the same, proven by manual review success)
- Human already demonstrated successful mental translation

### Fix 2: Simplify review-plan Skill References (REVISED)

**File:** `agent-core/skills/review-plan/SKILL.md` lines 259-283

**Action:** Section 11 already references `agents/decisions/runbook-review.md`. Once Fix 1 normalizes that document to type-agnostic language, this skill's reference "just works" without modification.

**Optional enhancement:** Add reminder that type-specific patterns exist:

```markdown
### 11. LLM Failure Modes (CRITICAL) — all phases

Criteria from `agents/decisions/runbook-review.md` (four axes). Apply regardless of phase type.

Each axis provides type-specific detection patterns:
- **TDD patterns:** For RED/GREEN/cycles (e.g., "RED satisfied by import X")
- **General patterns:** For steps/implementation (e.g., "step creates scaffolding")
- **Universal patterns:** Apply to both (e.g., "tests integration wiring not behavior")

**11.1 Vacuity** — See runbook-review.md for detection patterns
**11.2 Dependency Ordering** — See runbook-review.md for detection patterns
**11.3 Density** — See runbook-review.md for detection patterns
**11.4 Checkpoint Spacing** — See runbook-review.md for detection patterns
```

**Rationale:** Type-agnostic source document eliminates need for duplication. Skill references authoritative criteria without expansion.

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
| `agents/decisions/runbook-review.md` | Rewrite axes (type-agnostic language) | Medium — normalize 4 axes, preserve grounding/sources |
| `agent-core/skills/review-plan/SKILL.md` | Simplify criteria references | Low — type-agnostic criteria eliminate need for expansion |
| `agent-core/agents/runbook-outline-review-agent.md` | Enhance guidance | Low — append to existing section |
| `agent-core/skills/runbook/SKILL.md` | Add validation step | Low — 2-line addition to Phase 1, 5-line addition to Phase 0.95 |
| `agent-core/agents/plan-reviewer.md` | Update references (minimal) | Trivial — documentation pointer update if needed |
| `agents/decisions/feature-propagation.md` | Create checklist (systemic fix) | Low — new document, ~80 lines |

**Estimated effort:** 2-3 cycles (1 documentation normalization cycle, 1 skill update cycle, 1 validation cycle).

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

## 8. Deepening

### 8.1 Why Are Criteria TDD-Specific? Timeline Analysis

**Hypothesis:** Per-phase typing was introduced AFTER review criteria were written. This is a downstream consumer update gap.

**Timeline evidence:**

| Date | Event | File |
|------|-------|------|
| 2026-02-12 11:00 | runbook-review.md created | `agents/decisions/runbook-review.md` |
| 2026-02-12 14:51 | Per-phase typing designed | `plans/workflow-fixes/design.md` (commit b8b560d) |
| 2026-02-12 15:24 | Per-phase typing shipped | Unified /runbook skill (commit 6d753f9) |

**Analysis:**

runbook-review.md was created 4.5 hours BEFORE per-phase typing was designed and shipped. The review criteria document predates the feature it needs to support.

**From commit 6d753f9 message:**
```
- Unified /runbook skill with per-phase typing (2205→810 lines, 63% reduction)
- review-plan skill extends review-tdd-plan with general + LLM failure mode criteria
```

The commit message claims "review-plan skill extends... with general + LLM failure mode criteria," but the extension was incomplete. The skill references `agents/decisions/runbook-review.md` (line 260 in review-plan skill: "Criteria from `agents/decisions/runbook-review.md`") which still contains TDD-specific language.

**Downstream consumer update gap confirmed:**

Per-phase typing required updates to:
1. ✅ Runbook skill (Phase 1 expansion logic) — updated
2. ✅ prepare-runbook.py (already supported both via header detection) — no change needed
3. ✅ plan-reviewer agent definition (declares intent to check all phases) — updated
4. ✅ review-plan skill (references criteria document) — updated
5. ❌ **runbook-review.md (detection criteria themselves)** — NOT updated

**Root cause refined:** Per-phase typing introduction created a new requirement (type-agnostic criteria) that was not propagated to the authoritative criteria document.

### 8.2 Manual Review Succeeded — Axes Are Conceptually Type-Agnostic

**Observation:** Human reviewer applied runbook-review.md axes to general steps by mentally translating TDD terminology.

**Evidence from session.md:**
```
**Runbook review (manual, against runbook-review.md axes):**
- 2 Medium: density (Steps 1.3+1.4 same file), vacuity (Step 1.2 echo stub)
```

The human detected vacuity ("Step 1.2 echo stub") and density ("Steps 1.3+1.4 same file") in general-step phases using TDD-specific criteria. This proves the axes ARE conceptually type-agnostic.

**Translation performed:**

| TDD-specific language | Human interpretation for general steps |
|----------------------|---------------------------------------|
| "Cycles where RED tests don't constrain implementation" | "Steps that only create scaffolding without functional outcome" |
| "Cycle tests integration wiring (A calls B)" | "Step tests integration wiring (A calls B)" |
| "GREEN adds ≤3 lines of non-branching code" | "Step implementation adds ≤3 lines of non-branching code" |
| "Unnecessary cycles that dilute expansion quality" | "Unnecessary steps that dilute expansion quality" |

**Implication for Fix 1:**

The original proposal was:
> Add section "General-Step Equivalents" after the four TDD axes with parallel detection criteria

**Better approach:** Make existing axes type-agnostic by normalizing language.

**Rationale:**
1. **Simpler:** One section, not two parallel sections to maintain
2. **More maintainable:** Updates apply to both types automatically
3. **Conceptually accurate:** The axes ARE the same, only terminology differs
4. **Proven:** Human already demonstrated successful translation

**Revised Fix 1 proposal:**

**Before (TDD-specific):**
```markdown
### Vacuous Cycles

Cycles where RED tests don't constrain implementation.

**Detection — a cycle is vacuous when any of:**
- RED can be satisfied by `import X; assert callable(X)`
- GREEN adds ≤3 lines of non-branching code
- Cycle tests integration wiring (A calls B)
```

**After (type-agnostic):**
```markdown
### Vacuity

Items where tests/implementation don't constrain behavior. Haiku satisfies them with structural correctness without semantic meaning.

**Detection — an item is vacuous when any of:**
- **TDD:** RED can be satisfied by `import X; assert callable(X)` or structural assertion
- **TDD:** GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- **General:** Step creates scaffolding without functional content (mkdir, touch, echo stub)
- **General:** Step produces template text with no computation
- **Both:** Tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- **Both:** Tests presentation format (output shape) rather than semantic correctness
```

**Pattern:** Lead with type-agnostic concept, provide type-specific detection patterns as bullets. "Both" indicators show universally applicable criteria.

### 8.3 Meta Root Cause — No Propagation Checklist

**Question:** Is this a one-off gap or a systemic pattern?

**Analysis of feature introductions:**

| Feature | Date Introduced | Downstream Consumers | Update Status |
|---------|----------------|---------------------|---------------|
| **Per-phase typing** | 2026-02-12 | 5 consumers | 4/5 updated (80%) |
| **Continuation passing** | 2026-02-09 | Skills with tail-calls | Updated (commit 1f278b1 shows systematic doc sweep) |
| **MCP tools** | ~2025-12 | Skills, agents | No propagation gaps observed |
| **Rules files** | ~2026-01 | Agent definitions, CLAUDE.md | No propagation gaps observed |

**Detailed analysis: Continuation passing**

From commit 1f278b1 (2026-02-09):
```
- Create continuation-passing fragment (protocol, frontmatter, consumption, transport)
- Update design.md: D-1 multi-skill only, D-3 skills own default-exit, D-6 remove Mode 1
- Add continuation passing decisions to workflow-optimization.md
- Update jobs.md: continuation-passing → complete
- Fix invalidated learning (default exit ownership changed)
- Vet checkpoint: 6 issues fixed (terminology consistency across all docs)
```

This commit shows systematic propagation:
1. ✅ New fragment created (protocol documentation)
2. ✅ Design doc updated (decisions refined)
3. ✅ Workflow optimization doc updated (integration patterns)
4. ✅ Invalidated learning fixed (downstream knowledge)
5. ✅ Vet checkpoint caught 6 terminology consistency issues

**Contrast with per-phase typing:**

Continuation passing had a vet checkpoint that caught propagation issues. Per-phase typing did not have an explicit vet checkpoint checking "did all downstream consumers get updated?"

**Evidence of checklist gap:**

From workflow-fixes design (commit b8b560d):
```
**Changes by Artifact**

- Unified /plan skill (merge plan-tdd + plan-adhoc with per-phase typing)
- Review skill rename and expansion (review-tdd-plan → review-plan, add general + LLM failure mode criteria)
- plan-reviewer agent definition
- Pipeline contracts decision doc
- Orchestrate unified completion
- Design skill routing update
- Workflow terminology updates (CLAUDE.md, fragments)
- Vet skill context guidance
- Deprecation of plan-tdd and plan-adhoc skills
- Symlink synchronization (just sync-to-parent)
```

**Missing from "Changes by Artifact":** `agents/decisions/runbook-review.md`

The design document listed 10 artifacts to update but did not include the review criteria document. This is a planning-time gap, not an execution-time gap.

**Systemic pattern:**

Continuation passing (15-step runbook) had explicit vet checkpoints at steps 6 and 15. The workflow-fixes plan (unified /runbook) did NOT have a vet checkpoint specifically for "review criteria language normalization."

**Root cause of the root cause:**

When introducing new capabilities:
1. **Design identifies changed artifacts** — lists files to modify
2. **Implementation executes changes** — updates listed files
3. **No checklist validates:** "Did we find ALL downstream consumers?"

The gap is between "artifacts we know about" (explicit list) and "artifacts that depend on changed semantics" (requires impact analysis).

**Evidence this is systemic:**

From agents/learnings.md:
```
## Pipeline transformation gap analysis
- Anti-pattern: Patching individual artifacts when gaps are architectural (wrong routing, missing criteria, broken propagation)
- Correct pattern: Map pipeline as transformations (T1-T6), identify defect types per transformation, verify review gates match defect types
```

This learning (from workflow-fixes work itself) identified "broken propagation" as an anti-pattern. The learning was recorded WHILE experiencing a propagation gap (runbook-review.md not updated). Meta-awareness without meta-solution.

**Is there a checklist?**

Searched for:
- `git log --all --grep="propagation\|downstream\|consumer update\|checklist"` — no checklist commits
- agents/decisions/ files — no "feature introduction checklist" document
- CLAUDE.md fragments — no "propagation verification" fragment

**Conclusion:** No propagation checklist exists. Impact analysis is ad-hoc.

**Proposed systemic fix:**

Create `agents/decisions/feature-propagation.md` with checklist:

```markdown
# Feature Propagation Checklist

When introducing new capabilities (features, terminology changes, architectural patterns):

## Phase 1: Impact Analysis

- [ ] List direct consumers (files that reference the feature)
- [ ] List semantic consumers (files that reference related concepts)
- [ ] List downstream consumers (files that consume direct consumers)
- [ ] Identify decision documents (agents/decisions/*.md)
- [ ] Identify skill definitions (agent-core/skills/*/SKILL.md)
- [ ] Identify agent definitions (agent-core/agents/*.md)
- [ ] Identify fragments (agent-core/fragments/*.md)

## Phase 2: Update Verification

- [ ] Verify each consumer updated (grep for old terminology)
- [ ] Check if any examples need updating
- [ ] Validate cross-references still resolve
- [ ] Check if learnings contradict new feature (invalidation)

## Phase 3: Vet Checkpoint

- [ ] Run vet-fix-agent on changed decision docs
- [ ] Check terminology consistency across artifacts
- [ ] Verify examples use new patterns
- [ ] Confirm no stale references remain

## Phase 4: Test Propagation

- [ ] Create test case using new feature
- [ ] Verify downstream consumers handle it correctly
- [ ] Check error messages reference new terminology
- [ ] Validate documentation discoverability
```

This checklist would have caught runbook-review.md (Phase 1: decision document with related concept "cycles" when introducing "per-phase typing").

---

## 9. Conclusion (Revised)

General-step detection gap has THREE root causes:

1. **Immediate:** runbook-review.md uses TDD-specific language (RED/GREEN/cycles)
2. **Proximate:** Per-phase typing introduced 4.5 hours after review criteria were written; downstream consumer update gap
3. **Systemic:** No feature propagation checklist to ensure all semantic consumers are updated

**Fixes are low-risk with one revision:**

Original Fix 1 proposed parallel "General-Step Equivalents" section. **Revised Fix 1:** Normalize existing axes to be type-agnostic using bullet patterns (TDD: ... / General: ... / Both: ...). This is simpler, more maintainable, and reflects the conceptual unity of the axes.

**Highest impact fixes:**
1. **Fix 1 (revised):** Normalize runbook-review.md language — authoritative source
2. **Systemic fix:** Create feature-propagation.md checklist — prevents recurrence

**Fast-path remains critical path:** Phase 0.95 bypass is still the highest-risk gap. When outline promotes directly to runbook, it bypasses ALL downstream review. Outline review MUST validate LLM failure modes before promotion.

---

**Next steps:**
1. Implement revised Fix 1 (normalize runbook-review.md to type-agnostic language)
2. Test against known-bad general-step runbook
3. Implement Fix 2 (review-plan skill can reference type-agnostic criteria)
4. Implement Fixes 3-5 (outline review, fast-path validation)
5. **Systemic:** Create feature-propagation.md checklist
6. Full pipeline test (outline → expansion → review for general-step phases)
