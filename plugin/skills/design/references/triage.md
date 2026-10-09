# Triage

Read when Phase 0's artifact check falls through to "classify below" — no
`design.md` and no `outline.md` to resume from. A resumed job skips this node
entirely: its classification was taken when the artifact was first written.

Work through the sections in order, then return to §Routing in the skill body
with the filled-in classification block in hand.

## Classification Criteria

Assess two axes (Stacey Matrix-grounded), then classify. Classify only — do not
route yet.

**Axes:**
1. **Implementation certainty** — is the approach known? Prior art in codebase?
   Known technique?
2. **Requirement stability** — are FRs agreed and mechanism-specified? Scope
   bounded?

**Complex:** Either axis low. Architectural decisions with multiple valid
approaches, uncertain or evolving requirements, significant codebase impact.

**Moderate:** Both axes moderate-to-high. Clear requirements, no architectural
uncertainty, well-defined scope. Behavioral code changes: new functions, changed
logic paths, conditional branches.

**Simple:** Both axes high. Single file, obvious implementation, no
architectural decisions. **No behavioral code changes** — new functions, changed
logic paths, conditional branches are Moderate regardless of conceptual
simplicity.

**Defect:** Observed behavior ≠ expected behavior. Route to structured-bugfix
regardless of apparent complexity — the investigation structure replaces
architectural design. Cynefin Complicated domain: cause analyzable, fix
knowable, but analysis must be structured to prevent premature-closure bias.

## Work Type Assessment

Assess work type alongside complexity — independent dimension (XP spike/story,
Boehm throwaway/evolutionary). Work type determines execution ceremony (quality
obligations); complexity determines design ceremony.

| Work Type | Diagnostic Question | Deliverable | Done Criteria |
|-----------|-------------------|-------------|---------------|
| **Production** | Does this deliver capability to users/agents? | Working feature, behavior change | Tested, linted, reviewed, integrated |
| **Exploration** | Does this produce knowledge or validate an approach? | Prototype, spike, feasibility answer | Functional, produces intended learning |
| **Investigation** | Does this produce a decision or analysis? | Report, decision entry, requirements | Accurate, complete, actionable |

**Assessment signals:**
- Explicit constraints: "prototype first," "spike," "investigate," "explore"
- Artifact destination: `plans/prototypes/` → Exploration, `plans/reports/` →
  Investigation, `src/` → Production
- Requirement framing: "can we...?" → Exploration, "build X" → Production, "what
  is...?" → Investigation
- If ambiguous, default to Production (highest ceremony — safe default)

**Artifact destination** informs quality obligations (Boehm throwaway vs
evolutionary prototype distinction):

| Destination | Paths | Quality Obligations |
|------------|-------|-------------------|
| **production** | `src/`, `plugin/bin/`, `plugin/lib/` | Tests, lint, module structure, review |
| **agentic-prose** | `plugin/skills/`, `plugin/fragments/`, `plugin/agents/`, `agents/` | Wording quality, behavioral verification |
| **exploration** | `plans/prototypes/`, `plans/spikes/` | Functional, documented purpose, no test mirrors |
| **investigation** | `plans/reports/`, `docs/design.md` | Accuracy, completeness, grounding |
| **ephemeral** | `tmp/` | None |

## Multi-Item Decomposition

**Before classifying**, check both triggers. Either one means this invocation
covers more than one work item:

- **Implicit bundling** — the input artifact contains multiple discrete items
  (deliverable review findings, PR review comments, multi-FR implementation
  list).
- **Explicit bundling** — the task frame or session notes fold additional work
  into this invocation ("address X during /design").

Both triggers run the same procedure — the source of the item list does not
change how the items are handled:

1. Enumerate all discrete items explicitly, naming the trigger for each
2. Produce a per-item behavioral code check (does this item add functions,
   change logic paths, or add conditional branches?)
3. Classify each item individually, with its own visible output block
   (Requirements-clarity → Triage Recall → Classification) — any behavioral item
   elevates to Moderate minimum for that item
4. Only after every item is classified, route: Simple items can batch, Moderate+
   items get their own routing

**Why:** Batch classification averages heterogeneous items — a behavioral change
gets masked by non-behavioral siblings. The enumeration is the structural
anchor: it forces explicit acknowledgment of each item rather than silently
merging them into the primary task's classification.

## Classification Gate

**Structural check (D+B anchor):** If classification is borderline
Simple/Moderate, verify with `rg --files` or `rg` (Bash) on affected files to
confirm whether behavioral code changes are involved (new functions, changed
logic paths).

Produce this classification block before routing (visible output, not internal
reasoning — **per-item if composite**). A single-item job's block opens with the
job-level line. A composite job puts one job-level
`- **Classification:** <label>` line ahead of its blocks, one block per item:
- **Classification:** <label> — exactly one of `Simple`, `Moderate`, `Complex`
  or `Defect`, with nothing after it
- **Implementation certainty:** [High / Moderate / Low] — is approach known?
- **Requirement stability:** [High / Moderate / Low] — are FRs
  mechanism-specified?
- **Behavioral code check:** Does this task add functions, change logic paths,
  or add conditional branches? [Yes → Moderate minimum / No]
- **Work type:** [Production / Exploration / Investigation] — what does this
  deliver?
- **Artifact destination:** [production / agentic-prose / exploration /
  investigation / ephemeral]
- **Evidence:** Which criteria and recall entries informed the decision

**Classification persistence:** Write the filled-in block or blocks to
`plans/<job>/classification.md`. Write one job-level
`- **Classification:** <label>` line, at the start of its line, before any
per-item block, so that no other `Classification:` line, bulleted or bare, can
precede it; a heading or prose may come before it. Write `<label>` as exactly
`Simple`, `Moderate`, `Complex` or `Defect`, with nothing after it:
`triage-feedback.sh` reads the file's first `Classification:` line, and any
other value gives `no-classification`, so the job's row is lost to calibration.
A composite job's label is its most demanding item's class, in the order Simple
< Moderate < Complex, because triage measures the whole run's evidence against
that one label. In a mixed job a Defect item ranks as Moderate: Defect names the
bugfix route, not a size, and a defect fix changes a logic path, Moderate's
mark. `Defect` is the job-level label only when every item is a Defect, since
then the whole job takes that route. This ordering is ungrounded: no calibration
data backs it.
