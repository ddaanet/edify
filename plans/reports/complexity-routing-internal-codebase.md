# Complexity Routing Grounding — Internal Codebase Exploration Report

**Date:** 2026-02-26

**Purpose:** Surface current classification logic, routing decisions, decision gates, failure history, and work-type vocabulary as input for `/ground plans/complexity-routing/problem.md`.

**Key Finding:** Grounding reveals three distinct dimensions currently conflated:
1. **Code type** (behavioral vs prose) — classification criteria
2. **Work type** (production vs exploration vs investigation) — missing vocabulary
3. **Artifact destination** (src/ vs plans/prototypes/ vs etc.) — affects ceremony level, not currently assessed

---

## 1. Current Classification and Routing Logic

### Location: `/Users/david/code/edify-wt/session-scraping-prototype/plugin/skills/design/SKILL.md`

#### Phase 0: Complexity Triage (Lines 24-103)

**Requirements-Clarity Gate (D+B anchor):** Lines 26-37
- Assess completeness: each FR has concrete mechanism, each NFR has measurable criterion
- Produces visible output block: requirements source, completeness check, routing decision
- Routes to `/requirements` if vague; otherwise proceed to triage

**Triage Recall (D+B anchor):** Lines 47-59
- Loads: "when behavioral code", "when complexity", "when triage", domain keywords
- Invokes: `plugin/bin/when-resolve.py` before classification
- Purpose: surface codified decisions constraining classification before triage happens

**Classification Criteria (Lines 60-75):**

Uses Stacey Matrix framework (named axes):
1. **Implementation certainty** — approach known? Prior art in codebase? Known technique?
2. **Requirement stability** — FRs agreed and mechanism-specified? Scope bounded?

- **Complex:** Either axis low → architectural decisions, multiple valid approaches, uncertain/evolving requirements, significant codebase impact
- **Moderate:** Both axes moderate-to-high → clear requirements, no architectural uncertainty, well-defined scope, **behavioral code changes** (new functions, changed logic paths, conditional branches)
- **Simple:** Both axes high, **NO behavioral code changes** — single file, obvious implementation, no architectural decisions
- **Defect:** Observed ≠ expected behavior → structured-bugfix workflow

**Classification Gate (D+B anchor):** Lines 76-86
- Glob or Grep on affected files to confirm behavioral code involvement
- Produces visible output block: classification, implementation certainty, requirement stability, behavioral code check result, evidence

**Key constraint:** Behavioral code presence qualifies task as Moderate minimum, regardless of conceptual simplicity (line 72).

#### Phase B: Execution Readiness Gate (Lines 248-279)

**Sufficiency criteria (Lines 254-260):**
- Approach is concrete (specific algorithm/pattern, not "explore options")
- Key decisions resolved (no open questions)
- Scope boundaries explicit (IN/OUT enumerated)
- Affected files identified
- No architectural uncertainty remains

**Direct execution path (Lines 263-273):**
- All decisions pre-resolved
- **All changes are prose edits or additive (no behavioral code changes)**
- Insertion points identified
- No cross-file coordination
- No implementation loops
- → Execute inline, delegate to corrector, `/handoff --commit`

**Routing to `/runbook` (Lines 275-277):**
- If execution-ready criteria fail
- Routes incomplete design to `/runbook` for phase-by-phase planning
- → Commit design, `/handoff [CONTINUATION: /commit]`

### Location: `/Users/david/code/edify-wt/session-scraping-prototype/plugin/skills/runbook/SKILL.md`

#### Tier Assessment (Lines 72-175)

**Assessment Criteria (Lines 80-91):**
Output block shows:
- Files affected: ~N
- Open decisions: none / [list]
- Components: N (sequential/parallel/mixed)
- Cycles/steps estimated: ~N
- Model requirements: single/multiple
- Session span: single/multi

**Tier 1: Direct Implementation (Lines 95-117)**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit

**Tier 2: Lightweight Delegation (Lines 118-158)**
- Scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization)
- No model switching needed

**Tier 3: Full Runbook (Lines 166-175)**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running/multi-session execution
- Complex error recovery
- >15 files or complex coordination
- >10 TDD cycles with cross-component dependencies

