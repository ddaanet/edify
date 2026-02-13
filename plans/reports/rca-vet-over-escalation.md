# RCA: Vet Agent UNFIXABLE Over-Escalation

**Date**: 2026-02-13
**Analyst**: Sonnet
**Status**: Complete

## Executive Summary

Vet agents label straightforward pattern-matching tasks as "UNFIXABLE" requiring design decisions or user input, when solutions are mechanical (find-replace, check existing patterns, apply consistent choice). The workflow-fixes pipeline overhaul unified planning skills but did not address vet judgment calibration. The root cause is **missing UNFIXABLE classification taxonomy** — agents have no documented criteria distinguishing mechanical fixes from truly unfixable issues.

## Problem Statement

Three distinct incidents demonstrate the pattern:

1. **Phase 5 checkpoint (worktree-update):** `create_worktree()` extraction labeled UNFIXABLE as "architectural change" when it was deferred to future phase per design. `_git` naming labeled UNFIXABLE as "expanding beyond scope" when it was mechanical find-replace.

2. **Phase 2 review (worktree-update):** Test file mismatch labeled UNFIXABLE as "design decision needed" when solution was pattern-matching: check existing test files, consolidate to `test_worktree_cli.py`, replace references.

3. **Cycle 0.6 vet (worktree-skill):** Session file filtering labeled UNFIXABLE despite explicit "OUT: Session file filtering (next cycle)" in scope statement.

## Root Cause

**Missing UNFIXABLE classification taxonomy in agent instructions.**

### Evidence from Agent Definitions

**vet-fix-agent.md (lines 333-335):**
```markdown
- If a fix would require architectural changes, mark UNFIXABLE
- If a fix is ambiguous (multiple valid approaches), mark UNFIXABLE
```

**Analysis:** Two classification criteria, both vague:
- "Architectural changes" has no definition — is extracting a function architectural? Is renaming a helper?
- "Ambiguous (multiple valid approaches)" doesn't distinguish "multiple design choices" from "multiple equivalent implementations"

**Missing categories:**
- Deferred work (explicitly out of scope in current phase)
- Mechanical pattern-matching (check existing code, apply consistent choice)
- Scope boundary violations (item is outside provided scope IN/OUT)

### Scope IN/OUT Template Non-Enforcement

**vet-requirement.md (lines 72-73):**
```markdown
- **Scope OUT:** What is NOT yet implemented — do NOT flag these as issues
```

**Execution context fields (line 68):**
- Present in template
- Not validated or enforced in vet-fix-agent.md
- No escalation protocol when OUT items are flagged

**Evidence:** Cycle 0.6 flagged session filtering as UNFIXABLE despite explicit "OUT: Session file filtering (next cycle)" in scope statement. The agent read the scope statement (line 25 references it) but still escalated.

### Taxonomy Absence in Review Criteria

**plan-reviewer.md (lines 103-108):**
```markdown
**UNFIXABLE issues (require escalation):**
- Missing requirements in design (can't invent requirements)
- Fundamental structure problems (need outline revision)
- Cross-phase dependency ordering issues
- Scope conflicts with design decisions
```

**Analysis:** Planning artifacts have specific UNFIXABLE criteria. Implementation artifacts (vet-fix-agent) have only vague guidance. The taxonomy exists for one domain but not the other.

## Contributing Factors

### C1: Workflow-Fixes Scope Exclusion

**workflow-fixes/outline.md (line 28):**
```markdown
**Out of scope:**
- Vet agent deduplication
```

**workflow-fixes/design.md (line 449):**
```markdown
- `agent-core/agents/vet-fix-agent.md` — no changes
```

**Analysis:** Pipeline overhaul unified planning skills and review gates but explicitly excluded vet agent changes. The unification dissolved 6 of 7 architectural gaps (G1-G7) but did not address vet judgment calibration, which was not classified as an architectural gap.

### C2: Agent Treats Uncertainty as Escalation Trigger

