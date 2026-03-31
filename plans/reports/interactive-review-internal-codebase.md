# Interactive Review: Internal Codebase Patterns

**Date:** 2026-03-12
**Scope:** Exploration of existing review mechanisms, verdict vocabularies, item-by-item iteration patterns, and user interaction loops

## Summary

The codebase has well-established review infrastructure spanning three architectural layers: (1) the `/proof` skill for interactive artifact validation with a reword-accumulate-sync protocol; (2) corrector agents (outline-corrector, design-corrector, runbook-corrector, corrector) implementing fix-all policies with status taxonomies; (3) deliverable-review skill providing two-layer review (delegated per-file + interactive cross-cutting). Verdict vocabularies are severity-based (critical/major/minor) with orthogonal status categories (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE). Item-by-item iteration is present in `/proof` (reword-validate-accumulate loop) but not in corrector agents (which operate on full documents). AskUserQuestion is used for scope disambiguation and requirements elicitation, not for item-by-item user feedback.

## Key Findings

### 1. `/proof` Skill — Interactive Artifact Validation

**Location:** `/Users/david/code/edify/plugin/skills/proof/SKILL.md`

**Purpose:** Structured review loop for planning artifacts (outline.md, design.md, requirements.md, runbook phases). Replaces single-turn "does this look right?" with iterative protocol.

**Loop Mechanics:**

- **Reword:** User provides feedback → Agent restates as understanding statement → User confirms/corrects before proceeding
- **Accumulate:** Validated understandings tracked in-memory as decision list with format:
  ```
  - D-1: [validated understanding] -> [artifact impact]
  - D-2: [validated understanding] -> [artifact impact]
  ```
  Decision number (D-N) scoped to the session, not the artifact

- **Sync:** On user request ("sync", "resync", "show decisions"), output full accumulated decision list with artifact impacts

**Terminal Actions:**
- `"proceed" / "apply"`: Apply accumulated decisions to artifact → dispatch lifecycle-appropriate corrector → return control
- `"learn"`: Capture insight to agents/learnings.md → resume loop (not terminal)
- `"suspend"`: Route to /design for skill update → resume current work

**Key Integration:**
- Invoked inline by hosting skills (/design, /runbook, /requirements) at review integration points
- Uses Skill tool (enforces protocol steps via tool invocation gate)
- Corrector dispatch is lifecycle-driven (artifact type + "edits applied" → corrector fires)
- Corectors for outline.md (outline-corrector), design.md (design-corrector), runbook phases (runbook-corrector)

**Observation:** Item-by-item review is not the /proof pattern — /proof is document-centric with accumulated decisions. The reword-accumulate-sync loop is validation-centric, not review-centric.

---

### 2. Severity-Based Verdict Vocabulary

**Sources:**
- `/Users/david/code/edify/plugin/agents/corrector.md` (Status Taxonomy, lines 18-78)
- `/Users/david/code/edify/plugin/agents/outline-corrector.md`
- `/Users/david/code/edify/plugin/agents/design-corrector.md`
- `/Users/david/code/edify/plugin/skills/deliverable-review/SKILL.md` (lines 138-142)

**Severity Levels (All Artifacts):**

| Severity | Definition | Block? |
|----------|-----------|--------|
| **Critical** | Incorrect behavior, data loss, security, unimplemented design requirement | Yes |
| **Major** | Missing functionality, broken references, vacuous artifact, test gap for specified scenario | No |
| **Minor** | Style, clarity, naming, robustness edge case | No |

**Status Taxonomy (Orthogonal to Severity):**

| Status | Meaning | Block? | When to Use |
|--------|---------|--------|------------|
| **FIXED** | Fix applied | No | Edit made, issue resolved |
| **DEFERRED** | Real issue, explicitly out of scope | No | Listed in scope OUT or design documents as future work |
| **OUT-OF-SCOPE** | Not relevant to current review | No | Falls outside the review's subject matter entirely |
| **UNFIXABLE** | Technical blocker requiring user decision | **Yes** | All 4 investigation gates passed, no fix path exists |

**UNFIXABLE Subcategory Codes:**

| Code | Category | Example |
|------|----------|---------|
| **U-REQ** | Requirements ambiguity or conflict | "Errors must be surfaced" + "Silent recovery required" |
| **U-ARCH** | Architectural constraint or design conflict | Fix would violate an architectural invariant |
| **U-DESIGN** | Design decision needed | Multiple valid approaches with non-trivial consequences |