**Key constraint:** File count (lines 99-101, 121, 173) assumes production conventions (test mirrors, module splitting, lint gates).

**Artifact-type model override (Lines 60-68):**
- Editing skills, fragments, agents, workflow decisions → opus required regardless of task complexity
- These are agentic prose: wording directly determines downstream agent behavior

---

## 2. Decision Gates Between Entry and Execution

**Complete decision flow path:**

```
USER → /design skill invoked
  ↓
Phase 0: Complexity Triage
  ├─ Requirements-clarity gate (D+B: visible output block)
  │  ├─ Vague → route to /requirements (STOP)
  │  └─ Clear → proceed
  ├─ Triage Recall (D+B: when-resolve.py call)
  ├─ Classification Criteria (Stacey axes assessment)
  ├─ Classification Gate (D+B: Glob/Grep for behavioral code confirmation)
  │  Produces visible output block: classification, axes, evidence
  ├─ Routing decision:
  │  ├─ Simple → Execute directly (skip design ceremony)
  │  ├─ Moderate → Route to /runbook
  │  ├─ Complex → Proceed to Phase A
  │  └─ Defect → Route to structured-bugfix
  │
  ├─ Phase A: Research + Outline
  │  ├─ A.0: Requirements checkpoint
  │  ├─ A.1: Documentation checkpoint (invoke `/recall all`)
  │  ├─ A.2: Explore codebase (delegate if open-ended)
  │  ├─ A.3-5: Research and outline generation
  │  ├─ Post-outline complexity re-check (downgrade criteria: additive, no loops, no questions, explicit scope, no sequencing)
  │  │  └─ If downgrade criteria met → Skip A.6, proceed to Phase B
  │  │  └─ If not met → Continue to A.6
  │  └─ A.6: Outline review (FP-1 checkpoint, delegate to outline-corrector)
  │
  ├─ Phase B: Iterative Discussion + Sufficiency Gate
  │  ├─ User validates outline (interactive discussion)
  │  ├─ Sufficiency assessment (all 5 criteria met?)
  │  │  ├─ Sufficient + execution-ready criteria met → Execute inline, corrector, `/handoff --commit`
  │  │  ├─ Sufficient + not execution-ready → Commit design, `/handoff [/runbook]`
  │  │  └─ Insufficient → Proceed to Phase C
  │
  └─ Phase C: Generate Design
     ├─ C.1: Create design.md
     ├─ C.2: Checkpoint commit
     ├─ C.3: Review design (delegate to design-corrector, CDR criteria)
     ├─ C.4: Check for unfixable issues
     └─ C.5: Execution readiness gate
        ├─ Execution-ready → Execute, corrector, `/handoff --commit`
        └─ Not execution-ready → Commit design, `/handoff [/runbook]`
```

**Critical gates (present in /design skill):**
1. Requirements-clarity (D+B anchored) — Route to /requirements if vague
2. Triage-recall (D+B anchored) — when-resolve.py call
3. Classification-gate (D+B anchored) — Glob/Grep for behavioral code
4. Post-outline complexity re-check — Downgrade criteria
5. Sufficiency-gate (Phase B) — Execute inline vs route to /runbook
6. Execution-readiness-gate (Phase C.5) — Execute vs route to /runbook

**Gate enforcement mechanism:** D+B anchor pattern (Distinct + Before):
- Tool calls (Glob, Grep, when-resolve.py, Bash) produce visible output before routing decision
- Prevents prose-only gates where agents rationalize around instructions
- Observable output proves gate was executed

---

## 3. Git History — Failure Patterns and Corrections

### Commits Related to Routing and Classification

**Primary grounding session:**
- **557c2eed** (2026-02-25): `🏗️ Ground design skill against 6 external frameworks`
  - Stacey axes named (implementation certainty × requirement stability)
  - Requirements-clarity gate upgraded to D+B structured output
  - PDR/CDR differentiated criteria for outline-corrector and design-corrector
  - Defect/structured-bugfix path added (Cynefin Complicated domain)
  - Companion task enforcement via enumeration-before-processing
  - Decision tradeoff documentation rule added (ADR consequences pattern)
  - Generated comprehensive grounding report with internal codebase and external research branches

