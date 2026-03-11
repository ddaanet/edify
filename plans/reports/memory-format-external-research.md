# External Research: Knowledge Retrieval Key Design for Agent Memory

Research into established frameworks for retrieval key design, knowledge classification, hierarchical indexing, LLM agent memory architecture, and entry metadata schemas.

---

## 1. Trigger / Retrieval Key Design

### Cognitive Science: Encoding Specificity Principle (Tulving & Thomson, 1973)

A retrieval cue is effective when it matches the context in which information was originally encoded. The cue must reactivate a neural pattern similar to the encoded pattern.

**Key principles for retrieval key design:**

- **Encoding-retrieval overlap**: Cues work when they match the situation where the knowledge was stored. For agent memory: triggers should describe the *situation of need*, not just the topic of the knowledge.
- **Cue overload principle**: A cue loses effectiveness when linked to too many memories. A trigger that matches 50 entries is as useless as one that matches none. Effective triggers are *discriminating* — they match one or few entries in the target set.
- **Dynamic cueing hypothesis**: Effective cues must align with the *current state* of the memory, not just the original encoding. As knowledge evolves, retrieval keys may need updating.

**Implications for agent memory:** Triggers phrased as "when X happens" encode the *situation of need* — the context where the knowledge becomes relevant. This is encoding-specificity applied: the trigger matches the future retrieval context (the agent encountering situation X), not the knowledge content itself.