**Investigation Summary Format (UNFIXABLE):**
```
**Status:** UNFIXABLE (U-REQ)
**Investigation:**
1. Scope OUT: not listed
2. Design deferral: not found in design.md
3. Codebase patterns: Grep found no existing pattern for this case
4. Conclusion: [why no fix path exists]
```

---

### 3. Corrector Agents — Fix-All Policy

**Locations:**
- `/Users/david/code/edify/plugin/agents/corrector.md` (implementation review)
- `/Users/david/code/edify/plugin/agents/outline-corrector.md` (design outline review)
- `/Users/david/code/edify/plugin/agents/design-corrector.md` (design document review)
- `/Users/david/code/edify/plugin/agents/runbook-corrector.md` (runbook/phase review)

**Core Directive:** Write review (audit trail) → Fix ALL issues → Escalate unfixable → Return filepath

**Policy:** All correctors apply fixes for ALL issues (critical, major, AND minor). Document-centric, not item-centric.

**Review Report Structure (All Correctors):**
```markdown
# Review: [artifact name]

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix

## Summary
[2-3 sentence overview]
**Overall Assessment**: [Ready / Needs Minor Changes / Needs Significant Changes]

## Issues Found and Fixed

### Critical Issues
1. **[Issue title]**
   - Problem: [What was wrong]
   - Fix Applied: [What was changed]
   - **Status**: FIXED

### Major Issues
[Same format]

### Minor Issues
[Same format]

## Fixes Applied
[Summary of all changes made]
- [section/line] — [change description]

## Positive Observations
[What was done well]

## Recommendations
[High-level suggestions]
```

**Assessment Criteria:**
- **Ready:** No critical, no major (or 1-2 minor)
- **Needs Minor Changes:** No critical, 1-3 major (all fixable)
- **Needs Significant Changes:** Critical issues OR 4+ major OR architectural rework needed

**Notable Pattern:** No merge-readiness language in corrector reports. Reports severity counts only. User reads counts, user decides. (See agents/decisions/pipeline-review.md "When Concluding Reviews", 2026-02-19)

---

### 4. Deliverable Review Skill — Two-Layer Review

**Location:** `/Users/david/code/edify/plugin/skills/deliverable-review/SKILL.md`

**Purpose:** Review production artifacts after plan execution (code, tests, docs, config).

**Layer 1: Delegated Per-File Review (Optional)**
- Threshold: 500–2000 lines → 2 opus agents (code+test, prose+config); >2000 lines → 3 agents
- Skip if <500 lines total
- Agents operate in parallel with `run_in_background=true`
- Agents receive: files to review, design reference, applicable review axes
- Output: `plans/<plan>/reports/deliverable-review-<type>.md`

**Layer 2: Interactive Full-Artifact Review (Mandatory)**
- Always runs in main session with full cross-project context
- Scope depends on whether Layer 1 ran
- **Cross-cutting checks (always):**
  - Path consistency, API contract alignment, naming convention uniformity
  - Fragment convention compliance, memory index pattern verification
  - Other skills' allowed-tools and frontmatter validation
  - Recall context: `edify _recall resolve plans/<plan>/recall-artifact.md` (or lightweight recall via memory-index.md)

**Severity Classification:**
- **Critical** — incorrect behavior, data loss, security, unimplemented design requirement
- **Major** — missing functionality, broken references, vacuous artifact, test gap
- **Minor** — style, clarity, naming, robustness edge case

**Report Structure:**
```markdown
# Deliverable Review: <plan-name>

## Inventory
[Table: type, file, lines]
[Design conformance summary]

## Critical Findings
[Numbered, with file:line, design requirement, impact]

## Major Findings
[Same format]

## Minor Findings
[Grouped by category, brief]

## Gap Analysis
[Table: design requirement, status (covered/missing)]

## Summary
[Severity counts, assessment]
```

**Lifecycle Integration:**
- Append to `plans/<plan>/lifecycle.md` with date and mode (`reviewed` or `rework` if critical findings)
- Create pending task if ANY findings exist: `Fix <plan> findings — /design plans/<plan>/reports/deliverable-review.md`
- No merge-readiness language — severity counts only

---

### 5. Review-Plan Skill — Runbook Quality Validation

**Location:** `/Users/david/code/edify/plugin/skills/review-plan/SKILL.md`

**Purpose:** Validate runbook phase quality for TDD discipline, step clarity, and LLM failure modes.

