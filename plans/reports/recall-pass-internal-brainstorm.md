# Internal Recall Pass: Project-Specific Dimensions

Dimensions, constraints, desiderata, and evaluation axes for a multi-stage memory retrieval system integrated into the design-to-deliverable pipeline.

---

## 1. Structural Differences From Standard RAG

These properties make the recall pass fundamentally unlike vector-DB RAG systems and constrain the solution space.

### 1.1 Human-Curated Corpus, Not Embeddings

The memory corpus is 18 decision files (~4,540 lines), ~288-line memory index, ~28-line learnings buffer, plus ~1,958 lines of fragments. Total: ~6,800 lines. Each entry was written by a human or LLM with human review, organized into semantic sections with heading hierarchy. Retrieval is keyword-to-heading resolution, not nearest-neighbor in embedding space. This means recall quality depends on index key coverage and heading discoverability, not embedding model quality.

**Implication for recall pass:** The retrieval mechanism is deterministic (index lookup + fuzzy match), not probabilistic. False negatives come from missing index keys, not poor embedding quality. The recall pass must compensate for index sparsity at query time.

### 1.2 Multi-Agent Pipeline, Not Single-Turn Q&A

The consumer of recalled memory is not a user-facing chat — it's a chain of LLM agents with different models (opus/sonnet/haiku), different context windows, and different cognitive capabilities. Memory recalled at Pass 1 (design, opus) must remain useful when forwarded to Pass 3 (task agent, haiku). A haiku agent cannot re-evaluate whether a recalled decision is relevant — it will apply whatever is injected.

**Implication:** The recall artifact must be pre-filtered and pre-formatted per consumer capability. Injecting raw decision file excerpts into a haiku agent's prompt is worse than no injection — haiku treats injected context as instruction with recency bias (per `prompt-structure-research.md`: "persistent common context is stronger signal than one-time step file input").

### 1.3 Fire-and-Forget Agent Dispatch

Once an orchestrator dispatches a task agent, there is no mid-flight communication (`orchestration-execution.md`: "no mid-flight messaging available"). If the recall artifact is wrong (false positive), the agent cannot ask for clarification or request different memory. It either follows the injected guidance or ignores it. This makes false positive cost much higher than in interactive RAG where the user can say "that's not relevant."

### 1.4 Downstream Propagation Amplifies Errors

A false positive at Pass 1 (design recall) propagates through all 4 passes unless explicitly filtered. In standard RAG, each query is independent. Here, the recall artifact accumulates — Pass 2 inherits Pass 1, Pass 3 inherits 1+2. An irrelevant entry injected at Pass 1 consumes tokens at every subsequent stage. The cost is multiplicative, not additive.

---

## 2. Token Economy Constraints

### 2.1 Context Window Budget

The 200K token context window is shared between: system prompt (~43K tokens measured, per `orchestration-execution.md` measurement data), CLAUDE.md content (~15K tokens measured via `context-budget.py`), step file content, design reference, and the recall artifact. Available headroom for recall content: roughly 140K tokens minus step/design content.

**But this is misleading.** The effective budget is constrained by attention, not capacity. Per primacy/recency research (`prompt-structure-research.md`), content in the middle of context receives weakest attention. A recall artifact placed in the middle of a task agent's prompt (between system prompt and step instructions) falls in the "lost in the middle" zone.

**Dimension: Positional effectiveness.** Where in the agent prompt does the recall artifact appear? Primacy and recency positions are already claimed by system prompt and step instructions respectively. The recall artifact competes for limited effective attention.

### 2.2 Artifact Size vs. Agent Capability

- Opus can process ~5K tokens of recall context and correctly weight relevance
- Sonnet handles ~2K tokens reliably with clear structure
- Haiku needs <1K tokens, bulleted, with explicit applicability markers

These are ungrounded — no empirical measurement exists for this project's recall context. The dimension exists but thresholds need calibration.

### 2.3 Multiplicative Token Cost

If the recall artifact is R tokens, the total cost across a 20-step runbook with task injection (Pass 3) is approximately 20R (each agent loads it fresh — no cache sharing across Task agents). At R=2K tokens, that's 40K additional tokens per orchestration. At R=5K, it's 100K. The cache hit rate for task agents is unknown (main session cache is 94-100% after warmup, but each Task agent starts cold).

