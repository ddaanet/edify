# Memory Format Grounding: Format Specification

**Grounding:** Strong — three independent cognitive science/KM frameworks converge on the trigger format design; two educational psychology taxonomies validate the when/how distinction; hierarchical RAG research and faceted classification validate index hierarchy decisions.

**Consumers:** S-G extraction agent (trigger generation), S-K corrector (validation criteria), S-E metadata model, S-D index hierarchy design.

**Branch artifacts:**
- `plans/reports/memory-format-internal-codebase.md` — codebase pattern inventory
- `plans/reports/memory-format-external-research.md` — framework research

---

## 1. Trigger Format Specification

### Theoretical Foundation

LLMs have strong procedural knowledge from training data but weak conditional knowledge — they know *how* to do things but fail to recognize *when* to apply that knowledge. Spontaneous recall rates are low (~3% self-retrieval in this project's measurements), which is why structured retrieval pipelines exist: they inject the situational recognition that models lack. The memory system is predominantly when-class (304/367 entries) because conditional knowledge is the gap.

Effective retrieval cues encode the *situation of need*, not the knowledge topic. Three frameworks converge:

- **Encoding specificity** (Tulving & Thomson, 1973): A retrieval cue works when it matches the context where the knowledge was originally encoded. Triggers phrased as situations ("when X happens") encode the future retrieval context.
- **CBR predictive indexing** (Kolodner, 1993): Good indices predict a case's *usefulness* — "when would this help?" not "what is this about?" The predictive features hypothesis: the most useful indices predict potential problems and access plans to avoid failures.
- **ACT-R production rules** (Anderson): IF-condition-THEN-action rules — the condition side IS the retrieval mechanism. Conditions match the current situation to select applicable productions.

**Project validation:** The existing "when X" format directly implements all three principles. 366 entries demonstrate the pattern works empirically. The format encodes applicability conditions, not content descriptions.

### Trigger Syntax

**When-class (conditional knowledge):**

```
- when [present-participle] [object]
```

- Present participle verb names the *activity at the decision point*
- Object specifies the domain narrowly enough to discriminate
- No articles unless required for grammatical clarity
- Use broadest applicable verb (not hyper-specific outcome)

Examples (validated from codebase):
- `- when designing quality gates` — activity + domain
- `- when placing helper functions` — activity + object
- `- when handling malformed session data` — activity + failure condition

**How-class (procedural knowledge):**

```
- how [verb] [object]
```

- Verb form: pending grounding (bare imperative "format" vs natural infinitive "to format"). Measurement task: fuzzy match score comparison + agent query log analysis via session scraper
- Object specifies the operation scope

Examples (validated from codebase):
- `- how format runbook phase headers` — verb + object
- `- how split test modules` — verb + object
- `- how merge templates safely` — verb + object + manner

### Trigger Quality Criteria

Derived from CBR indexing vocabulary (Kolodner) and cue overload principle (Tulving):

| Criterion | Definition | Test |
|-----------|-----------|------|
| **Discriminating** | Trigger selects a small entry set, not dozens | Would an agent working on 3+ unrelated tasks match this trigger? If yes, too broad |
| **Abstract enough** | Retrieves across a variety of future situations | Would minor variation in the situation (different file, different tool) still match? If no, too specific |
| **Concrete enough** | Recognizable in the matching situation | Would an agent encountering the situation use these words naturally? If no, vocabulary mismatch |
| **Predictive** | Describes when knowledge helps, not what it contains | Does the trigger describe a situation or a topic? Topics are not triggers |
| **Recognizable** | Uses vocabulary the retrieving agent naturally encounters | Are the keywords domain terms the agent would see in context (error messages, tool names, code patterns)? |

**Specificity calibration:** Triggers should target N-M invocation contexts (default 3-20, calibrate against dataset). Below N is over-specific (won't be found); above M approaches cue overload (too many matches dilute signal). Thresholds are user-configurable.

### Naming Conventions

Consolidated from codebase analysis (workflow-advanced.md decisions) and CBR quality criteria:

1. **Activity at decision point** — name the activity, not the outcome. "When choosing" not "when the choice is made"
2. **Broadest applicable verb** — "when handling" covers more future situations than "when fixing the specific edge case in"
3. **No self-assessment terms** — no "correctly", "properly", "best way to". The entry content provides the quality guidance
4. **No articles** unless grammatically required — "when placing functions" not "when placing the functions"
5. **Present participle for when-class** — establishes ongoing activity context. "When designing" not "when designed" or "when to design"
6. **Verb form for how-class** — pending grounding. Bare imperative ("how format") vs natural infinitive ("how to format"). Not gerund ("how formatting"). Measurement needed: fuzzy match scores, agent query logs, retrieval accuracy
7. **Domain terms over synonyms** — use the term that appears in the codebase/toolchain. "pytest fixtures" not "test setup utilities"

### Format Drift Patterns (Anti-patterns)

Observed in codebase analysis; corrector (S-K) should flag these:

| Drift | Example | Correction |
|-------|---------|------------|
| Article insertion | "when placing the helper functions" | "when placing helper functions" |
| Verb tense drift | "when vet flags unused code" | "when vetting flags unused code" or reframe |
| Outcome framing | "when edit tool reports stale success" | "when debugging edit tool failures" (activity framing) |
| Adverb insertion | "how format batch edits efficiently" | "how format batch edits" (efficiency is content, not trigger) |
| Over-specific condition | "when fixture shadowing creates dead code" | "when test utilities shadow functions" (broader recognition) |

---

## 2. When/How Classification

### Theoretical Foundation

The when/how distinction maps onto an established cognitive taxonomy from educational psychology:

- **Conditional knowledge** (knowing *when and why*): Strategic application knowledge — "in this situation, apply this principle." Bloom's revised taxonomy places this in the metacognitive dimension. ACT-R encodes it as production rule conditions. This is `when`-class.
- **Procedural knowledge** (knowing *how*): Steps, methods, techniques for accomplishing tasks. Bloom's places this as its own dimension. ACT-R encodes it as production rule actions. This is `how`-class.

The distinction is cognitively fundamental (ACT-R, Bloom's, educational psychology all identify it independently). It is not a project convention — it reflects how human and agent cognition processes different knowledge types differently.

**Project validation:** Current 366 entries show 85-90% naturally follow when/how patterns. Edge cases exist but are resolvable (see classification rubric below).

### Classification Rubric

**Primary test: What does the retrieving agent need?**

| Agent need | Classification | Trigger form |
|-----------|---------------|--------------|
| "I'm in situation X — what should I do?" | Conditional (`when`) | `- when [situation]` |
| "I need to accomplish task Y — how?" | Procedural (`how`) | `- how [task]` |

**Decision tree for edge cases:**

```
Is the core value in WHEN to apply this, or HOW to do it?
├── When to apply → when-class
│   (Even if body includes procedural steps — the trigger is the situation)
├── How to do → how-class
│   (Even if body includes when-to-use guidance — the trigger is the task)
└── Genuinely both → Split into two entries
    (when-entry for the condition, how-entry for the procedure)
```

**Default classifications by source type:**

| Source type | Default class | Rationale |
|------------|---------------|-----------|
| Pattern/anti-pattern catalogs | `when` | The model knows how to implement patterns from training; value-add is the situational trigger (from S-G brief discussion) |
| API reference documentation | `how` | Task-oriented: "how to use X API" |
| Configuration/setup guides | `how` | Procedural steps |
| Architecture decisions | `when` | Situational: "when choosing X over Y" |
| Failure/debugging knowledge | `when` | Situational: "when encountering X failure" |
| Style/convention guides | `when` | Situational: "when writing X" — the convention IS the situation recognition |

### Edge Case Resolution

**Compound operations:** "When delegating TDD cycles to test-driver" — is this situational or procedural?
- **Test:** Does the value lie in *recognizing when to delegate* or *how to delegate*?
- If the entry is about conditions for delegation → `when`
- If the entry is about delegation mechanics → `how`
- If both → split: `- when delegating TDD cycles` + `- how delegate to test-driver`

**Procedural guidelines that feel situational:** "How write init files" — could be "when needing a module structure"
- **Test:** Is the trigger "I need to write an init file" (task) or "I'm structuring a module" (situation)?
- Documentation headings using "How to" form → `how` (task-oriented retrieval)

---

## 3. Index Hierarchy Specification

### Theoretical Foundation

- **Hierarchical RAG research:** Two-level routing (root → topic → entries) is sufficient for moderate collections. Branch nodes route, leaf nodes contain content. Mixed nodes create discoverability imbalance.
- **Miller's Law applied to LLM attention:** 5-9 items per level for meaningful comparison in a single context-window pass. The constraint is attention-based comparison, not storage.
- **Faceted classification** (Ranganathan): Use multiple independent dimensions only when entries require multi-axis retrieval. Single-dimension hierarchies (by topic domain) are simpler and sufficient when the primary retrieval axis is situational context.

### Hierarchy Design

**Structure:** Two-level routing hierarchy (extensible to three when a domain exceeds branching factor).

```
Root index (branch node — routing only)
├── Domain A index (leaf node — entries only)
├── Domain B index (leaf node — entries only)
├── Domain C/ (branch node — routing, when domain is large)
│   ├── Sub-domain C1 index (leaf node)
│   └── Sub-domain C2 index (leaf node)
└── ...
```

**Node types (no mixing):**
- **Branch node:** Contains only references to child nodes. No entries. Format: list of `[domain-name](path-to-child)` with optional 1-line domain description.
- **Leaf node:** Contains only entries. No child references. Format: entries with trigger syntax and metadata keywords.

**Branching factor targets:**
- Root level: 5-15 domain pointers (current codebase has ~25 decision files; some can merge into domains)
- Domain level: 10-40 entries per leaf (current average: ~15; scaling target accommodates bulk conversion growth)
- Split trigger: When a leaf exceeds 40 entries, split into sub-domains with a branch node

**Domain mapping from current structure:**
Current `agents/memory-index.md` sections (H2 headings = decision file paths) serve as natural domain boundaries. The domain name should be the *topic area*, not the file path:
- `agents/decisions/cli.md` → domain: `cli`
- `agents/decisions/testing.md` → domain: `testing`
- `agents/decisions/orchestration-execution.md` → domain: `orchestration`

**Naming convention for domain paths:**
- Space → `-` (compound noun): `defense-in-depth`
- No nesting encoded in name — hierarchy is structural (directory), not nominal

### Parser Requirements

- Detect node type (branch vs leaf) from content structure (presence of child links vs entry lines)
- Recursive traversal at arbitrary depth
- Entry format unchanged within leaf nodes
- Root entry point: single file path (configurable, defaults to `memory/index.md`)

---

## 4. Embedded Metadata Schema

### Theoretical Foundation

- **Dublin Core minimalism:** "As small and simple as possible." Not every entry needs all fields. Current trigger + body maps to Title + Description — the minimum viable format.
- **A-MEM pattern** (Zettelkasten-inspired): LLM-generated keywords and tags at write time. Dual retrieval: keyword-based (structured) alongside similarity-based (semantic). Atomic notes (one idea per entry).
- **RAKE/YAKE for batch processing:** Statistical keyword extraction as fallback for migrating existing entries without LLM cost per entry.

### Metadata Fields

**Entry format in leaf index files:**

```
- when [trigger text] | [keyword1] [keyword2] [keyword3] ...
```

The pipe-separated keywords are the embedded metadata. This format is already in use (codebase analysis confirmed `extra_triggers` parsing). The specification formalizes what's currently ad-hoc:

| Field | Location | Required | Purpose |
|-------|----------|----------|---------|
| **List marker** | `- ` prefix | Yes | Markdown list structure |
| **Operator** | `when` or `how` (lowercase, no `/`) | Yes | Knowledge type classification |
| **Trigger** | After operator | Yes | Primary retrieval key (situational/task description) |
| **Keywords** | After `\|` separator | Yes (for new entries) | Disambiguation terms, domain vocabulary, related concepts |

**Keyword guidelines:**
- 3-7 keywords per entry (enough to disambiguate, not so many as to dilute)
- Include domain terms not in the trigger text (expanding retrieval surface)
- Include concrete artifacts where applicable (tool names, file patterns, error messages)
- No stopwords, no trigger word repetition
- Keywords are retrieval enrichment, not content summary

**Generated vs authored:**
- **New entries (S-G pipeline, S-L capture-time):** LLM generates keywords at write time — highest semantic quality, negligible marginal cost since LLM is already processing the entry
- **Existing entries (migration):** Current pipe-separated keywords are retained. Entries without keywords get statistical extraction (RAKE/YAKE batch) or LLM enrichment during migration

### Index Generation

The index is a *generated artifact*, not hand-maintained (per brief.md architectural decision). Build step:

1. Read all entry files from `memory/` hierarchy
2. Extract trigger + keywords from each entry's metadata block
3. Generate leaf index files (grouped by domain)
4. Generate branch index files (domain routing)
5. Deterministic: same inputs produce same outputs

**Implication for S-K corrector:** Corrector validates the *entry file* (source of truth), not the *generated index*. Index quality is a function of entry quality + build step correctness.

---

## 5. Validation Rules (S-K Corrector Criteria)

All rules are errors (blocking). Agents ignore warnings — a non-blocking flag is no flag. Rules with thresholds require calibration against the 366-entry dataset before activation; all thresholds are user-configurable with feedback pipeline for ongoing calibration.

### Trigger Validation

| Rule | Check | Threshold |
|------|-------|-----------|
| **Discriminating** | Trigger does not match >N existing entries by keyword overlap | N=20 — calibrate against dataset |
| **Not over-specific** | Trigger contains ≤N content words (excluding operator) | N=5 — calibrate against dataset |
| **Activity framing** | When-class trigger uses present participle verb | — |
| **Imperative framing** | How-class trigger uses bare imperative verb | — |
| **No self-assessment** | Trigger contains no adverbs (properly, correctly, efficiently, safely) | — |
| **No articles** | Trigger contains no articles (a, an, the) unless grammatically required | — |
| **Predictive** | Trigger describes situation/task, not topic or content | Requires LLM judgment |

### Classification Validation

| Rule | Check | Threshold |
|------|-------|-----------|
| **Correct class** | Entry classified as when/how matches classification rubric | — |
| **No class confusion** | When-entry body is not purely procedural without situational framing | — |

### Metadata Validation

| Rule | Check | Threshold |
|------|-------|-----------|
| **Keywords present** | Entry has ≥N keywords after pipe separator | N=3 — calibrate against dataset |
| **Keyword count** | Entry has ≤N keywords | N=7 — calibrate against dataset |
| **No trigger duplication** | Keywords don't repeat trigger words | — |
| **No stopwords** | Keywords contain no stopwords | — |

### Deduplication

| Rule | Check | Threshold |
|------|-------|-----------|
| **Trigger uniqueness** | No two entries have identical trigger text | — |
| **Semantic dedup** | No two entries in same domain have keyword overlap >N% | N=70 — calibrate against dataset (requires LLM judgment) |

### Entry Quality

| Rule | Check | Threshold |
|------|-------|-----------|
| **Atomic** | Entry addresses one decision/procedure, not a compound topic | — |
| **Documentation anchor** | Entry points to permanent documentation (decision file, methodology doc), not orphan index entry | — |
| **Heading alignment** | Trigger text maps to an actual heading in the referenced file | — |

### Threshold Calibration

All numeric thresholds (N values above) are ungrounded defaults requiring measurement:
- Measure actual distributions across the 366-entry dataset
- Set thresholds at natural breakpoints in measured distributions
- Ship as user-configurable defaults (not hardcoded)
- Feedback pipeline: corrector flags → user adjudicates → threshold adjusts

---

## Grounding Assessment

**Quality label: Strong**

**Evidence basis:**
- Three independent cognitive science/KM frameworks (encoding specificity, CBR predictive indexing, ACT-R production rules) converge on validating the trigger format — each derived independently, all point to situation-encoding as the correct retrieval key design
- Two educational psychology taxonomies (Bloom's revised, declarative/procedural/conditional) independently validate the when/how distinction as cognitively fundamental
- Hierarchical RAG research and faceted classification validate the branch/leaf separation and branching factor guidance
- Dublin Core + A-MEM validate the metadata minimalism approach
- 366 existing entries provide empirical validation of format viability

**What searches were performed:**
- Encoding specificity principle, cognitive retrieval cues
- Case-based reasoning indexing vocabulary, Kolodner predictive features
- ACT-R production rules, knowledge types
- Bloom's revised taxonomy knowledge dimension
- Procedural vs conditional knowledge educational psychology
- Faceted classification design principles, Ranganathan
- Miller's Law application to information architecture
- Hierarchical RAG index design, branching factor
- LLM agent memory architecture (MemGPT/Letta, A-MEM, Mem0)
- Dublin Core metadata, keyword extraction methods (RAKE, YAKE, TextRank)
- Knowledge base naming conventions industry practice

**Gaps remaining:**
- Branching factor 5-9 at root level is Miller's Law applied analogically to LLM attention — not empirically measured for this specific system. Measurement should occur during S-D implementation using actual token counts (S-A cache).
- All validation thresholds (keyword overlap 70%, specificity 3-20, keyword count 3-7, content words ≤5, discriminating >20) require calibration against the 366-entry dataset. Ship as user-configurable defaults with feedback pipeline. No threshold is grounded until measured.
- How-class verb form (bare imperative vs natural infinitive) requires grounding: fuzzy match score comparison, agent query log analysis via session scraper, retrieval accuracy observation. Decision suspended pending measurement.

---

## Sources

### Primary (framework originators)

| Source | Used for |
|--------|----------|
| Tulving & Thomson (1973) — Encoding Specificity Principle | Trigger format validation: cues encode retrieval context |
| Kolodner (1993) — Case-Based Reasoning indexing | Trigger quality criteria: predictive, discriminating, abstract/concrete balance |
| Anderson (1983) — ACT-R | When/how as production rule conditions/actions |
| Anderson & Krathwohl (2001) — Revised Bloom's Taxonomy | Knowledge dimension: conditional vs procedural |
| Ranganathan — Faceted Classification (PMEST) | Index hierarchy: faceted vs hierarchical, mutual exclusivity |
| Dublin Core Metadata Initiative | Metadata minimalism: smallest effective schema |

### Secondary (implementations, summaries)

| Source | Used for |
|--------|----------|
| [Letta/MemGPT](https://www.letta.com/blog/agent-memory) | LLM agent memory tiers, self-managed retrieval |
| [A-MEM](https://arxiv.org/html/2502.12110v11) | Zettelkasten-inspired LLM memory, LLM-generated keywords |
| [Serokell design patterns](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures) | LLM memory paradigm taxonomy |
| [Laws of UX — Miller's Law](https://lawsofux.com/millers-law/) | Branching factor guidance |
| [Denton — Faceted Classification How-To](https://www.miskatonic.org/library/facet-web-howto.html) | Classification design methodology |
| [KnowledgeOwl KB naming](https://www.knowledgeowl.com/blog/posts/knowledge-base-naming-conventions) | Industry naming conventions |

### Internal (codebase evidence)

| Source | Used for |
|--------|----------|
| `agents/memory-index.md` (366 entries) | Empirical trigger format patterns, frequency analysis |
| `src/claudeutils/when/resolver.py` | Heading construction, resolution chain |
| `src/claudeutils/recall/index_parser.py` | Keyword extraction, entry parsing |
| `agents/decisions/workflow-advanced.md` | Existing naming conventions (decision-2026-02-18, -02-24) |
| `plans/active-recall/brief.md` | Architectural decisions, embedded keywords design |
| `agents/learnings.md` | Hierarchical index anti-patterns (mixed nodes) |