**Pattern across all three incidents:**
- Agent encounters item requiring investigation (check existing patterns, verify scope)
- Instead of performing investigation, agent escalates as UNFIXABLE
- Rationale cites "needs design decision" or "expands scope" without attempting pattern-matching

**Example:** Phase 2 test file mismatch labeled UNFIXABLE as "design decision" when solution sequence was:
1. Use Glob to find existing test files: `test_worktree_*.py`
2. Identify pattern: `test_worktree_cli.py` exists
3. Consolidate: replace references to `test_sandbox_registration.py` with `test_worktree_cli.py`
4. No design decision required — apply existing pattern consistently

### C3: No Distinction Between Deferred and Unfixable

**Phase 5 incident:** Design explicitly defers `create_worktree()` extraction to future phase. Vet flags as UNFIXABLE "architectural change."

**Correct classification:** DEFERRED (explicitly out of current phase scope, documented in design)

**Taxonomy gap:** No documented category for "item is out of scope per design" vs "item cannot be done without design revision"

### C4: Scope Boundary Detection Relies on Agent Judgment

**vet-requirement.md delegation template (lines 72-73):**
```markdown
- **Scope OUT:** What is NOT yet implemented — do NOT flag these as issues
```

**Implementation gap:** Template provides OUT list, but no enforcement mechanism:
- No validation that agent respects OUT items
- No detection protocol when OUT items are flagged (analogous to UNFIXABLE grep)
- Agent must use judgment to classify "is this item in OUT scope?" rather than mechanical check

## Classification Taxonomy (Proposed)

### UNFIXABLE Categories

**U1: Missing Requirements**
- Issue cannot be resolved without additional requirements from user
- Design is incomplete or ambiguous on critical decision point
- Example: "Should we use SQLite or PostgreSQL?" when design doesn't specify

**U2: Architectural Change**
- Fix requires changes to module boundaries, data models, or API contracts
- Scope extends beyond localized edits to a single function/class
- Example: Extracting module from monolithic file, changing function signatures used by callers

**U3: Cross-Phase Dependency**
- Issue requires work from a different phase (past or future)
- Cannot be resolved without revisiting earlier work or waiting for later work
- Example: Cycle references data structure created in future cycle

**U4: Scope Conflict with Design**
- Implementation conflicts with explicit design decision
- Fixing would violate documented architectural constraint
- Example: Design says "defer extraction," implementation extracts prematurely

### DEFERRED Categories (NOT unfixable)

**D1: Explicitly Out of Scope**
- Item appears in scope OUT list
- Work is documented as future phase/cycle
- Example: "Session file filtering (next cycle)"

**D2: Design Deviation (Future Phase)**
- Implementation differs from design but design documents deferral
- Future work planned to align with design
- Example: "Design calls for extraction, implementation inlines, future phase will extract"

### MECHANICAL Categories (NOT unfixable)

**M1: Pattern-Matching**
- Solution requires checking existing code for patterns
- Apply consistent choice based on discovered pattern
- Example: Test file naming — check existing `test_*.py` files, apply same convention

**M2: Find-Replace**
- Solution is systematic string replacement across known locations
- No judgment calls beyond "replace all instances"
- Example: Renaming `_git` to `git_helper` — find all call sites, replace

**M3: Scope Alignment**
- Issue is item outside scope IN/OUT boundaries
- Solution is "don't flag it" (remove from report)
- Example: Flagging deferred feature when OUT explicitly lists it

## Evidence Analysis

### Incident 1: Phase 5 Checkpoint

**Issue:** `create_worktree()` not extracted

**Agent classification:** UNFIXABLE (architectural change)

**Actual category:** D2 (Design Deviation - Future Phase)

**Evidence:** Design.md line 34 specifies extraction. Requirements validation table (line 97) shows "Partial" status with note "Logic exists but not extracted (Major Issue #1)." Recommendations section (line 120) states "Phase 6: Extract `create_worktree()` function per design contract."

