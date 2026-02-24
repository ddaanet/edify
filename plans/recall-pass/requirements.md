# Recall Pass

## Requirements

### Functional Requirements

**FR-1: Design-stage recall**
When a design session begins (Phase A.1), produce a recall artifact containing relevant decision file content selected from the memory corpus. The artifact is a persistent file in the plan directory with named references to each selected entry. Supplements the existing Documentation Checkpoint — the checkpoint's results die with the context window; the recall artifact persists and forwards.

Acceptance criteria:
- Reads `memory-index.md` on demand (skip if already in context from earlier recall in same session), selects relevant entries by problem-domain matching. Memory-index keyword-rich entries amplify thin user input — even sparse queries surface relevant decisions through index cross-references, superior to direct corpus search.
- Batch-resolves multiple entries via `when-resolve.py "when <trigger>" "how <trigger>" ...` (single call for efficiency)
- Reads whole decision files for selected entries
- Writes artifact to `plans/<job>/recall-artifact.md` (or equivalent path)
- Each entry identified by name (heading + source file)
- Artifact readable by downstream passes without re-reading source files
- When no requirements.md exists, derive domain keywords from user request and task description for memory-index matching — wider net compensates for weaker signal

**FR-2: Planning-stage recall**
When runbook planning begins, augment the design recall artifact with implementation and testing learnings relevant to the planned work. Adds the implementation lens: TDD cycle pitfalls, step file quality patterns, precommit gotchas, model selection failures.

Acceptance criteria:
- Inherits Pass 1 artifact (reads, does not regenerate)
- Adds entries from `decisions/implementation-notes.md`, `decisions/testing.md`
- Adds planning-relevant entries only (model selection, phase typing, checkpoint placement) — not execution-relevant entries (mock patching, test structure)
- Writes augmented artifact back to plan directory

**FR-3: Execution-stage injection**
During orchestration, inject a filtered subset of the accumulated recall artifact into each task agent's prompt. The orchestrator selects per-step content; the task agent receives recall content without discovering it.

Acceptance criteria:
- Orchestrator reads accumulated artifact and filters per phase/step
- Filtering is a mechanical operation (tag/label matching, not semantic judgment)
- Filtered content injected in task agent prompt alongside step file content
- Task agents that lack Skill tool access receive recall content directly (content injection, not reference injection)

**FR-4: Review-stage recall**
When review/correction agents execute, provide recall content focused on failure modes and quality anti-patterns relevant to the reviewed artifacts.

Acceptance criteria:
- Inherits accumulated artifact
- Adds review-specific entries: common review failures, quality anti-patterns, over-escalation patterns
- Injected into corrector and deliverable-review agent prompts

**FR-5: Persistent recall artifacts**
Each recall pass writes output to a file in the plan directory. Artifacts are human-readable markdown, auditable post-execution, and available for recall effectiveness measurement.

Acceptance criteria:
- Artifact is a markdown file in `plans/<job>/`
- Shows which entries were selected and from which source files
- Reviewable: a human or review agent can assess selection quality
- Survives session boundaries (file-based, not context-only)

**FR-6: Reference forwarding**
Later recall passes inherit and augment earlier artifacts rather than re-discovering from scratch. Breadth accumulates through forwarding; no convergence iteration needed.

Acceptance criteria:
- Pass 2 reads Pass 1 artifact and appends
- Pass 3 reads accumulated artifact and filters
- Pass 4 reads accumulated artifact and appends review entries
- No pass re-queries the memory corpus for entries already in the artifact

**FR-7: Named enumeration**
Each recalled entry is identified by name in the artifact, enabling explicit downstream reference (e.g., "the learning about merge commit --amend failures").

Acceptance criteria:
- Entries have unique identifiers (heading text + source path, or equivalent)
- Downstream agents and review artifacts can reference entries by name
- Traceable: any recalled entry can be located in the source corpus

**FR-8: Mechanical filterability**
The recall artifact structure supports filtering by a haiku-tier orchestrator without semantic judgment. Tags, phase labels, or structural markers enable mechanical selection.

Acceptance criteria:
- Each entry tagged with applicability metadata (phase type, artifact type, domain)
- Orchestrator can select relevant entries using string matching or structural position
- No reasoning about entry content required for filtering
- Haiku orchestrator produces correct filtered subset for a given step

**FR-9: Model-tier formatting**
Recall content formatted per consumer model capability. Same decision entry rendered differently for different model tiers.

Acceptance criteria:
- Haiku consumers: constraint format (<1K tokens) — DO/DO NOT rules, explicit applicability markers
- Sonnet consumers: structured bullets (~2K tokens) — key points with rationale summary
- Opus consumers: full rationale with context — complete decision text

**FR-10: Applicability scoping**
Each recalled entry includes scope conditions indicating when it applies. Prevents unconditional application of all injected content and protects against anti-pattern misinterpretation by weaker models.

Acceptance criteria:
- Entries include "applies when" conditions
- Anti-pattern entries framed to prevent haiku from implementing the anti-pattern
- Scope conditions evaluable by the consuming agent without external lookups