**Dimension: Per-agent cost ceiling.** The recall artifact token budget must account for multiplicative dispatch, not single-query cost. A "reasonable" 3K artifact becomes expensive at 20x replication.

---

## 3. Recall Artifact Format Dimensions

### 3.1 Reference vs. Content Injection

Two strategies:
- **Content injection:** Include the actual decision text in the artifact
- **Reference injection:** Include decision file path + heading, rely on agent to Read

Content injection is deterministic — the agent sees the content. Reference injection depends on the agent actually reading the reference. Task agents with constrained tool access may not have Read available (depends on agent definition). Haiku agents often skip optional reads.

**Dimension: Delivery guarantee.** Content injection guarantees the agent receives the memory. Reference injection saves tokens but creates a delivery gap. The current pipeline shows this exact failure mode: 2.9% recall rate when agents are expected to invoke `/when` proactively.

### 3.2 Structured vs. Prose Format

The memory index uses trigger-based keys (`/when writing mock tests`). The recall artifact could use:
- Raw decision text (prose paragraphs)
- Condensed bullet summaries
- Trigger-keyed entries (preserving index structure)
- Constraint format: "DO" / "DO NOT" rules extracted from decisions

For haiku consumption, constraint format is most effective (per `prompt-structure-research.md`: "Haiku: Explicit steps, markers, DO NOT examples"). For opus design recall, the full decision context with rationale is more useful.

**Dimension: Format per consumer tier.** The recall artifact needs model-appropriate formatting, not one-size-fits-all. This adds complexity to the artifact generation but directly affects recall effectiveness.

### 3.3 Applicability Scoping

Each recalled entry needs a scope signal: "This applies when [condition]." Without scoping, the agent applies every injected entry unconditionally. This is particularly dangerous with anti-pattern entries — haiku seeing "Anti-pattern: X" in context sometimes implements X (interpreting the negative example as the pattern to follow).

**Dimension: Conditional vs. unconditional injection.** Entries with anti-pattern examples need careful framing for weak models. Scope conditions must be explicit enough for haiku to correctly skip inapplicable entries.

---

## 4. Pass-Specific Dimensions

### 4.1 Pass 1: Design Recall

**Consumer:** Opus designer in main session.
**Available context:** Full 200K window, already loaded with CLAUDE.md (~15K), design problem statement.
**Memory access:** Can invoke `/when` and `/how` directly (has Skill tool). Can Read full decision files.

**Key question:** Does Pass 1 need to be a separate mechanism, or is the existing Documentation Checkpoint (design skill Phase A.1) sufficient? The design skill already specifies: "Check loaded memory-index context for entries related to the task domain. When entry is relevant, Read the referenced file."

**Dimension: Additive value over existing process.** Pass 1 must produce something the A.1 Documentation Checkpoint doesn't — otherwise it's ceremony for no benefit. The checkpoint is domain-keyword driven; the recall pass could be problem-statement driven (semantic matching against decision content, not just index keys).

**Unique contribution candidate:** Enumeration of relevant entries by name produces a recall artifact that downstream passes can inherit. The checkpoint doesn't produce a persistent artifact — its results live only in the designer's context window, lost at session boundary.

### 4.2 Pass 2: Runbook Recall

**Consumer:** Sonnet planner, possibly delegating to review agents.
**Available context:** Design document loaded, CLAUDE.md loaded, runbook outline being constructed.
**Memory access:** Has Skill tool (can invoke `/when`).

**Key question:** What implementation/testing learnings are relevant at planning time vs. execution time? The planner makes model assignments, step decomposition, and checkpoint placement decisions — all of which have documented failure modes in the corpus (e.g., haiku rationalizing test failures, haiku over-implementing, wrong model for prose artifacts).

**Dimension: Planning-relevant vs. execution-relevant filtering.** The corpus contains both planning decisions (model selection, phase typing, checkpoint placement) and execution decisions (mock patching, test structure, commit hygiene). Pass 2 needs to filter for planning-relevant entries only. Injecting execution-relevant entries at planning time wastes tokens and may confuse the planner.

### 4.3 Pass 3: Task Agent Injection

