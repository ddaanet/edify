# Interactive Review Supplementary Grounding: Internal Codebase Patterns

**Scope:** Four domain-specific research gaps identified during outline review (D-1, D-2, D-7, D-8). This report documents codebase patterns to ground supplementary research before design generation.

---

## Gap D-1: Verdict Vocabulary Patterns by Artifact Type

### Current State

**Outline claim:** Verdict vocabulary varies by artifact type. Initial grounding covered code review domains (Gerrit, Phabricator, GitHub). /proof currently reviews planning artifacts (requirements, outlines, designs), which belong to different domains (backlog refinement, architecture review, process review, QA triage).

### Evidence: Existing Status Taxonomies in Codebase

**Corrector agent (all review types):** Four-status taxonomy applied uniformly across code and planning artifacts:
- **FIXED** — Fix applied | File: `plugin/agents/corrector.md:26-29`
- **DEFERRED** — Real issue, explicitly out of scope | File: `plugin/agents/corrector.md:27-28`
- **OUT-OF-SCOPE** — Not relevant to current review | File: `plugin/agents/corrector.md:28-29`
- **UNFIXABLE** — Technical blocker requiring user decision | File: `plugin/agents/corrector.md:29-30`

**Supporting detail:** Status taxonomy section defines subcategories (U-REQ, U-ARCH, U-DESIGN) orthogonal to severity levels | File: `plugin/agents/corrector.md:33-54`