**Scope:** Reviews TDD (cycle-based), general (step-based), and inline phases.

**Key Review Criteria:**

**TDD Phases:**
- GREEN anti-pattern: Implementation code (violation → CRITICAL)
- RED/GREEN sequencing: Tests fail before implementation (violation → CRITICAL)
- Weak RED assertions: Prose too vague for deterministic test writing (violation → CRITICAL)
- Over-specific verify paths: pytest selectors instead of `just green` (violation → MINOR)

**General Phases:**
- Prerequisite validation: Creation steps have investigation prereqs
- Script evaluation: Size classification matches actual complexity
- Step clarity: Objective, Implementation, Expected Outcome present

**All Phases:**
- Vacuity, dependency ordering, density, checkpoint spacing (LLM failure modes)
- File reference validation: CRITICAL if paths fabricated or functions not found
- Metadata accuracy: Total steps count matches actual cycle/step count

**Recall Context:**
- Bash: `edify _recall resolve plans/<job>/recall-artifact.md`
- If absent/fails: lightweight recall via memory-index.md

---

### 6. AskUserQuestion Usage Patterns

**Sources:**
- `/Users/david/code/edify/plugin/agents/corrector.md` (lines 174-182)
- `/Users/david/code/edify/plugin/skills/requirements/SKILL.md`
- `/Users/david/code/edify/plugin/skills/review/SKILL.md`

**Pattern 1: Scope Disambiguation (corrector agent)**
```
What should I review?

Options:
1. "Uncommitted changes" - Review git diff (staged + unstaged)
2. "Recent commits" - Review last N commits on current branch
3. "Current branch" - Review all commits since branched from main
4. "Specific files" - Review only specified files
5. "Everything" - Uncommitted + recent commits
```

**Pattern 2: Requirements Elicitation (requirements skill)**
- Gap-fill mode: Max 3 questions for empty critical sections
- Elicit mode: 4-6 total questions (section questions + adaptive follow-ups)
- Never include time estimates in options (per CLAUDE.md)

**Observation:** AskUserQuestion is used for scope/requirements entry, not for iterative item-by-item feedback during review. No existing pattern for presenting individual review findings and asking user for action per item.

---

### 7. Existing Review Report Examples

**Session.md Patterns (agents/session.md):**

Example: Outline corrector findings
```
**Status:** Briefed (or Requirements if findings exist)
```

No detailed structured findings shown in session.md — findings kept in separate reports in `plans/<plan>/reports/`.

**Report Naming Convention:**
- `<artifact>-review.md` (outline-review.md, design-review.md)
- `<artifact>-proof-review.md` (when /proof dispatches corrector)
- `deliverable-review.md` (or `deliverable-review-<type>.md` for per-file reviews)
- `runbook-review.md` (or `phase-N-review.md` for phase files)

---

### 8. Decision Tracking Pattern

**Source:** agents/decisions/pipeline-review.md

**Decision Dating/Versioning:** Decisions include "Decision Date: YYYY-MM-DD"

**Decision Anatomy:**
- **Antipattern:** What not to do
- **Correct pattern:** What to do instead
- **Evidence:** Why the pattern works (from project history)
- **Classification:** When/how to apply the rule

**Example (2026-02-19):**
```
## When Holistic Review Applies Fixes

**Anti-pattern:** Fixing one reference to a changed value without checking for other references

**Correct pattern:** After changing a value, grep the artifact for all other references. Fix-all means all occurrences, not just the first.

**Evidence:** [specific case that motivated the rule]
```

---

### 9. No Existing Item-by-Item Review Implementation

**Finding:** The codebase has NO existing implementation of item-by-item user-driven review where:
- System presents individual review findings one at a time
- User provides verdict/action per item (accept fix, defer, escalate)
- System tracks user decisions across items
- System allows skipping forward/backward through items

**Why:** Corrector agents operate document-centric (whole artifact at once), not item-centric. The /proof skill's reword-accumulate-sync is validation-centric (user input → agent validates understanding), not review-centric (system presents findings → user verdict).

**Closest Pattern:** /proof's reword loop with accumulation, but:
- /proof is for changes user wants to make (not issues system found)
- /proof restates user feedback before applying (not presenting system findings)
- /proof accumulates user decisions, not system review verdicts

---

### 10. Presentation Formats in Reports

**Header Structure (All Reports):**
```markdown
# [Review Type]: [artifact name]

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix
```