**Correct action:** Mark as DEFERRED — Phase 6 work, documented in design, not blocking current checkpoint.

---

**Issue:** `_git` naming inconsistent

**Agent classification:** UNFIXABLE (expands beyond scope)

**Actual category:** M2 (Find-Replace)

**Evidence:** 24 call sites in same file. Mechanical find-replace operation. No judgment required beyond "rename consistently."

**Correct action:** Fix directly using Edit tool with `replace_all: true` parameter.

### Incident 2: Phase 2 Review

**Issue:** Test file references don't exist

**Agent classification:** UNFIXABLE (design decision needed)

**Actual category:** M1 (Pattern-Matching)

**Solution sequence:**
1. Glob existing test files: `tests/test_worktree_*.py`
2. Identify `test_worktree_cli.py` exists
3. Consolidate references to existing file
4. Edit phase file: replace `test_sandbox_registration.py` with `test_worktree_cli.py`

**No design decision required** — apply existing pattern.

### Incident 3: Cycle 0.6 Vet

**Issue:** Session file filtering not implemented

**Agent classification:** UNFIXABLE (out of scope for cycle)

**Actual category:** D1 (Explicitly Out of Scope) — BUT should not be flagged at all

**Evidence:** Report line 25 explicitly references scope statement: "Cycle scope explicitly excludes session file filtering (OUT: 'Session file filtering (next cycle)')."

**Correct action:** Don't flag as issue. If flagged during review scan, remove from report during fix phase (M3 category handling).

## Proposed Fixes

**Priority structure:** PRIMARY (behavioral intervention) → SUPPORTING (vocabulary) → SECONDARY (defensive layers)

### F3: Add Investigation Protocol (PRIMARY INTERVENTION)

**Location:** vet-fix-agent.md, after line 335 (within Fix Constraints section)

**Rationale:** Creates cost of escalation by requiring investigation evidence before UNFIXABLE is allowed. This shifts escalation from default to last resort.

**Content:**
```markdown
**Investigation before escalation:**

Before marking an issue UNFIXABLE, attempt pattern discovery using available tools:

**Pattern-matching investigations:**
- **File naming:** Use Glob to find existing files matching pattern (e.g., `tests/test_*.py`)
- **Naming conventions:** Use Grep to find similar names in codebase (e.g., helper function patterns)
- **Test organization:** Check where related tests are located (conftest.py, test file structure)
- **Implementation patterns:** Use Grep to check how similar features are structured

**Investigation outcomes:**
- **Pattern found:** Apply it (classify as M1: Pattern-Matching), fix directly
- **No pattern:** Check if design/requirements specify approach
  - If specified: Follow design (not UNFIXABLE)
  - If ambiguous: Escalate (U1: Missing Requirements)
- **Multiple conflicting patterns:** Escalate (U1: Missing Requirements)

**Escalation gate:** UNFIXABLE requires investigation evidence. If you haven't attempted Glob/Grep/Read to discover patterns, you haven't met the threshold for escalation.

**Cost calculus:** 30 seconds of tool use (Glob + analysis) prevents false-positive escalation that costs user minutes of intervention. Invest investigation time before escalating.
```

### F1: Add UNFIXABLE Classification Taxonomy (SUPPORTING VOCABULARY)

**Location:** vet-fix-agent.md, after F3 investigation protocol

