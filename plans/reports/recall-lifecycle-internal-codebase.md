# Recall Artifact Lifecycle: Internal Codebase Inventory

**Date:** 2026-02-28
**Scope:** Inventory of `recall-artifact.md` handling across pipeline skills, consumer-specific artifact patterns, and shared artifact lifecycle across pipeline stages.

---

## Executive Summary

`recall-artifact.md` is a transient, curated trigger-phrase index created at design time and consumed across planning and execution stages. The lifecycle demonstrates a **progressive augmentation** pattern: initial creation at `/design` A.1 → augmentation at `/runbook` Phase 0.5 → selective curation for specific consumer types at execution time. Consumer-specific artifacts (`tdd-recall-artifact.md`, `corrector-recall-artifact.md`, `skill-review-recall-artifact.md`) represent a parallel pattern where the parent session curates context before delegating to sub-agents (context isolation principle).

The pipeline uses **three distinct shared artifact types** with overlapping lifecycles:
1. **recall-artifact.md** — pipeline-wide trigger index (decision keys only)
2. **classification.md** — execution classification checkpoint (work-type, tier, artifact destination)
3. **outline.md / design.md** — architectural specification (refined across A.1→A.5→C.1 in design)

Each artifact serves a specific gate and is consumed by specific downstream stages.

---

## 1. Per-Skill Recall Artifact Handling

### 1.1 `/requirements` Skill

**File:** `/Users/david/code/edify/plugin/skills/requirements/SKILL.md`

**Artifact Role:** CREATES initial `recall-artifact.md`

**Reference Location:** Lines 32-64

**Process:**
- **Trigger:** Lines 32-40 — "Recall Pass" section describes `/recall all` invocation for grounding extraction
- **Creation:** Lines 44-63 — "Recall Artifact" format specifies trigger-phrase-only entries (no summaries, 1-line relevance notes)
- **Format rule:** Lines 50-59 — Standard format with entry keys and relevance notes
- **Selection criteria:** Lines 61-62 — Include entries that "informed requirements or constrain implementation"; exclude read-but-irrelevant entries
- **Output location:** Line 63 — `plans/<job>/recall-artifact.md`

**Consumption Mode:** Broad + topic-scoped — `/recall all` protocol (deep + broad per plugin/skills/recall/SKILL.md, not shown but referenced)

**Key Characteristics:**
- Generated AFTER mode detection and BEFORE extraction/elicitation
- Curated (not exhaustive) — selection judgment applied at requirements stage
- Contains only entry keys (triggers) — downstream consumers resolve content fresh
- Written once per `/requirements` invocation; does not augment from prior artifacts

---

### 1.2 `/design` Skill

**File:** `/Users/david/code/edify/plugin/skills/design/SKILL.md`

**Artifact Role:** CREATES, AUGMENTS, and CONSUMES `recall-artifact.md`

**Reference Locations:**
- Lines 46-57: "Triage Recall" (D+B anchor, reads memory-index before classification)
- Lines 190-211: "Recall Artifact Generation" (Phase A.1 creation)
- Lines 219-225: "Post-Explore Recall" (Phase A.2.5 augmentation after codebase exploration)
- Lines 349-351: "Recall diff" (Phase C.1 augmentation after design completion)

**Process Timeline:**

1. **Phase 0 — Triage Recall (Lines 46-57)**
   - Structural anchor: before classification, load triage-relevant decisions
   - Command: `plugin/bin/when-resolve.py "when behavioral code" "when complexity" ...`
   - Purpose: Codified decisions constrain classification before it happens
   - Consumption mode: Targeted (domain + triage keywords)

2. **Phase A.1 — Documentation Checkpoint (Lines 190-211)**
   - **Creation rule:** Lines 190-211 — After Level 1-5 documentation loading (lines 174-182), write `recall-artifact.md`
   - **Format:** Lines 196-207 — Entry keys only, trigger phrase + 1-line relevance note
   - **Selection:** Lines 209-210 — Entries that "informed design decisions or constrain implementation"
   - **Output:** Line 211 — `plans/<job>/recall-artifact.md`
   - **Purpose:** Persist documentation findings from current context (context window expires) for downstream consumption

3. **Phase A.2.5 — Post-Explore Recall (Lines 219-225)**
   - **Gate anchor:** Mandatory tool call on both paths (new entries or no-op)
   - **Augmentation rule:** Lines 224-225 — Append NEW entry keys if exploration revealed domains not caught by A.1 topic-based recall
   - **No-op path:** If no new entries: `when-resolve.py null` proves gate was reached
   - **Output:** Append to existing `recall-artifact.md` (Edit, not Write)