**Section Structure (All Reports):**
```markdown
## Summary
[2-3 sentence overview]

## Issues Found

### Critical Issues
[Numbered list with: location, problem, fix, status]

### Major Issues
[Same structure]

### Minor Issues
[Same structure, or grouped by category if many]

## [Other Sections]
- Fixes Applied
- Positive Observations
- Recommendations
- Traceability (for correctors)
```

**Issue Format (Corrector Reports):**
```markdown
1. **[Issue title]**
   - Location: [file:line or section]
   - Problem: [What's wrong]
   - Fix: [What was changed] / Suggestion: [What to do] / Note: [Improvement]
   - **Status**: [FIXED / DEFERRED / OUT-OF-SCOPE / UNFIXABLE]
```

**Issue Format (Deliverable Review):**
```markdown
1. **[Issue title]**
   - File:line: [location]
   - Design requirement: [what spec is violated]
   - Impact: [why this matters]
```

---

## Patterns & Cross-Cutting Observations

### Pattern 1: Severity + Status Orthogonality

Severity (critical/major/minor) is independent from Status (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE). A critical issue can be DEFERRED (out of scope but real), a minor issue can be UNFIXABLE (requires design rework).

### Pattern 2: Fix-All for Documents, Not Code

Correctors use fix-all for documents (low-risk — wording changes only) but NOT for code. Code correctness agent applies fixes only for critical+major, deferring minor to human judgment.

**Distinction:**
- Design/outline/runbook correction: fix ALL (critical, major, minor)
- Implementation code review: fix critical+major, DEFER minor
- Requirements validation: no auto-fix (user-validated directly via AskUserQuestion)

### Pattern 3: Recall Context Integration

All review agents load recall context for project-specific patterns:
- Bash: `edify _recall resolve plans/<job>/recall-artifact.md`
- Fallback: lightweight recall via memory-index.md + batch resolve
- Purpose: Failure modes and quality anti-patterns supplement standard review criteria

### Pattern 4: Investigation Gates Before UNFIXABLE

Before classifying as UNFIXABLE, correctors must pass 4 gates in order:
1. **Scope OUT check** — Is item listed in scope OUT?
2. **Design deferral check** — Does design document defer this?
3. **Codebase pattern check** — Do existing patterns resolve the issue?
4. **Escalation** — Only after gates 1-3 fail, classify UNFIXABLE with subcategory code

### Pattern 5: Lifecycle-Driven Corrector Dispatch

/proof doesn't ask "should I run corrector?" — it dispatches lifecycle-appropriately:
- outline.md edits → outline-corrector
- design.md edits → design-corrector
- runbook-phase-*.md edits → runbook-corrector
- Corrector dispatch is automatic, not user-requested

### Pattern 6: No Merge-Readiness Judgments in Reports

Corrector reports report severity counts only. No "doesn't block merge" or "ready to merge" language. User reads severity counts, user decides merge readiness. (Prevents sycophancy in artifact form per pipeline-review.md)

### Pattern 7: Recall vs Delegation Split