**Recall gate anchoring (multiple commits):**
- **59904514** (2025-09-29): `🤖 Anchor recall gates with when-resolve.py in /reflect and /runbook`
  - Root cause: prose-only gates fail, agents rationalize around skip conditions
  - Fix pattern: D+B anchor — tool calls providing observable evidence
  - Applied to all high-stakes gates

- **e1a35cd1** (2025-09-29): `🤖 Restructure design skill triage with 4 structural fixes`
  - Separated Classification Criteria / Classification Gate / Routing into distinct sections
  - Added visible output blocks at each decision point
  - Prevents premature closure (decision-maker commits before completing assessment)

**Complexity re-check gate:**
- **41a4b163** (2025-09-21): `🤖 Add execution readiness gate to design skill`
  - Added post-outline complexity downgrade assessment
  - Root cause: Cynefin principle states domain can shift; one-shot triage insufficient
  - Evidence: outline-corrector + design.md + design-corrector tokens wasted on two-file prose edit
  - Fix: downgrade criteria (additive, no loops, no questions, explicit scope, no sequencing)

**Session-scraper routing (evidence of problem):**
- **a86043cc** (2026-02-12): `🏗️ Design session scraper; RCA pipeline routing for prototypes`
  - Classified Complex (correct — data model decisions needed)
  - Design outline resolved all complexity
  - Routed to `/runbook` Phase 0.5 discovery (would assess as Tier 3, ~20 TDD cycles)
  - User interrupted: "that was supposed to be a quick prototype"
  - Root cause: behavioral-code gate routes ALL non-prose to /runbook regardless of artifact destination

- **2c0e5996** (2026-02-13): `⚗️ Add session-scraper.py prototype — 4-stage pipeline`
  - Implemented directly as `plans/prototypes/session-scraper.py` (single prototype file, no tests, no TDD)
  - No runbook, no orchestration, no production ceremony
  - Demonstrates actual needed ceremony level: direct implementation

### Pattern Class: Procedural Momentum

**Evidence:** Multiple sessions show agents following pipeline procedures (design → runbook → orchestrate) even when explicit constraints (prototype, spike, exploration) suggest different path.

**Mechanism:** Behavioral-code classification gate has single output path (route to /runbook) with no assessment of artifact destination or work type. Pipeline momentum overrides contextual judgment.

**Timeline:**
1. 2026-02-12: Session-scraper design produced
2. 2026-02-12: Runbook skill Phase 0.5 discovery begins
3. 2026-02-12: User interrupts: "quick prototype"
4. 2026-02-12: Session notes RCA: "design skill's behavioral-code gate routes ALL non-prose work to /runbook; no exploration/prototype work type in pipeline vocabulary"
5. 2026-02-25: Full grounding session on complexity routing (not yet executed)

---

## 4. Learnings and RCA Evidence

### From `/Users/david/code/edify-wt/session-scraping-prototype/agents/learnings.md`

**Line 59-63: "When routing prototype/exploration work through pipeline"**

Anti-pattern:
- Design skill's behavioral-code gate routes ALL non-prose work to /runbook
- /runbook tier assessment counts files against production conventions (test mirrors, module splitting, lint gates)
- C-3 prototype script in plans/prototypes/ assessed as Tier 3 (~20 TDD cycles)
- Procedural momentum from practiced pipeline overrides explicit prototype constraint

Correct pattern:
- Artifact destination determines ceremony level
- Prototype scripts (plans/prototypes/, one-off analysis, spikes) don't need runbooks, TDD, or test files
- Design resolves complexity; post-design a prototype is direct implementation regardless of behavioral code

Evidence:
- Session-scraping prototype interrupted by user after /runbook began Phase 0.5 discovery for "quick prototype"

Related learning:
- **Line 46-50: "When redesigning a process skill"**
  - The skill's own failure modes govern its redesign if used on itself (circular dependency)
  - Correct pattern: ground against external frameworks first
  - By grounded skill's own classification criteria, the redesign has clear requirements, no architectural uncertainty → Moderate, routes to direct execution or /runbook, not full /design