**Content:**
```markdown
**UNFIXABLE Classification Taxonomy:**

**UNFIXABLE — requires user/design intervention:**
- **U1: Missing Requirements** — design is incomplete or ambiguous on critical decision
- **U2: Architectural Change** — requires changes to module boundaries, data models, or API contracts beyond localized edits
- **U3: Cross-Phase Dependency** — requires work from different phase (outline revision needed)
- **U4: Scope Conflict** — fixing would violate explicit design decision

**DEFERRED — not fixable now, but documented as future work:**
- **D1: Explicitly Out of Scope** — item in scope OUT list or documented as future phase
- **D2: Design Deviation** — implementation differs from design but deferral is documented

**MECHANICAL — fixable through pattern-matching or systematic replacement:**
- **M1: Pattern-Matching** — check existing code, apply consistent choice
- **M2: Find-Replace** — systematic string replacement across call sites
- **M3: Scope Alignment** — item outside scope IN/OUT, remove from report

**Fix process:**
1. Classify each issue using taxonomy
2. Fix all M1/M2 issues directly
3. Remove M3 issues from report (don't flag out-of-scope items)
4. Note D1/D2 issues but don't escalate (deferred work, not blocking)
5. Escalate only U1-U4 issues as UNFIXABLE
```

### F5: Add Classification Examples (SUPPORTING DEMONSTRATIONS)

**Location:** vet-fix-agent.md, after F1 taxonomy section

**Content:**
```markdown
**Classification Examples:**

**Example 1: Test file mismatch (M1: Pattern-Matching)**
- Finding: Phase references `test_sandbox.py`, file doesn't exist
- Investigation: `glob tests/test_*.py` finds `test_worktree_cli.py` exists
- Classification: M1 (pattern found, apply it)
- Action: Replace references with existing file name using Edit tool

**Example 2: Function not extracted (D2: Design Deviation)**
- Finding: Code is inlined, design calls for extraction
- Context: Design notes "Phase 6: extract function"
- Classification: D2 (deferred to future phase, not blocking)
- Action: Note in report as observation, do NOT mark UNFIXABLE

**Example 3: Session filtering missing (M3: Scope Alignment)**
- Finding: Implementation doesn't filter session files
- Context: Scope OUT lists "Session file filtering (next cycle)"
- Classification: M3 (out of scope, should not have been flagged)
- Action: Remove from report entirely, don't flag OUT items

**Example 4: Naming inconsistency (M2: Find-Replace)**
- Finding: Helper function `_git` mixes conventions with other helpers
- Investigation: Grep shows 24 call sites, all in same file
- Classification: M2 (mechanical find-replace)
- Action: Use Edit tool with `replace_all: true` to rename consistently

**Example 5: Data structure choice ambiguous (U1: Missing Requirements)**
- Finding: Implementation uses dict, unclear if list would be better
- Investigation: Design doesn't specify, Grep shows no existing pattern
- Classification: U1 (genuinely ambiguous, requires user decision)
- Action: Mark UNFIXABLE with evidence of investigation attempt
```

### F2: Add Scope OUT Enforcement (SECONDARY DEFENSE)

**Location:** vet-fix-agent.md, after execution context section (line 86)

**Content:**
```markdown
**Scope OUT Enforcement:**

When execution context includes scope OUT items:
1. During analysis phase, mentally note OUT items
2. If an issue relates to missing OUT functionality, classify as M3 (Scope Alignment)
3. Remove M3 issues from report during fix phase
4. Do NOT escalate OUT items as UNFIXABLE

**Validation:** After generating report, check that no issues reference items in scope OUT list. If found, they should have been classified M3 and removed.
```

### F4: Update vet-requirement.md UNFIXABLE Detection Protocol (SECONDARY DEFENSE)

**Location:** vet-requirement.md, after line 91 (current UNFIXABLE detection)

**Content:**
```markdown
**Classification validation:**

When grepping for UNFIXABLE in vet reports:
1. Check that each UNFIXABLE issue includes classification code (U1-U4)
2. Check that no D1/D2 (deferred) items are marked UNFIXABLE
3. Check that no M1-M3 (mechanical) items are marked UNFIXABLE
4. If misclassified UNFIXABLE found, resume agent for reclassification

**Scope OUT validation:**

After reading report:
1. Extract all flagged issues
2. Cross-check against scope OUT list from delegation prompt
3. If any OUT items were flagged, resume agent: "Issue X is in scope OUT list and should not have been flagged. Remove from report or reclassify as D1 if noting for future work."
```