4. **Phase C.1 — Recall Diff (Lines 349-351)**
   - **Command:** `plugin/bin/recall-diff.sh <job-name>` (bash script, lines 1-28 in recall-diff.sh)
   - **Purpose:** Approach commitment, revised scope, or rejected alternatives change relevance
   - **Augmentation rules:** Add entries surfaced by discussion, remove entries for rejected approaches
   - **Output:** Update existing `recall-artifact.md`

**Downstream Consumption:**
- **Phase A.6 (outline-corrector delegation):** Review-relevant entries from `recall-artifact.md` included in corrector prompt (line 278)
- **Phase C.3 (design-corrector delegation):** Review-relevant entries included in delegation prompt (line 380)

**Key Characteristics:**
- Artifact persists across all three Phase A passes (A.1 creation, A.2.5 augmentation, C.1 refinement)
- Selection judgment applied at multiple gates (A.1 domain matching, A.2.5 exploration-informed, C.1 scope-change-informed)
- Never deleted/replaced — only appended or refined
- Content: trigger phrases only (no summaries — downstream resolves fresh)

---

### 1.3 `/runbook` Skill

**File:** `/Users/david/code/edify/plugin/skills/runbook/SKILL.md`

**Artifact Role:** CONSUMES (reads), AUGMENTS, and PASSES DOWNSTREAM

**Reference Locations:**
- Lines 116-120: Tier 1 recall context — lightweight recall if no artifact exists
- Lines 132-136: Tier 2 recall context — lightweight recall if no artifact exists
- `plugin/skills/runbook/references/tier3-planning-process.md` lines 26-33: Phase 0.5 augmentation

**Process Timeline:**

1. **Tier 1 & 2 — Recall Context (Lines 116-136)**
   - **Consumption:** If `plans/<job>/recall-artifact.md` exists, Read it
   - **Fallback (no artifact):** Lightweight recall — resolve domain keywords via `when-resolve.py` single call
   - **Purpose:** Ground Tier 1/2 execution decisions in domain knowledge
   - **Artifact usage:** No augmentation; Read-only consumption

2. **Tier 3 — Phase 0.5 Augmentation (tier3-planning-process.md lines 26-33)**
   - **Condition:** Design stage may have generated artifact (A.1) OR artifact absent
   - **Augmentation rule:** If existing, add implementation + testing learnings (Phase 0.5 lines 27-31)
   - **Content to add:** Planning-relevant only — model selection failures, phase typing, checkpoint placement, precommit gotchas (lines 29-30)
   - **Exclusion:** Do NOT add execution-level entries (mock patching, test structure) — those belong in step files
   - **Fallback:** If absent, generate from scratch — Read memory-index, select entries by domain matching, batch-resolve, write artifact
   - **Output:** Write augmented artifact back to `plans/<job>/recall-artifact.md`

3. **Tier 3 — Phase 0.75 Augmentation via Recall Diff (tier3-planning-process.md lines 47-49)**
   - **Gate anchor:** Same as `/design` C.1 — file locations, discovered patterns make different entries relevant
   - **Command:** `plugin/bin/recall-diff.sh <job-name>`
   - **Augmentation:** Add entries revealed by codebase discovery, remove entries for non-applicable patterns
   - **Output:** Update existing artifact

4. **Tier 3 — Phase 0.75 & Phase 1 Corrector Delegations**
   - **Outline corrector (tier3-planning-process.md line 90):** Include review-relevant entries from artifact
   - **Phase expansion corrector (tier3-planning-process.md line 291):** Include review-relevant entries from artifact
   - **Final holistic corrector (tier3-planning-process.md line 405):** Include review-relevant entries from artifact

**Downstream Consumption:**
- Per-phase correctors receive curated subset of artifact entries relevant to review context
- Corrector excludes execution-level entries (stored in step files instead)

**Key Characteristics:**
- Reads artifact from `/design` OR generates from scratch if absent
- Augments with implementation-specific learnings (not execution learnings)
- No consumer-specific curation at runbook stage (curation happens at `/inline` Phase 3 delegation)
- Artifact passed to correctors as reference context, not mechanically loaded

---

### 1.4 `/inline` Skill

**File:** `/Users/david/code/edify/plugin/skills/inline/SKILL.md`

**Artifact Role:** CONSUMES, CURATES consumer-specific variants, PASSES to sub-agents