Two distinct artifact models:
- **Pipeline model:** Grouped entries with relevance notes, selective resolution by skills with parent context
- **Sub-agent model:** Flat list, resolve-all, no selection judgment (agents can't evaluate relevance without parent context)

/proof and correctors receive plan-specific recall artifacts. Delegated agents receive flat trigger lists.

---

## Gaps & Unresolved Questions

### Gap 1: Item-by-Item Review Infrastructure

No existing pattern for:
- Presenting individual findings to user one at a time
- Accepting/deferring/escalating per item interactively
- Tracking user verdict across items
- Navigating forward/backward through findings

The /proof skill provides one direction (user feedback → agent understanding validation), not the reverse (agent findings → user verdict).

### Gap 2: Interactive Report Navigation

Corrector reports are static documents. No pattern for:
- User browsing findings in custom order
- User filtering by severity/status/component
- User requesting more detail on a specific finding
- User marking findings as "already known" or "out of date"

### Gap 3: Verdict Presentation Format

No guidance on how to present a finding to a user for action (vs. how to present a finding to a user for validation of agent understanding). For example:

"Agent found: X violates requirement Y. Status: UNFIXABLE (U-REQ) because requirements Z and W contradict. **User action?** [fix myself] [mark as accepted] [escalate to designer]"

vs.

"User says: I want to change X. **Agent understanding?** 'You want to add Y to section Z. Correct?'"

These are structurally different interaction patterns.

### Gap 4: Completion Signaling

No pattern for when item-by-item review is "done":
- All items reviewed and verdict given? (terminal)
- All critical/major items resolved? (terminal)
- User says "done"? (terminal)
- Automatic checkpoints after N items? (monitoring)

### Gap 5: Rollback / Change of Mind

No pattern for user changing a verdict after moving forward:
- Can user un-defer an item?
- Can user request more detail on a closed finding?
- What's the UX for "I changed my mind on item 3"?

---

## Recommendations for Interactive Review Design

### 1. Build on /proof's Reword-Accumulate Protocol

/proof demonstrates effective turn-taking and decision accumulation. Interactive review could mirror this for agent-presented findings:
- **Present:** Agent displays one finding
- **Reword:** User provides verdict (accept, defer, escalate, more info)
- **Accumulate:** Track user decisions in-memory (D-1, D-2, ... for findings instead of changes)
- **Sync:** On request, show full accumulated verdict list
- **Terminal:** When all items have verdicts OR user says "apply verdicts"

### 2. Separate Finding Presentation from Understanding Validation

/proof validates user understanding of their own feedback. Interactive review validates agent understanding of its own findings:

**Agent Finding Presentation:**
```
Finding 1 of 18: CRITICAL
**Issue:** Method signature doesn't match spec
**Location:** app/auth.py:42
**Why:** Spec requires (user, force_refresh) but implementation has (user_id, refresh)
**Recommendation:** Rename parameters to match spec
**User action?** [Accept fix] [Defer] [More info] [Escalate] [Skip]
```

### 3. Use Flat Verdicts, Not Status Taxonomy

For user-driven verdicts, simpler vocabulary:
- **Accept:** User approves the fix recommendation
- **Defer:** Real issue but user wants to handle separately
- **Escalate:** Agent can't fix (design decision, requirement conflict)
- **More info:** User needs details before deciding
- **Skip:** User needs to think about this one

Map back to Status Taxonomy (FIXED/DEFERRED/UNFIXABLE) after completion.

### 4. Accumulate Before Applying

Like /proof, collect all user verdicts before making changes:
- User makes verdicts for all items (or subset)
- User requests "apply verdicts" or "apply and show summary"
- System applies fixes for "Accept" items
- System creates notes for "Defer/Escalate/Skip" items
- Return summary + report filepath

### 5. Integrate with Corrector Report

Output the item-by-item session results in the corrector report:
```markdown
## User-Guided Review Session

Date: [timestamp]
Items: 18 total

**Verdicts:**
- Accepted: 12 (5 critical, 7 major)
- Deferred: 3 (reasons: out of scope, design decision pending)
- Escalated: 2 (U-REQ, U-ARCH)
- Skipped: 1 (marked for follow-up)

**Fixes Applied:** [From Accept items]
**Deferred Items:** [From Defer items]
**Escalation:** [From Escalate items]
```

---

## References

### Skill/Agent Files

- `/Users/david/code/edify/plugin/skills/proof/SKILL.md` — Interactive artifact validation
- `/Users/david/code/edify/plugin/skills/deliverable-review/SKILL.md` — Two-layer production review
- `/Users/david/code/edify/plugin/skills/review-plan/SKILL.md` — Runbook quality validation
- `/Users/david/code/edify/plugin/agents/corrector.md` — Implementation review + fix-all
- `/Users/david/code/edify/plugin/agents/outline-corrector.md` — Outline review + fix-all
- `/Users/david/code/edify/plugin/agents/design-corrector.md` — Design review + fix-all
- `/Users/david/code/edify/plugin/agents/runbook-corrector.md` — Runbook review + fix-all

### Decision/Pattern Files

- `/Users/david/code/edify/agents/decisions/pipeline-review.md` — Review model selection, routing decisions
- `/Users/david/code/edify/agents/decisions/validation-quality.md` — Quality criteria definitions
- `/Users/david/code/edify/agents/session.md` — Workflow integration patterns, review scope markers

### Configuration

- `/Users/david/code/edify/.claude/tools.md` — Tool availability per context (AskUserQuestion listed)

---

## Metadata

**Explored Files:** 11 primary + 8 decision files + 2 configuration files
**Verdict Vocabulary Size:** 3 severity levels × 4 status categories + 3 unfixable subcodes
**Interactive Patterns Found:** 1 major (reword-accumulate-sync in /proof) + 5 minor (AskUserQuestion for scope/requirements)
**Item-by-Item Implementations:** 0 (gap identified)
