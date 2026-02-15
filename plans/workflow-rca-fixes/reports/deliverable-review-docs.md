# Deliverable Review: Human Documentation (workflow-rca-fixes)

Review of 7 documentation deliverables against design specifications (20 FRs, 6 phases).

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 2 |
| Minor | 3 |
| Total | 6 |

---

## workflows-terminology.md (FR-16)

### Critical

**1. Non-existent agent reference — `runbook-review-agent`**
- File: `agent-core/fragments/workflows-terminology.md:19`
- Axis: Accuracy
- Text: "Opus-tier agents (runbook-review-agent, skill-reviewer, agent-creator) invoked in parallel."
- No file `runbook-review-agent.md` exists in `agent-core/agents/` or `.claude/agents/`. The review-related agents on disk are: `plan-reviewer.md`, `runbook-outline-review-agent.md`, `outline-review-agent.md`, `review-tdd-process.md`. This is the same agent-name misresolution class that FR-19 and FR-20 were created to prevent.
- Impact: Reader following this instruction would look for a non-existent agent. If used programmatically, delegation would fail.

### No other findings for this file.

FR-16 acceptance: "Workflow terminology section references deliverable review as post-orchestration step with model requirement." The route on line 12 includes `[deliverable review]` and the description on line 19 specifies "Optional post-orchestration review." Model requirement present ("Opus-tier agents"). Conformance satisfied except for the broken agent name.

---

## runbook-review.md (FR-1)

### No Critical or Major findings.

FR-1 required: type-agnostic 4 axes with TDD/General bullets, behavioral vacuity detection, file growth as 5th axis, "item (cycle or step)" terminology.

Verified:
- 5 axes present: Vacuity (line 9), Dependencies (line 33), Density (line 50), Checkpoints (line 69), File Growth (line 90)
- Each axis has `**TDD:**` and `**General:**` bullets
- Behavioral vacuity detection present (lines 24-27) with heuristic covering both types
- Process section uses "item (cycle or step)" terminology (lines 111-113)
- File growth includes 350-line threshold, >10 items flag (lines 97, 102)

### Minor

**2. Heuristic description uses singular "items" comparison instead of ratio**
- File: `agents/decisions/runbook-review.md:27`
- Axis: Usability
- Text: "items > LOC/20 signals consolidation"
- The heuristic compares item count to LOC/20, but "items" is ambiguous — does it mean total runbook items, items in a phase, or items targeting a specific file? The design spec (line 128) says the same: "cycles/steps > LOC/20." The denominator (LOC of what?) is unspecified in both design and implementation. A reviewer applying this heuristic would need to decide scope.
- Severity is minor because the heuristic is a signal, not a threshold.

---

## vet-requirement.md (FR-9, FR-10)

### No Critical findings.

**FR-9 verification (UNFIXABLE validation):**
- Four statuses defined (lines 99-103) with blocking semantics
- Detection steps (lines 107-113): read report, grep UNFIXABLE, validate, resume for reclassification
- Validation criteria (lines 115-119): subcategory code, investigation summary (4 gates), scope OUT cross-reference
- Reclassification guidance with examples (line 119)
- Full taxonomy reference to `vet-taxonomy.md` (line 105)
- DEFERRED vs UNFIXABLE distinction (line 121)
- OUT-OF-SCOPE vs DEFERRED distinction (line 123)

**FR-10 verification (execution context enforcement):**
- Structured IN/OUT scope fields (lines 49-53) with "must be structured lists, not empty prose"
- Fail loudly requirement (line 49): "Fail loudly if any field is missing or contains only placeholder text"
- Delegation template (lines 67-91) with all required fields
- Enforcement paragraph (line 93): "orchestrator must halt and populate fields"

### Major