**Reference Locations:**
- Lines 69-81: Phase 2.3 recall consumption (cold-start pre-work)
- Lines 96-102: Phase 3 delegated execution — sub-agent recall curation

**Process Timeline:**

1. **Phase 2.3 — Recall Loading (Lines 69-81, cold-start only)**
   - **Consumption rule:** Read `plans/<job>/recall-artifact.md`
   - **Resolution:** Batch-resolve design-related entries via `when-resolve.py`
   - **Fallback:** If no artifact, lightweight recall — Read memory-index, identify domain-relevant entries, batch-resolve
   - **Purpose:** Load design context before execution begins
   - **Artifact role:** Read-only consumption; no modification

2. **Phase 3 — Delegated Execution (Tier 2) — Sub-Agent Recall Curation (Lines 96-102)**
   - **Curation rule:** "Curate subset of plan recall-artifact entries relevant to delegation target"
   - **Creation:** Write separate artifact per consumer type: `plans/<job>/tdd-recall-artifact.md`, `plans/<job>/corrector-recall-artifact.md`, etc.
   - **Format:** Per-type format rules (constraint format for haiku, rationale for sonnet/opus)
   - **Principle:** Parent does cognitive work (selecting relevant entries); child does mechanical work (resolving them) — context isolation
   - **Delegation prompt:** "Read `plans/<job>/<type>-recall-artifact.md`, then batch-resolve via `plugin/bin/when-resolve.py`"
   - **Output:** Create consumer-specific artifact files alongside primary artifact

**Consumption Model:**
- **test-driver:** Receives `tdd-recall-artifact.md` (CLI testing, assertions, lint gate entry keys)
- **corrector:** Receives `corrector-recall-artifact.md` (D+B pattern, model selection, holistic fixes)
- **Optional skill-reviewer:** Receives `skill-review-recall-artifact.md` (skill editing, D+B propagation)

**Phase 4a Corrector Dispatch (Lines 127-137):**
- **Recall context:** Uses `corrector-recall-artifact.md` if prepared during Phase 3 delegation (corrector-template.md line 46)
- **Fallback:** Lightweight recall if artifact absent (corrector-template.md lines 50-65)
- **Scope:** Changed files only (`git diff --name-only $BASELINE`) — implementation changes, not planning artifacts
- **Report:** `plans/<job>/reports/review.md`

**Key Characteristics:**
- Primary artifact (`recall-artifact.md`) consumed once at Phase 2.3
- Consumer-specific variants created at Phase 3 execution time (not design time)
- Curation judgment applied per delegation type (what matters for test-driver ≠ what matters for corrector)
- Sub-agents resolve content fresh within their own context (no inherited parent context)
- Prevents cognitive overload on sub-agents — they receive only mechanically resolvable trigger phrases

---

### 1.5 `/orchestrate` Skill

**File:** `/Users/david/code/edify/plugin/skills/orchestrate/SKILL.md`

**Artifact Role:** READS (indirect, via checkpoints and inline execution), PASSES to sub-agents

**Reference Locations:**
- Lines 161 (Phase 3.3 checkpoint delegation): `recall-resolve.sh` invocation for artifact resolution
- Lines 74-77 (Phase 3.0 inline execution): No explicit recall handling; inline phases are self-contained

**Process:**

1. **Phase 3.3 Checkpoint Delegation (Line 161)**
   - **Command:** `Bash: plugin/bin/recall-resolve.sh plans/<name>/recall-artifact.md` (hypothetical wrapper — actual script is `recall-diff.sh` or `when-resolve.py` batch calls)
   - **Purpose:** Resolve artifact entries into checkpoint agent context
   - **Fallback:** Lightweight recall if artifact absent or script fails
   - **Delegation:** Corrector receives resolved entries for review-relevant patterns

2. **Phase 3.0 Inline Execution (Lines 65-78)**
   - **Artifact role:** None — inline phases are self-contained (all decisions pre-resolved at planning time)
   - **Corrector dispatch:** Not performed inline; deferred to Phase 4 (outside orchestrator scope)

**Downstream Consumption:**
- Plan-specific agents (crew-<runbook-name>-p*.md) do not receive recall artifacts directly
- Recall passed via checkpoint corrector delegate, not via step file headers

**Key Characteristics:**
- Orchestrator does NOT create or augment artifacts
- Checkpoint delegation uses artifact for corrector context (same pattern as `/inline` Phase 4a)
- Inline phases bypass recall entirely (decisions pre-made at planning time)

---

### 1.6 `/deliverable-review` Skill

**File:** `/Users/david/code/edify/plugin/skills/deliverable-review/SKILL.md`

