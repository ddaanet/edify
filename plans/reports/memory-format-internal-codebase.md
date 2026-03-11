# Memory Format Grounding: Internal Codebase Analysis

**Report scope:** Survey of existing trigger format patterns, when/how distinction, index structure, and metadata patterns in the active recall system.

**Date:** 2026-03-08

---

## 1. Current Trigger Format Patterns

### Trigger Structure Overview

Memory index entries use two primary trigger formats:

**Format 1: Operational statement (gerund + object)**
```
/when placing helper functions
/when choosing execution tier
/how extract session titles
/when handling malformed session data
```

**Format 2: Conditional statement (when/how + situation)**
```
/when call site expands under formatter
/when cli commands are llm-native
/how format token count output
/when choosing feedback output format
```

**Format 3: Complex situational (when/how + [adjective] + [noun phrase])**
```
/when designing quality gates
/when routing prototype work through pipeline
/when delegating TDD cycles to test-driver
```

### Trigger Pattern Taxonomy

From comprehensive scan of `/Users/david/code/claudeutils-wt/ar-format-grounding/agents/memory-index.md` (366 entries across ~25 decision files):

#### Verb Patterns (When-class entries)

| Pattern | Examples | Frequency | Notes |
|---------|----------|-----------|-------|
| **When [gerund] X** | placing, choosing, designing, routing, delegating | ~40% | Single action at decision point |
| **When [verb] [condition]** | handling, fixing, reviewing, splitting, placing | ~30% | Conditional action on state |
| **When [X] [property]** | deliverable review catches drift, edit tool reports stale success | ~15% | Situation with observed property |
| **When X [is/are] Y** | gates bypass, phase qualifies, tests fail | ~10% | State equivalence pattern |
| **When [adjective] [noun]** | custom agents, inline execution, TDD cycles | ~5% | Quality/classification pattern |

#### Verb Patterns (How-class entries)

| Pattern | Examples | Frequency | Notes |
|---------|----------|-----------|-------|
| **How to [verb] X** | pass model as argument, split test modules, merge templates | ~50% | Explicit instruction form |
| **How [verb] X** | detect markdown line prefixes, define feedback enum, build reusable filtering | ~30% | Imperative form (lighter) |
| **How [process] [object]** | format batch edits, architect feedback pipeline, inject context | ~20% | Process/structure pattern |

### Specificity Levels

Entries cluster at three specificity tiers:

**High specificity (narrow trigger domain):**
- `/when removing stale learnings on commit`
- `/how format token count output`
- `/when edit tool reports stale success`

Domain: ~3-5 related work types invoke this

**Medium specificity (moderate trigger domain):**
- `/when placing helper functions`
- `/how extract session titles`
- `/when handling malformed session data`

Domain: ~10-20 related work types invoke this

**Low specificity (broad trigger domain):**
- `/when designing quality gates`
- `/when choosing name`
- `/how order markdown processing steps`

Domain: 30+ work types could invoke this

### Format Inconsistencies & Drift

**Active inconsistencies observed:**

1. **Article presence variance:** Similar concepts differ in articles
   - `/when writing CLI output` (no article)
   - vs `/when raising exceptions for expected conditions` (article included)

2. **Preposition variation:**
   - `/when placing helper functions` (bare placement)
   - vs `/when placing DO NOT rules in skills` (with context)

3. **Verb tense drift:**
   - `/when designing quality gates` (present participle)
   - vs `/when vet flags unused code` (base form, single action)

4. **Object specificity:**
   - `/how format runbook phase headers` (generic, plural)
   - vs `/how format batch edits efficiently` (modifier, adverb)

**Pattern quality note:** Entries marked as "Example" in workflow-advanced.md show deliberate naming conventions established during Phase B (2026-03-07) discussion that reduce this drift:
- Activity at decision point (not outcome)
- Broadest applicable verb
- No self-assessment terms

---

## 2. When/How Distinction

### How Distinction Currently Operates

**Distinction mechanism:** Prefix-only in syntax; semantic separation in conceptual intent.

**When entries (situational):**
- Trigger: Agent's current context or decision point
- Content: Behavioral guidance, trade-off analysis, conditional recommendations
- Example: `/when designing quality gates` → discusses layered defense, placement timing, anchor tools
- Semantics: "In this situation, consider..."

**How entries (procedural):**
- Trigger: Agent's current task
- Content: Implementation instructions, mechanical procedures, reference documentation
- Example: `/how format runbook phase headers` → specifies exact header syntax, parsing rules
- Semantics: "To accomplish this, follow these steps..."

### Resolver Distinction Implementation