**Consumer:** Haiku/sonnet task agent, dispatched by orchestrator.
**Available context:** Common context (from prepare-runbook.py), step file, design reference. No Skill tool — cannot invoke `/when`.
**Memory access:** Can use `plugin/bin/when-resolve.py` via Bash (if Bash is in allowed-tools).

**This is the critical pass.** Task agents are where 2.9% recall manifests. They have the most constrained context and the least capability to self-retrieve.

**Unique constraints:**
- Orchestrator must filter the accumulated artifact per phase and per step
- The orchestrator itself may be haiku/sonnet — it must mechanically filter, not semantically evaluate
- Phase context separation rule: "Common context must be phase-neutral" (from `orchestration-execution.md`)
- Injected recall must not conflict with step instructions (recency vs. persistence signal conflict)

**Dimension: Mechanical filterability.** The orchestrator filters the recall artifact without understanding it. The artifact must be structured so filtering is a mechanical operation (e.g., tagged by phase type, tagged by artifact type being modified) rather than requiring semantic judgment.

### 4.4 Pass 4: Review Recall

**Consumer:** Corrector/review agent (opus for checkpoints, sonnet for light reviews).
**Available context:** Changed files, execution scope (IN/OUT), design reference.
**Memory access:** Varies by reviewer definition.

**Key question:** What failure-mode patterns from the corpus are relevant to this specific review? The corpus documents specific review failures: over-escalation, out-of-scope flagging, ungrounded corrections, missing cross-cutting invariants, batch routing errors.

**Dimension: Review-specific pattern matching.** The reviewer doesn't need implementation decisions — it needs review methodology decisions. Pass 4 must filter the artifact to review-relevant entries only. The existing pipeline-contracts.md already serves this role partially (centralized review contracts), but reviewer-specific failure modes are scattered across decision files.

---

## 5. Failure Modes Unique to Forwarded Context

### 5.1 Staleness Across Pipeline Stages

The recall artifact is generated at Pass 1 (design time). By Pass 3 (execution, possibly days later in multi-session work), the corpus may have changed (new learnings, codified decisions). The forwarded artifact reflects the corpus state at design time, not execution time.

**Dimension: Artifact freshness.** Should the recall artifact be regenerated at each pass, or forwarded with staleness accepted? Regeneration costs tokens but ensures currency. Forwarding is cheaper but may miss recently-added decisions.

### 5.2 Context Compression Under Forwarding

Each pass adds to the artifact. If Pass 1 produces 2K tokens and Pass 2 adds 1K, the artifact entering Pass 3 is 3K tokens. Across 4 passes with growth, the artifact may exceed the per-agent budget for haiku task agents.

**Dimension: Artifact growth control.** The system needs either: (a) a compression mechanism between passes, (b) a fixed budget per pass with eviction, or (c) a replacement model where later passes can override earlier entries.

### 5.3 Conflicting Guidance Between Passes

Pass 1 might recall "when choosing feedback output format" (favoring structured JSON). Pass 2 might recall "how output errors to stderr" (favoring stderr for errors). If both are injected into a task agent building CLI output, the agent faces contradictory guidance. The resolution depends on which entry is more specific to the current task — a judgment call that haiku cannot reliably make.

**Dimension: Conflict resolution strategy.** When entries from different passes contradict, which wins? Later pass (recency)? More specific match (relevance)? The system needs a tiebreaker that's mechanical, not judgment-based.

### 5.4 Phantom Applicability

A recalled entry may have been relevant at design time but not at execution time. Example: "when choosing naming convention format" recalled during design because the design discussed naming. At execution time, the task agent is writing tests, not choosing names. The entry persists in the forwarded artifact as phantom applicability — technically present, actually irrelevant.

**Dimension: Applicability decay.** Entries should have scope conditions that can be mechanically evaluated at each stage. Without this, the forwarded artifact accumulates phantom entries that waste tokens and attention.

---

## 6. Corpus Scaling Dimensions

### 6.1 Index Key Density

The memory index currently has ~213 trigger entries across 18 decision files and ~4,540 lines. That's roughly 1 trigger per 21 lines of decision content. As the corpus grows, two failure modes emerge:
- **Sparse coverage:** New decision content without corresponding index keys (invisible to recall)
- **Key collision:** Similar triggers resolving to different entries (ambiguous recall)

**Dimension: Index coverage ratio.** Recall effectiveness degrades as corpus grows faster than index. The `/codify` consolidation process adds entries but doesn't guarantee index coverage.