**Artifact Role:** OPTIONALLY CONSUMES via lightweight recall fallback

**Reference Location:** Lines 95 (Phase 3 Layer 2 interactive review)

**Process:**

1. **Phase 3 Layer 2 — Interactive Full-Artifact Review (Line 95)**
   - **Command:** `Bash: plugin/bin/recall-resolve.sh plans/<plan>/recall-artifact.md` (conditional)
   - **Condition:** If artifact exists and recall-resolve succeeds, use resolved content
   - **Fallback:** Lightweight recall — Read memory-index, identify review-relevant entries, batch-resolve via `when-resolve.py`
   - **Purpose:** Supplement cross-cutting checks with resolved decision content (common review failures, quality anti-patterns)
   - **Note:** Supplements, does not replace, existing review axes

**Key Characteristics:**
- Artifact consumption is optional (conditional on artifact existence)
- Recall augments review context but is not mandatory for decision
- Read-only consumption; no artifact modification

---

## 2. Consumer-Specific Artifact Handling

### 2.1 Overview: Context Isolation Pattern

The codebase implements a **context isolation principle** for delegated execution: the parent session does cognitive work (selecting relevant entries from full recall-artifact), the child sub-agent does mechanical work (resolving those entries into fresh context).

**Source:** agents/session.md lines 13-16; plugin/skills/inline/SKILL.md lines 96-102

**Consumer Types:**

| Consumer | Artifact | Created At | Content | Source |
|----------|----------|-----------|---------|--------|
| test-driver | `tdd-recall-artifact.md` | `/inline` Phase 3 (before delegation) | CLI testing, assertions, lint gate (5 entries) | Curated from primary recall-artifact |
| corrector | `corrector-recall-artifact.md` | `/inline` Phase 3 (before delegation) | D+B pattern, model selection, holistic fixes (7 entries) | Curated from primary recall-artifact |
| skill-reviewer | `skill-review-recall-artifact.md` | `/inline` Phase 3 (before delegation) | Skill editing, D+B propagation (6 entries) | Curated from primary recall-artifact |

**Format Rules:**
- Haiku/Sonnet consumers: Constraint format — DO/DO NOT rules with explicit applicability markers
- Opus consumers: Rationale format — key points with context
- All: Single command included — `plugin/bin/when-resolve.py "entry1" "entry2" ...` for mechanical invocation

### 2.2 Consumer Artifact Examples

**Source:** Plans recall-null/outline.md lines 88-101

**Plan:** recall-null (Tier 2, TDD + inline execution)

**Execution Model:**

| Phase | Agent | Model | Recall Artifact | Location |
|-------|-------|-------|-----------------|----------|
| 1 (TDD) | test-driver (Task) | sonnet | `plans/recall-null/tdd-recall-artifact.md` | Phase 3 curation |
| 2 (inline) | direct (session) | opus | In-context (from `/recall broad` session start) | Not delegated |
| 4a (corrector) | corrector (Task) | opus | `plans/recall-null/review-recall-artifact.md` | Phase 3 curation |

**Invocation Pattern (line 93):**
```
Piecemeal TDD dispatch — one cycle per test-driver invocation, resume between.
Prompt includes: "Read `plans/recall-null/tdd-recall-artifact.md`, then batch-resolve ALL entries via `plugin/bin/when-resolve.py`."
```

**Skill-Reviewer Optional Delegation (line 99):**
```
Skill-reviewer: scope = modified skill files (cross-project context needed). Recall: `plans/recall-null/skill-review-recall-artifact.md`.
Optional — corrector may suffice for standardized pattern propagation. Invoke if corrector flags skill-specific issues.
```

### 2.3 Sub-Agent Recall Protocol

**Source:** plugin/skills/inline/SKILL.md lines 96-102

**Protocol Rules:**
1. **Curation happens in parent:** "Curate subset of plan recall-artifact entries relevant to delegation target"
2. **Per-consumer artifact:** "Write separate artifact per type (e.g., `plans/<job>/tdd-recall-artifact.md`)"
3. **Mechanical invocation:** Include in each prompt: "Read `plans/<job>/<type>-recall-artifact.md`, then batch-resolve via `plugin/bin/when-resolve.py`"
4. **Context isolation:** "Parent does cognitive work (selecting entries, curating context). Child does mechanical work (resolving entries, executing). Sub-agents have no parent context."

**Anti-Pattern from Execution Feedback:**

**Source:** plans/inline-execute/reports/execution-feedback.md lines 20-29