**3. Delegation template lacks "Constraints" enforcement parity**
- File: `agent-core/fragments/vet-requirement.md:88`
- Axis: Completeness
- The template includes a `**Constraints:**` field with "Do NOT flag items outside provided scope (scope OUT list)" but the enforcement paragraph (line 93) only checks for "empty IN, empty OUT, or missing changed files." The Constraints field is not mentioned in enforcement. An orchestrator following the enforcement rules mechanically would populate IN/OUT/changed-files but could omit the Constraints section.
- This matters because the scope OUT constraint ("Do NOT flag items outside provided scope") is the primary mechanism preventing confabulation of future-phase issues (lines 55-61). If the constraint is omitted from the delegation prompt, the vet agent may still flag out-of-scope items.

### Minor

**4. Investigation summary says "4 gates" but only 3 named in vet-requirement.md**
- File: `agent-core/fragments/vet-requirement.md:117`
- Axis: Consistency
- Text: "investigation summary showing all 4 gates checked (scope OUT, design deferral, codebase patterns, conclusion)"
- The parenthetical lists 4 items but "conclusion" is not a gate — it is the output of passing the gates. The investigation-before-escalation protocol (FR-8, implemented in `vet-fix-agent.md`) defines 4 gates: (1) scope OUT, (2) design deferral, (3) Glob/Grep codebase patterns, (4) conclusion with evidence. The term "gate" for the conclusion is imprecise — it is the classification decision, not a diversion point.
- Minor because the full taxonomy is in `vet-taxonomy.md` (line 105 reference) where the investigation format is fully specified.

---

## orchestration-execution.md (FR-17)

### No Critical findings.

FR-17 required: document execution-to-planning feedback as three-tier escalation (item-level, local recovery, global replanning) with handoff to `wt/error-handling`.

Verified:
- Three tiers present: item-level (line 81), local recovery (line 91), global replanning (line 101)
- Each tier has trigger, response, and distinction criteria
- Implementation deferral section (line 116) with `wt/error-handling` reference
- Grounding from when-recall incident and planner-executor research (line 120)
- Cross-reference to existing vet-requirement.md protocol (line 89)
- Global replanning symptoms enumerated: design assumptions invalidated, scope creep accumulation, runbook structure broken, test plan inadequate (lines 107-110)
- Constraint C-4 satisfied: documents requirement only, implementation deferred

### Major

**5. Local recovery tier references "refactor agent" without path or disambiguation**
- File: `agents/decisions/orchestration-execution.md:97`
- Axis: Accuracy, Usability
- Text: "Delegate to refactor agent within current phase."
- The actual agent file is `agent-core/agents/refactor.md`. The decision document uses bare name "refactor agent" — no path, no backtick-wrapped identifier. Other entries in this same file use backtick-wrapped references (e.g., line 89: `` `vet-requirement.md` ``). An orchestrator following this would need to resolve the name. The name "refactor" is unambiguous (only one agent with that name exists), but the inconsistent referencing style reduces usability.
- Severity is major because this is in a decision document defining escalation protocol. Ambiguous agent references in escalation paths can cause incorrect routing. The refactor agent is the recovery mechanism — getting it wrong means local recovery fails.

### Minor

**6. Dot-prefix convention on subsection heading `.Implementation Deferral`**
- File: `agents/decisions/orchestration-execution.md:116`
- Axis: Consistency
- The `.Implementation Deferral` heading (line 116) uses `### .` (h3 with dot prefix) as a subsection of `.Execution Escalation` (h2 with dot prefix). Other subsections in this file (e.g., lines 81, 91, 101) use `###` without dot prefix. This is the only `### .` heading in the file.
- The dot-prefix convention in decision documents marks top-level organizational sections at h2 level. Using it at h3 level is inconsistent with the pattern in this file and others.
- Minor because the heading still renders correctly and the content is findable.

---

## general-patterns.md (FR-4)

### No Critical or Major findings.

FR-4 required: granularity criteria, prerequisite validation patterns, composable vs atomic operations.

Verified:
- Granularity criteria section (lines 7-39): atomic, composable, complex steps with split/merge guidance
- Prerequisite validation patterns (lines 42-91): creation, transformation, investigation gate types with heuristics
- Step structure template (lines 95-126): complete template with all required fields
- Design divergence acknowledged: separate file instead of section in `patterns.md` — documented in design-review and checkpoint-5-vet reports as intentional

