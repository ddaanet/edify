---
name: requirements
description: >-
  Capture and document requirements for implementation. Triggers on "capture
  requirements", "document requirements", "what do I want to build", or feature
  discussions without clear documentation. Produces requirements.md artifact
  for design and planning phases.
allowed-tools: Read, Write, Edit, Bash, Skill
user-invocable: true
---

# Capture Requirements

Dual-mode requirements capture: extract from conversation or elicit through
semi-structured questions. Produces `plans/<job>/requirements.md` artifact
consumed by `/design` and `/runbook`.

## Usage

```
/requirements <job-name>
```

Detect the mode from conversation history (see §Mode Detection).

## Mode Detection

**Primary signal:** `test -f plans/<job>/requirements.md` — if it exists, Read
it and use as base for update/refinement (extract mode with existing artifact).
If absent, fall through to conversation heuristic.

**Conversation heuristic (fallback):**
- **Extract mode** — conversation contains substantive discussion (feature
  descriptions, constraints, scope)
- **Elicit mode** — fresh conversation or minimal context (no prior feature
  discussion, cold-start)

**STOP and report to the user when:**
- **No job name given.** `plans/<job>/` cannot be derived. Ask for one.
- **Extract mode with no substantive conversation to extract from.** Mode
  detection misfired. Switch to elicit mode rather than inventing requirements
  from an empty transcript.

## Recall Pass

**Runs after mode detection, before either procedure.** Ground extraction in
existing infrastructure, patterns, and decisions — prevents naive requirements.

### Process

Invoke
`Skill(skill: "edify:recall", args: "<topic derived from job name and conversation>")`.

**Gate anchor:** No plan-dir argument: this skill *creates* the artifact, so
there is none to resolve. The artifact **write** is the structural anchor — a
tool call that fires whether or not anything relevant turns up.

**Boundaries:**
- No agent delegation, no Context7, no web research — those belong to /design
  A.1
- Purpose: ground the extraction, not exhaustive documentation loading

### Recall Artifact

Read `references/formats-and-exit.md` now — read it once, here, on every run. It
carries the recall artifact's shape and its null form, the gap-fill question
template step 4 asks for, the `requirements.md` format step 3 writes by, the
skill-dependency table and the exit routing step 6 uses, and the STOP conditions
that abort before an artifact exists.

Write `plans/<job>/recall-artifact.md` by it, with the null entry when nothing
relevant turned up.

## Extract Mode Procedure

When conversation contains requirements signals:

### 1. Scan Conversation

Read `plans/<job>/requirements.md` if it exists, then extract from history:
- **Functional requirements:** What should the system do?
- **Non-functional requirements:** Performance, usability, constraints
- **Explicit constraints:** Technology, compatibility, architecture
- **Scope boundaries:** What's in vs out of scope
- **Dependencies:** Blocking work, prerequisites
- **Open questions:** Unresolved items mentioned

**Critical rule:** Extract from what was said, do NOT infer unstated
requirements. Hallucination risk — if not discussed, flag as Open Question
rather than inventing. Basis: `references/empirical-grounding.md` §Hallucination
Risk and §AI Weaknesses.

### 2. Lightweight Codebase Discovery

Quick scan to ground requirements (runs after extraction, so scan is targeted):

**Discovery actions** (guideline: ~5 tool calls, flexible based on complexity):
1. `rg --files` (Bash) for `plans/*/requirements.md` and `plans/*/design.md` —
   find related work
2. `rg` (Bash) for key terms from extracted requirements — check what exists
3. `Read` existing patterns in relevant area — inform constraints

**Boundaries:**
- Direct tool use only (Read, Write, Bash (`rg`, `rg --files`, `test -f`))
- No agent delegation
- No Context7, no web research, no scout
- Purpose: prevent naive requirements (e.g., "add X" when X exists)
- Tool count is a guideline, not a hard limit — use judgment for complex domains
- Save exploration prototypes to `plans/prototypes/` (not `tmp/`) — they are
  referenced artifacts, not ephemera

### 2.5 Post-Explore Recall Gate

Discovery via `rg --files`/`rg` (Bash) may surface domains not anticipated
during the initial recall pass. Run the recall procedure already loaded in
§Recall Pass inline, with no topic — do not issue a second `Skill` call.

**Gate anchor (D+B — tool call required):**
- **New entries found:** add the paths recall selected to the recall artifact —
  recall has already Read the bodies
- **No new entries:** state that explicitly in the response — the gate was
  reached and yielded nothing

### 3. Structure Requirements

Format the extracted items by §Standard Format in
`references/formats-and-exit.md`, already read at the recall pass:
- Number items sequentially within each section (FR-1, FR-2, ...)
- Include acceptance criteria for functional requirements
- Capture rationale for constraints
- Omit empty sections entirely

### 4. Gap Detection

Read the structured draft, then check for empty critical sections:

**Critical sections** (ask if empty):
- Functional Requirements — "What should the system do?"
- Out of Scope — "What should it NOT do?"

**Non-critical sections** (note absence, don't ask):
- NFRs, Constraints, Dependencies — many tasks genuinely have none

**Question budget (applies to both Extract and Elicit modes):**
- Extract mode: Maximum 3 gap-fill questions for empty critical sections
- Elicit mode: 4-6 total questions (section questions + adaptive follow-ups)

Ask gap-fill questions by §Gap-Fill Questions in
`references/formats-and-exit.md` — numbered prose in a single turn, each
question carrying a proposed answer.

Never reach for `AskUserQuestion`. A picker hides the exchange from the
transcript, so the requirements artifact ends up with no readable record of how
its content was settled — and the option list silently bounds what the user can
say, which is the opposite of elicitation. Numbered prose keeps both the
question and the user's own words in the thread, and a stated default lets the
turn proceed without a round-trip.

### 5. Write the Draft and Validate

Write the draft to `plans/<job>/requirements.md` (create the directory if
needed) — where that file already exists and the draft records a narrower scope
than it does, confirm the overwrite with the user before writing, since
requirements loss is silent downstream. Then invoke
`/edify:proof plans/<job>/requirements.md` — a structured reword-accumulate-sync
loop on it. Present the artifact path, summarize the sections populated, note
Open Questions.

/proof runs the iterative validation loop. No corrector dispatch for
requirements (user-validated directly). On terminal action "apply", accumulated
decisions are applied to the artifact.

### 6. Finalise

After /proof applies the accumulated decisions, by
`references/formats-and-exit.md`:
- Confirm the artifact on disk matches the validated state
- Scan for skill dependencies (§Skill Dependency Scanning)
- Suggest the next step (§Default Exit)

## Elicit Mode Procedure

**When mode detection lands on elicit:** Read `references/elicit-mode.md` and
run its elicitation round, then rejoin Extract mode above at steps 2, 2.5 and
3-6. Extract mode never reads it.