**Problem (Recall artifact word-splitting):**
- First attempt: Told agent "already resolved in parent context — do not re-resolve" (WRONG — sub-agent has no parent context)
- Second attempt: Told agent to run when-resolve.py with specific entries (WRONG — delegates recall judgment to execution agent)
- Third attempt: Created tdd-recall-artifact.md with mechanical invocation command (CORRECT — no judgment, single command)

**Root Cause:** "Treating Task agents as context-sharing rather than context-isolated."

**Fix:** `triggers=("${(@f)$(< plans/inline-execute/tdd-recall-artifact.md)}") && plugin/bin/when-resolve.py "${triggers[@]}"`

---

## 3. Recall-Diff Handling

### 3.1 Script Specification

**File:** `/Users/david/code/edify/plugin/bin/recall-diff.sh` (lines 1-28)

**Purpose:** Detect files changed since recall-artifact was written, determine if relevance has shifted

**Invocation Pattern:**
- `/design` Phase C.1 (line 349 in design SKILL.md)
- `/runbook` Phase 0.75 (line 47 in tier3-planning-process.md)

**Logic:**
```bash
JOB="$1"
ARTIFACT="plans/${JOB}/recall-artifact.md"

# Get artifact modification time
MTIME=$(date -r "$ARTIFACT" "+%Y-%m-%dT%H:%M:%S")

# List files changed after artifact was written
git log --since="${MTIME}" --name-only --pretty=format: -- "plans/${JOB}/" \
  | grep -v '^$' \
  | grep -v "^plans/${JOB}/recall-artifact\.md$" \
  | sort -u
```

**Trigger Condition:** Files changed since artifact mtime → relevance may have shifted

### 3.2 Augmentation Pattern

Both `/design` C.1 and `/runbook` Phase 0.75 follow the same pattern:

1. **Run recall-diff.sh** to detect changed files
2. **Review changed files list** — determine if change affects recall relevance
3. **If relevance shifted:**
   - Add entries surfaced by change
   - Remove entries for approaches that were rejected/replaced
   - Write updated artifact back
4. **If no relevance shift:** Proceed without updating

**Difference between stages:**

| Stage | Trigger | Entries to Add | Entries to Remove |
|-------|---------|---|---|
| `/design` C.1 | Approach commitment, revised scope, rejected alternatives | Entries for finalized approach | Entries for rejected alternatives |
| `/runbook` Phase 0.75 | File locations, discovered patterns, structural constraints | Implementation patterns in discovered modules | Entries for patterns not found in actual codebase |

### 3.3 Augmentation Rules (Design vs Planning)

**Design augmentation (C.1):**
- "Add entries surfaced by the discussion" — outline/design clarifications reveal new constraint domains
- "Remove entries for approaches that were rejected" — architectural decisions narrow scope
- "Approach commitment, revised scope" — these changes shift what's relevant

**Planning augmentation (Phase 0.5 & 0.75):**
- Add "implementation and testing learnings" from memory-index (Phase 0.5)
- Add entries revealed by codebase discovery (Phase 0.75)
- Remove entries for "patterns that don't apply to the actual codebase"
- **Exclusion rule:** "Do NOT add execution-level entries (mock patching, test structure details) — those belong in step files"

---

## 4. Shared Artifact Lifecycle

### 4.1 Artifact Trio: recall-artifact, classification.md, outline.md

The pipeline uses three interdependent artifacts that evolve across stages:

| Artifact | Created | Augmented | Consumed | Purpose |
|----------|---------|-----------|----------|---------|
| **recall-artifact.md** | `/design` A.1 | `/design` A.2.5, C.1; `/runbook` 0.5, 0.75 | `/requirements` (none), `/design` A.6/C.3 (correctors), `/runbook` tiers 1-3 (correctors), `/inline` 2.3/4a (execution + corrector), `/orchestrate` 3.3 (checkpoint) | Trigger-phrase index for context loading; decision persistence across sessions |
| **classification.md** | `/design` Phase 0 (lines 114) | Never | `/inline` Phase 4b (triage-feedback.sh at line 32 in script) | Work-type/tier/artifact-destination checkpoint; post-execution comparison point for classification drift detection |
| **outline.md / design.md** | `/design` Phase A.5/Phase C.1 | `/design` Phase B (user discussion) | `/inline` Phase 4a (corrector scope baseline), `/deliverable-review` Phase 1 (design conformance), `/runbook` phases (inline references) | Architectural specification; binding constraint for implementation |

### 4.2 Lifecycle Sequence Across Pipeline Stages