No findings. The file is well-structured, concrete, and covers all specified content areas.

---

## anti-patterns.md (FR-4)

### No Critical, Major, or Minor findings.

FR-4 required: general-step anti-patterns section.

Verified:
- General Step Anti-Patterns section present (line 23)
- 6 anti-patterns in table format with Bad Example and Correct Pattern columns
- Includes: missing investigation prerequisite, vague success criteria, structure-only validation, missing Expected Outcome, ambiguous Error Conditions, downstream reference in bootstrapping
- Bootstrapping anti-pattern (line 32) directly addresses learnings entry "Reference upstream in bootstrapping"

No findings.

---

## examples.md (FR-4)

### No Critical, Major, or Minor findings.

FR-4 required: complete general-step example.

Verified:
- General Step Examples section (line 240)
- Two complete examples: creation step with investigation prerequisite (line 242), transformation step self-contained (line 292)
- Both examples include all template fields: Objective, Prerequisites, Implementation, Expected Outcome, Error Conditions, Validation, Report location
- Key Observations section (line 330) explains creation vs transformation patterns
- Four-status taxonomy used correctly in creation example (lines 258-261)

No findings.

---

## Cross-Cutting Checks

### Path consistency

- `vet-requirement.md:105` references `agent-core/agents/vet-taxonomy.md` — verified exists on disk
- `runbook-review.md:5` references `deliverable-review.md` — verified exists at `agents/decisions/deliverable-review.md`
- `orchestration-execution.md:89` references `vet-requirement.md` — exists at `agent-core/fragments/vet-requirement.md`
- `orchestration-execution.md:118` references `wt/error-handling` worktree — consistent with session.md worktree tasks
- `workflows-terminology.md:19` references `runbook-review-agent` — **DOES NOT EXIST** (Finding #1)

**SKILL.md references section gap:** `agent-core/skills/runbook/SKILL.md` line 806 lists `references/patterns.md` but does not list `references/general-patterns.md`. The inline reference at line 719 says "See `references/patterns.md` for granularity criteria" — but granularity criteria for general steps are in `general-patterns.md`, not `patterns.md`. This is outside the reviewed file set (SKILL.md is not in scope) but affects discoverability of the FR-4 deliverable. Planners creating general-step runbooks and following SKILL.md references would find only TDD patterns.

### Terminology consistency

Four-status taxonomy (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE) used consistently across:
- `vet-requirement.md` lines 99-103 (definitions)
- `orchestration-execution.md` lines 85, 87, 89, 108 (UNFIXABLE only, appropriate for escalation context)
- `examples.md` lines 258-261, 277, 284, 322 (in example steps)
- `general-patterns.md` line 120 (UNFIXABLE in validation template)

No terminology inconsistencies found.

### Design cross-references

- Escalation tiers in `orchestration-execution.md` match design Phase 6 spec
- Vet taxonomy in `vet-requirement.md` matches design Section "Vet Status Taxonomy"
- Behavioral vacuity detection in `runbook-review.md` matches design Section "Key Design Decisions" #8
- Deliverable review in `workflows-terminology.md` matches design Phase 5 FR-16 spec

---

## Finding Summary

| # | File | Severity | Axis | Description |
|---|------|----------|------|-------------|
| 1 | workflows-terminology.md:19 | Critical | Accuracy | Non-existent agent name `runbook-review-agent` |
| 2 | runbook-review.md:27 | Minor | Usability | LOC/20 heuristic scope ambiguous |
| 3 | vet-requirement.md:88 | Major | Completeness | Constraints field not covered by enforcement paragraph |
| 4 | vet-requirement.md:117 | Minor | Consistency | "4 gates" includes "conclusion" which is output not gate |
| 5 | orchestration-execution.md:97 | Major | Accuracy | Bare "refactor agent" name without path or backtick |
| 6 | orchestration-execution.md:116 | Minor | Consistency | Dot-prefix on h3 subsection inconsistent with file convention |

**Cross-cutting note (not a finding against reviewed files):** SKILL.md References section omits `general-patterns.md`, reducing discoverability of FR-4 general-step guidance for planners.