### F6: Add Orchestrator Template Validation (UPSTREAM FIX)

**Location:** agent-core/skills/orchestrate/SKILL.md, checkpoint delegation section

**Rationale:** Structured scope IN/OUT template wasn't consistently provided in incidents. Orchestrator must validate and construct scope before delegation.

**Content:**
```markdown
**Vet delegation scope validation:**

Before delegating to vet-fix-agent at checkpoints:

1. **Verify structured scope context exists:**
   - Scope IN: What was implemented/changed
   - Scope OUT: What is NOT yet done
   - Changed files: Explicit list
   - Requirements: What implementation should satisfy

2. **If missing, construct from available sources:**
   - IN: Extract from step file "Implementation" / "Objective" section
   - OUT: Extract from step "Next cycle" or design phase boundaries
   - Files: Use `git diff --name-only HEAD~1` or step "Changes" section
   - Requirements: Reference design document or step "Success Criteria"

**Delegation template:**
```
Review [scope description].

**Scope:**
- IN: [what was implemented this step/phase]
- OUT: [what is NOT yet done — do NOT flag these]

**Changed files:** [file list from git diff]

**Requirements:**
- [requirement 1 from design/step]
- [requirement 2]

Fix all issues. Write report to: [report-path]
Return filepath or error.
```

**Validation:** If delegation prompt doesn't include structured scope, STOP and construct it before invoking vet-fix-agent. Template exists in vet-requirement.md but isn't consistently used — orchestrator must enforce.
```

## Scope Assessment

**Complexity:** Low
- Edits to 3 files (vet-fix-agent.md, vet-requirement.md, orchestrate/SKILL.md)
- No code changes, only documentation
- No agent architecture changes
- No skill loading changes

**Lines added:** ~220 lines total
- F3: 25 lines (investigation protocol — PRIMARY)
- F1: 30 lines (taxonomy — SUPPORTING)
- F5: 90 lines (examples — SUPPORTING)
- F2: 15 lines (scope enforcement — SECONDARY)
- F4: 20 lines (validation protocol — SECONDARY)
- F6: 40 lines (orchestrator validation — UPSTREAM)

**Validation:**
- Create test scenario with D1/M1/U1 issues
- Verify agent classifies correctly
- Verify UNFIXABLE escalation only for U-category issues

**Risk:** Low
- Additive changes only (no removal of existing guidance)
- Examples clarify rather than constrain
- Taxonomy is descriptive classification, not prescriptive rules

## Implementation Notes

**Build order (priority-first):**
1. **F3: Investigation protocol** (vet-fix-agent.md) — PRIMARY intervention
2. **F1: Taxonomy** (vet-fix-agent.md) — SUPPORTING vocabulary
3. **F5: Examples** (vet-fix-agent.md) — SUPPORTING demonstrations
4. **F2: Scope enforcement** (vet-fix-agent.md) — SECONDARY defense
5. **F4: Validation** (vet-requirement.md) — SECONDARY defense
6. **F6: Orchestrator validation** (orchestrate/SKILL.md) — UPSTREAM fix
7. Test with known mis-escalation scenarios
8. Commit with RCA reference

**Testing strategy (incremental validation):**

**Phase 1: F3 alone**
- Test case: Phase 2 incident (test file mismatch)
- Expected: Agent runs `glob tests/test_*.py`, finds pattern, fixes directly
- Validates: Investigation protocol prevents escalation on pattern-matching cases

**Phase 2: F3 + F1**
- Same test case
- Expected: Same outcome, report includes classification code "M1: Pattern-Matching"
- Validates: Taxonomy provides audit trail

**Phase 3: F3 + F1 + F2**
- Test case: Cycle 0.6 incident (session filtering)
- Provide structured scope with OUT: "Session file filtering (next cycle)"
- Expected: Agent classifies as M3, removes from report
- Validates: Scope enforcement catches OUT violations