```
/requirements → /design → /runbook → /inline → /deliverable-review
                                   └─→ /orchestrate → [correctors] → /deliverable-review

recall-artifact.md progression:
- /requirements: WRITES initial artifact (optional, from /recall all)
- /design:
  - A.1: CREATES (or reads if req artifact exists)
  - A.2.5: AUGMENTS (post-explore)
  - C.1: AUGMENTS (recall-diff after approach finalized)
  - A.6, C.3: CONSUMES (corrector review delegation)
- /runbook:
  - Phase 0.5: AUGMENTS (planning-focused learnings)
  - Phase 0.75: AUGMENTS (recall-diff after codebase discovery)
  - Phases 0.75, 1, 3: CONSUMES (corrector delegations)
  - (Tier 1/2): CONSUMES (lightweight execution)
- /inline:
  - Phase 2.3: CONSUMES (cold-start recall loading)
  - Phase 3: CURATES consumer-specific variants (tdd-*, corrector-*, skill-review-*)
  - Phase 4a: CONSUMES via consumer variant (corrector dispatch)
- /orchestrate:
  - Phase 3.3: CONSUMES (checkpoint corrector delegation)
- /deliverable-review:
  - Phase 3: OPTIONALLY CONSUMES (lightweight recall fallback)

classification.md progression:
- /design Phase 0: WRITES
- /inline Phase 4b: CONSUMES (triage-feedback.sh for drift detection)

outline.md / design.md progression:
- /design Phase A.5: WRITES outline
- /design Phase B: REFINES outline (user discussion)
- /design Phase C: WRITES design (if outline insufficient)
- /inline Phase 4a: CONSUMES (corrector baseline)
- /runbook: REFERENCES (decisions scoped to outline/design)
```

### 4.3 Artifact Staleness Vectors

**Identified in session.md line 40-44:**

**Two drift vectors:**

1. **Stale recall-artifact** (entries loaded not persisted)
   - When: Sub-agents resolve recall entries and discover new implementation constraints
   - Impact: Subsequent planning/execution phases lack updated learnings
   - Mitigation: Pending task "Artifact staleness gate" (line 40-44) proposes sentinel-based detection

2. **Stale skill artifacts** (decisions loaded after artifact written)
   - When: Design decisions change after recall-artifact was written
   - Impact: Downstream stages have outdated recall context
   - Mitigation: recall-diff.sh gate at design C.1 and planning 0.75 re-evaluates relevance

**Proposed Staleness Gate (session.md lines 40-44):**
```
- Mechanical checkpoint at /requirements, /design, /runbook exit points
- when-resolve.py touches sentinel; skill compares sentinel mtime to:
  - recall-artifact.md mtime
  - primary skill artifact (requirements.md, outline.md, design.md, runbook.md) mtime
- If recall newer than either artifact, trigger update step
```

---

## 5. Patterns and Conventions

### 5.1 Recall Artifact Format Consistency

**Across all skills, consistent format (lines 50-59 in requirements SKILL.md):**

```markdown
# Recall Artifact: <Job Name>

Resolve entries via `plugin/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

<trigger phrase> — <1-line relevance note>
<trigger phrase> — <1-line relevance note>
```

**Rules:**
- Entry keys only (trigger phrases) — no content excerpts, no summaries
- 1-line relevance notes — why this entry is relevant to this plan's decisions
- Curated (not exhaustive) — selection judgment applied per stage
- Downstream consumers batch-resolve all entries to get current content

### 5.2 Progressive Augmentation Pattern

Artifact is **never replaced**, only **appended or refined**:

1. Initial creation at design A.1
2. Augmentation at design A.2.5 (post-explore)
3. Refinement at design C.1 (recall-diff)
4. Augmentation at runbook Phase 0.5 (planning learnings)
5. Refinement at runbook Phase 0.75 (recall-diff post-discovery)
6. Curation at inline Phase 3 (consumer-specific subsets)

Each stage builds on prior stages. No deletion or wholesale replacement.

### 5.3 D+B Gate Pattern: Mandatory Tool Calls

Both `/design` and `/runbook` enforce structural anchors via mandatory tool calls:

**Design Phase 0 — Triage Recall (line 46):**
```bash
plugin/bin/when-resolve.py "when behavioral code" "when complexity" "when triage" "when <domain-keyword>" ...
```
Structural anchor: prevents classification from being skipped or rationalized.

**Design Phase A.2.5 — Post-Explore Recall (line 223):**
```bash
# New entries found:
plugin/bin/when-resolve.py "when <trigger>" ...

