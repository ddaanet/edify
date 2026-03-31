# Complexity Routing: Grounded Classification and Routing Model

**Grounding:** Strong — 7 external frameworks researched (Cynefin, Stacey Matrix, Boehm Spiral, XP Spikes, SAFe Enablers, Lean Startup, Gartner Bimodal IT), 3 directly applicable with structural mappings, codebase evidence from 6+ commits and 1 documented failure case.

**Purpose:** Revised classification + routing model that separates complexity (design ceremony) from work type (execution ceremony) and artifact destination (quality obligations). Consumers: `/design` skill (Phase 0 classification, Phase B routing), `/runbook` skill (tier assessment).

---

## Framework Mapping

### Selected Frameworks

**Primary — XP Spikes (Beck):** Most directly applicable. Operates at story level (maps to task level). Provides categorical distinction: user story (delivers capability, full ceremony) vs spike (delivers knowledge, minimal ceremony). Binary but structurally sound — the routing question is "what does this produce?"

**Primary — Boehm Spiral (Boehm, 1986):** Risk-driven process selection per cycle. Throwaway prototyping is first-class: prescribed when requirements or interface risks dominate, explicitly expected to be discarded. Key contribution: process selection happens per iteration, not project-wide.

**Secondary — Cynefin (Snowden):** Validated existing Stacey-based complexity model. Complex domain routes to "probe → sense → respond" (experimentation before planning). Confirms: design resolves complexity by moving work from Complex to Complicated domain; post-resolution routing should reflect the shift.

**Secondary — Lean Startup (Ries):** Sharpest vocabulary for transition gate. Pivot-or-persevere decision provides explicit ceremony graduation model. Contribution: exploration deliverables are "validated learning" not shipped capability; transition to production requires explicit decision.

**Secondary — SAFe Enablers:** Formalizes exploration as first-class backlog type (exploration enabler). Contribution: different done criteria for exploration vs production, even when using same process structure.

### Framework-to-Internal Mapping

| External Concept | Internal Equivalent | Mapping Tightness |
|-----------------|---------------------|-------------------|
| XP spike vs story | Work type dimension (exploration vs production) | Tight — same categorical distinction |
| Boehm throwaway prototype | `plans/prototypes/` artifact destination | Tight — both are explicitly disposable |
| Boehm risk-driven process selection | Per-task ceremony routing (not per-project) | Tight — same granularity |
| Cynefin domain shift | Post-outline complexity re-check | Tight — existing gate implements this |
| Cynefin Complex → probe | Design phases A-C (outline, iterate, resolve) | Tight — probing before committing |
| Lean pivot-or-persevere | Prototype → production promotion gate | Loose — no explicit gate exists yet |
| SAFe exploration enabler done criteria | Knowledge-based vs capability-based done | Moderate — implicit in artifact destination |

### Where Mappings Are Loose

- **Ceremony graduation:** No external framework provides a continuous spectrum. XP is binary (spike/story), Lean Startup has one gate (pivot/persevere). The routing model needs at least three levels (direct/lightweight/full), which is a project adaptation without direct external precedent.
- **Artifact destination as routing signal:** No framework uses filesystem location as a routing criterion. This is a project-specific operationalization of Boehm's throwaway vs evolutionary prototype distinction.
- **Time-boxing:** XP spikes are explicitly time-boxed. Current pipeline has no time-boxing concept for exploration. Not addressed in this model — flagged as future consideration.

---

## Adapted Principles

### Principle 1: Work type and complexity are independent dimensions

Exploration and production are categorically different work types requiring different process — every framework examined distinguishes them (Cynefin Complex vs Complicated, XP spike vs story, Boehm throwaway vs evolutionary, Lean experiment vs persevere). The distinction is universal despite varying vocabulary.

**Project instance:** Current pipeline conflates work type into the complexity axis. A prototype script is Complex (correct: data model decisions) AND Exploration (not assessed). After design resolves complexity, the work type remains Exploration — but routing treats resolved-Complex the same as production Moderate.

**Implication:** Classify work type alongside complexity at Phase 0. Both are properties of the incoming work, knowable before design begins. They serve different routing gates: complexity → design ceremony, work type → execution ceremony.

### Principle 2: Deliverable type determines done criteria, not code type

Whether the deliverable is knowledge (validated learning, technical understanding, feasibility answer) or capability (working feature, behavior change, user-facing output) determines quality obligations — not whether the code is behavioral (XP spikes produce behavioral code with spike-level obligations; Boehm throwaway prototypes are explicitly disposable despite being functional code).

