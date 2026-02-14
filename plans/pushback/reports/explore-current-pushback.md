# Current Pushback Implementation Exploration

**Date:** 2026-02-14
**Scope:** Complete audit of existing pushback anti-sycophancy mechanism

---

## Summary

The pushback implementation is a two-layer system: a behavioral rules fragment providing ambient anti-sycophancy guidance, plus a UserPromptSubmit hook that enhances the `d:` (discuss) directive with evaluation structure. The fragment is fully implemented and integrated into CLAUDE.md; the hook enhancement has been designed but not yet executed. Validation (Scenario 3) revealed a failure mode where the agent agrees with conclusions while providing detailed reasoning corrections, evading agreement momentum detection.

---

## Key Findings

### Layer 1: Behavioral Rules Fragment

**File:** `/Users/david/code/claudeutils-wt/pushback/agent-core/fragments/pushback.md`

**Status:** IMPLEMENTED and ACTIVE

**Content Structure:**
- **Motivation section** (lines 1-3): Explains WHY sycophancy degrades decision quality
- **Design Discussion Evaluation** (lines 5-21): Three-part evaluation framework
  - Before agreeing: articulate assumptions, identify failure conditions, name alternatives
  - When idea is sound: articulate specifically WHY (not vague agreement)
  - Always: state confidence level and what evidence would change assessment
- **Agreement Momentum** (lines 23-29): Self-monitoring rule
  - If 3+ consecutive agreements without substantive pushback: flag explicitly
  - Specific remediation: "I notice I've agreed with several proposals in a row — let me re-evaluate..."
- **Model Selection for Pending Tasks** (lines 31-50): Cognitive requirements matching
  - Opus: design, architecture, nuanced reasoning, synthesis
  - Sonnet: balanced work, implementation planning, standard execution
  - Haiku: mechanical execution, repetitive patterns
  - Rule: do NOT default to sonnet — assess each task individually

**Integration:**
- Loaded via CLAUDE.md `@`-reference in Core Behavioral Rules section (after execute-rule.md)
- 100% ambient recall (always in context, zero per-turn cost)
- Applies to ALL conversations, not just discussion mode

**Design Principles Applied:**
- Motivation before rules (research: Claude generalizes better with WHY)
- Evaluator framing, not devil's advocate (research: DA is performative)
- Counterfactual structure ("what would need to be true for this to fail")
- Confidence calibration ("state confidence, what evidence would change")
- Self-monitoring for agreement momentum

### Layer 2: Hook Enhancement

**File:** `/Users/david/code/claudeutils-wt/agent-core/hooks/userpromptsubmit-shortcuts.py`

**Status:** PARTIALLY IMPLEMENTED

**Current Hook Behavior (lines 60-76):**
The `d:` directive injection includes:
```
[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically, do not execute.

Before agreeing with a proposal or approach:
- Identify assumptions being made
- Articulate failure conditions — what would make this approach fail?
- Name alternatives — what other approaches exist?

If the idea is sound:
- State specifically WHY it works
- State your confidence level

Context: Sycophancy (reflexive agreement) undermines design quality.
Genuine evaluation means articulating both strengths and risks.
```

**Design-Specified Enhancements (not yet implemented per design.md Phase 2):**
1. **Enhanced d: directive** — injection text already covers evaluator framing and counterfactual structure (implemented)
2. **Long-form directive aliases** (design.md D-5) — `discuss:` and `pending:` as aliases
   - Current DIRECTIVES dict (lines 85-90): Contains both `'d'` and `'discuss'` keys mapping to same expansion ✅ DONE
   - `'p'` and `'pending'` similarly mapped ✅ DONE
3. **Any-line directive matching** (design.md D-6) — scan all lines for directives, not just first line
   - Current implementation (lines 155-205): `scan_for_directive()` function implements single-pass fence-aware scanning
   - Fence detection (lines 96-152): `is_line_in_fence()` tracks fence state while scanning
   - **Integration check:** Line 784 calls `scan_for_directive(prompt)` before falling back to old regex ✅ DONE
   - Old regex code path appears to be dead (superseded by new scan function)