# No new entries (no-op path):
plugin/bin/when-resolve.py null
```
Structural anchor: proves gate was reached (both success and no-op paths recorded).

**Runbook Phase 0.75 — Recall Diff (line 47):**
```bash
plugin/bin/recall-diff.sh <job-name>
```
Structural anchor: detects if changed files alter recall relevance before expansion.

### 5.4 Consumer-Specific Curation Rules

**Source:** plugin/skills/inline/SKILL.md lines 96-102

**Rule 1: Parent does cognitive work, child does mechanical work**
- Parent session: Reads primary artifact, selects relevant entries per consumer type
- Child sub-agent: Receives curated artifact, resolves entries via single command, executes
- Prevents sub-agent from making relevance judgments it lacks context for

**Rule 2: Per-consumer artifact (not shared)**
- test-driver: `tdd-recall-artifact.md` (CLI testing, assertions, lint)
- corrector: `corrector-recall-artifact.md` (D+B pattern, model selection, holistic fixes)
- skill-reviewer: `skill-review-recall-artifact.md` (skill editing, D+B propagation)
- Each artifact contains only entries relevant to that consumer's domain

**Rule 3: Mechanical invocation command included**
- Standard pattern: "Read `plans/<job>/<type>-recall-artifact.md`, then batch-resolve ALL entries via `plugin/bin/when-resolve.py`"
- No sub-agent decision judgment — command is mechanical
- Prevents word-splitting bugs (when invocation was inline) and ensures complete resolution

### 5.5 Review Gate Recall Context Pattern

**Source:** corrector-template.md lines 25-65

**Corrector dispatch always includes recall context:**

Lines 46, 89: "Curate from plan recall-artifact. Include entries about review failure modes, quality anti-patterns, over-escalation patterns."

**Fallback (lines 50-65):** If artifact absent, lightweight recall:
```bash
plugin/bin/when-resolve.py \
  "when concluding reviews" \
  "when corrector rejects planning artifacts" \
  "when recall-artifact is absent during review" \
  "when batch changes span multiple artifact types" \
  "when routing implementation findings"