### From `/Users/david/code/edify-wt/session-scraping-prototype/plans/complexity-routing/problem.md`

**Current Model (Line 11-17):**
- Classification (design skill Phase 0): Stacey Matrix — implementation certainty × requirement stability → Simple/Moderate/Complex/Defect
- Execution-readiness (design skill Phase B): Binary — prose edits → execute directly, behavioral code → /runbook
- Tier assessment (runbook skill): File count, cycle count, session span → Tier 1/2/3. Assumes production conventions.

**Gaps Identified (Line 19-27):**

1. **No exploration/prototype work type:** Vocabulary is Simple/Moderate/Complex/Defect. Missing: Prototype, Spike, Exploration, One-off. C-3-style constraints don't map to pipeline concept.

2. **Behavioral code always routes to /runbook:** Sufficiency gate has no path for "behavioral code that doesn't need planning ceremony." Resolved design for single prototype script gets same routing as multi-module production feature.

3. **Tier assessment ignores artifact destination:** `/runbook` counts files against production conventions regardless of whether target is `src/` (production, needs tests) or `plans/prototypes/` (exploration, no tests).

4. **Complexity resolved but routing not reassessed:** Design resolves architectural uncertainty, but routing decisions at sufficiency gate use static criteria rather than post-resolution state.

---

## 5. Existing Work-Type Vocabulary

### Locations and Current Usage

**1. Problem statement vocabulary (problem.md, lines 21-24):**
- Prototype (constraint C-3: "standalone prototype first")
- Spike
- Exploration
- One-off analysis
- Migration helpers

**Note:** These are mentioned as MISSING from the pipeline vocabulary, not as existing categories.

**2. Artifact destination vocabulary (implicit, not systematized):**

From requirement definitions:
- `plans/prototypes/` — exploration, one-off analysis, spikes (no test mirrors, no TDD required)
- `plans/spikes/` — exploratory investigations (no formal ceremony)
- `src/` — production code (requires test mirrors, lint gates, module structure)
- `plugin/bin/` — utility scripts (production-grade, may need tests)
- `plans/<job>/` — plan artifacts (prose design, runbooks, reports)

