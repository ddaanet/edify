# Recall Pass: Grounding Report

**Grounding:** Moderate — 2 established frameworks (Context Engineering, Agentic RAG) with partial applicability, supplemented by project-specific analysis. No directly applicable multi-stage-pipeline-memory framework found.

---

## Research Foundation

### External Sources

**Context Engineering** (LangChain / Lance Martin, June 2025): Defines context engineering as "filling the context window with just the right information for the next step." Organizes into 4 strategies: Write (persist outside window), Select (retrieve into window), Compress (token efficiency), Isolate (structural separation). Classifies memory into procedural, semantic, and episodic types.

**Context Engineering for Agents** (Weaviate, 2025): Layered memory architecture (short-term, working, long-term). Just-in-time retrieval with Thought-Action-Observation cycle. Six-pillar integration creating feedback loops rather than sequential stages. Context failure modes: poisoning, distraction, confusion, clash.

**Agentic RAG Survey** (Singh et al., arXiv 2501.09136, Jan 2025): Taxonomy of agentic retrieval systems. Agents dynamically manage retrieval strategies, iteratively refine context, adapt workflows. Design patterns: prompt chaining, routing, parallelization, orchestrator-worker, evaluator-optimizer.

**Multi-Step Agentic Retrieval** (EmergentMind, 2025): Treats information-seeking as sequential decision process. Multi-hop knowledge traversal. Error propagation in chains is the primary challenge.

**Iterative RAG** (IRAGKR, ScienceDirect 2025): Interleaving retrieval and generation across reasoning steps. Progressive answer construction through evidence refinement.

### Internal Analysis

**Opus brainstorm** (27 dimensions across 9 sections): Project-specific constraints from measured data. Written to `tmp/ground-internal-recall-pass.md`. Key unique properties: human-curated deterministic corpus, fire-and-forget agent dispatch, multiplicative token cost, model-tier-dependent formatting.

---

## Framework Mapping

### Context Engineering → Recall Pass

| CE Strategy | Recall Pass Mapping | Fit |
|-------------|-------------------|-----|
| **Select** (retrieve into window) | Core mechanism — all 4 passes are Select operations | Tight |
| **Write** (persist outside window) | Recall artifact as persistent file, forwarded between stages | Tight |
| **Compress** (token efficiency) | Artifact growth control, per-tier formatting, budget constraints | Moderate |
| **Isolate** (structural separation) | Task agent isolation already exists; recall artifact crosses isolation boundary | Loose — CE isolates; recall pass deliberately bridges |

The 3-type memory taxonomy maps cleanly:

| Memory Type | Project Analog | Recall Pass Role |
|-------------|---------------|-----------------|
| **Procedural** | Fragments, CLAUDE.md rules | Already loaded via system prompt — not recall pass scope |
| **Semantic** | Decision files (decisions/*.md) | Primary recall pass content |
| **Episodic** | Learnings.md (recent experiences) | Secondary — transient, less validated |

**Key insight from CE:** Context failure modes (poisoning, distraction, confusion, clash) map to the project's observed failure modes. "Context distraction" = phantom applicability (Pass 5.4 in internal analysis). "Context clash" = conflicting guidance between passes (5.3). "Context confusion" = anti-pattern entries misinterpreted by haiku (3.3). The CE framework provides naming and classification for failure modes the internal analysis identified independently.

### Agentic RAG → Recall Pass

| Agentic RAG Pattern | Recall Pass Mapping | Fit |
|---------------------|-------------------|-----|
| **Iterative refinement** | Progressive augmentation across 4 passes | Moderate — passes are pipeline stages, not iteration loops |
| **Agent-decided retrieval** | Orchestrator filters artifact per step | Loose — orchestrator is mechanical, not adaptive |
| **Multi-hop traversal** | Index → decision file → section → entry | Tight — existing retrieval is multi-hop |
| **Error propagation in chains** | Forwarding amplifies false positives multiplicatively | Tight |

**Critical divergence:** Agentic RAG assumes agents dynamically decide when and what to retrieve. The recall pass model rejects this — the 2.9% recall rate demonstrates agents fail at self-directed retrieval. The recall pass is **prescriptive** (retrieve at fixed pipeline points) not **adaptive** (retrieve when the agent decides to). This is a deliberate departure from the Agentic RAG paradigm, justified by measured failure of the adaptive approach.

### Multi-Step Retrieval → Recall Pass

The iterative RAG pattern (interleave retrieval and generation) partially maps to the 4-pass model but with an important distinction: iterative RAG refines a single query across iterations. The recall pass model uses different queries at each stage (design-domain → implementation → per-step → failure-modes). It's **staged diversification**, not iterative refinement.

---

## Adaptations

### From CE: Just-In-Time Selection with Observable Artifacts

**General principle:** Context should be selected just-in-time — retrieved when the consuming agent needs it, not preloaded speculatively. The selection should be observable and auditable.

**Project implementation:** Each recall pass writes to a file artifact in the plan directory. The artifact is readable by humans and downstream agents. This satisfies CE's "Write" strategy (persist outside window) while enabling JIT "Select" at each stage.

**Adaptation:** CE treats Write and Select as independent strategies. The recall pass chains them — Write at one stage enables Select at the next. This "Write-forward, Select-on-demand" pattern is not in the CE framework but emerges naturally from the multi-stage pipeline.

### From CE: Failure Mode Classification

**General principle:** Context injection has 4 failure modes (poisoning, distraction, confusion, clash) that must be designed against, not just observed post-hoc.

**Project implementation:**
- **Distraction** → Applicability scoping on each entry (mechanical condition, not agent judgment)
- **Clash** → Later-pass-wins tiebreaker for conflicting entries
- **Confusion** → Model-tier-appropriate formatting (constraint format for haiku, full rationale for opus)
- **Poisoning** → Staleness detection across multi-session pipelines

### From Agentic RAG: Prescriptive Over Adaptive Retrieval

**General principle:** When agents fail at self-directed retrieval, replace adaptive decisions with prescriptive triggers at fixed pipeline points.

**Project implementation:** 4 fixed recall points (design, runbook, injection, review) rather than agent-decided retrieval. This inverts the Agentic RAG paradigm deliberately — the system's measured 2.9% adaptive recall rate justifies the inversion.

**Adaptation rationale:** Agentic RAG literature assumes retrieval-capable agents with tool access. This project's task agents are dispatched without Skill tool access and operate fire-and-forget. The adaptive model's prerequisites are absent.

### From Multi-Step Retrieval: Staged Diversification

**General principle:** Multi-stage retrieval should diversify at each stage, not just refine. Each stage adds its domain lens rather than narrowing the same query.

**Project implementation:** Pass 1 (design-domain, broad), Pass 2 (+implementation, +testing), Pass 3 (filtered to phase), Pass 4 (+failure-modes). Each pass widens then filters, rather than iteratively narrowing.

### Project-Specific Additions (Not in Any Source)

1. **Multiplicative token cost accounting** — No external source addresses the cost of forwarding retrieved context through a multi-agent pipeline where each agent loads the artifact fresh. The per-agent budget must account for replication count.

2. **Mechanical filterability constraint** — The orchestrator (possibly haiku) must filter the artifact per-step without semantic judgment. No CE or RAG source addresses filtering by a less-capable model than the original retriever.

3. **Format-per-consumer-tier** — CE identifies memory types but not model-tier-dependent formatting. The same decision entry needs constraint format for haiku and full-rationale format for opus.

4. **Observable artifact as design requirement** — CE mentions persistence; the project requires file-based artifacts for audit, review, and recall effectiveness measurement.

5. **Additive value gate** — Pass 1 must produce something the existing design skill Documentation Checkpoint doesn't. The unique contribution is a persistent, forwardable artifact — the checkpoint's results die with the context window.

### Deliberately Excluded

- **Vector DB / embedding-based retrieval** — The corpus is human-curated with deterministic index lookup. Embedding quality is irrelevant; index key coverage drives recall.
- **Reinforcement learning for retrieval optimization** — Multiple RAG sources suggest RL for adaptive retrieval. Excluded: too complex for a prescriptive system, and the prescriptive approach deliberately avoids learned retrieval decisions.
- **User feedback loops** — CE emphasizes user-in-the-loop correction. Excluded: no human user in the agent pipeline between dispatch and review.

---

## Grounding Assessment

**Quality label: Moderate**

**Evidence basis:**
- CE framework (LangChain, Weaviate) provides structural vocabulary (Select/Write/Compress/Isolate, failure modes) that maps well to the recall pass model
- Agentic RAG survey provides multi-step retrieval patterns but assumes adaptive agents — the recall pass deliberately departs from this
- No existing framework addresses multi-stage memory forwarding through a heterogeneous-model agent pipeline specifically

**What was searched:**
- "multi-stage RAG retrieval augmented generation pipeline progressive context 2025 2026" → CE evolution, RAG surveys
- "LLM agent memory architecture multi-step retrieval context propagation framework" → A-MEM, Mem0, CE blog posts
- "agentic RAG pipeline stages retrieval methodology 2025" → Agentic RAG survey, multi-step agentic retrieval
- "context engineering LLM agent pipeline right information right time 2025" → LangChain CE, Weaviate CE
- "iterative retrieval augmented generation multi-hop progressive refinement" → IRAGKR, LevelRAG, RT-RAG

**Gaps remaining:**
- No framework addresses prescriptive (non-adaptive) multi-stage retrieval in agent pipelines — the recall pass model is novel in this regard
- Token cost modeling for forwarded context through agent chains is not addressed in literature
- Model-tier-dependent formatting of retrieved content has no established pattern
- The convergence problem (how many recall iterations are needed) remains unaddressed theoretically — the staged diversification model sidesteps it rather than solving it

---

## Sources

- [Context Engineering for Agents — Lance Martin](https://rlancemartin.github.io/2025/06/23/context_engineering/) — Primary. 4-strategy taxonomy (Write/Select/Compress/Isolate), memory types, positional effectiveness. Blog post distilling LangChain patterns.
- [Context Engineering — Weaviate](https://weaviate.io/blog/context-engineering) — Primary. Layered memory architecture, failure modes, six-pillar integration. Enterprise perspective.
- [Agentic RAG Survey — Singh et al.](https://arxiv.org/abs/2501.09136) — Primary. Taxonomy of agentic retrieval, design patterns, multi-step orchestration.
- [From RAG to Context — InfiniFlow/RAGFlow](https://ragflow.io/blog/rag-review-2025-from-rag-to-context) — Secondary. RAG evolution narrative, context engine concept.
- [Multi-Step Agentic Retrieval — EmergentMind](https://www.emergentmind.com/topics/multi-step-agentic-retrieval) — Secondary. Sequential decision process framing.
- [A-MEM: Agentic Memory](https://arxiv.org/abs/2502.12110) — Secondary. Zettelkasten-inspired memory with linked notes.
- [Mem0: Production AI Agent Memory](https://arxiv.org/abs/2504.19413) — Secondary. Graph-based memory, multi-hop retrieval.
- [Context Engineering — LangChain Docs](https://docs.langchain.com/oss/python/langchain/context-engineering) — Secondary. Implementation patterns for agent memory.