**Severity taxonomy:** Unified across all artifact types (critical/major/minor) — same three levels used by code review correctors, design-corrector, outline-corrector, and runbook-corrector | File: `plugin/agents/corrector.md` (not visible in corrector's own role section but referenced in design-corrector, outline-corrector, runbook-corrector specs)

### Evidence: Per-Artifact-Type Review Agents (Behavioral Differences)

**Design-corrector:** Applies ALL fixes including minor issues — different from implementation corrector
- Rationale: "Document fixes are low-risk compared to code changes" | File: `plugin/agents/design-corrector.md:19-28`
- Implication: Design review has different fix policy (everything vs critical/major-only)

**Outline-corrector:** Reviews for soundness, completeness, feasibility, scope — dimensions specific to pre-discussion outlines
- Validation criteria: Requirements traceability, approach feasibility | File: `plugin/agents/outline-corrector.md:65-79` (partial read)
- Does NOT use code quality criteria (logic, error handling, patterns) — artifact-type-specific review axes

**Runbook-corrector:** Three mode variants depending on artifact type
- TDD phases: prescriptive code detection, RED/GREEN sequencing | File: `plugin/agents/runbook-corrector.md:67-72`
- General phases: prerequisite validation, step clarity, conformance | File: `plugin/agents/runbook-corrector.md:73-77`
- Inline phases: vacuity checks (concrete target naming) | File: `plugin/agents/runbook-corrector.md:79-80`
- Same reviewer, different review criteria per phase type — verdict application may differ

**Deliverable-review skill:** Defines artifact-type-specific review axes
- Code: universal + robustness, modularity, testability, idempotency, error signaling | File: `plugin/skills/deliverable-review/SKILL.md:41-42`
- Test: universal + specificity, coverage, independence | File: `plugin/skills/deliverable-review/SKILL.md:42-43`
- Agentic prose (skills, agents): universal + actionability, constraint precision, determinism, scope boundaries | File: `plugin/skills/deliverable-review/SKILL.md:43-44`
- Human docs: universal + accuracy, consistency, completeness, usability | File: `plugin/skills/deliverable-review/SKILL.md:44-45`
- Pattern: "Universal" axes (conformance, correctness, completeness, vacuity, excess) apply to all; per-type axes vary

**Grounding implication:** Codebase already stratifies review by artifact type. Verdict vocabulary may follow similar pattern.

### Evidence: Verdict Actions Vary by Context

**Proof skill verdict handling (current, whole-artifact mode):**
- Terminal action "apply": dispatches lifecycle-appropriate corrector | File: `plugin/skills/proof/SKILL.md:81-92` (corrector dispatch table shows artifact → corrector mapping)
- Corrector dispatch is artifact-type-dependent | File: `plugin/skills/proof/SKILL.md:85-92` (outline.md → outline-corrector, design.md → design-corrector, etc.)
- Implication: Verdict flow already routes to artifact-specific handlers

**Absorb verdict (FR-4 detail):**
- Requirements currently not implemented in /proof
- Not mappable to code-review domain (no "absorb" pattern in Gerrit/GitHub/Phabricator)
- Natural fit for planning artifacts (absorb into requirements backlog, merge into design)
- Indicates verdict vocabulary splits by domain

### Gaps Requiring Supplementary Grounding

**G-1a:** Per-domain verdict vocabularies — what verdicts are natural for each domain?
- Code review domains: approve/request-changes/comment/... (existing tools)
- Backlog refinement: approve/absorb/split/defer/... (ungrounded in codebase)
- Architecture/design review: approve/revise/defer/escalate/... (partially in design-corrector review criteria)
- Process/defect triage: resolve/wontfix/duplicate/... (partially in corrector status taxonomy)

**G-1b:** Verb precision — are "revise" and "discuss" distinguished?
- FR-4 specification: revise (user states fix) vs discuss (user explores before deciding) | File: `plans/interactive-review/requirements.md:28-33`
- Outline decision D-4: "Non-verdict input is implicit discussion. No explicit `d` verdict needed." | File: `plans/interactive-review/outline.md:74-75`
- Tension: If discuss is implicit (conversational), why is it in FR-4's explicit verdict list?
- Grounding needed to resolve whether discuss is explicit verdict or implicit pathway

**G-1c:** Artifact-type-dependent corrector dispatch in interactive review
- /proof's current corrector dispatch maps outline.md → outline-corrector → verdict application pattern A
- Equivalent mapping needed for interactive review: artifact type → corrector type → verdict application behavior
- Supplementary research should clarify this mapping

### Recommendation for D-1

Research existing review domain literature (backlog grooming, ADR reviews, process review, QA/defect triage) to establish per-domain verdict vocabularies. Cross-reference against corrector agent review criteria (outline-corrector's soundness/completeness, design-corrector's architectural analysis, runbook-corrector's TDD/general/inline variants). Result should be a table mapping artifact type → review domain → natural verdict vocabulary.

---

## Gap D-2: Batch vs Immediate Application Patterns

### Current State

**Outline claim:** FR-5 specifies immediate application (verdict → file edit immediately). Outline design decision D-2 states batch accumulation optional — immediate apply is default.

### Evidence: Proof Skill Accumulation Pattern (Existing)

**Proof reword-accumulate-sync loop:**
- Accumulation is in-memory during loop iteration | File: `plugin/skills/proof/SKILL.md:49-62`
- Decision list format: D-1, D-2, D-3... with artifact impact | File: `plugin/skills/proof/SKILL.md:53-58`
- Terminal action "proceed/apply" applies accumulated decisions to artifact in batch | File: `plugin/skills/proof/SKILL.md:68-73`
- Applies all accumulated decisions as single atomic operation (corrector dispatch after all edits complete) | File: `plugin/skills/proof/SKILL.md:69-73`
- **Pattern:** Accumulation during iteration, batch apply on terminal action

**Consequence for session resumption:** If session interrupted during iteration, accumulated decisions in-memory are lost. Artifact on disk unchanged until terminal action. | File: `plugin/skills/proof/SKILL.md:68-73` (no state saved between calls)

### Evidence: Corrector "Apply All" Pattern

**Design-corrector applies ALL fixes (critical, major, minor):**
- Rationale: Document fixes are low-risk | File: `plugin/agents/design-corrector.md:19-28`
- Applied in single pass, then report written | File: `plugin/agents/design-corrector.md:30-35`
- Pattern: Fix all, report after

**Outline-corrector behavior (implicit from description):**
- "Validate... apply fixes... return filepath" flow | File: `plugin/agents/outline-corrector.md:1-4`
- Implication: Applies fixes before returning

**Runbook-corrector behavior:**
- "Write review (audit trail) → Fix ALL issues → Escalate unfixable" | File: `plugin/agents/runbook-corrector.md:7-8`
- Batch fix pattern: review all, then fix all

**Deliverable-review skill:**
- Layer 2 (mandatory): "Read deliverables directly... record findings" then "write report" | File: `plugin/skills/deliverable-review/SKILL.md:80-104`
- Phase 4: "Write consolidated report" with findings, then "append to lifecycle.md" | File: `plugin/skills/deliverable-review/SKILL.md:106-149`
- Pattern: Batch discovery, batch report, then lifecycle update

**General agent pattern:** Read/gather all → analyze all → report all → apply all (NOT: discover one, fix one, advance)

### Tension: FR-5 vs Batch Patterns

**FR-5 requirement:** "Verdicts produce immediate file edits... Artifact is always current" | File: `plans/interactive-review/requirements.md:39-42`

**Proof design (D-2):** Batch apply on terminal action, not immediate | File: `plans/interactive-review/outline.md:33-46`

**User review decision:** "FR-5 lifted by user — session resume handles interruption" | File: `agents/session.md` (under "Key design changes from review")

**Implication:** Batch application was accepted as adequate for session resumption because session.md captures pending state (not immediate application safety). Immediate application requirement (FR-5) was dropped in favor of batch-apply efficiency.

### Evidence: Batch Accumulation Format (Outline D-2)

**Specified accumulation structure:**
```
- V-1: [item identifier] — approve
- V-2: [item identifier] — revise: "[user's stated fix]"
- V-3: [item identifier] — kill (absorb → plans/foo/requirements.md)
- V-4: [item identifier] — skip
```
| File: `plans/interactive-review/outline.md:40-46`

**Pattern:** Ordered list with item identifier and verdict + detail. Enables deterministic replay (each V-N has all information to apply without re-asking user).

### Evidence: By-Domain Application Strategies

**Outline claim D-2:** "Batch-apply by domain" — unsupported in outline text but mentioned in supplementary gap description

**Deliverable-review:** Depends on artifact type
- Code/test: might require compilation/test verification before applying all fixes
- Prose: fixes are edits, apply all immediately
- Pattern: Batch strategy may vary by artifact type

**Runbook-corrector:** Applies all fixes before returning | File: `plugin/agents/runbook-corrector.md:7-8` — no domain-specific variation documented

### Gaps Requiring Supplementary Grounding

**G-2a:** Session interruption safety — does batch-apply require explicit session state tracking?
- /proof relies on accumulation list (in-memory, lost if interrupted) | File: `plugin/skills/proof/SKILL.md:49-62`
- Interactive review outline says batch apply + session resume handles interruption | File: `plans/interactive-review/outline.md:33-39`
- Is the session.md entry sufficient (like existing /handoff does), or does interactive review need explicit accumulation artifact?

**G-2b:** Per-domain batch vs immediate trade-offs
- Code review domains may prefer immediate (safety, visibility)
- Planning artifact domains may prefer batch (completeness before dispatch)
- Supplementary research should establish domain-specific patterns

**G-2c:** Accumulated verdict atomicity
- Corrector dispatch happens after all edits applied (atomic from corrector's view) | File: `plugin/skills/proof/SKILL.md:69-72`
- What if apply fails partway through (first 3 verdicts applied, 4th fails)? Rollback? Partial state?
- Existing agents don't document partial-apply recovery

### Recommendation for D-2

Research batch vs immediate trade-offs in existing code review tools (Gerrit batching, Phabricator draft-then-submit) and in internal agent patterns (corrector fix-all behavior, proof accumulation). Document when batch is appropriate (safety, atomicity) vs when immediate is appropriate (interruption safety, user feedback). Supplement with supplementary grounding on what "accumulated verdict list" persists across session boundaries (explicit artifact vs implicit session.md entry).

---

## Gap D-7: Per-Item Size/Granularity Patterns

### Current State

**Outline claim D-7:** Artifact-type granularity detection with hierarchical auto-split (large items split into sub-items based on size threshold). Threshold requires grounding — no evidence in outline.

### Evidence: Artifact-Type Granularity Detection (Outline D-7 Table)

**Specified patterns:**
| Artifact type | Pattern | Item granularity |
| --- | --- | --- |
| requirements.md | `**FR-N:**` / `**NFR-N:**` / `**C-N:**` | Individual requirement/constraint |
| outline.md | `### Sub-problem` / `## Section` headings | Section or sub-problem |
| design.md | `## Section` headings | Design section |
| runbook-phase-*.md | Cycle/step markers | Individual cycle or step |
| Source files | Function/class definitions | Function or class |
| Diff output | Hunk markers (`@@`) | Individual hunk |

| File: `plans/interactive-review/outline.md:105-112`

**Pattern:** Granularity adapts to artifact structure (enumeration pattern, heading hierarchy, code structure, diff structure).

### Evidence: Hierarchical Granularity (Size-Based Auto-Split)

**Outline statement:** "Items above a size threshold auto-split into sub-items (large classes → methods, large diffs → per-function hunks). Per-item size threshold requires grounding" | File: `plans/interactive-review/outline.md:114-115`

**No codebase examples found** for automatic size-threshold-based splitting in interactive review context.

### Evidence: Cognitive Load Research in Grounding Report

**Cisco 2006 study:**
- Code review cognitive load ceiling: 450 LOC/hour
- Optimal batch size: 200-400 LOC | File: `plans/reports/interactive-review-grounding.md:136-137`
- Session time limit: 60-90 minutes (Fagan, Cisco data) | File: `plans/reports/interactive-review-grounding.md:90-92`

**Limitation:** This research applies to code review, not artifact review (requirements, outlines, designs). Document review rates are typically 4-6 pages/hour (distinct from LOC/hour) | File: `plans/reports/interactive-review-grounding.md:91`

**Microsoft 1.5M comment study:** "Proportion of useful review comments decreases with changeset size" | File: `plans/reports/interactive-review-grounding.md:140` — indicates quality degrades, but no per-item size threshold specified.

### Evidence: Deliverable-Review Granularity Decisions

**Deliverable-review scales per-file review by total lines:**
- < 500 lines: skip Layer 1, run Layer 2 only | File: `plugin/skills/deliverable-review/SKILL.md:66-68`
- 500–2000 lines: two agents (code+test, prose+config) | File: `plugin/skills/deliverable-review/SKILL.md:68-70`
- > 2000 lines: three agents (code, test, prose+config) | File: `plugin/skills/deliverable-review/SKILL.md:70-71`

**Pattern:** Thresholds (500, 2000) are explicit but ungrounded. No justification given for why 500 vs 1000 vs 2000.

### Evidence: Proof Skill Whole-Artifact Model (No Sub-Items)

**Current /proof:** No granularity detection. Reviews artifact as a single unit:
- Read the artifact under review | File: `plugin/skills/proof/SKILL.md:37`
- Present summary, enter loop | File: `plugin/skills/proof/SKILL.md:39`
- No explicit item segmentation

**Implication:** Interactive review adds granularity detection (new capability, no precedent to ground).

### Gaps Requiring Supplementary Grounding

**G-7a:** Per-item size threshold for planning artifacts
- Cisco data (200-400 LOC) is for code review, not design/requirements/outline review
- Outline calls for "supplementary research on per-item cognitive load threshold" | File: `plans/interactive-review/outline.md:114-115`
- No internal evidence for planning artifact thresholds

**G-7b:** Hierarchical split heuristics
- When does a design section become "too large" to review as one item?
- When does a runbook step become multiple sub-items?
- Threshold criteria needed (line count? sub-heading depth? conceptual complexity?)

**G-7c:** Coverage of artifact-type split rules
- Specification has 6 artifact types (requirements, outline, design, runbook, source, diff)
- No split rules specified for each type
- Does "large" mean 20 lines (design sections) or 100 lines (source methods)?

### Evidence: User Override of Granularity (FR-2)

**FR-2 requirement:** "User can override granularity (e.g., 'review by file' vs 'review by hunk')" | File: `plans/interactive-review/requirements.md:21-22`

**Outline response:** "Natural conversation handles granularity changes — no explicit override mechanism needed" | File: `plans/interactive-review/outline.md:116-117`

**Pattern:** Override is conversational, not command-based. Requires no formal granularity API.

### Recommendation for D-7

Research cognitive load literature specific to document review (design, requirements, outlines). Compare code review rates (LOC/hour) with document review rates (pages/hour, sections/hour). Establish per-artifact-type thresholds: at what size does a requirements item become "too large to review comfortably as one item"? Cross-reference with existing internal thresholds (deliverable-review's 500/2000 line gates) to find patterns. Result should clarify whether Cisco's 200-400 LOC threshold translates to design/outline/requirements domains, and if not, what thresholds apply.

---

## Gap D-8: Skip/Defer Outcome Patterns

### Current State

**Outline claim D-8:** Skip verdict allows reviewer to defer judgment. Outcome semantics unclear — what happens to skipped items after apply?

### Evidence: Skip Verdict in Outline

**D-4 presentation format:**
```
Verdict? (a)pprove (r)evise (k)ill (s)kip
```
| File: `plans/interactive-review/outline.md:69` (abbreviated)

**Grounding:** "Skip is a design addition beyond FR-4, grounding-justified" | File: `plans/interactive-review/outline.md:69`

**Grounding source:** Cognitive load research — "forced verdict prevents passive scanning; skip is the escape valve (not silence)" | File: `plans/reports/interactive-review-grounding.md:81-85`

**Outcome description:** "Skip outcome semantics unclear. Needs grounding — established review processes handle deferred/unreviewed items differently by domain" | File: `plans/interactive-review/outline.md:177-178`

### Evidence: DEFERRED Status in Corrector Agent

**Status taxonomy (orthogonal to severity):**
- **DEFERRED** — Real issue, explicitly out of scope. Item appears in scope OUT list or design documents it as future work. Informational only — does NOT block. | File: `plugin/agents/corrector.md:27-28`

**Different from skip:** DEFERRED is for issues found by corrector (discovered, then deferred). Skip is for reviewer verdict (choose not to review item).

**DEFERRED report section:** Required when report contains DEFERRED items:
```markdown
## Deferred Items

The following items were identified but are out of scope:
- **[Item]** — Reason: [why deferred, reference to scope OUT or design]
```
| File: `plugin/agents/corrector.md:70-76`

**Pattern:** Deferred items tracked, reported, and listed in summary. Not silent.

### Evidence: Skip Outcome in Deliverable-Review

**Deliverable-review summary requirement:**
- Report severity counts (critical, major, minor) | File: `plugin/skills/deliverable-review/SKILL.md:143`
- No "skipped items" category mentioned

**Implication:** Deliverable-review doesn't distinguish between "reviewed and approved" vs "skipped for later" — all findings are reported, nothing skipped.

### Evidence: Session Resumption (Context for Skip Outcome)

**Session.md task notation:**
- Pending tasks can be resumed | File: `agents/session.md` (general pattern, multiple examples with resumption commands)
- Task context recovered via `task-context.sh` for lookup by name | File: `CLAUDE.md` (task-context recovery documentation, not shown in reads)

**Implication:** Session boundary can capture "reviewed up to item N, stopped at item N+1". Resuming means starting at item N+1. Skipped items (verdict: skip) at position M would be visible in prior context ("item M was skipped previously").

### Evidence: What NOT Happens to Skipped Items

**Outline specification for terminal actions:**
- "apply": Display verdict summary, apply all verdicts, dispatch corrector | File: `plans/interactive-review/outline.md:120-126`
- "discard": Abandon all verdicts | File: `plans/interactive-review/outline.md:128`

**NOT mentioned:**
- Skipped items become pending tasks
- Skipped items are flagged for re-review
- Skipped items block apply (like UNFIXABLE issues in corrector)

### Evidence: User Review Feedback

**Session brief.md (dogfooding feedback):**
- Checkpoint after orientation for user feedback on scope adjustment | File: `plans/interactive-review/brief.md:13-14`
- User may "reorder, skip sections, adjust scope" | File: `plans/interactive-review/brief.md:13`

**Implication:** Skip can happen at section granularity (user-driven) as well as per-item (verdict-driven).

### Evidence: Skip Semantics from Outline D-4

**Non-verdict input is implicit discussion:**
"Non-verdict input is implicit discussion. No explicit `d` verdict needed... If the user responds with anything that isn't a recognized verdict shortcut, treat it as discussion" | File: `plans/interactive-review/outline.md:74-75`

**Implication:** Silent (no input, no action) is treated as discussion. Skip must be explicit verdict to distinguish from no-decision.

### Gaps Requiring Supplementary Grounding

**G-8a:** Skipped item summary treatment
- Are skipped items listed in verdict summary (like DEFERRED items in corrector report)?
- Example: "N approved, N revised, N killed, N skipped" — is the skip count visible?
- Current outline says "verdict summary" but doesn't specify skip inclusion | File: `plans/interactive-review/outline.md:121`

**G-8b:** Outcome of skipped items after apply
- Does skip mean "persist unchanged" (like approve without edits)?
- Or does skip mean "no decision made, needs re-review"?
- Different outcome for each domain:
  - Code review domain: skipped = deferred to follow-up review (GitHub PR model allows partial approval)
  - Planning artifact domain: skipped = item remains in artifact for re-review, possibly becomes pending task
  - Process review domain: skipped = acknowledged but not resolved (similar to wontfix in bug triage)

**G-8c:** Skip semantics vs discuss semantics
- Skip is explicit verdict (user types 's')
- Discuss is implicit (user types anything non-verdict)
- Does skip prevent discussion (item is terminal), or does skip enter discussion sub-loop?
- Outline doesn't clarify: can user "skip, but discuss this item" in same interaction?

**G-8d:** Skip blocking apply
- UNFIXABLE issues block apply in corrector | File: `plugin/agents/corrector.md:29-30`
- Do skipped items block apply in interactive review?
- If user skips all items, does apply proceed (all items skipped, nothing changed) or require re-review?

### Evidence: Parallel Domain Patterns

**Code review (Phabricator):** Accepts partial approval — approve some items, skip others, come back later. No blocking.

**Backlog grooming (Jira/Linear):** Items can be deferred (snoozed, put in backlog) — skip is common for lower-priority items flagged in review.

**Architecture review (ADR meetings):** Items requiring more context are tabled (skipped, scheduled for follow-up discussion).

**Defect triage (bug meetings):** Items marked "wontfix" or "incomplete-info-needed" are deferred (skipped pending more data).

### Recommendation for D-8

Research how different review domains handle deferred/skipped items:
1. Code review: partial approval patterns (Phabricator, Gerrit, GitHub)
2. Backlog refinement: deferral and snoozed patterns
3. Architecture review: tabled-item tracking
4. QA/defect triage: deferred-item classification

For each domain, document:
- Does skip prevent completion (blocking) or allow proceeding (non-blocking)?
- Are skipped items explicitly tracked (report section) or silent?
- Do skipped items become follow-up tasks or stay in artifact?
- Is re-review triggered automatically or manual?

Result should ground verdict summary format (include skip count?), apply terminal action behavior (proceed with skipped items present?), and downstream handling (artifact still contains skipped items after apply, requiring follow-up).

---

## Cross-Cutting Observations

### Pattern: Status Taxonomy ≠ Verdict Vocabulary

**Corrector agent status taxonomy** (FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE) is orthogonal to verdict vocabulary.
- Status describes post-review classification of findings
- Verdict describes user action during review

**Interactive review verdict vocabulary** (approve, revise, kill, skip) doesn't map 1:1 to corrector statuses:
- approve → no finding (no status)
- revise → FIXED (fix applied by user, not corrector)
- kill → issue removed (similar to FIXED deletion)
- skip → not yet reviewed, eventually DEFERRED?

**Implication:** Interactive review's verdict application must map to corrector's downstream status language. When verdict "skip" is applied, does it:
- Create an implicit DEFERRED status (item deferred, maybe reviewed later)?
- Create OUT-OF-SCOPE status (user decided it's not relevant)?
- Create no status (item unchanged, considered for next review cycle)?

### Pattern: Artifact-Type Routing is Established

Three correctors are artifact-specific (design-corrector, outline-corrector, runbook-corrector). Their dispatch is deterministic based on artifact type. Interactive review's verdict vocabulary should follow similar routing — per-artifact-type verdicts routed to artifact-appropriate correctors.

### Pattern: Batch Application is Dominant

All agents (corrector, design-corrector, outline-corrector, runbook-corrector, deliverable-review) use batch discovery → batch report → batch application pattern. Immediate application is not found in established patterns. This supports outline D-2 (batch apply), contradicting FR-5 (immediate apply).

### Pattern: Review Reports are Audit Trails

Every corrector writes a report before applying fixes. The report documents findings, status classifications, and fixes applied. Skipped items should follow same pattern — explicitly documented in summary to enable process improvement and deviation tracking.