**Evidence:**
- `/Users/david/code/edify-wt/session-scraping-prototype/plugin/skills/requirements/SKILL.md` line 96 states: "Save exploration prototypes to `plans/prototypes/` (not `tmp/`) — they are referenced artifacts, not ephemera"
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/session-scraping/requirements.md` line 61 states: "Start as scripts in `plans/prototypes/` or `plugin/bin/`. Integration into `src/edify/` happens later"

**3. Behavior-type classification (current, lines 340-343 in workflow-planning.md):**
- Behavioral code: new functions, changed logic paths, conditional branches (routes Moderate minimum)
- Prose edits: documentation, configuration, declarations (routes to Simple/direct execution)

**4. Work-type in execution roles (implicit):**

From `/Users/david/code/edify-wt/session-scraping-prototype/plugin/docs/general-workflow.md` line 3:
- Purpose: Execute one-off, ad-hoc tasks that don't repeat

From `/Users/david/code/edify-wt/session-scraping-prototype/plugin/docs/tdd-workflow.md` lines 20, 41:
- Prototype/exploration → opposite of "feature requires behavioral verification"

---

## 6. Session-Scraper Case Study: Conflation in Action

**Timeline and Classification:**

1. **Requirements:** `/Users/david/code/edify-wt/session-scraping-prototype/plans/session-scraping/requirements.md`
   - 4 FRs (scanner, parser, aggregator, correlator)
   - 3 constraints (C-1: targeted expansion, C-2: optional detail, C-3: standalone prototype first)
   - 5 out-of-scope items

2. **Classification at /design entry:**
   - **Code type:** Behavioral (new data models, pipeline code)
   - **Complexity:** Complex (C-3 requires design: data model decisions, multiple valid approaches)
   - **Work type:** Exploration/Prototype (C-3: "standalone prototype first")
   - **Artifact destination:** `plans/prototypes/` (not src/)

3. **Design Phase 0 routing:** Complex → Proceed to Phase A-C (correct for complexity level)

4. **Design Phase A-B outcome:** Outline resolved all complexity
   - Approach concrete (4-stage pipeline, specific models)
   - Key decisions resolved (no open questions)
   - Scope explicit (7 entry types, FR-specific mapping)

5. **Design Phase C.5: Execution Readiness Assessment**
   - All decisions pre-resolved: ✓
   - All changes behavioral code: ✗ (fails execution-ready criteria)
   - → Routes to `/runbook` for planning

6. **/runbook entry: Tier Assessment**
   - Files affected: 1 (plans/prototypes/session-scraper.py)
   - Cycles/steps estimated: ~20+ (based on production conventions)
   - **Assessment:** Tier 3 (Full Runbook)
   - Rationale: Behavioral code (data models, pipeline functions), >10 cycles
   - **Problem:** Assessment ignores artifact destination (plans/prototypes/, not src/)

7. **Runbook Phase 0.5: Discovery begins**
   - Discovers file structure, module dependencies
   - Plans 20+ cycles of TDD
   - User interrupts: "this was supposed to be a quick prototype"

**Root Cause Analysis:**

| Dimension | Assessment | Consequence |
|-----------|------------|-------------|
| Code type | Behavioral | Routes to Moderate/Complex in design |
| Complexity | Complex | Justified full design (outline resolved it) |
| Work type | Prototype | Not assessed in pipeline |
| Artifact destination | plans/prototypes/ | Not assessed in tier assignment |
| Ceremony needed | Minimal (direct implementation) | Not surfaced by any gate |
| Ceremony applied | Tier 3 (full runbook) | User interrupted |

**What should have happened:**

After design outline resolved complexity:
- Post-outline complexity re-check gate: Passed (additive changes, no loops, no questions, explicit scope)
- Should have downgraded to Moderate/Simple
- Should NOT have routed to /runbook for behavioral code in prototype script

Or, at /runbook entry:
- Tier assessment should assess artifact destination
- plans/prototypes/ → Direct implementation category (no test mirrors required)
- 1-file prototype → Tier 1, not Tier 3

**What actually happened:** Procedural momentum (design → runbook → orchestrate) overrode contextual judgment (prototype constraint, artifact destination, ceremony mismatch).

---

## 7. Grounding Report: Design Skill (2026-02-25)

**Location:** `/Users/david/code/edify-wt/session-scraping-prototype/plans/reports/design-skill-grounding.md`

**Key grounding principles applied to complexity routing:**

**Principle 1:** Complexity classification is a routing signal, not a quality judgment
- Cynefin: Clear domain routes to best-practice; Complicated to expert analysis; Complex to experimentation
- Stacey: Two concrete axes (certainty × agreement) determine appropriate workflow
- Project adaptation: Simple/Moderate/Complex routing

**Principle 2:** Complexity can shift mid-task; one-shot triage insufficient
- Cynefin: Expect reassessment as intrinsic; domains shift
- Project adaptation: Post-outline complexity re-check gate (downgrade criteria)

**Principle 3:** Requirements completeness is prerequisite to design
- IEEE 29148: Requirements validation produces observable artifact before design begins
- Project adaptation: Requirements-clarity gate with D+B anchor

**Principle 4:** Problem definition must precede solution design
- Double Diamond: Diamond 1 (discover/define) before Diamond 2 (develop/deliver)
- Project adaptation: /requirements → /design routing based on problem-definition completeness

**Principle 5:** Design output must record context, decision, AND consequences
- ADR: Each decision includes context, decision, status, consequences
- Project adaptation: design-content-rules.md should require tradeoffs element

**Principle 6:** Validation requires observable evidence, not self-assessment
- IEEE 29148, Cynefin, Stacey all require observable validation
- Project adaptation: D+B anchor pattern (tool calls proving gate execution)

**Principle 7:** Design review should be staged with differentiated criteria
- NASA PDR/CDR: PDR validates direction; CDR validates implementability
- Project adaptation: outline-corrector (PDR) vs design-corrector (CDR) with distinct criteria

**Principle 8:** Assessment must be separated from action
- Decision science: Separate evaluation from disposition to prevent premature closure
- Project adaptation: Classification Criteria / Classification Gate / Routing as distinct sections

**Gap identified (Principle 2 relevance to routing):**
- Cynefin expects domain reassessment as intrinsic
- Current design skill has post-outline re-check
- Runbook tier assessment has NO re-assessment gate
- Gap: Tier assessment should re-assess artifact destination after design complexity is resolved

---

## 8. Patterns Across Findings

### Conflation Points (Where Multiple Dimensions Collapse)

**Design Skill Behavioral-Code Classification (Line 72 of SKILL.md):**
```
"No behavioral code changes — new functions, changed logic paths,
conditional branches are Moderate regardless of conceptual simplicity."
```
- Conflates: Code type (behavioral vs prose) with complexity (Simple vs Moderate)
- Problem: Prototype scripts are behavioral but not complex post-design
- Missing: Work-type dimension (exploration vs production)

**Runbook Tier Assessment File Count (Lines 99-101, 121, 173 of SKILL.md):**
```
Tier 1: <6 files
Tier 2: 6-15 files
Tier 3: >15 files
```
- Conflates: File count with ceremony level
- Assumption: All files need production conventions (tests, lint, module structure)
- Problem: plans/prototypes/ scripts don't need test mirrors
- Missing: Artifact-destination dimension

### Decision Gate Sequence Issues

**Current sequence in /design:**
1. Complex classification → Design phases A-C
2. Outline generated
3. Post-outline re-check → Downgrade to Moderate if criteria met
4. Sufficiency assessment → Route to /runbook if not execution-ready

**Issue:** Execution-ready criteria (line 265-268) exclude "behavioral code changes" globally
- Does not account for: behavioral code in exploration/prototype context
- Does not distinguish: production modules vs prototype scripts

**In /runbook:**
1. Tier assessment → Determines ceremony (Tier 1/2/3)
2. No re-assessment of complexity post-design
3. No assessment of artifact destination
4. No assessment of work type

### Vocabulary Gaps

| Dimension | Current Vocabulary | Missing Vocabulary |
|-----------|-------------------|-------------------|
| Code type | Behavioral vs Prose | (adequate) |
| Complexity | Simple, Moderate, Complex, Defect | (adequate, Stacey-grounded) |
| Work type | (none) | Prototype, Spike, Exploration, One-off, Investigation, Production |
| Artifact destination | (implicit in paths) | Production (src/), Exploration (plans/prototypes/), Investigation (plans/*/reports/) |
| Artifact permanence | (implicit) | Prototype (referenced, saved), Ephemeral (tmp/), Production (version-controlled) |

---

## 9. Scope of Grounding

**Problem Statement** (`plans/complexity-routing/problem.md`):
- Conflation of code type (behavioral vs prose) with work type (production vs exploration)
- Routes prototype scripts through production TDD ceremony

**Scope Defined (Line 36-38 of problem.md):**
- Ground the classification + routing model
- Don't redesign /design or /runbook wholesale
- Produce revised taxonomy and routing rules
- Skill edits are separate execution task (moderate complexity)

**Expected Output:**
- Revised classification model including work-type dimension
- Revised routing rules informed by artifact destination
- Grounded in external frameworks (Cynefin, XP spikes, Lean, etc.)

**Related Grounding Already Done:**
- Design skill grounded against 6 external frameworks (report: plans/reports/design-skill-grounding.md)
- Recall pass grounded against 4-pass pipeline memory model (report: plans/reports/recall-pass-grounding.md)
- Skill optimization grounded against Segment → Attribute → Compress framework (report: plans/reports/skill-optimization-grounding.md)

---

## 10. Key File Locations (Absolute Paths)

### Classification and Routing Logic
- `/Users/david/code/edify-wt/session-scraping-prototype/plugin/skills/design/SKILL.md` — Phase 0 (triage), Phase B (sufficiency), Phase C.5 (execution readiness)
- `/Users/david/code/edify-wt/session-scraping-prototype/plugin/skills/runbook/SKILL.md` — Tier 1/2/3 assessment criteria

### Grounding and Evidence
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/complexity-routing/problem.md` — Problem statement, gaps, grounding questions
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/reports/design-skill-grounding.md` — Design skill grounded against 6 frameworks, 8 principles, gap analysis
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/reports/design-skill-internal-codebase.md` — Internal codebase exploration (part of grounding research)

