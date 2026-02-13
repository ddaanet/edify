# RCA: Vet Over-Escalation Persists Post-Overhaul

**Date:** 2026-02-13
**Analyst:** Opus
**Status:** Complete

## Root Cause

The vet-fix-agent has a binary status model (FIXED or UNFIXABLE) applied to a problem space that requires at least three categories. When an agent encounters an issue that is not immediately fixable with a targeted edit, the only available label is UNFIXABLE. There is no DEFERRED status for documented future work, no SKIP status for out-of-scope items, and no guidance to investigate before escalating.

The binary model creates a forced choice: either apply a fix right now, or escalate. For items that are intentionally deferred, explicitly out of scope, or solvable through pattern-matching investigation, "escalate" is the wrong answer but the only alternative the agent has.

## Contributing Factors

### CF-1: Vague UNFIXABLE criteria invite over-application

`vet-fix-agent.md` lines 333-334:
```
- If a fix would require architectural changes, mark UNFIXABLE
- If a fix is ambiguous (multiple valid approaches), mark UNFIXABLE
```

Neither term is defined. "Architectural changes" could mean anything from splitting a module to renaming a variable across call sites. "Ambiguous" conflates "genuine design decision needed" with "I haven't looked at existing patterns yet." Without thresholds, the agent defaults to escalation on any uncertainty.

### CF-2: Scope OUT instruction is present but structurally weak

`vet-fix-agent.md` line 79:
```
- Do NOT flag OUT-scope items as missing features or issues
```

This instruction exists, but it is:
- A single bullet in a list of six context-handling rules
- Phrased as a prohibition without a mechanism (what to do instead of flagging)
- Not reinforced by examples showing correct handling
- Not checked post-hoc (no validation step in the report verification section)

Evidence it does not work: Cycle 0.6 vet flagged session filtering as UNFIXABLE despite explicit "OUT: Session file filtering (next cycle)" in the delegation prompt. The agent acknowledged the scope statement in its report text, then flagged the item anyway. The instruction was read but not followed.

### CF-3: No investigation step before escalation

The fix process (lines 322-335) goes directly from "identify issue" to "apply fix or mark UNFIXABLE." There is no intermediate step requiring the agent to investigate whether a pattern exists before concluding the issue is unfixable.

Phase 2 test file mismatch: the agent labeled this UNFIXABLE ("test file naming convention needs design decision") without using Glob to check what test files already exist. Had it run `Glob("tests/test_worktree_*.py")`, it would have found the existing convention and applied it.

The available tools (Glob, Grep, Read) can resolve pattern-matching questions mechanically. The agent instructions never direct it to use them for classification decisions.

### CF-4: Workflow-fixes explicitly excluded vet agent changes

`workflow-fixes/design.md` line 449: "`agent-core/agents/vet-fix-agent.md` -- no changes"

`workflow-fixes/outline.md` line 136: "OUT: vet-fix-agent vs vet-agent duplication extraction"

The pipeline overhaul scoped vet-fix-agent as unchanged. The seven architectural gaps (G1-G7) focused on review routing, recommendation propagation, and completion behavior. Vet judgment calibration was not classified as a gap because it manifests at agent behavior level, not pipeline architecture level. The overhaul fixed the plumbing, not the judgment criteria of the agent at the end of the pipe.

### CF-5: UNFIXABLE is a stop-the-world signal

The UNFIXABLE detection protocol (`vet-requirement.md` lines 82-101) treats any UNFIXABLE as a hard stop: grep for it, stop if found, escalate to user. This is correct for genuine UNFIXABLE issues but creates disproportionate cost for misclassification. A single over-escalation blocks the entire pipeline, requiring user intervention for what may be a mechanical fix.

The high cost of UNFIXABLE should make classification criteria more rigorous, not less. Currently the reverse is true -- the criteria are vague, making false positives common, while the escalation protocol treats all positives as real.

## Evidence

### Incident 1: Phase 5 checkpoint -- `create_worktree()` extraction

**Agent said:** "UNFIXABLE -- requires architectural change affecting function signature and multiple test assumptions"

**Reality:** The design explicitly documents extraction as Phase 6 work (line 120 of the same report: "Phase 6: Extract `create_worktree()` function per design contract"). The agent recognized the work was planned for a future phase (mentioned it in Recommendations), yet classified it as UNFIXABLE rather than deferred. The binary model has no deferred category.

### Incident 2: Phase 5 checkpoint -- `_git` naming convention

**Agent said:** "UNFIXABLE -- renaming `_git` would require updating all call sites across implementation and tests, expanding beyond checkpoint scope"

