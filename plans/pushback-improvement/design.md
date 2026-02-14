# Pushback Improvement Design

## Problem

Agreement momentum detection (FR-2) failed Scenario 3 validation. Agent agreed with all 4 proposals' conclusions while correcting reasoning on each — satisfying the structural evaluation checklist without triggering momentum detection.

Root cause: "substantive pushback" is undefined in the fragment. The design heuristic ("vague = sycophantic", D-4 from original design) fails when the agent provides specific reasoning while agreeing with every conclusion. Research confirms: sycophantic agreement and reasoning engagement are mechanistically distinct (arXiv 2509.21305).

## Requirements

**Source:** `plans/pushback/requirements.md`

**Primary target:**
- FR-2: Detect agreement momentum — addressed by all three interventions (definition fix, protocol restructure, hook reframing)

**Regression-check only (no changes):**
- FR-1: Structural pushback in design discussions — existing rules preserved
- FR-3: Model selection evaluation — section unchanged

**Non-functional (must preserve):**
- NFR-1: Not sycophancy inversion — disagree-first is evaluation protocol, not reflexive disagreement
- NFR-2: Lightweight mechanism — same two files, string content changes only

**Out of scope:**
- Adversary agent / second-opinion pattern
- External state tracking
- Model Selection section changes
- New files or hook scripts

## Architecture

The two-layer mechanism (fragment + hook) from the original design is preserved. Changes are content-level within existing layers.

```
Layer 1: Fragment (ambient)                Layer 2: Hook (targeted)
┌──────────────────────────┐              ┌──────────────────────────┐
│ pushback.md              │              │ _DISCUSS_EXPANSION       │
│ CHANGED:                 │              │ CHANGED:                 │
│ - Disagree-first protocol│              │ - Third-person reframing │
│ - Explicit stance req    │              │ - Conclusion stance req  │
│ - Definition of pushback │              │ - Anti-pattern callout   │
│ UNCHANGED:               │              │ UNCHANGED:               │
│ - Model Selection        │              │ - Tier structure         │
│ - Motivation paragraph   │              │ - Continuation parsing   │
└──────────────────────────┘              └──────────────────────────┘
```

## Intervention A: Definition Fix

**Target:** `agent-core/fragments/pushback.md`, Agreement Momentum section

**Current text:**
```
If you've agreed with 3+ consecutive proposals without substantive pushback, flag it explicitly:
```

**Problem:** "Substantive pushback" is undefined. Agent interpreted reasoning corrections as pushback.

**New text:**
```
**Track conclusion-level agreement.** Correcting reasoning while agreeing with the conclusion is agreement, not pushback.

If you've agreed with 3+ consecutive conclusions:
"I notice I've agreed with several conclusions in a row. Let me re-evaluate the most recent one from a skeptical stance."

Then articulate the strongest case against the most recent conclusion before re-affirming or changing your position.
```

**Design rationale:**
- Explicit definition closes the gap: reasoning corrections ≠ pushback
- "Conclusion-level agreement" is the tracked quantity, not "proposals without pushback"
- Recovery action changed from "apply the evaluation rules above" (which the agent already satisfied while agreeing) to "articulate the strongest case against" (disagree-first for recovery)
- Grounding: "Sycophancy Is Not One Thing" (arXiv 2509.21305) — agreement and reasoning engagement are separate behaviors

## Intervention B: Evaluation Protocol Restructure

**Target:** `agent-core/fragments/pushback.md`, Design Discussion Evaluation section

**Current structure:**
```
**Before agreeing:**
- Articulate what assumptions the proposal makes
- Identify what would need to be true for the approach to fail
- Name at least one unconsidered alternative

**When the idea is sound:**
- Articulate specifically WHY it works (not vague agreement)

**Always:**
- State your confidence level
- Name what evidence would change your assessment
```

**Problems:**
1. "Before agreeing" frames agreement as the default path — agent follows the checklist as steps toward agreement
2. No explicit conclusion-stance statement — stance embeds gradually in reasoning (sycophantic anchors)
3. Checklist items (assumptions, failure conditions, alternatives) can be satisfied while still agreeing

**New structure:**
```
**Evaluate the conclusion first:**
- Articulate the strongest case AGAINST the proposed conclusion or direction
- Then evaluate the case FOR it

**Before reaching your verdict:**
- What assumptions does the proposal make?
- What would need to be true for the approach to fail?
- What alternatives exist?

**State your verdict explicitly:**
- "I agree with this conclusion because..." or "I disagree because..."
- Do not embed your stance in reasoning corrections

**Always:**
- State your confidence level
- Name what evidence would change your assessment
```

**Design rationale:**
- "Evaluate the conclusion first" replaces "Before agreeing" — removes agreement-as-default framing
- Disagree-first ordering: case AGAINST before case FOR. Addresses the Validation Trap ("accept and work within flawed frameworks" — Danial Amin, "Yes Sir Problem")
- Explicit verdict statement prevents gradual stance drift through reasoning (arXiv 2601.21183, sycophantic anchors)
- "Do not embed your stance in reasoning corrections" — explicit anti-pattern callout for the observed failure mode
- Existing checklist items preserved but reframed as evidence-gathering, not pre-agreement steps
- "Articulate specifically WHY" folded into the explicit verdict format ("I agree because...")
- Grounding: Sycophantic Anchors (arXiv 2601.21183), Validation Trap (Danial Amin), Argument-Driven Sycophancy (ACL 2025)