**Project instance:** The behavioral-code gate at Phase B routes all behavioral code to `/runbook` regardless of deliverable type. A prototype script (knowledge deliverable: "does this pipeline approach work?") gets production-level ceremony (capability obligations: test mirrors, lint gates, module structure).

**Implication:** The execution-readiness gate should assess deliverable type, not just code type. Behavioral code producing knowledge has different obligations than behavioral code producing capability.

### Principle 3: Process weight should match current uncertainty, not initial classification

Uncertainty drives process selection in every framework: Cynefin routes by cause-effect knowability, Stacey by requirement clarity × approach certainty, Boehm by dominant risk per cycle. Critically, Boehm re-assesses risk per spiral cycle and Cynefin treats domain shifts as intrinsic — process selection is dynamic, not fixed at entry.

**Project instance:** Design resolves architectural uncertainty (moving work from Complex toward Complicated/Clear in Cynefin terms). The post-outline re-check gate implements this for complexity. But the execution routing at Phase B still uses pre-resolution criteria ("behavioral code → /runbook") rather than post-resolution state.

**Implication:** Phase B routing should assess post-resolution uncertainty. When design resolves all questions and the deliverable is exploration-grade, routing to /runbook applies production ceremony to resolved-exploration work.

### Principle 4: Throwaway artifacts are a first-class category deserving explicit routing

Boehm's spiral model treats throwaway prototyping as one of four prescribed approaches, selected when requirements or interface risks dominate. The prototype is explicitly expected to be discarded; it produces learning. XP spikes have the same property: code may be throwaway, the point is the learning.

**Project instance:** `plans/prototypes/` directory exists and is recognized by requirements skill ("Save exploration prototypes to plans/prototypes/"). But no routing gate recognizes this destination. Tier assessment counts files against production conventions regardless of destination.

**Implication:** Artifact destination should inform execution ceremony. Files destined for `plans/prototypes/` have Boehm-throwaway obligations (functional, produces learning); files destined for `src/` have production obligations (tested, linted, modular).

### Principle 5: Risk type drives process selection per task, not project-wide

Boehm's spiral model selects from waterfall, incremental, evolutionary prototyping, or throwaway prototyping per cycle based on the dominant risk type for that cycle. A project can use throwaway prototyping in early cycles and switch to structured development once uncertainty is resolved.

**Project instance:** The pipeline applies the same process model to all tasks regardless of their individual risk profile. A single prototype script gets the same tier assessment mechanics as a multi-module production feature. /runbook's tier criteria (file count, cycle count, session span) assume production risk profile for all inputs.

**Implication:** Tier assessment should account for artifact destination when computing file counts and ceremony level. Production destinations warrant production conventions; exploration destinations warrant functional-only conventions.

### Principle 6: Transition from exploration to production requires explicit decision

Lean Startup's pivot-or-persevere is the clearest model: after sufficient validated learning, the team makes an explicit decision to transition from exploration to production. Without this gate, exploratory artifacts silently accumulate or get promoted without quality transition.

**Project instance:** No explicit gate between `plans/prototypes/` and `src/`. Prototypes are written with exploration obligations; promotion to production would require a separate task with production obligations. This is already implicitly handled (requirements note "integration into src/ happens later") but not formalized in routing.

**Implication:** The routing model should acknowledge but not formalize this gate — it's a future task creation event, not a routing decision within the current pipeline. Note as a recognized boundary.

---

## Revised Classification Model

### Dimension 1: Complexity (existing — Stacey-grounded)

Unchanged. Two axes: implementation certainty × requirement stability → Simple / Moderate / Complex / Defect.

**Routes:** Design ceremony level (skip design / outline only / full design / structured bugfix).

### Dimension 2: Work Type (new — XP/Boehm/Lean-grounded)

**Assessed at:** Phase 0, alongside complexity. The work type is a property of the incoming task, typically knowable from requirements, constraints, or explicit user framing.

**Values:**

| Work Type | Diagnostic Question | Deliverable | Done Criteria |
|-----------|-------------------|-------------|---------------|
| **Production** | Does this deliver capability to users/agents? | Working feature, behavior change | Tested, linted, reviewed, integrated |
| **Exploration** | Does this produce knowledge or validate an approach? | Prototype, spike, feasibility answer | Functional, produces intended learning |
| **Investigation** | Does this produce a decision or analysis? | Report, decision entry, requirements | Accurate, complete, actionable |

**Grounding basis:** XP spike/story distinction (knowledge vs capability), Boehm throwaway/evolutionary distinction (disposable vs production-bound), SAFe enabler taxonomy (exploration/architectural/infrastructure/compliance).

**Assessment signals:**
- Explicit constraints: "prototype first," "spike," "investigate," "explore"
- Artifact destination: `plans/prototypes/`, `plans/spikes/`, `plans/reports/`
- Requirement framing: "can we...?" vs "build X" vs "what is...?"
- C-3-style constraints in requirements documents