### 6.2 Decision File Growth

Individual decision files range from 115 to 397 lines. At the growth rate observed (18 files in ~2 months), the corpus could reach 10K+ lines within months. Full-file reads at Pass 1 (design recall, file mode: `when ..testing.md`) become expensive as files grow.

**Dimension: Sub-file retrieval granularity.** The current system supports file mode (whole file), section mode (heading), and trigger mode (index key). As files grow, section-level retrieval becomes essential — file-level retrieval wastes tokens on irrelevant sections.

### 6.3 Cross-File Decision Scatter

Related decisions are sometimes split across files. "Model selection" appears in `orchestration-execution.md`, `pipeline-contracts.md`, and `workflow-optimization.md`. A single recall query might need entries from 3+ files. As the corpus grows, decision scatter increases.

**Dimension: Multi-file retrieval coherence.** The recall pass must either: (a) query multiple index entries and merge results, or (b) maintain cross-references between related entries across files.

---

## 7. Evaluation Axes

### 7.1 Recall Rate Improvement

Baseline: 2.9% (agents invoke `/when` proactively). Target: ungrounded — no empirical basis for a numeric target. Measurement method: count memory-relevant decisions made during execution, count how many had recall support.

**Measurement challenge:** Determining "memory-relevant" requires post-hoc analysis by opus — itself an expensive evaluation. The ground truth (which decisions should have triggered recall) is subjective.

### 7.2 Precision (False Positive Rate)

Injected entries that the agent ignores or that cause confusion. Measurable by: (a) post-execution diff between injected entries and entries actually referenced in agent output, (b) cases where agent behavior contradicts injected guidance (indicating confusion, not recall failure).

### 7.3 Token Overhead Per Orchestration

Total additional tokens consumed by the recall system across all 4 passes and all task agents. Measurable directly from usage metadata.

### 7.4 Defect Prevention Rate

The ultimate metric: do orchestrations with recall passes produce fewer defects than without? Requires A/B comparison across multiple orchestrations — expensive and slow to accumulate statistical significance.

### 7.5 Latency Impact

Each pass adds processing time. Pass 1 and 2 are in the critical path (design and planning must complete before execution starts). Pass 3 adds per-step overhead. Pass 4 adds per-review overhead.

---

## 8. Design Desiderata

### 8.1 Mechanical Over Cognitive

The recall system should minimize judgment calls. The current failure (2.9% recall) is a cognitive failure — agents must judge when to invoke `/when`. The replacement must be mechanical: trigger conditions, filtering rules, and injection decisions should be deterministic or near-deterministic.

### 8.2 Incremental Adoption

The system should layer on top of the existing pipeline without restructuring it. Each pass should be independently deployable and independently measurable. Pass 3 (task agent injection) is highest impact due to the agent capability gap; it should be prioritizable.

### 8.3 Corpus-Format Stability

The recall system should work with the existing decision file format (markdown, heading hierarchy, prose entries). It should not require reformatting the corpus or adding metadata annotations to every entry.

### 8.4 Composability With Existing Mechanisms

The recall artifact should compose with existing context injection mechanisms: prepare-runbook.py common context, CLAUDE.md fragment loading, documentation perimeter in design.md. It should not create a parallel context channel that competes with these.

### 8.5 Observable

The recall artifact should be a file artifact (not ephemeral prompt content) so it can be audited, reviewed, and used for recall effectiveness measurement. Each pass should write/update a file in the plan directory.

---

## 9. Open Questions

- **UserPromptSubmit hook timing:** The planned keyword-injection hook fires before semantic context is established. Does the recall pass replace this hook, complement it, or does the hook serve a different purpose (ambient awareness vs. targeted recall)?
- **Cache interaction:** If Pass 1 produces a file artifact, can subsequent agents load it from cache rather than re-processing? The 94-100% cache hit rate is for the main session; Task agents start cold.
- **Learnings buffer interaction:** learnings.md is transient (consolidated periodically). Should the recall pass include learnings, or only consolidated decision content? Learnings may contain the most recent and relevant entries, but they're also the least validated.
- **Cross-worktree recall:** When executing in a worktree, the memory corpus on main may have diverged. `git show main:agents/decisions/X.md` is available but adds retrieval complexity.