Sources:
- [Encoding Specificity Principle - The Decision Lab](https://thedecisionlab.com/reference-guide/psychology/encoding-specificity-principle)
- [Encoding Specificity Principle - Wikipedia](https://en.wikipedia.org/wiki/Encoding_specificity_principle)

### Case-Based Reasoning: Indexing Vocabulary (Kolodner, 1993; Schank, 1982)

CBR systems face the same problem: how do you index a "case" (past experience) so it's retrieved when a relevantly similar new situation arises?

**Kolodner's qualities of good indexes:**

- **Predictive**: Indexes predict a case's *usefulness* — they describe what tasks the case can address, not what the case contains. An index answers "when would this case help?" not "what is this case about?"
- **Abstract enough**: To retrieve in a variety of future situations (not over-specific to one context)
- **Concrete enough**: To be easily recognizable in future situations (not so abstract as to match everything)
- **Functional approach**: Examine what each case accomplishes and how it must be described to remain accessible
- **Reminding approach**: Study how experts naturally recall past experiences — which features of a new situation trigger relevant memories

**Indexing vocabulary structure**: Two components — *descriptive dimensions* (the facets along which cases vary) and *values* assigned to each dimension. Together these create a framework for organizing and retrieving cases.

**Predictive features hypothesis**: The most useful indices predict potential problems and access plans that help avoid failures. Indices are not descriptions of content but predictions of when the case will be useful.

**Implications for agent memory:** The "when" trigger format directly implements Kolodner's predictive indexing. "When parsing JSONL message content" predicts the *situation* where this knowledge helps, not the knowledge topic. The quality criteria (abstract-enough, concrete-enough, discriminating) provide evaluation dimensions for trigger design.

Sources:
- [Kolodner 1996 Tutorial Introduction to CBR (summary)](http://www.jimdavies.org/summaries/kolodner1996-2.html)
- [CBR: Foundational Issues - Springer](https://link.springer.com/article/10.1007/BF00155578)
- [Predictive Features in Indexing - Machine Learning](https://link.springer.com/article/10.1023/A:1022678818081)

### Knowledge Base Naming Conventions (Industry Practice)

Industry knowledge bases use naming conventions optimized for human browsing:

- **Hierarchical path naming**: "HR > Benefits > Health Insurance Overview" — structured, consistent
- **5-7 broad categories** with logical subcategories (not 20 top-level categories)
- **Action-oriented titles**: Describe what the article helps you *do*, not what it *contains*
- **Consistent terminology**: Same feature/concept uses the same name everywhere

**Limitations for agent retrieval:** Industry KB naming optimizes for browsing (human scanning a list) not for semantic matching (agent resolving a situation against triggers). The action-oriented principle transfers, but the hierarchical path structure is a navigation aid, not a retrieval mechanism.

Sources:
- [KnowledgeOwl: KB Naming Conventions](https://www.knowledgeowl.com/blog/posts/knowledge-base-naming-conventions)
- [MatrixFlows: KB Taxonomy Design Principles](https://www.matrixflows.com/blog/10-best-practices-for-creating-taxonomy-for-your-company-knowledge-base)

---

## 2. Procedural vs Situational Knowledge Classification

### Anderson's ACT-R (Adaptive Control of Thought—Rational)

ACT-R divides knowledge into two irreducible types:

| Type | Representation | Example |
|------|---------------|---------|
| **Declarative** | Semantic net of propositions, images, sequences | "Python uses indentation for blocks" |
| **Procedural** | Production rules (IF condition THEN action) | IF goal is to parse JSON AND input has nested arrays THEN use recursive descent |

**Production rules** are the core unit: each has conditions (pattern to match in declarative memory) and actions (what to do). Retrieval is activation-based — units are selected based on statistical fit to the current context.

**Implication:** Production rules are structurally similar to "when X, do Y" entries. The condition side IS the retrieval trigger; the action side IS the knowledge payload. ACT-R validates the when/how separation as cognitively fundamental.

Sources:
- [ACT-R - Wikipedia](https://en.wikipedia.org/wiki/ACT-R)
- [ACT-R Theory - InstructionalDesign.org](https://www.instructionaldesign.org/theories/act/)

### Revised Bloom's Taxonomy: Knowledge Dimension (Anderson & Krathwohl, 2001)

Four knowledge types on a concrete-to-abstract continuum:

| Type | Definition | Agent Memory Analog |
|------|-----------|-------------------|
| **Factual** | Terminology, specific details, elements | Configuration values, API signatures |
| **Conceptual** | Categories, principles, theories, models | Architecture decisions, design patterns |
| **Procedural** | Techniques, methods, criteria for when to use them | How-to knowledge, algorithms, workflows |
| **Metacognitive** | Strategic knowledge, conditional knowledge, self-knowledge | When-to-apply knowledge, context-sensitivity rules |

**Conditional knowledge** lives within the metacognitive dimension — it's "knowledge about cognitive tasks, including appropriate contextual and conditional knowledge." This is the "when and why to apply" layer that sits above procedural "how to" knowledge.

**Implication:** The project's knowledge entries mix procedural ("anti-pattern/correct-pattern") with conditional ("when X happens, apply Y"). Bloom's taxonomy suggests these are distinct cognitive types requiring different retrieval strategies — conditional knowledge needs *situation matching*, procedural knowledge needs *task matching*.

Sources:
- [Bloom's Taxonomy Knowledge Dimension - National University LibGuide](https://resources.nu.edu/c.php?g=1417092&p=10504052)
- [Learning Theories: Types of Knowledge](https://www.learning-theories.org/doku.php?id=knowledge_assessment:types_if_knowledge)

### Educational Psychology: Declarative / Procedural / Conditional

The three-part taxonomy from educational psychology:

- **Declarative**: Knowing *that* (facts, concepts)
- **Procedural**: Knowing *how* (steps, methods, techniques)
- **Conditional**: Knowing *when and why* (strategic application, context sensitivity)

Conditional knowledge represents higher-order thinking — students who only develop declarative and procedural knowledge lack the ability to apply knowledge strategically in novel contexts.

**Implication:** The "when" trigger format encodes conditional knowledge — it captures the *conditions under which* procedural knowledge applies. An entry with trigger "when Edit tool fails repeatedly" and body "stop after second identical error" packages conditional knowledge (when) wrapping procedural knowledge (what to do). This is the correct structure per educational psychology — the conditional layer serves as the retrieval index for the procedural payload.

Sources:
- [Educational Psychology - Lumen Learning](https://courses.lumenlearning.com/suny-oneonta-education106/chapter/5-4-educational-psychology/)
- [4 Types of Knowledge - LearningStrategist](https://learningstrategist.org/2018/03/01/4-types-of-knowledge/)

---

## 3. Hierarchical Index Design

### Faceted Classification (Ranganathan; Denton)

**PMEST categories** — five universal facets for any domain:
- **Personality**: The primary subject/entity
- **Matter**: Material/composition
- **Energy**: Processes, activities, operations
- **Space**: Location/context
- **Time**: Temporal dimension

**Design methodology** (Denton's 7-step process):
1. Collect representative domain entities
2. Break descriptions into component concepts
3. Identify high-level facets across entities
4. Arrange foci within facets, test completeness
5. Establish citation order (default facet sequence)
6. Apply classification to all entities
7. Revise and maintain

**Key design principles:**
- **Mutual exclusivity**: Each facet represents one characteristic only
- **Relevance**: Facets reflect classification purpose and user needs
- **Ascertainability**: Properties must be verifiable/definite
- **Permanence**: Represent stable qualities
- Use faceted classification when 3+ independent dimensions exist; simpler structures (trees, hierarchies) for fewer dimensions

**Implication:** The project's knowledge index could use faceted classification for entries with multiple independent dimensions (topic area, knowledge type, situational context). But the current "when X" trigger format is essentially single-dimension (situational context only). Faceted classification adds value when entries need retrieval along multiple axes — by topic AND by situation AND by knowledge type.

Sources:
- [How to Make a Faceted Classification - Denton](https://www.miskatonic.org/library/facet-web-howto.html)
- [Faceted Classification - Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification)

### Miller's Law: 7 +/- 2 and Chunking

The average person holds 7 +/- 2 items in working memory. A "chunk" is a meaningful unit — grouping elements into chunks increases effective capacity.

**Application to index design:**
- Organize categories into 5-9 items per level for human navigability
- Chunking categories logically increases recall
- The principle governs *cognitive load during navigation*, not storage capacity
- For agent retrieval: Miller's law constrains *index browsability* (how many items an LLM can meaningfully compare in a single context window pass), not the total index size

**Implication:** If an LLM resolves triggers by scanning an index, the branching factor at each level should stay within cognitive/attention limits. For an LLM with a context window, this translates to: how many index entries can be meaningfully compared in a single pass? The answer depends on entry length and model attention, not a fixed number. But the principle of chunking into meaningful groups remains valid.

Sources:
- [Miller's Law - Laws of UX](https://lawsofux.com/millers-law/)
- [7 Plus or Minus 2 Rule & Chunking](https://instructionaldesignjunction.com/2021/08/23/george-a-millers-7-plus-or-minus-2-rule-and-simon-and-chases-chunking-principle/)

### Hierarchical RAG Indices

In retrieval-augmented generation, hierarchical indices organize documents at multiple granularity levels:

- **Summary level**: High-level document/section summaries
- **Chunk level**: Specific passages with embeddings
- **Retrieval flow**: Query matches summary first, then drills into relevant chunks

Branching factor can be fixed (B-tree style) or data-driven (clustering with adaptive splits). The key design choice is whether nodes are *routing nodes* (pure indices, no content) or *mixed nodes* (contain both content and child references).

**Implication:** The project's index hierarchy (root index > topic indices > entries) is a two-level routing hierarchy. The research supports clean separation: branch nodes route, leaf nodes contain content. Mixed nodes (both entries and child references) create discoverability imbalance — already identified as an anti-pattern in the project's learnings.

Sources:
- [Hierarchical Indexing - EmergentMind](https://www.emergentmind.com/topics/hierarchical-indexing-hiindex)

---

## 4. LLM Agent Memory Systems

### MemGPT / Letta: OS-Inspired Memory Hierarchy

**Architecture** (three-tier):

| Tier | Analog | Contents | Access |
|------|--------|----------|--------|
| **Core memory** | RAM | In-context blocks (user, persona, task) | Always visible in prompt |
| **Recall memory** | Disk (logs) | Full conversation history | Keyword/time search via tool calls |
| **Archival memory** | Disk (knowledge) | Processed, indexed knowledge | Semantic search via tool calls |

**Key design decisions:**
- Agents *self-manage* memory via tool calls (`conversation_search`, `archival_memory_search`, `core_memory_append`, `core_memory_replace`)
- Eviction at ~70% capacity triggers summarization of older messages
- Core memory blocks have labels, descriptions, values, and character limits
- Recall vs archival distinction: raw history vs processed knowledge

**Implication:** The project's recall system is closest to Letta's "archival memory" — processed knowledge indexed for semantic retrieval. The trigger-based retrieval (`when X`) is a structured alternative to embedding-based semantic search. Letta's label/description/value structure for core memory blocks parallels the project's trigger/body structure for entries.

Sources:
- [Letta: Agent Memory](https://www.letta.com/blog/agent-memory)
- [Letta Docs: Memory Management](https://docs.letta.com/advanced/memory-management/)
- [MemGPT as Operating System - Leonie Monigatti](https://www.leoniemonigatti.com/papers/memgpt.html)

### A-MEM: Zettelkasten-Inspired Agent Memory

**Memory note structure** (7 components):

| Field | Purpose |
|-------|---------|
| Original content | Raw interaction data |
| Timestamp | When stored |
| Keywords | LLM-generated key concepts |
| Tags | LLM-generated categorical labels |
| Contextual description | Rich semantic summary |
| Dense vector | Embedding for similarity search |
| Links | Bidirectional connections to related notes |

**Retrieval**: Cosine similarity between query embedding and note vectors (k=10). Retrieved notes automatically surface linked neighbors.

**Connection formation**: New notes trigger link generation — embedding pre-filter finds nearest neighbors, LLM evaluates "potential common attributes," meaningful connections established bidirectionally.

**Design principles from Zettelkasten:**
- Atomic notes (one idea per note)
- Flexible linking (notes can belong to multiple "boxes"/clusters)
- Continuous evolution (links updated as new notes arrive)

**Implication:** A-MEM's dual retrieval (embedding similarity + keyword/tag attributes) is relevant. The project's triggers serve as the "keyword" equivalent — structured text enabling attribute-based discovery alongside any embedding similarity. The Zettelkasten principle of atomic notes aligns with the project's one-learning-per-entry pattern. A-MEM's LLM-generated metadata (keywords, tags, descriptions) suggests that trigger generation could be LLM-assisted rather than purely manual.

Sources:
- [A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/html/2502.12110v11)

### Mem0: Graph-Based Memory

Mem0 dynamically extracts, consolidates, and retrieves salient information from conversations using graph-based representations to capture relational structures.

### Design Pattern Taxonomy (Serokell, 2024)

Four paradigms for LLM long-term memory:

| Pattern | Key Mechanism | Index Strategy |
|---------|--------------|----------------|
| **OS paradigm** (MemGPT) | Hierarchical memory tiers, self-managed paging | Function-call retrieval, FIFO buffer |
| **Product-first** (OpenAI) | Global user-centric memory, hybrid storage | Parallel fact + semantic search |
| **User-controlled** (Claude) | Project-scoped, version-controlled context files | Explicit user management, keyword search |
| **Toolkit** (LangChain etc.) | Pluggable primitives, developer-composed | Vector/graph/KV stores, custom extractors |

**Emerging trends:**
- Unstructured snippets → knowledge graph structures
- Single-agent → multi-agent shared memory
- Untyped → strict typing with audit trails
- Direct context → autonomous memory orchestration

**Implication:** The project sits in the "user-controlled" paradigm (CLAUDE.md, explicit management) but the recall system adds elements of the OS paradigm (structured retrieval via triggers). The trend toward strict typing and knowledge graphs supports the project's move toward structured entry formats with explicit metadata.

Sources:
- [Serokell: Design Patterns for Long-Term Memory](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures)
- [Mem0 Paper](https://arxiv.org/abs/2504.19413)

---

## 5. Embedded Metadata for Knowledge Entries

### Dublin Core Metadata Element Set

15 core elements for resource description, designed for simplicity and interoperability:

| Element | Relevance to Knowledge Entries |
|---------|-------------------------------|
| **Title** | Entry trigger / retrieval key |
| **Subject** | Topic area / category tags |
| **Description** | Entry body / knowledge payload |
| **Type** | Knowledge type (procedural, conditional, factual) |
| **Date** | When entry was created/last modified |
| **Source** | Evidence / originating session |
| **Relation** | Links to related entries |
| **Coverage** | Scope / applicability bounds |

**Design philosophy**: Keep metadata "as small and simple as possible to allow a non-specialist to create simple descriptive records easily and inexpensively, while providing for effective retrieval."

**Implication:** Dublin Core's minimalism is instructive. Not every entry needs all 15 fields. The project's current format (trigger + body) maps to Title + Description. Adding Subject (topic tags) and Type (knowledge classification) would be the highest-value metadata additions per Dublin Core's design philosophy.

Sources:
- [Dublin Core Metadata Basics](https://www.dublincore.org/resources/metadata-basics/)
- [Using Dublin Core](https://www.dublincore.org/specifications/dublin-core/usageguide/)

### Keyword Extraction Methods

For automatically generating metadata tags from entry content:

| Method | Approach | Characteristics |
|--------|----------|----------------|
| **TF-IDF** | Statistical frequency vs corpus frequency | Domain-dependent, needs corpus |
| **RAKE** | Co-occurrence of content words | Domain-independent, fast, unsupervised |
| **TextRank** | Graph-based word importance | Balanced precision/recall |
| **YAKE** | Statistical features without corpus | Outperforms TF-IDF and RAKE on benchmarks |
| **LLM-based** | Prompt LLM to extract keywords | Highest semantic quality, highest cost |

**Implication:** For the project's knowledge entries, LLM-based extraction is the natural fit — entries are already processed by an LLM during creation. A-MEM validates this approach (LLM-generated keywords and tags). The cost concern is minimal since entries are written infrequently. RAKE/YAKE could serve as a fallback for batch processing existing entries.

Sources:
- [Automated Keyword Extraction - TF-IDF, RAKE, TextRank](https://www.tiernok.com/posts/automated-keyword-extraction-tf-idf-rake-and-textrank.html)
- [Keyword Extraction Methods in NLP - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2022/03/keyword-extraction-methods-from-documents-in-nlp/)

---

## Synthesis: Frameworks Applied to Project Needs

The project's knowledge system stores conditional knowledge ("when X, do Y") in a hierarchical index resolved by an LLM agent. Research findings converge on several validated design principles:

### Trigger Format Validation

The "when X" trigger format is independently validated by three frameworks:
- **Encoding specificity** (cognitive science): Triggers should encode the *retrieval context* (situation of need), not the knowledge topic
- **CBR predictive indexing** (Kolodner): Indices should predict a case's *usefulness* — "when would this help?" not "what is this about?"
- **ACT-R production rules** (Anderson): The condition side of IF-THEN rules IS the retrieval mechanism — conditions match the current situation to select applicable productions

### Trigger Quality Criteria

From CBR indexing vocabulary and cue overload principle:
- **Discriminating**: A trigger that matches too many entries is overloaded (cue overload principle). Each trigger should select a small set.
- **Abstract enough**: Not so specific that it only matches one exact situation
- **Concrete enough**: Not so abstract that it matches everything ("when coding" is useless)
- **Predictive**: Describes the situation where knowledge helps, not the knowledge content
- **Recognizable**: Uses vocabulary the retrieving agent will naturally encounter in the matching situation

### Knowledge Classification

Entries should distinguish knowledge types (Bloom's taxonomy + educational psychology):
- **Conditional**: "When X happens, apply Y" — situation-indexed, the primary format
- **Procedural**: "How to do X" — task-indexed, complements conditional
- **Conceptual**: Architecture decisions, design principles — topic-indexed
- **Factual**: Configuration values, API details — reference-indexed

Different types may benefit from different retrieval strategies (situation matching vs task matching vs topic lookup).

### Index Hierarchy Design

From faceted classification and hierarchical RAG:
- **Clean separation**: Branch nodes (routing only) vs leaf nodes (entries only) — no mixed nodes
- **Branching factor**: 5-9 items per level for navigability (Miller's law applied to LLM attention)
- **Facets when needed**: If entries need retrieval along multiple independent dimensions, use faceted classification rather than forcing a single hierarchy
- **Depth vs breadth**: Two levels (root > topic > entries) is validated by RAG research as sufficient for moderate collections; add depth only when a topic exceeds the branching factor

### Metadata Schema

From Dublin Core minimalism and A-MEM's note structure:
- **Minimum viable metadata**: Trigger (retrieval key) + body (knowledge payload) — the current format
- **High-value additions**: Topic tags (subject), knowledge type classification, evidence/source reference
- **LLM-generated metadata**: Keywords and tags generated at write time (A-MEM pattern) provide retrieval enrichment at low marginal cost
- **Link structure**: Bidirectional connections between related entries (A-MEM/Zettelkasten) could improve recall by surfacing related knowledge