### Dimension 3: Artifact Destination (new — Boehm-derived)

**Assessed at:** Phase 0 (from requirements) or Phase B (after design specifies output location).

**Values:**

| Destination | Quality Obligations | Convention Set |
|------------|-------------------|----------------|
| `src/`, `plugin/` | Production: tests, lint, module structure, review | Full production conventions |
| `plugin/skills/`, `agents/` | Agentic prose: wording quality, behavioral verification | Opus-tier editing, behavior invariance |
| `plans/prototypes/`, `plans/spikes/` | Exploration: functional, documented purpose, no test mirrors | Minimal conventions |
| `plans/reports/`, `agents/decisions/` | Investigation: accuracy, completeness, grounding | Prose quality conventions |
| `tmp/` | Ephemeral: none | No conventions |

**Grounding basis:** Boehm's throwaway vs evolutionary prototype distinction — the same code has different obligations based on whether it's disposable or production-bound.

---

## Revised Routing Rules

### Phase 0: Classification Output (expanded)

Current output block:
```
Classification: [Simple/Moderate/Complex/Defect]
Implementation certainty: [high/moderate/low]
Requirement stability: [high/moderate/low]
Behavioral code: [yes/no + evidence]
```

Expanded output block:
```
Classification: [Simple/Moderate/Complex/Defect]
Implementation certainty: [high/moderate/low]
Requirement stability: [high/moderate/low]
Behavioral code: [yes/no + evidence]
Work type: [Production/Exploration/Investigation]
Artifact destination: [path or category]
```

Work type and artifact destination are assessed from requirements, constraints, and user framing. If ambiguous, default to Production (highest ceremony — safe default).

### Phase B: Execution Routing (expanded)

Current logic:
```
IF all prose edits → direct execution
ELSE (behavioral code) → /runbook
```

Revised logic:
```
IF all prose edits → direct execution
ELSE IF work type = Investigation → direct execution (behavioral code unlikely; if present, minimal)
ELSE IF work type = Exploration AND design resolved all questions → direct execution
ELSE (work type = Production AND behavioral code) → /runbook
```

**Key change:** Exploration work with resolved design routes to direct execution, not /runbook. Design resolved the architectural uncertainty (Principle 3); the remaining work is implementation of a known approach at exploration-grade quality (Principle 2).

**Constraint:** "Design resolved all questions" means Phase B sufficiency criteria are met (approach concrete, decisions resolved, scope explicit, files identified). The work type only affects execution ceremony, not design sufficiency.

### Tier Assessment: Artifact-Destination-Aware (expanded)

If exploration or investigation work reaches /runbook (e.g., large exploration with multiple components), tier assessment should apply destination-appropriate conventions:

| Destination | File Count Basis | Cycle Conventions |
|-------------|-----------------|-------------------|
| Production (`src/`) | Include test mirrors, lint, module split | Full TDD cycles |
| Exploration (`plans/prototypes/`) | Script files only, no test mirrors | General steps (write, verify, iterate) |
| Agentic prose (`plugin/skills/`) | Skill files + behavior verification | Prose review cycles |
| Investigation (`plans/reports/`) | Report files only | General steps |

**Effect:** A single-file prototype in `plans/prototypes/` assessed against exploration conventions → Tier 1 (direct, <6 files, single session). Same script assessed against production conventions → inflated count from test mirrors, lint setup, module structure.

---

## Fix Points Summary

| Location | Current Behavior | Proposed Change | Principle |
|----------|-----------------|-----------------|-----------|
| Phase 0 output | Complexity + behavioral code only | Add work type + artifact destination | P1: independent dimensions |
| Phase B routing | Behavioral code → always /runbook | Exploration + resolved → direct execution | P2, P3: deliverable type, current uncertainty |
| Tier assessment | Production conventions for all | Destination-aware conventions | P4, P5: throwaway artifacts, per-task risk |
| Work-type vocabulary | None | Production / Exploration / Investigation | P1: categorical distinction |

---

## Grounding Assessment

**Quality label: Strong**