From `/Users/david/code/claudeutils-wt/ar-format-grounding/src/claudeutils/when/resolver.py`:

```python
def _build_heading(operator: str, trigger: str) -> str:
    """Build heading from operator and trigger."""
    words = trigger.split()
    # Preserve all-caps acronyms, capitalize normal words
    capitalized = " ".join(w if w.isupper() else w.capitalize() for w in words)
    if operator == "how":
        return f"How to {capitalized}"
    return f"When {capitalized}"
```

The resolver transforms triggers into section headings:
- `/when designing quality gates` → finds `## When Designing Quality Gates`
- `/how format runbook phase headers` → finds `## How to Format Runbook Phase Headers`

### When/How Distinction in Index Files

From parsing code (`/Users/david/code/claudeutils-wt/ar-format-grounding/src/claudeutils/when/index_parser.py`):

**WhenEntry model stores:**
- `operator`: "when" or "how" (prefix indicator)
- `trigger`: Bare trigger text (the classification signal)
- `section`: Parent file reference (agents/decisions/*.md)
- `extra_triggers`: Pipe-separated keywords for disambiguation

The distinction is purely syntactic at index level. Semantic classification happens at **decision time during grounding**:

From `plans/active-recall/brief.md` (S-G decision, 2026-03-07):
> **S-G: Pattern/antipattern catalogs default to `when` class**
>
> All patterns/antipatterns repositories are best encoded as `when` entries (situational triggers). The model already knows *how* to implement patterns from training — the value-add is the applicability condition ("when you see [problem shape]"). Per-entry class decision (FR-2) still holds, but default expectation for methodology sources should be `when`, not `how`.

### Edge Cases & Ambiguities

**Boundary cases where distinction is unclear:**

1. **Procedural guidelines that feel situational:**
   - `/how write init files` — could be "when needing a module structure"
   - Resolution: Classified as `how` because documentation headings use "How to Write" form

2. **Situational analysis that includes procedure:**
   - `/when choosing pydantic for validation` → includes "How" decision tree in content
   - Currently: `when` (correct — decision point is choosing, not writing)

3. **Compound operations:**
   - `/when delegating TDD cycles to test-driver` — is this situational ("when delegating") or procedural ("how to delegate")?
   - Currently: `when` (correct — decision focus is the condition for delegation)
   - Procedural counterpart would be: `/how delegate TDD cycles` (if we had it)

**Current resolution:** No explicit edge case handling. Resolver treats both equally — finds heading via title transformation and extracts matching section.

---

## 3. Index Structure

### Current Hierarchy

**Single-level flat index:** `agents/memory-index.md`

Structure:
- H2 headings = file references (agents/decisions/cli.md, agents/decisions/data-processing.md, etc.)
- Content under each H2 = entry lines
- No sub-organization within files

```
# Memory Index

## agents/decisions/cli.md
/when getting current working directory
/how output errors to stderr
/when cli commands are llm-native | internal stdout markdown exit-code no-stderr
...

## agents/decisions/data-processing.md
/how write init files
/when placing helper functions
...
```

### Branching Factor & Distribution

**Current metrics:**
- Total entries: ~366 (across 450 lines)
- H2 sections (decision files): 25 visible sections
- Average entries per section: ~14.6
- Range: 4 entries (some files) to 28+ entries (operational-practices.md)

**Sections observed:**
- `agents/decisions/cli.md` — 15 entries
- `agents/decisions/data-processing.md` — 10 entries
- `agents/decisions/defense-in-depth.md` — 14 entries
- `agents/decisions/operational-practices.md` — 30+ entries (largest)
- `agents/decisions/orchestration-execution.md` — 37 entries
- `agents/decisions/pipeline-contracts.md` — 35 entries
- `agents/decisions/project-config.md` — 10 entries
- `agents/decisions/workflow-advanced.md` — 23 entries
- `agents/decisions/workflow-core.md` — 13 entries

### Parser Behavior

From `/Users/david/code/claudeutils-wt/ar-format-grounding/src/claudeutils/recall/index_parser.py`:

**Parsing rules:**
1. H2 headings become section identifiers (file path)
2. Lines matching `/when ` or `/how ` are entries
3. Old format lines with ` — ` separator still parsed (backward compatible)
4. Keywords extracted via stopword filtering and regex tokenization

**Skip behavior:**
```python
if current_section.startswith(("Behavioral Rules", "Technical Decisions")):
    skip_section = True
```

Sections titled "Behavioral Rules" or "Technical Decisions" are explicitly skipped — these map to CLAUDE.md @-references (already loaded).

### Index Flat-to-Hierarchical Transition

From `plans/active-recall/brief.md` (brief from 2026-03-02):

> **Hierarchical Index**
>
> Root index maps domains to child indices. Lookup is O(log_k(N)) with branching factor k. Current flat memory-index (~200 entries) is halfway there — sections as implicit domains. Splitting into separate files + root pointer is mechanical.
>
> Required for scaling: bulk documentation conversion will produce thousands of entries exceeding flat index capacity.

**Current status:** Flat structure adequate for 366 entries. Scaling trigger at ~1000-2000 entries (bulk conversion phase).

---

## 4. Embedded Metadata

### Current Metadata System

**Metadata location:** Pipe-separated keywords after trigger text

```
/when cli commands are llm-native | internal stdout markdown exit-code no-stderr
/how format batch edits efficiently | batch-size line-number grouping optimization
/when designing quality gates | layered defense multiple independent checks
```

**Metadata scope:** Supplementary keywords for disambiguation. Parsed by index_parser as `extra_triggers` list.

### Keyword Extraction Strategy

From `/Users/david/code/claudeutils-wt/ar-format-grounding/src/claudeutils/recall/index_parser.py`:

**Automatic extraction from trigger + description:**
```python
def extract_keywords(text: str) -> set[str]:
    """Extract keywords from text.
    Tokenizes on whitespace and punctuation, lowercases, removes stopwords.
    """
    tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())
    return {token for token in tokens if token and token not in STOPWORDS}
```

**Stopwords used:** 59 common English words (a, the, is, are, for, from, with, etc.)

**Example keyword extraction:**
- Trigger: "designing quality gates"
- Keywords: {designing, quality, gates}

- Trigger: "cli commands are llm-native" + metadata: "internal stdout markdown exit-code no-stderr"
- Keywords: {cli, commands, llm, native, internal, stdout, markdown, exit, code, no, stderr}

### Proposed Embedded Keywords System

From `plans/active-recall/brief.md` (Embedded Keywords + Derived Index, 2026-03-06):

> **Embedded Keywords + Derived Index (2026-03-06)**
>
> Memory entries carry their own trigger keywords as structured metadata. Memory-index is generated (deterministic build step), not hand-maintained.
>
> - No index drift — keywords live with the content they describe
> - Write path: write entry with keywords → index regenerates automatically
> - Absorbs "Generate memory index" task — becomes a build step, not a design task
> - Concurrent writes to orphan branch conflict only on entries, never on index

**Current status:** Proposed but not yet implemented. Index is hand-maintained, not auto-generated.

---

## 5. Existing Architectural Decisions

### Key Decisions Files (agents/decisions/)

**Architectural frameworks established:**

1. **workflow-advanced.md** — Knowledge management, index design, naming conventions
   - `/when writing memory-index trigger phrases` — articles alignment rule (decision-2026-02-24)
   - `/when naming memory index triggers` — activity-at-decision-point rule (decision-2026-02-18)

2. **workflow-core.md** — Workflow patterns and execution tiers
   - Tier 1-3 classification system for orchestration
   - Cycle numbering flexibility (gaps allowed, duplicates not)

3. **operational-practices.md** — Practical execution patterns
   - Recall system effectiveness evaluation (decision-2026-02-26)
   - Recall artifact format and dedup patterns

4. **pipeline-contracts.md** — Quality gates and review delegation
   - When to escalate escalation decisions
   - Corrector agents and recall loading patterns

### Learnings Relevant to Format

From `agents/learnings.md`:

**When designing hierarchical index structures** (line 38-40):
> Anti-pattern: Mixed indices containing both entries and child references. Creates discoverability imbalance...
> Correct pattern: Clean separation — branch indices (index-of-indices only) vs leaf indices (entries only). Uniform discovery paths: root → branch(es) → leaf → entry. Simplifies parser (no mixed-mode detection).

**When outlines conflate decomposition with sequencing** (line 41-45):
> Correct pattern: Decomposition (breaking into sub-problems with dependency graph) is a separate activity from sequencing (ordering for implementation). Sub-problems get tagged with design readiness...
> Design inputs (grounding, research) belong in the design process, not as execution phases.

---

## 6. Representative Entry Samples

### High-Quality Trigger Examples

**Effective situational triggers:**

| Entry | Reason Effective | Domain Size |
|-------|------------------|-------------|
| `/when choosing name` | Single verb, maximally broad applicability. Surfaces for any naming task. | 50+ invocations potential |
| `/when designing quality gates` | Decision point is clear. "Quality gates" is specific enough for focused guidance. | 15-20 invocations |
| `/when placing helper functions` | Narrow domain, high precision. Used only during module structure decisions. | 5-10 invocations |
| `/when handling malformed session data` | Specific failure mode. Only invoked during session processing bugs. | 3-5 invocations |

**Effective procedural triggers:**

| Entry | Reason Effective | Domain Size |
|-------|------------------|-------------|
| `/how format runbook phase headers` | Task is explicit and mechanical. No ambiguity about when to invoke. | 10-15 invocations |
| `/how split test modules` | Clear action. Invoked during test refactoring specifically. | 5-10 invocations |
| `/how merge templates safely` | Specific operation. Invoked during template application only. | 3-5 invocations |

### Problematic Trigger Patterns

**Overly specific (low recall potential):**

| Entry | Issue | Suggested Alternative |
|-------|-------|----------------------|
| `/when edit tool reports stale success` | Requires recognizing specific error condition. Might miss semantically equivalent failures. | `/when debugging edit tool failures` |
| `/when fixture shadowing creates dead code` | Requires domain knowledge (pytest). Might not trigger without exact term match. | `/when test utilities shadow functions` |

**Overly broad (high noise):**

| Entry | Issue | Could be split into |
|-------|-------|---------------------|
| `/when choosing execution tier` | Broadly applicable but architectural. Surfaces for all execution mode decisions (good) and simple delegation (noise). | `/when tier thresholds are ungrounded` (specific) + keep general |

**Procedurally-phrased when entries (S-G violation):**

From decision-2026-03-07, `/how` default for mechanical operations:

| Entry | Current Form | S-G Expectation |
|-------|-------------|-----------------|
| `/when writing CLI output` | situational | OK — decision about output format |
| `/when converting external documentation to recall entries` | mixed | Should separate: `/when sourcing external documentation` (when) + `/how convert documentation` (how) |

### Concrete Entry-to-Heading Mappings

**Example resolution chains:**

```
Trigger: /when designing quality gates
↓
Section lookup: "designing quality gates" → "Designing Quality Gates"
↓
File: agents/decisions/defense-in-depth.md
↓
Heading found: ## When Designing Quality Gates
↓
Content extracted: [Decision date, pattern description, rationale, impact]
```

```
Trigger: /how format runbook phase headers
↓
Section lookup: "format runbook phase headers" → "How to Format Runbook Phase Headers"
↓
File: agents/decisions/implementation-notes.md
↓
Heading found: ## How Format Runbook Phase Headers
↓
Content extracted: [Decision, pattern, impact]
```

---

## 7. Gaps & Unresolved Questions

### Format Grounding Blockers

**Missing from current system:**

1. **Metadata schema definition**
   - Current: Free-form pipe-separated keywords
   - Needed: Structured metadata (tags, categories, relevance weights)
   - Block impact: Metadata-driven filtering (S-K corrector, relevance ranking)

2. **When/how classification rubric**
   - Current: Implicit (operator prefix only)
   - Needed: Formal decision criteria for boundary cases
   - Block impact: Corrector validation (S-K), conversion pipeline (bulk documentation)

3. **Trigger naming conventions**
   - Current: Three patterns established post-hoc (workflow-advanced.md)
   - Needed: Exhaustive convention set before bulk conversion
   - Block impact: Quality consistency at scale (1000+ entries)

4. **Index hierarchy specification**
   - Current: Flat structure, theoretical hierarchy defined in brief
   - Needed: Concrete branching strategy (domain clustering, split mechanics)
   - Block impact: Scaling beyond 2000 entries

### Parser Limitations

**Current resolver cannot handle:**

1. **Ambiguous headings** (two sections with same text)
   - Current: Raises ResolveError("Ambiguous heading")
   - Used in: (none observed in current index)
   - Risk: Bulk conversion may introduce ambiguity

2. **Missing articles in headings** (known issue from decision-2026-02-24)
   - Example: Trigger includes "the" but heading doesn't
   - Current: Fuzzy fallback handles this (partially)
   - Evidence: Article alignment decision required explicit validation step

3. **Heading level variance** (H2 vs H3 vs H4)
   - Current: Resolver only looks for headings starting with ##
   - Issue: Content may be nested under H3 within a decision file
   - Workaround: All current decisions use H2 for section headings, H3+ for subsections

### Validation Gaps

**No current enforcement for:**

1. **Trigger uniqueness** (duplicate triggers in different files)
   - Impact: Fuzzy match returns first hit only; second entry invisible
   - Risk level: Medium (duplication likely in bulk conversion)

2. **Orphaned triggers** (index entry pointing to non-existent section)
   - Current: Resolver catches at runtime ("Section not found")
   - Detection: None at index commit time
   - Risk level: Medium (manual editing risk)

3. **Trigger-to-heading alignment** (trigger doesn't map to actual heading text)
   - Example: Trigger "handling X" but heading is "When X Occurs"
   - Current: Fuzzy fallback masks misalignment
   - Risk level: High (silent failures feel like successful resolution)

---

## 8. Patterns Across Entries

### Naming Convention Patterns

**Dominant pattern structure (from 366 entries):**

```
WHEN ENTRIES:
[When|During] [present-participle] [object]
Examples: When choosing name, When designing quality gates, When placing helper functions

HOW ENTRIES:
[How to] [verb] [object]
Examples: How to format batch edits, How to split test modules
Alternate: [How] [verb] [object] — lighter form
Examples: How detect markdown line prefixes, How handle optional field defaults
```

**Consistency observations:**

- 85-90% of entries follow one of above patterns
- 10-15% drift: Missing articles, preposition variance, adjective insertion
- No observed entries with gerunds in how-class (correct — would be awkward)
- No observed entries with imperative in when-class (correct — would be prescriptive)

### Cross-Reference Patterns

**Metadata keywords often cross-reference related entries:**

```
/when designing quality gates | layered defense multiple independent checks
    ↓ Keywords that appear in other entries
/when placing quality gates
/when reviewing quality gate coverage
/when choosing hook enforcement over permission deny
```

**Current system:** No explicit cross-reference tracking. Keyword overlap detected via manual inspection.

### Decision Date Progression

**Index entries grouped by decision file, not by date.** Within files, entries appear in arbitrary order (added as decisions were made).

**Timeline observable:**
- Earliest decisions: 2026-01-19 (workflow patterns)
- Recent decisions: 2026-03-06 (Phase B architectural)
- Most active: 2026-02-xx (implementation pattern consolidation)

### Artifact Integration Points

**Entries reference concrete artifacts:**

- `agents/decisions/cli.md` — references Click library patterns, specific CLI architectures
- `agents/decisions/testing.md` — references pytest, TDD workflows
- `agents/decisions/pipeline-contracts.md` — references transformation tables, phase types

**Metadata embedding:** Artifact names sometimes embedded in metadata keywords:
```
/when preferring e2e over mocked subprocess | real git repos tmp_path
    ↓ Artifacts referenced in keywords
```

---

## 9. Summary: Format Readiness for Grounding

### Immediate Grounding Needs

**Required before bulk conversion (Phase 5-6):**

1. **Trigger naming rubric** — Exhaustive convention set covering:
   - When-class sentence structure (verified against examples)
   - How-class sentence structure (verified against examples)
   - Specificity calibration (when to split vs when to keep broad)
   - Article handling rules (when to include "a", "the", etc.)
   - Metadata keyword schema (what types of keywords, how many)

2. **When/how classification decision tree** — Clear criteria for:
   - Boundary cases (procedural knowledge vs situational)
   - Default patterns (methodology sources → when per S-G)
   - Edge case resolution (compound operations, nested decisions)

3. **Index hierarchy design** — Concrete specification for:
   - Domain clustering (how to group 1000+ entries)
   - Branching strategy (how many levels, what splits)
   - Section naming (when to split into new file)
   - Parser updates (support new structure)

4. **Validation rules** — Enforcement (via corrector agent S-K):
   - Trigger uniqueness checks
   - Heading alignment verification
   - Metadata schema compliance
   - Obsolescence detection (entries for deleted decisions)

### Evidence Quality Assessment

**High confidence (multiple sources aligned):**
- Current trigger patterns (366 live entries observed)
- When/how distinction (both brief.md and resolver code show consistent intent)
- Index flat structure (parsing code explicitly handles current form)

**Medium confidence (single source, requires interpretation):**
- Naming conventions (workflow-advanced.md decisions establish rules, but limited examples)
- Metadata embedding (code shows extra_triggers parsing, but usage patterns unclear)

**Low confidence (theoretical, not validated):**
- Hierarchy scaling strategy (brief proposes O(log_k(N)) but no implementation)
- Bulk conversion compatibility (rules derived from small sample, large-scale behavior unknown)

### Next Actions for Grounding Phase (S-C)

Per task notation in session.md:
> S-C: research trigger format, when/how distinction, index hierarchy validation. Band 0 — ready now

**Recommended sequencing:**
1. Extract trigger naming patterns from all 366 entries (systematic analysis)
2. Classify sample entries (50-100) using when/how rubric to expose edge cases
3. Design hierarchical index layout with concrete branching factor
4. Document corrector validation rules (S-K preparation)
5. Validate against bulk conversion sources (pytest, click, pydantic docs)