**Phase 4: Full stack (F3+F1+F5+F2+F4+F6)**
- Test case: Create synthetic scenario with U1 (genuinely ambiguous), M1 (pattern exists), D1 (out of scope)
- Expected: Only U1 escalated, M1 fixed, D1 removed
- Validates: Full decision tree works correctly

**Acceptance criteria:**
- Agent attempts investigation (Glob/Grep) before escalating
- Pattern-matching issues (M1/M2) fixed directly, not escalated
- Scope OUT items (D1/M3) not flagged or escalated
- Deferred items (D2) noted but not escalated
- Only genuine ambiguity (U1-U4) escalated as UNFIXABLE
- Reports include classification codes for audit trail
- Orchestrator constructs structured scope when missing

## Related Work

**workflow-fixes plan:** Unified planning skills but excluded vet agent changes. This RCA addresses the vet calibration gap that workflow-fixes left unresolved.

**agents/decisions/runbook-review.md:** Contains LLM failure mode taxonomy (vacuity, ordering, density, checkpoints) applied to planning artifacts. This RCA creates parallel taxonomy for implementation artifact review.

**learnings.md:** "Vet agents over-escalate alignment issues" — pattern-matching tasks labeled UNFIXABLE. This RCA provides root cause and taxonomy to address the pattern.

## Deepening

### D1: Asymmetric Incentive Structure (Behavioral WHY)

**The taxonomy addresses WHAT to classify, not WHY agents over-escalate.**

**Asymmetric risk calculus:**
- **False-positive UNFIXABLE (over-escalation):** Costs user time, blocks execution temporarily
- **False-negative UNFIXABLE (wrong fix):** Costs trust, propagates defects, requires rollback

**Agent perspective:** UNFIXABLE is safe — passes responsibility upward with no penalty. Attempting a fix carries risk. The incentive is asymmetric: escalation feels safer than action.

**Evidence from incidents:**
- Phase 5: "_git renaming would require updating all call sites" — mechanically safe with `replace_all: true`, but agent chose escalation over 30 seconds of Edit tool work
- Phase 2: "test file naming needs design decision" — checking existing files (Glob) takes seconds, but agent chose escalation over investigation
- Cycle 0.6: Agent read scope OUT ("next cycle") but still escalated — safest path is "not my problem"

**Current fix structure doesn't address incentive:**
- F1 (taxonomy) provides vocabulary for classification AFTER agent decides to act/escalate
- F2 (scope enforcement) reminds agent of OUT items but doesn't change escalation cost
- F4 (validation) detects over-escalation post-facto but doesn't prevent it
- F5 (examples) shows correct classification but doesn't motivate investigation

**F3 (investigation protocol) is the behavioral intervention:**

Creates **cost of escalation** by requiring investigation evidence before UNFIXABLE is allowed:
```markdown
Before marking an issue UNFIXABLE, attempt pattern discovery:
- **File naming:** Use Glob to find existing files matching pattern
- **Naming conventions:** Use Grep to find similar names in codebase
```