**Evidence basis:**
- 7 external frameworks researched across complexity theory, agile practices, risk management, and organizational models
- 3 frameworks directly applicable with structural mappings (XP Spikes, Boehm Spiral, Cynefin)
- 2 frameworks providing supporting vocabulary (SAFe Enablers, Lean Startup)
- 2 frameworks providing negative evidence (Gartner Bimodal — critique validates against false dichotomy; Stacey Matrix — confirms existing model but doesn't address work type)
- Internal evidence: 6+ relevant commits, 1 documented failure case with user interruption, 3 decision gates analyzed

**Searches performed:**
- "Cynefin framework software development work types routing"
- "spike prototype agile ceremony level process weight"
- "software development work type taxonomy classification"
- "process ceremony calibration software development"
- "Lean software development build-measure-learn spike exploration vs production"
- Codebase: design skill, runbook skill, decision files, learnings, git history

**Gaps resolved during discussion:**
- **Three-tier execution structure:** ~~Binary models adapted to three-level without external precedent.~~ Resolved: three tiers grounded in execution environment constraints (context window capacity, delegation overhead, prompt generation cost), not external methodology. See `agents/decisions/execution-strategy.md`.
- **Time-boxing:** ~~XP spikes are time-boxed; model doesn't incorporate time-boxing.~~ Removed: not relevant to agentic execution. Context window capacity is the natural bound; session scope enforces focus. Time-boxing solves a human-attention problem that doesn't exist in this execution environment.
- **Prototype-to-production gate:** ~~Lean Startup pivot-or-persevere not formalized.~~ Removed: handled by existing pipeline. User invokes `/design` with productization framing when ready. The decision is the user's; the process is standard `/design`.
- **Artifact destination as routing signal:** ~~No framework uses filesystem path as classification input.~~ Reclassified as adaptation, not gap. Principle grounded (Boehm throwaway vs evolutionary prototype). Mechanism (infer work type from destination path) is project-specific operationalization — same class as every other adaptation in this report.

**Out of scope (separate task):**
- **Tier thresholds:** File count and cycle count thresholds (<6, 6-15, >15) are ungrounded operational parameters needing empirical calibration.

---

## Sources

### Primary (framework originators)

- **Cynefin Framework** — Dave Snowden (IBM, 1999). [Wikipedia](https://en.wikipedia.org/wiki/Cynefin_framework), [TechTarget application guide](https://www.techtarget.com/searchsoftwarequality/tip/Agile-project-management-using-the-Cynefin-framework). Used: domain-based complexity routing, probe-sense-respond for exploration, domain shift principle.

- **Stacey Matrix** — Ralph Stacey. [Praxis Framework](https://www.praxisframework.org/en/library/stacey-matrix). Used: confirmation of existing two-axis classification model; limitation analysis (no work-type dimension).

- **Spiral Model** — Barry Boehm (1986). [Wikipedia](https://en.wikipedia.org/wiki/Spiral_model), [Original 1988 paper](https://www.cse.msu.edu/~cse435/Homework/HW3/boehm.pdf). Used: risk-driven per-cycle process selection, throwaway prototype as first-class category.

- **XP Spikes** — Kent Beck (late 1990s). [Mountain Goat Software](https://www.mountaingoatsoftware.com/blog/spikes), [PMAspirant](https://pmaspirant.com/what-is-a-spike-in-extreme-programming). Used: spike vs story categorical distinction, knowledge vs capability deliverable type, time-boxing.

- **Lean Startup** — Eric Ries (2011). [Methodology page](https://theleanstartup.com/principles), [Wikipedia](https://en.wikipedia.org/wiki/Lean_startup). Used: experiment vs production mode, pivot-or-persevere transition gate, validated learning as deliverable type.

### Secondary (extensions and critiques)

- **SAFe Enablers** — Scaled Agile, Inc. [Enablers](https://framework.scaledagile.com/enablers), [Spikes](https://framework.scaledagile.com/spikes). Used: exploration enabler as formal backlog type, differentiated done criteria.

- **Gartner Bimodal IT** — Gartner (2014). [Glossary](https://www.gartner.com/en/information-technology/glossary/bimodal), [Martin Fowler critique](https://martinfowler.com/bliki/BimodalIT.html). Used: negative evidence — Fowler's critique of false quality trade-off validates that exploration ≠ lower quality, just different obligations.

### Internal (codebase evidence)

- `plans/complexity-routing/problem.md` — Problem statement with 4 identified gaps
- `agents/learnings.md` lines 59-63 — "When routing prototype/exploration work through pipeline"
- `plugin/skills/design/SKILL.md` — Phase 0 classification, Phase B routing gates
- `plugin/skills/runbook/SKILL.md` — Tier 1/2/3 assessment criteria
- Commit `a86043cc` — Session-scraper design routing failure evidence
- Commit `557c2eed` — Prior design skill grounding (6 frameworks, 8 principles)
- `plans/reports/design-skill-grounding.md` — Prior grounding report with gap analysis

### Branch Artifacts

- `plans/reports/complexity-routing-internal-codebase.md` — Internal codebase exploration report
- `plans/reports/complexity-routing-external-research.md` — External framework research report