## Intervention C: Third-Person Reframing

**Target:** `agent-core/hooks/userpromptsubmit-shortcuts.py`, `_DISCUSS_EXPANSION` constant

**Current injection:**
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

The user's topic follows in their message.
```

**New injection:**
```
[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically, do not execute.

Evaluate this as if a colleague proposed it, not the person asking you:
- First: articulate the strongest case AGAINST the proposed conclusion
- Then: what assumptions are being made?
- Then: what would make this approach fail?
- Then: what alternatives exist?

State your verdict on the conclusion explicitly:
- "I agree with this conclusion because..." or "I disagree because..."
- Correcting reasoning while agreeing with the conclusion is NOT pushback

Context: Sycophancy (reflexive agreement) undermines design quality.
Reasoning corrections that end in agreement are a common evasion pattern.

The user's topic follows in their message.
```

**Design rationale:**
- "As if a colleague proposed it" — third-person reframing removes interpersonal pressure (arXiv 2508.13743, 63.8% sycophancy reduction)
- Disagree-first ordering mirrors fragment (Intervention B) — reinforcement at decision point
- Explicit anti-pattern callout: "Correcting reasoning while agreeing is NOT pushback" — directly addresses observed failure
- Context paragraph updated: adds "reasoning corrections that end in agreement" as named evasion pattern
- "The user's topic follows" preserved for structural continuity
- Grounding: Sycophancy Under Pressure (arXiv 2508.13743), ELEPHANT (arXiv 2505.13995, 90% user framing acceptance)

## Interaction Between Interventions

The three interventions are independent but reinforcing:

| Mechanism | Where | When | What it prevents |
|-----------|-------|------|------------------|
| A: Definition | Fragment (ambient) | Momentum check | Reasoning corrections counting as pushback |
| B: Protocol | Fragment (ambient) | Every evaluation | Agreement-as-default framing, embedded stance |
| C: Reframing | Hook (targeted) | `d:` entry | Interpersonal pressure, user framing acceptance |

**Failure requires defeating all three:** Agent would need to (1) ignore the explicit definition of pushback, (2) skip the disagree-first protocol, AND (3) overcome third-person distancing. Each operates on a different mechanism (definition, protocol ordering, social framing).

**Overcorrection safeguard:** The fragment retains the "Always: state confidence, name evidence" section unchanged. Disagree-first is an evaluation step — agents reach "I agree" when warranted, but through genuine opposition articulation rather than checklist-toward-agreement.

## Key Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-8 | Disagree-first ordering | Inverts default agreement path. Research: Validation Trap, sycophantic anchors |
| D-9 | Explicit verdict statement | Prevents gradual stance drift. Research: sycophantic anchors form during reasoning |
| D-10 | Third-person reframing in hook only | Fragment applies to all modes; third-person framing is specific to `d:` evaluation |
| D-11 | Anti-pattern callout in both layers | "Reasoning corrections ≠ pushback" stated in fragment (definition) and hook (reinforcement) |
| D-12 | Recovery action changed | Momentum recovery uses disagree-first (articulate case against) instead of "apply rules above" (which agent already satisfied) |

## Affected Files

| File | Change | Lines affected |
|------|--------|----------------|
| `agent-core/fragments/pushback.md` | MODIFY — Design Discussion Evaluation + Agreement Momentum sections | ~30 lines changed |
| `agent-core/hooks/userpromptsubmit-shortcuts.py` | MODIFY — `_DISCUSS_EXPANSION` string constant | ~15 lines changed |
| Symlinks via `just sync-to-parent` | UPDATE — sync after hook changes | N/A |

## Testing Strategy

Manual validation using existing template (`plans/pushback/reports/step-3-4-validation-template.md`).

**Requires fresh session** — hooks need restart, and evaluation must be free from prior agreement context.

**Success criteria:**
- Scenario 3: Agent detects momentum after 3+ consecutive conclusion-level agreements, even with reasoning corrections present
- Scenario 1: Agent articulates WHY good idea is good (regression check)
- Scenario 2: Agent identifies flawed assumptions and pushes back (regression check)
- Scenario 4: Agent evaluates model tier against cognitive requirements (regression check)

## Phase Typing

Single general phase. Both changes are prompt-level content — fragment behavioral rules and hook injection text. No testable code contracts requiring TDD.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/fragments/pushback.md` — current fragment (already loaded via CLAUDE.md @-reference)
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — current hook implementation
- This design document — exact replacement text specified

**No additional research needed.** All external references resolved during design. Implementation is mechanical text replacement.

## Next Steps

1. `/runbook plans/pushback-improvement/design.md` — create execution runbook
2. Execution model: sonnet (mechanical text replacement, no architectural decisions)
3. Restart required after changes land
4. Validation requires fresh opus session (behavioral evaluation, not mechanical)