**FR-11: Recall at cognitive boundaries**
Recall relevant context before every cognitive work boundary in the pipeline. Within-session recall serves as compaction insurance (low token cost, high upside against context loss). Extends FR-1 through FR-4 (pipeline stage boundaries) to cover all cognitive transitions.

Acceptance criteria — recall at each boundary:
- Before requirements capture: domain context, prior art, settled decisions
- Before exploration (A.2, Phase 0.5 step 4, Tier 1/2 ad-hoc): recall domain context to target exploration — especially critical when no formal requirements exist (derive keywords from user request)
- Before design outline (A.5): re-surface artifact after exploration/research
- Before full design (C.1): re-surface artifact after user discussion
- Before runbook outline (Phase 0.75): re-surface artifact after codebase discovery
- Before phase expansion (Phase 1): re-surface per-phase with phase-specific entries
- Before implementation: recall implementation decisions (per-tier: direct read / delegation injection / Common Context)
- Before tests: recall testing conventions (same per-tier mechanism)
- Before review/correction: recall quality patterns, failure modes, artifact-type conventions

### Non-Functional Requirements

**NFR-1: Token economy**
Multiplicative cost accounting: if the recall artifact is R tokens, total cost across N task agents is approximately N×R. Per-agent injection budget must account for replication count, not single-query cost.

**NFR-2: Incremental adoption**
Each pass independently deployable and measurable. Pass 3 (task agent injection) is highest-impact due to agent capability gap and should be prioritizable for first delivery.

**NFR-3: Composability**
Composes with existing context injection mechanisms (prepare-runbook.py common context, CLAUDE.md fragment loading, documentation perimeter) without creating a parallel competing channel.

### Constraints

**C-1: Prescriptive retrieval at fixed points**
Recall triggers at predetermined cognitive boundaries, not when agents decide to retrieve. Justified by 2.9% measured adaptive recall rate. The system inverts the Agentic RAG paradigm deliberately — agents lack the capability for self-directed retrieval (no Skill tool in task agents, fire-and-forget dispatch).

**C-2: Existing corpus format**
Works with the current decision file format (markdown, heading hierarchy, prose entries). No reformatting, annotation, or metadata additions to the corpus required.

**C-3: Existing pipeline integration points**
Integrates into `/requirements` (capture), `/design` (A.1, A.5, C.1), `/runbook` (Phase 0.5, 0.75, 1, Tier 1/2), `/orchestrate` (dispatch), and `/deliverable-review` (review). No new top-level skills or pipeline stages.

**C-4: Fire-and-forget dispatch**
No mid-flight communication with task agents. Recall content must be complete and correct at injection time — no correction possible after dispatch.

**C-5: Haiku orchestrator capability**
The orchestrator filtering recall content may run on haiku. All filtering operations must be mechanical — no semantic evaluation of entry relevance.

### Out of Scope

- **Vector DB / embedding retrieval** — corpus is human-curated with deterministic index lookup; embedding quality is irrelevant
- **Reinforcement learning for retrieval optimization** — too complex for prescriptive system; deliberately avoids learned retrieval decisions
- **User feedback loops in pipeline** — no human user between dispatch and review
- **UserPromptSubmit topic detection hook** — complementary but separate work item (already a distinct pending task); cheap first layer vs. deep pipeline integration
- **Corpus restructuring** — no changes to decision file organization, heading conventions, or memory-index format
- **Cache optimization across Task agents** — cache behavior for dispatched agents is unknown (94-100% main session rate doesn't apply); out of scope for recall pass design

### Open Questions

- Q-1: Artifact growth control — when accumulated artifact exceeds per-agent budget, what eviction or compression mechanism applies? (Compression, fixed budget with eviction, or later-pass replacement model)
- Q-2: Conflict resolution — when entries from different passes contradict, which wins? Needs a mechanical tiebreaker (not agent judgment)
- Q-3: Staleness across pipeline stages — artifact generated at design time may be stale by execution time (days later in multi-session work). Regenerate vs. accept staleness?
- Q-4: Mid-design recall — RESOLVED by FR-11: yes, recall before A.5 and C.1 as compaction insurance within same session
- Q-5: Positional effectiveness — where in the agent prompt does the recall artifact appear? Primacy/recency positions already claimed by system prompt and step instructions

### References

- `plans/recall-pass/brief.md` — 4-pass model, reference forwarding, discussion conclusions
- `plans/reports/recall-pass-grounding.md` — Moderate grounding: CE framework (Write/Select/Compress/Isolate), Agentic RAG paradigm inversion, failure mode classification (poisoning, distraction, confusion, clash)
- `plans/reports/recall-pass-internal-brainstorm.md` — 27 dimensions across 9 sections: structural RAG differences, token economy, artifact format, pass-specific constraints, forwarding failure modes, corpus scaling, evaluation axes, design desiderata
- [Context Engineering — Lance Martin](https://rlancemartin.github.io/2025/06/23/context_engineering/) — 4-strategy taxonomy informing artifact design (Write/Select/Compress/Isolate)
- [Agentic RAG Survey — Singh et al.](https://arxiv.org/abs/2501.09136) — multi-step retrieval patterns; recall pass deliberately departs from adaptive retrieval paradigm