**Reality:** Renaming a function across call sites is a mechanical find-replace operation. The agent had Edit tool with `replace_all` parameter available. "Expanding beyond checkpoint scope" is a scope judgment, not an architectural constraint. A consistent rename touching 24 call sites in 2 files is the textbook definition of a mechanical fix.

### Incident 3: Phase 2 review -- test file mismatch

**Agent said:** "UNFIXABLE (escalation: test file naming convention needs design decision)"

**Reality:** The recommendation section of the same report says "Check Phase 1 runbook for actual test file created" and "If Phase 1 uses `test_worktree_cli.py`, update Phase 2 to match." The agent identified the resolution procedure but still escalated. Glob for `tests/test_worktree_*.py` would have resolved the question in one tool call.

### Incident 4: Cycle 0.6 vet -- session filtering

**Agent said:** UNFIXABLE for missing session filtering.

**Reality:** Scope OUT explicitly listed "Session file filtering (next cycle)." The agent acknowledged this in the report text but still flagged and escalated. The scope OUT instruction (line 79) was insufficient to prevent flagging.

### Incident 5: vet-review.md -- skill documentation issues

Five minor issues all marked "UNFIXABLE -- Write tool denied." This is a different failure mode (tooling limitation, not judgment error) but demonstrates that the UNFIXABLE label is overloaded. Write access issues are not architectural problems requiring user design decisions -- they are tool permission constraints that should have a different status or workaround.

## Classification Taxonomy

Current model: `FIXED | UNFIXABLE`

Proposed model: `FIXED | DEFERRED | OUT-OF-SCOPE | UNFIXABLE`

### FIXED
Agent applied a targeted edit that resolves the issue. No change from current definition.

### DEFERRED
Issue is real but resolution is explicitly documented as future work. The agent should note it for awareness without escalating.

**Criteria (any one sufficient):**
- Item appears in scope OUT list with future-phase reference
- Design document explicitly schedules the work for a named future phase
- Implementation deviates from design but design notes deferral

**Examples:**
- "Design calls for function extraction in Phase 6" -- note it, move on
- "Scope OUT: Session file filtering (next cycle)" -- do not flag
- "Implementation inlines logic; design defers extraction" -- note observation

**Report format:** Include in a "Deferred Items" section (separate from Issues Found). No UNFIXABLE label. No escalation triggered.

### OUT-OF-SCOPE
Item is outside the scope boundaries provided in the delegation. Should not appear in the report at all.

**Criteria:**
- Item matches an entry in scope OUT list
- Item concerns functionality not listed in scope IN and not in changed files

**Action:** Remove from report during fix phase. If caught during analysis, do not add.

### UNFIXABLE
Issue requires intervention that the agent cannot provide: missing requirements, genuine architectural decisions, cross-cutting concerns that span multiple unrelated modules.

**Criteria (all must be met):**
1. The agent attempted to investigate (used Glob/Grep to check patterns)
2. Investigation did not reveal a clear existing pattern to follow
3. The fix requires information the agent does not have (user preference, missing requirement, design gap)
4. The item is NOT in scope OUT

**Subcategories:**
- **U-REQ:** Missing or ambiguous requirements. Design does not specify, no existing pattern to follow.
- **U-ARCH:** Fix requires changes to module boundaries, public API contracts, or data models that would cascade to callers/consumers not in the changed files list.
- **U-DESIGN:** Fixing would violate an explicit design decision. The design is wrong or the implementation is wrong, but the agent cannot determine which without user input.

**Required in report:** UNFIXABLE label must include subcategory code and a sentence explaining what investigation was performed and why it was insufficient.

## Proposed Fixes

### F1: Add status taxonomy to vet-fix-agent.md

Replace the two-line UNFIXABLE criteria (lines 333-334) with the four-status taxonomy above. Add it immediately after "Fix constraints:" section header.

Key additions:
- DEFERRED status with criteria and report format
- OUT-OF-SCOPE handling (remove from report)
- Investigation requirement before UNFIXABLE classification
- Subcategory codes (U-REQ, U-ARCH, U-DESIGN)
- Three concrete examples mapping to the incidents in this RCA

### F2: Add investigation-before-escalation protocol to vet-fix-agent.md

Insert after the fix process (line 328, after "Apply fix using Edit tool") a mandatory investigation step:

```
Before marking any issue UNFIXABLE:
1. Check scope OUT list -- if item matches, classify as OUT-OF-SCOPE (remove)
2. Check if design documents deferral -- if so, classify as DEFERRED (note only)
3. Use Glob/Grep to search for existing patterns in codebase
4. If pattern found, apply it (FIXED via pattern-matching)
5. Only if steps 1-4 fail, classify as UNFIXABLE with subcategory and investigation summary
```

### F3: Add scope OUT validation to report verification

In the Verification section (lines 412-415), add:

```
5. If scope OUT was provided, verify no issues reference OUT items
6. If DEFERRED items exist, verify they have future-phase reference
7. If UNFIXABLE items exist, verify each has subcategory code and investigation summary
```

### F4: Add "Deferred Items" section to report template

After the Issues Found sections, add:

```
## Deferred Items

[Items that are real observations but explicitly scheduled for future work.
These do NOT trigger UNFIXABLE escalation.]

1. **[Item title]**
   - Context: [Where deferral is documented]
   - Phase: [Which future phase addresses this]
```

### F5: Update vet-requirement.md UNFIXABLE detection

After the grep-for-UNFIXABLE step, add validation:

```
4. For each UNFIXABLE found, verify:
   a. Has subcategory code (U-REQ, U-ARCH, or U-DESIGN)
   b. Includes investigation summary
   c. Item is not in scope OUT list from delegation
5. If validation fails, the UNFIXABLE may be misclassified.
   Resume agent with: "Issue X appears misclassified. [reason]. Reclassify."
```

This keeps the mechanical grep but adds a lightweight validation layer.

### F6: Update pipeline-contracts.md T6 review criteria

Add to T6 criteria: "Status taxonomy: FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE (see vet-fix-agent.md)"

## Why Workflow-Fixes Did Not Address This

Workflow-fixes targeted the planning pipeline architecture (G1-G7 gaps). The gaps were identified by analyzing how artifacts flow between skills and agents. Vet judgment calibration is not a flow problem -- it is a criteria problem within a single agent. The pipeline analysis methodology (transformation table, defect types, review gates) correctly identified that T6 uses vet-fix-agent with scope IN/OUT criteria. It did not analyze whether the agent's internal classification logic was adequate to use those criteria correctly.

The scope exclusion was reasonable at the time: vet-fix-agent was functioning (fixing issues, writing reports, returning results) and the pipeline gaps were more structurally impactful. The over-escalation pattern was visible in learnings but not classified as a pipeline gap.

## Scope Assessment

**Complexity:** Low. All changes are additive text in two files.

**Files modified:**
- `agent-core/agents/vet-fix-agent.md` -- F1, F2, F3, F4 (taxonomy, investigation protocol, verification, report template)
- `agent-core/fragments/vet-requirement.md` -- F5 (detection validation)
- `agents/decisions/pipeline-contracts.md` -- F6 (one line)

**Estimated additions:** ~100 lines
- F1: 35 lines (taxonomy with criteria)
- F2: 10 lines (investigation protocol)
- F3: 5 lines (verification additions)
- F4: 15 lines (report template section)
- F5: 10 lines (detection validation)
- F6: 1 line

**Risk:** Low. Additive changes to agent instructions. No architectural modifications. Existing FIXED/UNFIXABLE behavior preserved for genuine cases; new categories capture previously misclassified cases.

**Validation approach:** Re-run a vet delegation using the Phase 2 test file mismatch scenario. Verify agent uses Glob to investigate, finds existing pattern, classifies as FIXED via pattern-matching instead of UNFIXABLE.

## Deepening

### Axis 1: Two-Layer Failure — Template Provision vs Template Respect

**Independent verification confirms the sonnet finding.** The failure is two-layered, and this changes the root cause framing.

**Layer 1 — Upstream: Orchestrator does not follow the template.**

The orchestrate skill (SKILL.md lines 125-148) provides a well-structured checkpoint delegation template with explicit `IN:` / `OUT:` fields:

```
**Scope:**
- IN: [list methods/features implemented in this phase]
- OUT: [list methods/features for future phases — do NOT flag these]
```

But the actual checkpoint reports reveal the orchestrator did not populate those fields:

- **Phase 5 checkpoint** (`checkpoint-phase-5-vet.md` line 3): `**Scope**: Phase 5 implementation — create_worktree() / new command` — prose description only, no structured IN/OUT
- **Phase 2 checkpoint** (`checkpoint-phase-2-vet.md` line 3): `**Scope**: Phase 2 - add_sandbox_dir() implementation and tests` — prose description only, no structured IN/OUT
- **Phase 1 checkpoint** (`worktree-skill/checkpoint-1-vet.md` line 3): `**Scope**: Phase 1 worktree-skill implementation (new + rm subcommands)` — prose description only
- **Phase 0 checkpoint** (`worktree-skill/checkpoint-0-vet.md` line 3): `**Scope**: Phase 0 foundation (cycles 0.1-0.9)` — prose description only