### Learning and RCA
- `/Users/david/code/edify-wt/session-scraping-prototype/agents/learnings.md` — Line 59-63 "When routing prototype/exploration work"; Line 46-50 "When redesigning a process skill"
- `/Users/david/code/edify-wt/session-scraping-prototype/agents/session.md` — Line 16-21 RCA from session-scraping interruption

### Work-Type References
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/session-scraping/requirements.md` — Constraint C-3 "standalone prototype first"; line 61 "Start as scripts in plans/prototypes/"
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/session-scraping/outline.md` — Design outline for prototype (4-stage pipeline approach)
- `/Users/david/code/edify-wt/session-scraping-prototype/plans/prototypes/session-scraper.py` — Actual implemented prototype (single file, no tests, direct implementation)

### External Framework Grounding (in design skill grounding report)
- Cynefin (Snowden, IBM, 1999) — Domain-based complexity classification
- Stacey Matrix (1990s) — Two-axis triage (certainty × agreement)
- IEEE 29148:2018 — Requirements validation and design prerequisites
- Double Diamond (UK Design Council, 2005) — Diverge-converge workflow
- ADR process (Nygard 2011) — Architectural decision recording
- NASA PDR/CDR — Staged design review gates

### Decision File References
- `/Users/david/code/edify-wt/session-scraping-prototype/agents/decisions/workflow-planning.md` — Line 341-343 behavioral code classification rule
- `/Users/david/code/edify-wt/session-scraping-prototype/agents/decisions/workflow-execution.md` — Model selection, design review patterns
- `/Users/david/code/edify-wt/session-scraping-prototype/agents/decisions/orchestration-execution.md` — Tier assessment and routing