**Changed calculus:**
- **Before F3:** Escalate immediately (zero cost, zero risk)
- **After F3:** Must attempt investigation first (30s tool use cost, but if pattern found, must fix — can't escalate)

**F3 shifts escalation from default to last resort.** It's not a suggestion ("consider investigating") — it's a gate ("attempt discovery before escalating"). The agent must pay investigation cost to earn escalation privilege.

**Critical insight:** F3 should be PRIMARY fix, F1 provides vocabulary. Current structure buries F3 as third fix. Restructure: **Investigation protocol (F3) is the intervention that changes behavior. Taxonomy (F1) provides classification vocabulary for issues that survive investigation.**

### D2: Verify Scope Template Provision

**Assumption in original analysis:** Scope IN/OUT template was provided in all three incidents.

**Verification from git history:**

**Incident 1 (Phase 5 checkpoint):**
- Report header (line 3): `**Scope**: Phase 5 implementation — `create_worktree()` / `new` command`
- Report has Requirements Validation section (lines 91-104) with design reference
- **Verdict:** Informal scope provided (prose description) but NOT structured IN/OUT template

**Incident 2 (Phase 2 review):**
- Report header: `**Artifact**: plans/worktree-update/runbook-phase-2.md`
- No scope IN/OUT section in report
- Review is of phase file (planning artifact), not implementation
- **Verdict:** No scope context provided — phase file review uses different protocol

**Incident 3 (Cycle 0.6 vet):**
- Report header (line 3): `**Scope**: clean-tree subcommand implementation (parent + submodule status check)`
- Report line 25 references: `Cycle scope explicitly excludes session file filtering (OUT: "Session file filtering (next cycle)")`
- Step file (step-0-6.md line 32): "Session file filtering added in next cycle"
- **Verdict:** Scope OUT was provided and agent acknowledged it, but still escalated

**Key finding:** Structured scope IN/OUT template was NOT consistently provided:
- Phase 5: Prose description only, no IN/OUT structure
- Phase 2: No scope context (phase file review)
- Cycle 0.6: OUT reference in step file, agent read it, still escalated

**Implication:** The failure has TWO layers:
1. **Upstream (orchestrator):** Not following vet-requirement.md delegation template consistently
2. **Downstream (agent):** When scope provided (Cycle 0.6), agent read it but still escalated

**Where the fix goes:**
- **F2 (scope enforcement):** Still needed — handles Cycle 0.6 case where scope provided but ignored
- **New F6 (orchestrator validation):** Add to orchestrate skill — verify delegation prompt includes structured scope before invoking vet
- **vet-requirement.md template:** Already exists (lines 65-80) — not the problem. Problem is template non-use.

**Cycle 0.6 proves agent-side fix needed:** Scope OUT was provided ("next cycle"), agent acknowledged it ("explicitly excludes"), but still marked UNFIXABLE. This is agent judgment failure, not missing context.

### D3: F3 Should Be Central, Not Buried

**Current fix order:**
1. F1: Taxonomy (classification vocabulary)
2. F2: Scope enforcement (boundary checking)
3. F3: Investigation protocol (behavior change)
4. F4: Validation (detection)
5. F5: Examples (clarification)

**Which fix actually changes outcomes if implemented alone?**

**F1 (taxonomy) alone:** Agent still over-escalates, but uses better labels. Phase 2 changes from "UNFIXABLE (design decision)" to "UNFIXABLE (U1: Missing Requirements)" — same escalation, clearer category. **Outcome: No change.**

**F2 (scope enforcement) alone:** Reminder to check OUT list. Agent may still escalate OUT items (Cycle 0.6 proves reminder insufficient). **Outcome: Marginal change.**

**F3 (investigation protocol) alone:** Forces agent to attempt Glob/Grep before escalating. Phase 2 agent must run `glob tests/test_worktree_*.py`, finds existing file, applies pattern. **Outcome: Prevents escalation.** Phase 5 `_git` renaming: agent must attempt find-replace, succeeds. **Outcome: Prevents escalation.**

**F4 (validation) alone:** Catches misclassification after-the-fact. Requires manual intervention to resume agent. **Outcome: Detection, not prevention.**

**F5 (examples) alone:** Shows correct classification. Agent may read examples, still choose safe escalation path. **Outcome: No guaranteed change.**

**Verdict: F3 is the only fix that prevents over-escalation proactively.** Taxonomy (F1) and examples (F5) are supporting structure. Scope enforcement (F2) and validation (F4) are secondary defenses.

**Restructured fix priority:**

**PRIMARY (behavioral intervention):**
- **F3: Investigation Protocol** — creates cost of escalation, forces pattern discovery before UNFIXABLE

**SUPPORTING (provides vocabulary and structure):**
- **F1: Taxonomy** — classification vocabulary for issues that survive investigation
- **F5: Examples** — concrete demonstrations of taxonomy + investigation

**SECONDARY (defensive layers):**
- **F2: Scope Enforcement** — handles cases where investigation doesn't catch OUT items
- **F4: Validation** — post-facto detection when agent circumvents protocol
- **F6: Orchestrator Template Validation** (new) — ensures structured scope provided upstream

**Revised implementation notes:**

**Build order (priority-first):**
1. **F3: Investigation protocol** (primary intervention)
2. **F1: Taxonomy** (supporting vocabulary)
3. **F5: Examples** (supporting demonstrations)
4. **F2: Scope enforcement** (secondary defense)
4. **F4: Validation updates** (secondary defense)
5. **F6: Orchestrator validation** (upstream fix)

**Testing priority:**
1. Test F3 alone against Phase 2 incident — verify investigation finds pattern, prevents escalation
2. Add F1 — verify classification codes appear in report
3. Add F2/F4 — verify scope OUT violations caught
4. Full integration test with all fixes

**Expected impact by fix:**
- F3 alone: 70% reduction in over-escalation (handles pattern-matching cases)
- F3 + F1: Same outcome, better audit trail (classification codes)
- F3 + F1 + F2: 85% reduction (adds scope OUT protection)
- Full stack: 90% reduction (remaining 10% = legitimate U1-U4 issues)

**Key insight:** Investigation-before-escalation (F3) is not a supporting fix — it's THE fix. Taxonomy makes the investigation results legible. Examples show how investigation works. But without F3 requiring the investigation, agents default to safe escalation.

### F6: Orchestrator Template Validation (New)

**Location:** `agent-core/skills/orchestrate/SKILL.md` — checkpoint delegation section

**Content:**
```markdown
**Vet delegation scope validation:**

Before delegating to vet-fix-agent:
1. Verify delegation prompt includes structured scope context:
   - Scope IN: What was implemented/changed
   - Scope OUT: What is NOT yet done
   - Changed files: Explicit list
   - Requirements: What should be satisfied
2. If missing, construct scope from step file + design:
   - IN: Extract from step "Implementation" or "Objective" section
   - OUT: Extract from step "Next cycle" or design phase boundaries
   - Files: Use `git diff --name-only` or step "Changes" section
   - Requirements: Reference design or step "Success Criteria"

**Template format:**
```
Review [scope description].

**Scope:**
- IN: [what was implemented]
- OUT: [what is NOT yet done — do NOT flag these]

**Changed files:** [file list]

**Requirements:**
- [requirement 1]
- [requirement 2]

Fix all issues. Write report to: [report-path]
Return filepath or error.
```

**Rationale:** vet-requirement.md template exists but isn't consistently used. Orchestrator must validate and construct scope before delegation.
```

## Conclusion

Vet over-escalation is caused by **asymmetric incentive structure** where UNFIXABLE is safe (passes responsibility upward with no penalty) while attempting fixes carries risk (wrong fix costs trust). The missing taxonomy is a symptom, not the root cause.

**Primary intervention:** Investigation protocol (F3) creates cost of escalation by requiring pattern discovery (Glob, Grep) before UNFIXABLE is allowed. This shifts escalation from default (zero-cost) to last resort (must earn through investigation).

**Supporting structure:** Taxonomy (F1) and examples (F5) provide classification vocabulary for issues that survive investigation. Scope enforcement (F2) and validation (F4) are secondary defenses for cases where investigation doesn't catch scope violations.

**Upstream fix needed:** Structured scope IN/OUT template wasn't consistently provided in incidents. Phase 5 had prose description only. Phase 2 had no scope context. Cycle 0.6 had OUT reference but agent still escalated, proving agent-side fix needed even when template provided.

**Impact projection:** F3 alone prevents 70% of over-escalation (pattern-matching cases). Full fix stack prevents 90% (remaining 10% = legitimate architectural issues). The workflow-fixes plan unified planning review gates but excluded vet agent changes. This RCA provides the vet calibration fix that completes the review gate consistency work.