Every checkpoint across both plans (worktree-update and worktree-skill) uses prose-level scope. Not a single one follows the structured template from the orchestrate skill. The template exists but was never used.

**Layer 2 — Downstream: Agent ignores template when provided.**

Cycle 0.6 is the one incident where structured scope WAS provided. The vet report explicitly acknowledges the OUT boundary: "Cycle scope explicitly excludes session file filtering (OUT: 'Session file filtering (next cycle)')." The agent read it, quoted it, then flagged the item as UNFIXABLE anyway.

**Impact on root cause framing:**

My original framing ("binary status model") is necessary but insufficient. Even with a perfect taxonomy, the two-layer failure persists:

- **Without structured scope** (Phase 5, Phase 2): The agent has no OUT list to check against. Adding DEFERRED and OUT-OF-SCOPE statuses helps only if the agent receives the information to classify against. The taxonomy is inert without input data.
- **With structured scope** (Cycle 0.6): The agent has the OUT list and still ignores it. The taxonomy alone does not change this behavior.

**Revised root cause:** The primary failure is the upstream layer — the orchestrator does not populate the structured scope template it is given. Without scope data, no downstream classification can work correctly. The secondary failure is that even when scope data is provided, the single-bullet prohibition (line 79) is too weak to override the agent's default behavior of flagging observations as issues.

**Fix implication:** F2 (investigation-before-escalation protocol) must include the scope check as the FIRST step (before investigation), and the protocol must be structured as a checklist gate, not a prohibition. The orchestrate skill also needs enforcement: the checkpoint delegation prompt should fail validation if IN/OUT fields are empty.

### Axis 2: Asymmetric Incentive Structure

**The behavioral question:** Why do agents default to UNFIXABLE when uncertain?

**Asymmetric cost analysis:**

| Action | If correct | If wrong |
|--------|-----------|----------|
| Fix it | Issue resolved (invisible success) | Wrong fix propagates, trusted by orchestrator, may cause cascading damage |
| UNFIXABLE | Pipeline pauses, user reviews (visible but safe) | User dismisses, pipeline resumes after delay (low cost to agent) |

The incentive is structurally asymmetric:
- **Attempting a fix** carries risk of *invisible damage*. A wrong fix is committed, passes through the mechanical UNFIXABLE grep (because the issue is now marked FIXED), and propagates downstream. The agent bears responsibility for the wrong fix.
- **Escalating as UNFIXABLE** carries cost of *visible delay*. The pipeline stops, the user reviews, and either agrees (agent was right) or dismisses (agent was wrong but no damage done). The agent bears no responsibility for the delay.

From the agent's perspective, UNFIXABLE is the risk-free option. The cost of over-escalation falls entirely on the user (time spent reviewing false positives). The cost of under-escalation falls on the system (wrong fix propagated).

**Does the taxonomy alone change this incentive?**

No. Adding DEFERRED and OUT-OF-SCOPE categories gives the agent more vocabulary but does not change the risk calculus. An agent uncertain about whether something is DEFERRED vs UNFIXABLE will still default to UNFIXABLE for the same reason: it is the safer choice.

**The investigation protocol creates escalation cost.**

F2 (investigation-before-escalation) is the fix that changes the incentive. It makes UNFIXABLE classification require demonstrated work:

1. Agent must show it checked the scope OUT list (mechanical)
2. Agent must show it checked the design for deferral documentation (mechanical)
3. Agent must show it used Glob/Grep to search for patterns (observable)
4. Agent must include investigation summary in the UNFIXABLE label (verifiable)

The investigation protocol works because:
- It converts UNFIXABLE from a zero-cost default to a gated status requiring evidence
- Each gate is a checkpoint where the agent may discover the issue is actually DEFERRED, OUT-OF-SCOPE, or mechanically fixable — diverting it to the correct classification before reaching UNFIXABLE
- The investigation summary is verifiable by the orchestrator's UNFIXABLE detection protocol (F5), creating accountability

Without the investigation protocol, the taxonomy is vocabulary without teeth. An agent can label something UNFIXABLE-U-REQ without having checked whether existing patterns answer the question. The protocol forces the agent to exhaust the cheaper classifications first.

**Broader insight:** In any agent system where escalation is zero-cost and intervention carries risk, agents will over-escalate. The fix is not to add categories (vocabulary) but to add process gates that make escalation more expensive than investigation (behavioral change). The taxonomy enables the gates (you need status names to build a checklist), but the gates do the work.