```

**Rationale:** Corrector needs domain-specific guidance on review failure modes (common mistakes, over-escalation patterns) that generic axes miss.

---

## 6. Gaps and Unresolved Questions

### 6.1 Consumer-Specific Artifact Generation Timing

**Question:** Should consumer-specific artifacts be **prepared during planning** or **curated at execution time**?

**Current State:** Curated at `/inline` Phase 3 execution time (inline SKILL.md lines 96-102)

**Alternative Proposal:** Prepare during `/runbook` planning as separate artifact files (session.md lines 13-16 suggest these are pre-prepared, not inline-created)

**Evidence:** session.md "Per-consumer recall artifacts prepared" context suggests advance creation, but current code shows inline curation

**Impact:** If prepared advance, would enable pre-validation and corrector review of artifacts themselves. Inline curation prevents this.

### 6.2 Recall Artifact Staleness Detection

**Question:** How to detect and trigger updates when artifact has drifted from current decision state?

**Current State:** Partial — recall-diff.sh detects file changes since artifact mtime, triggering re-evaluation. No automatic update trigger.

**Proposed Solution:** (session.md lines 40-44) "Artifact staleness gate" with sentinel-based detection

**Open:** Implementation approach (sentinel touching, mtime comparison logic, update triggering mechanism)

### 6.3 Execution-Level Entry Segregation

**Question:** Where should execution-level entries (mock patching, test structure details) be stored?

**Current Rule:** (tier3-planning-process.md line 30) "Do NOT add execution-level entries... those belong in step files, not recall"

**Practice:** Step files (steps/step-*.md) include imperative instructions but don't segregate recall-artifact subsets

**Open:** Whether step-file-embedded recall would be cleaner than parallel corrector-dispatch artifacts

### 6.4 Consumer Artifact Coverage

**Question:** Are there other consumer types beyond test-driver, corrector, and skill-reviewer?

**Known Consumers:**
- test-driver (via tdd-recall-artifact.md)
- corrector (via corrector-recall-artifact.md)
- skill-reviewer (via skill-review-recall-artifact.md, optional)
- outline-corrector (via runbook-outline-corrector agent, no dedicated artifact)
- design-corrector (via design-corrector agent, no dedicated artifact)
- runbook-corrector (via runbook-corrector agent, no dedicated artifact)

**Gap:** Design/runbook correctors receive recall entries inline in delegation prompt, not via dedicated artifact. Inconsistent with test-driver / implementation-corrector pattern.

**Open:** Whether to create dedicated artifacts for all corrector types or consolidate consumer-artifact approach

### 6.5 Artifact Consumption in Deliverable-Review

**Question:** Why is recall-artifact consumption optional in deliverable-review (line 95)?

**Current State:** "If artifact exists and recall-resolve succeeds, use... If artifact absent or fails: do lightweight recall"

**Rationale:** Deliverable review is post-execution — artifact may be stale or artifacts may have been post-execution modifications

**Gap:** No guidance on when artifact is sufficiently current for use vs when to ignore it

**Open:** Staleness detection mechanism (sentinel, mtime comparison) would enable confident consumption

---

## 7. File Locations and References

### Core Skill Files
- `/Users/david/code/edify/plugin/skills/requirements/SKILL.md` — recall-artifact creation (lines 32-64)
- `/Users/david/code/edify/plugin/skills/design/SKILL.md` — recall-artifact lifecycle A.1/A.2.5/C.1 (lines 46-57, 190-211, 219-225, 349-351)
- `/Users/david/code/edify/plugin/skills/runbook/SKILL.md` — recall-artifact consumption/augmentation (lines 116-136)
- `/Users/david/code/edify/plugin/skills/inline/SKILL.md` — consumer-specific curation (lines 96-102)
- `/Users/david/code/edify/plugin/skills/orchestrate/SKILL.md` — checkpoint delegation (line 161)
- `/Users/david/code/edify/plugin/skills/deliverable-review/SKILL.md` — optional recall consumption (line 95)

### Reference Files
- `/Users/david/code/edify/plugin/skills/design/references/research-protocol.md` — recall diff application (lines 15-17)
- `/Users/david/code/edify/plugin/skills/runbook/references/tier3-planning-process.md` — Phase 0.5 augmentation (lines 26-33), Phase 0.75 recall-diff (lines 47-49)
- `/Users/david/code/edify/plugin/skills/inline/references/corrector-template.md` — corrector recall context, lightweight fallback (lines 25-65)

### Helper Scripts
- `/Users/david/code/edify/plugin/bin/recall-diff.sh` — detect changed files since artifact mtime (lines 1-28)
- `/Users/david/code/edify/plugin/bin/recall-check.sh` — verify artifact exists and non-empty (lines 1-20)
- `/Users/david/code/edify/plugin/bin/when-resolve.py` — resolve entry keys to current content (referenced throughout)

### Plan Examples
- `/Users/david/code/edify/plans/recall-null/outline.md` — consumer-artifact execution model (lines 88-101)
- `/Users/david/code/edify/plans/recall-null/recall-artifact.md` — example primary artifact
- `/Users/david/code/edify/plans/inline-execute/reports/execution-feedback.md` — sub-agent context isolation pattern failure (lines 20-40)

### Decision Files
- `/Users/david/code/edify/agents/decisions/pipeline-contracts.md` — transformation table with artifact flow (lines 1-17)
- `/Users/david/code/edify/agents/session.md` — per-consumer artifacts and staleness gap (lines 13-16, 40-44)

---

## Summary: Key Takeaways

1. **Transient, Curated Index:** recall-artifact.md is not comprehensive documentation; it's a curated trigger-phrase index for decision loading, created at design time and refined across planning.

2. **Progressive Augmentation:** Artifact grows across design (A.1 → A.2.5 → C.1) and planning (0.5 → 0.75) gates, never replaced, reflecting evolving scope and discovered constraints.

3. **D+B Structural Anchors:** Mandatory tool calls (recall phases in design/runbook) enforce gate execution, preventing skips or rationalizations.

4. **Context Isolation in Delegation:** Parent does cognitive work (curating recall entries per consumer type); child sub-agents do mechanical work (batch-resolving entries into fresh context). Consumer-specific artifacts enforce this separation.

5. **Staleness Vectors:** Two drift modes — stale artifacts (entries not persisted) and stale decisions (entries no longer relevant) — partially mitigated by recall-diff gates, pending full implementation of sentinel-based staleness detection.

6. **Recall-Consuming Stages:** `/design` (corrector review), `/runbook` (tier 1/2/3 execution + corrector review), `/inline` (pre-work loading + consumer variants + corrector), `/orchestrate` (checkpoint corrector), `/deliverable-review` (optional lightweight fallback).

7. **Three-Artifact Trio:** recall-artifact (decision index), classification.md (execution checkpoint), outline.md/design.md (architectural spec) form interdependent system for requirements-to-deliverable traceability.