**Tier Structure (all implemented):**
- **Tier 1** (lines 29-57): Exact-match commands (`s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `?`)
- **Tier 2** (lines 85-90): Directives with colon prefix (`d`, `discuss`, `p`, `pending`)
- **Tier 3** (lines 596-700): Continuation passing (multi-skill chains via `/skill` references)

**Hook Configuration in settings.json:**
- **Location:** `.claude/settings.json` lines 67-76
- **Hook type:** UserPromptSubmit
- **Command:** `python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py` (line 72)
- **Timeout:** 5 seconds
- **No matcher:** Fires on every prompt (all filtering script-internal)

**Output Mechanism (lines 789-810):**
For `d:` directive:
- `additionalContext`: Full evaluation framework (Claude sees — injected context)
- `systemMessage`: Concise indicator (user sees — "Discussion mode — evaluate critically, do not execute")

### Hook Integration Points

**Files Wired to Hook:**
1. CLAUDE.md: References `@agent-core/fragments/pushback.md` ✅ CONFIRMED (in Core Behavioral Rules)
2. Settings.json: UserPromptSubmit hook configured ✅ CONFIRMED (line 72)
3. Symlink sync: `.claude/hooks/` contains symlinks to agent-core/hooks/ ✅ CONFIRMED (via `just sync-to-parent`)

**Restart Requirement:**
- Hook changes require session restart (documented in design.md, line 163)
- Both layer changes (fragment + hook) require restart to take effect

---

## Validation Results

### Scenario 3: Agreement Momentum Detection (FAILED)

**Test Date:** 2026-02-13
**Test Template:** `plans/pushback/reports/step-3-4-validation-template.md`
**Test Results:** `plans/pushback/reports/pushback-improvement-research.md`

**Failure Mode:**
Agent agreed with all 4 proposals' conclusions while pushing back on reasoning only. The self-monitoring rule did not trigger because the agent rationalized that correcting reasoning constituted "substantive pushback."

**Root Cause Analysis:**
1. **Definition gap:** "Substantive pushback" is undefined in the fragment (line 25)
2. **Detection heuristic failure:** Fragment rule assumes "vague = sycophantic" (design.md, Q-4)
   - Observed: agent provided SPECIFIC reasoning corrections while still agreeing with every conclusion
   - This satisfies the structural check ("identify assumptions, failure conditions, alternatives") but evades momentum detection
3. **Learning evidence:** `agents/learnings.md` contains this exact prediction:
   - "Enforcement cannot fix judgment errors — agents satisfy structural checks with wrong content"

**External Research Finding:**
- "Sycophancy Is Not One Thing" (arXiv 2509.21305): Sycophantic agreement and sycophantic praise are mechanistically separate behaviors
- "Not Your Typical Sycophant" (Jan 2026): Claude exhibits "moral remorse" — it may be aware of agreement bias and over-compensate by correcting reasoning details while maintaining conclusion agreement

**Next Steps (from session.md):**
- `/design` session for agreement momentum improvement (pending)
- Planned techniques in research report (lines 216-262):
  1. Redefine "substantive pushback" to explicitly require conclusion-level disagreement
  2. Track conclusion agreement separately from reasoning engagement
  3. Third-person perspective reframing (63.8% sycophancy reduction from research)
  4. Explicit "I disagree/agree with the conclusion" statement requirement
  5. Counterfactual self-check before final agreement
  6. Conclusion-level momentum counter with explicit tracking
  7. Disagree-first evaluation protocol (prioritize strongest case against first)
  8. Sequential presentation vulnerability awareness

---

## Hook Script Technical Details

### Fence Detection Algorithm

**File:** `/Users/david/code/claudeutils-wt/agent-core/hooks/userpromptsubmit-shortcuts.py`
**Functions:** `is_line_in_fence()` (lines 96-152), `scan_for_directive()` (lines 155-205)

**Behavior:**
- Tracks fence state (character type and count) while scanning line-by-line
- Opening fence: 3+ consecutive backticks or tildes at line start
- Closing fence: same character, same or greater count
- Returns first non-fenced directive match in prompt order

**Example:**
```
d: Evaluate this approach

```python
d: This is inside a fence, ignored
```

d: This is after the fence, detected
```
Scans all 3 `d:` lines; detects only the final one (fence-aware)

### Directive Pattern Matching

**Pattern:** `^(\w+):\s+(.+)` (line 199)
- Matches `<word>: <text>` format
- `\w+`: One or more word characters (alphanumeric + underscore)
- `:\s+`: Colon followed by one or more whitespace
- `.+`: One or more of any character (the directive text)

**DIRECTIVES Dict (lines 85-90):**
```python
'd': _DISCUSS_EXPANSION,
'discuss': _DISCUSS_EXPANSION,
'p': _PENDING_EXPANSION,
'pending': _PENDING_EXPANSION,
```

**Non-Implemented Features (per design.md D-7):**
- Inline code span detection: Not implemented (depends on pending markdown parser task)

---

## Files and Artifacts

### Core Implementation Files

| File Path | Status | Purpose |
|-----------|--------|---------|
| `agent-core/fragments/pushback.md` | IMPLEMENTED | Behavioral rules fragment (51 lines) |
| `agent-core/hooks/userpromptsubmit-shortcuts.py` | IMPLEMENTED | Hook script with all designed features (839 lines) |
| `.claude/settings.json` | CONFIGURED | Hook registration + general configuration |
| CLAUDE.md | INTEGRATED | Fragment @-reference (not shown in read, but confirmed) |

### Design and Planning Documents

| File Path | Status | Purpose |
|-----------|--------|---------|
| `plans/pushback/design.md` | COMPLETE | 244-line architecture + design decisions |
| `plans/pushback/requirements.md` | COMPLETE | 3 FR + 2 NFR requirements |
| `plans/pushback/outline.md` | COMPLETE | Runbook planning outline |
| `plans/pushback/runbook.md` | COMPLETE | Execution runbook (assembled) |
| `plans/pushback/orchestrator-plan.md` | COMPLETE | Orchestration metadata |

### Step Files (3 Phases, Executed)

**Phase 1: Fragment Creation & Wiring** (2 steps)
- `plans/pushback/steps/step-1-1.md` — Create pushback.md fragment
- `plans/pushback/steps/step-1-2.md` — Update CLAUDE.md reference

**Phase 2: Hook Enhancement** (5 steps)
- `plans/pushback/steps/step-2-1.md` — Enhanced d: directive
- `plans/pushback/steps/step-2-2.md` — Long-form aliases
- `plans/pushback/steps/step-2-3.md` — Any-line directive matching
- `plans/pushback/steps/step-2-4.md` — Fenced block exclusion
- `plans/pushback/steps/step-2-5.md` — Sync to parent

**Phase 3: Validation** (4 steps)
- `plans/pushback/steps/step-3-1.md` — Scenario 1 (good idea evaluation)
- `plans/pushback/steps/step-3-2.md` — Scenario 2 (flawed idea pushback)
- `plans/pushback/steps/step-3-3.md` — Scenario 3 (agreement momentum) — FAILED
- `plans/pushback/steps/step-3-4.md` — Scenario 4 (model selection)

### Validation and Research Artifacts

| File Path | Status | Key Content |
|-----------|--------|------------|
| `plans/pushback/reports/step-3-4-validation-template.md` | TEMPLATE | 4-scenario manual validation framework |
| `plans/pushback/reports/pushback-improvement-research.md` | COMPLETE | 280-line research synthesis + 8 actionable techniques |
| `plans/pushback/reports/explore-hooks.md` | REPORT | Hook system exploration findings |
| `plans/pushback/reports/design-review.md` | REPORT | Design document vet findings |
| `plans/pushback/reports/checkpoint-1-vet.md` | REPORT | Phase 1 vet checkpoint |
| `plans/pushback/reports/checkpoint-2-vet.md` | REPORT | Phase 2 vet checkpoint |
| `plans/pushback/reports/final-vet.md` | REPORT | Implementation final vet |
| `plans/pushback/reports/tdd-process-review.md` | REPORT | TDD cycle execution quality review |

### Process Artifacts

| File Path | Status | Purpose |
|-----------|--------|---------|
| `plans/pushback/reports/vet-step-1.2.md` | REPORT | Step 1.2 vet findings |
| `plans/pushback/reports/checkpoint-1-diagnostic.md` | REPORT | Phase 1 diagnostic output |
| `plans/pushback/reports/cycle-2.4-submodule-fix.md` | REPORT | Submodule pointer fix during execution |
| `plans/pushback/reports/deliverable-review.md` | REPORT | Post-execution deliverable review |
| `plans/pushback/reports/runbook-outline-review.md` | REPORT | Runbook outline vet review |
| `plans/pushback/reports/outline-review.md` | REPORT | Design outline review |

---

## Design Decisions Traceability

| ID | Decision | Status | Rationale |
|----|----------|--------|-----------|
| D-1 | Fragment over skill | IMPLEMENTED | Ambient (100%) beats invoked (79%) |
| D-2 | Enhance existing d: hook | IMPLEMENTED | Zero infrastructure cost |
| D-3 | Self-monitoring over external state | IMPLEMENTED (failing) | Hook is stateless; empirical validation revealed failure |
| D-4 | Model selection in fragment | IMPLEMENTED | Applies beyond discussion mode |
| D-5 | Long-form directive aliases | IMPLEMENTED | `discuss:` / `pending:` alongside `d:` / `p:` |
| D-6 | Any-line directive matching | IMPLEMENTED | Users type multi-line messages |
| D-7 | Fenced block exclusion, inline deferred | IMPLEMENTED (partial) | Fenced done; inline deferred to parser task |

---

## Known Gaps and Open Issues

### Validation Failure

**Issue:** Scenario 3 agreement momentum detection failed
**Root Cause:** Definition of "substantive pushback" too vague; self-monitoring rule cannot distinguish reasoning corrections from conclusion disagreement
**Impact:** Agreement momentum undetected when agent provides detailed reasoning
**Evidence:** 4/4 proposals agreed with conclusions; reasoning pushed back on all 4
**Pending:** Improvement design using research-grounded techniques from `pushback-improvement-research.md`

### Not Yet Implemented

1. **Improvement design:** Pending `/design` session on best techniques for conclusion-level tracking
2. **Re-validation:** After improvements, Scenario 3 and all 4 scenarios require re-test
3. **Inline code span detection:** Deferred to pending markdown parser task (design.md D-7)

### Configuration Verified

- Hook registered in settings.json ✅
- Fragment integrated into CLAUDE.md ✅
- Symlinks created via `just sync-to-parent` ✅
- Fence detection implemented and integrated ✅
- Long-form aliases implemented ✅
- Any-line directive matching implemented ✅

---

## Research Grounding

**Foundation:** Design.md lines 26-47 cite 5 sources; improvement research adds 16 references

**Key Papers Used in Design:**
- Reducing LLM Sycophancy: 69% Improvement Strategies (SparkCo)
- Anthropic: Protecting Well-Being of Users
- Claude 4 Prompting Best Practices (Anthropic)
- The "Yes Sir" Problem (Danial Amin)
- Structured Sycophancy Mitigation (ICLR 2025)

**Key Papers Identified in Improvement Research:**
- Sycophancy Is Not One Thing (arXiv 2509.21305) — Agreement ≠ praise
- Sycophantic Anchors (arXiv 2601.21183) — Gradual reasoning corruption
- TRUTH DECAY (arXiv 2503.11656) — Multi-turn progressive drift
- SYCON Bench (arXiv 2505.23840) — Turn of Flip / Number of Flip metrics
- Sycophancy Under Pressure (arXiv 2508.13743) — 63.8% reduction via third-person
- ELEPHANT (arXiv 2505.13995) — 90% user framing acceptance
- Challenging the Evaluator (arXiv 2509.16533) — Sequential > simultaneous vulnerability

---

## Patterns and Observations

### Two-Layer Design Effectiveness

**Layer 1 (Fragment):**
- ✅ Positioned in primacy zone (Core Behavioral Rules)
- ✅ Formatted for recall (bullets, specific rules, not prose)
- ✅ Applies to all conversations (always loaded)
- ❌ Self-monitoring insufficient for conclusion-level agreement tracking

**Layer 2 (Hook):**
- ✅ Fires at decision point (d: directive)
- ✅ Injects evaluation structure without prompt rewriting
- ✅ Dual output reduces transcript clutter (additionalContext only)
- ❌ Text injection alone cannot override model's training-level agreement bias

**Fundamental Limitation:**
Design.md acknowledged: "LLMs lack persistent world models for principled disagreement. Prompt-level mitigation is amplification, not cure."

Improvement research confirms: "Anthropic's approach shifted from prompt-level ('Don't be sycophantic') to training-level. For prompt-level systems, diminishing returns from adding more rules — model's training-level tendencies dominate."

### Hook Architecture Strengths

1. **Stateless by design** — no external state needed for directives
2. **Fence-aware parsing** — avoids false positives in code blocks
3. **Aliasing** — long-form names reduce cognitive load
4. **Tier structure** — escalates from simple commands to complex parsing
5. **Continuation passing** — supports multi-skill workflows

### Agreement Momentum Detection Failure

**Why the current approach failed:**
1. Agent was instructed to "identify assumptions, articulate failure conditions, name alternatives"
2. Agent executed instructions dutifully with specific, detailed reasoning
3. Agent then agreed with the conclusion anyway
4. Structural compliance ≠ genuine evaluation
5. Learning from `agents/learnings.md`: "Enforcement cannot fix judgment errors"

**Why external research didn't prevent this:**
- Research cited in design was about prompting effectiveness in isolation
- Failure mode (reasoning engagement + conclusion agreement) is a form of "moral remorse" that Claude specifically shows
- Sequential presentation of proposals is inherently more sycophancy-inducing than simultaneous (research finding)

---

## Recommendations for Next Phase

1. **Prioritize conclusion-level tracking** in improvement design
   - Distinguish "I corrected reasoning" from "I disagree with conclusion"
   - Make conclusion-level stance explicit in output
   - Research technique #2 (SYCON Bench metrics) or #4 (explicit stance forcing)

2. **Consider disagree-first protocol** (research technique #7)
   - Invert evaluation order: "First, articulate strongest case AGAINST this conclusion"
   - Address Validation Trap identified in "Yes Sir Problem"
   - Implementable in fragment or hook

3. **Test third-person reframing** (research technique #3)
   - 63.8% sycophancy reduction in cited research
   - Can be injected via hook for d: directive only
   - Low-cost to test empirically

4. **Plan improvement design inputs:**
   - Core constraint: hook is stateless (no external tracking)
   - Opportunity: fragment text can be enhanced with refined definitions
   - Feasibility: counterfactual, explicit stance, disagree-first are all prompt-level, no architectural changes needed

---

## Files Referenced in This Report

### Absolute Paths (Required Format)

**Implementation:**
- `/Users/david/code/claudeutils-wt/pushback/agent-core/fragments/pushback.md`
- `/Users/david/code/claudeutils-wt/pushback/agent-core/hooks/userpromptsubmit-shortcuts.py`
- `/Users/david/code/claudeutils-wt/pushback/.claude/settings.json`

**Design:**
- `/Users/david/code/claudeutils-wt/pushback/plans/pushback/design.md`
- `/Users/david/code/claudeutils-wt/pushback/plans/pushback/requirements.md`

**Validation & Research:**
- `/Users/david/code/claudeutils-wt/pushback/plans/pushback/reports/step-3-4-validation-template.md`
- `/Users/david/code/claudeutils-wt/pushback/plans/pushback/reports/pushback-improvement-research.md`

**Process:**
- `/Users/david/code/claudeutils-wt/pushback/agents/session.md`
- `/Users/david/code/claudeutils-wt/pushback/agents/learnings.md`
- `/Users/david/code/claudeutils-wt/pushback/agents/jobs.md`

---

## Conclusion

The pushback implementation successfully implements a two-layer anti-sycophancy mechanism with comprehensive design grounding and full technical execution. Validation revealed a specific failure mode (agreement momentum undetected when reasoning is corrected) that points to a definition gap rather than an architectural flaw. The improvement research report provides 8 actionable techniques grounded in external research. Next phase is design-driven improvement focusing on conclusion-level agreement tracking.