### Axis 3: Fix Prioritization — Impact in Isolation

Ranking by "which single fix, implemented alone, prevents the most over-escalation":

**Rank 1: F2 — Investigation-before-escalation protocol**

This is the only fix that changes agent behavior. It interposes a mandatory checklist between "found issue" and "label UNFIXABLE." In isolation, this fix:

- **Prevents Incident 3 (Phase 2 test file mismatch):** Step 3 (Glob/Grep for patterns) would find existing test files and resolve the question. Agent fixes instead of escalating.
- **Prevents Incident 2 (Phase 5 `_git` naming):** Step 3 would identify that all 24 call sites are in 2 files, confirming this is a mechanical find-replace. Agent fixes instead of escalating.
- **Partially prevents Incident 1 (Phase 5 `create_worktree()`):** Step 2 (check design for deferral) would find the Phase 6 note. But without the DEFERRED vocabulary (F1), the agent has no label to apply. It would still face the binary FIXED/UNFIXABLE choice.
- **Prevents Incident 4 (Cycle 0.6 session filtering):** Step 1 (check scope OUT list) would match. But without OUT-OF-SCOPE vocabulary (F1), the agent again has no correct label.

**Impact in isolation:** Prevents 2 of 4 judgment incidents outright. Partially addresses 2 more (investigation succeeds but labeling remains awkward).

**Rank 2: F1 — Status taxonomy (vocabulary)**

Adding DEFERRED and OUT-OF-SCOPE gives agents correct labels for cases they already recognize but cannot express. In isolation:

- **Does not prevent Incidents 2 or 3:** Agent did not recognize these as mechanical; new vocabulary does not change recognition.
- **Potentially prevents Incident 1:** Agent recognized future-phase deferral (mentioned it in Recommendations) but had no label. DEFERRED category provides it. However, without investigation protocol, agent may still shortcut to UNFIXABLE.
- **Potentially prevents Incident 4:** Agent acknowledged scope OUT in its text. OUT-OF-SCOPE category provides the correct action (remove from report). However, Cycle 0.6 shows the agent already knew the item was out of scope and flagged it anyway — vocabulary alone may not override this behavior.

**Impact in isolation:** Might prevent 1-2 incidents, depending on whether vocabulary alone changes classification behavior. Evidence from Incident 4 suggests it does not: the agent had the information and the instruction but still escalated.

**Rank 3: F3+F5 — Scope enforcement and UNFIXABLE validation (defensive layer)**

Post-hoc validation catches misclassifications after they occur. In isolation:

- **Does not prevent any incident** — over-escalation still happens.
- **Enables recovery** — orchestrator detects misclassification and resumes agent for reclassification.
- **Adds cost** — another round-trip (orchestrator reads report, validates, resumes agent) vs preventing the error.

**Impact in isolation:** Zero prevention, but provides a safety net. Most valuable when combined with F1+F2 (catches cases where the protocol was followed but classification was still wrong).

**Rank 4: F4 — Deferred Items report section**

Template change. Without F1 (taxonomy), the section has no defined semantics. Without F2 (investigation protocol), agents have no reason to use it.

**Impact in isolation:** Near zero. A formatting change without behavioral or classificatory support.

**Rank 5: F6 — Pipeline contracts update**

One line change. Informational. No behavioral impact alone.

**Implementation recommendation:**

The minimum viable fix is F2 alone. It changes behavior, creates escalation cost, and prevents the most incidents. F1 should be implemented alongside F2 (the investigation protocol references DEFERRED and OUT-OF-SCOPE as diversion targets). F3+F5 should follow as the defensive layer. F4 and F6 are polish.

But the two-layer failure (Axis 1) adds a prerequisite: the orchestrate skill's checkpoint delegation must actually populate the IN/OUT fields. Without structured scope data flowing into the vet delegation, neither the investigation protocol nor the taxonomy can function for scope-related classifications. The upstream fix — enforcing template compliance in the orchestrate skill — is a precondition for F1 and F2 to work on scope-boundary incidents (Incidents 1 and 4).

**Revised fix ordering:**
1. **Orchestrate template enforcement** (precondition) — fail loudly if IN/OUT are not populated
2. **F2: Investigation protocol** (behavioral change) — highest single-fix impact
3. **F1: Taxonomy** (vocabulary) — enables correct labeling after investigation
4. **F3+F5: Validation** (defensive layer) — catches residual misclassification
5. **F4, F6** (polish)