---

## 11. Unresolved Questions

**From Problem Statement (lines 29-34 of problem.md):**

1. What dimensions should complexity classification use beyond implementation certainty × requirement stability?
   - **Evidence:** Current Stacey axes adequate for code complexity; work-type dimension needed separately

2. How do established frameworks (Cynefin, Boehm spiral, XP spikes, Lean build-measure-learn) handle exploratory work?
   - **Evidence:** XP spikes are explicitly short-term exploratory timeboxes; Lean validates assumptions in build-measure-learn cycles; Cynefin Complex domain routes to experimentation

3. What routing decisions should change based on artifact destination (production module vs prototype vs one-off)?
   - **Evidence:** Tier assessment ignores destination; same file count triggers same ceremony regardless of src/ vs plans/prototypes/

4. Where should fix points land — triage (Phase 0), sufficiency gate (Phase B), tier assessment (/runbook), or a new pre-routing gate?
   - **Evidence:** Multiple candidates, each with constraints:
     - Phase 0: Early, but adds surface area to already-crowded triage
     - Phase B: Post-complexity-resolution, can assess work-type contextually, but only for Complex jobs
     - Tier assessment: All jobs routed here, but after design already committed
     - New pre-routing gate: Between design sufficiency and runbook invocation?

---

## Summary

**Current state:** Three dimensions conflated in single behavioral-code classification gate:
1. Code type (behavioral vs prose) — present, working
2. Complexity (Simple/Moderate/Complex) — present, grounded against Stacey Matrix
3. Work type (production vs exploration/prototype/spike) — missing

**Consequence:** Prototype and exploratory scripts routed through production TDD ceremony based on code type, not work type.

**Evidence:** Session-scraper prototype interrupted by user after /runbook began Tier 3 planning for "quick prototype."

**Grounding foundation available:** Design skill grounded against 6 external frameworks (commit 557c2eed); 8 principles; gap analysis completed. Ready for /ground session on complexity-routing problem.

**Next step:** `/ground plans/complexity-routing/problem.md` to produce revised classification + routing model informed by XP spikes, Lean, Cynefin exploratory domains, and artifact-destination assessment.
