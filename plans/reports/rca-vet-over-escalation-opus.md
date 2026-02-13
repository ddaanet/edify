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
