# Research Synthesis: Grounding Skill Design

Consolidated from: 3 web searches, 2 web fetches, 1 opus brainstorm, discussion analysis.

## Established Frameworks

### Double Diamond (Design Council, 2005)

Origin: Bánáthy's 1996 divergence-convergence model, adapted by UK Design Council.

Structure: Two diamonds, each diverge→converge.
- **Diamond 1 (Problem):** Discover (diverge: explore problem space) → Define (converge: frame the problem)
- **Diamond 2 (Solution):** Develop (diverge: generate solutions) → Deliver (converge: validate and ship)

Key properties:
- Communication tool, not rigid recipe — adapt to context
- "Groan zone" at diverge→converge transition: abandoning ideas is necessary but difficult
- Divergent thinking is free-flowing, non-linear; convergent is focused, linear
- The two diamonds are sequential: problem definition informs solution exploration

**Mapping to our pattern:** Our grounding skill uses Diamond 2 (Solution space). The "problem" (what methodology to apply) is already framed by the user's request. We diverge via brainstorm + research, converge via synthesis.

Source: [Fountain Institute](https://www.thefountaininstitute.com/blog/what-is-the-double-diamond-design-process)

### Rapid Review (evidence synthesis methodology)

Origin: Academic knowledge synthesis adapted for time-constrained decisions.

Definition: "A form of knowledge synthesis in which components of the systematic review process are simplified or omitted to produce information in a timely manner."

Steps:
1. **Plan** — Frame question, determine inclusion/exclusion criteria, set scope
2. **Identify** — Determine search terms and sources, retrieve and document
3. **Evaluate** — Screen, select, appraise quality
4. **Synthesize** — Narrative synthesis of surviving sources

Key properties:
- Explicitly acknowledges rigor/speed tradeoff
- Flags when evidence is thin rather than hiding gaps
- Scoping the question is the most important step
- Typical timeline: 5 weeks to 3 months (vs. 1-2 years for systematic review)

**Mapping to our pattern:** The external research branch follows Rapid Review steps. Plan = scope the search query. Identify = web search. Evaluate = assess source relevance. Synthesize = extract applicable elements.

Sources: [VCU Rapid Review Guide](https://guides.library.vcu.edu/rapidreview), [PMC Rapid Review Definition](https://pmc.ncbi.nlm.nih.gov/articles/PMC10392303/)

### RAG-as-Grounding (LLM hallucination mitigation)

Origin: Retrieval-Augmented Generation research, extended to agentic systems.

Core principle: External retrieval anchors generated output in verified sources, reducing hallucination by 42-68%.

Agentic-specific patterns:
- **Iterative retrieval feedback** (KiRAG): step-by-step retrieval where each query is informed by current reasoning
- **Multi-agent verification** (WebWalker): parallel verification paths rather than single-pass generation
- **Traceability**: explicit link between output and source documents

Key distinction: External grounding is mandatory for factual/methodological claims. Internal reasoning suffices for logical decomposition and project-specific analysis.

**Mapping to our pattern:** The brainstorm branch = internal reasoning (project-specific). The web search branch = RAG-style external retrieval. The skill's trigger condition = "producing factual/methodological claims that need grounding."

Source: [Agentic hallucination mitigation survey](https://arxiv.org/html/2510.24476v1)

---

## Internal Analysis (Opus Brainstorm)

The opus brainstorm produced 13 project-specific evaluation axes for the prioritization use case. The relevant meta-observations about the *process*:

- Internal branch value: captured project-specific dimensions (self-referential bootstrap risk, artifact readiness depth, restart amortization) that no external framework would surface
- External branch value: provided the skeleton (WSJF formula, CoD decomposition, Fibonacci scoring) that the internal dimensions mapped onto
- Neither branch alone would have produced the result: internal-only = confabulated framework; external-only = generic WSJF without project adaptation
- Parallel execution worked because the synthesis step is where integration happens

---

## Design Decisions for Grounding Skill

### When to trigger (from hallucination literature)

External grounding is mandatory when output makes:
- **Methodological claims** — "the best way to X is Y"
- **Framework claims** — "these are the dimensions/axes/criteria for X"
- **Best practice claims** — "established practice is to X"
- **Taxonomic claims** — "there are N types of X"

External grounding is NOT needed for:
- Project-specific logical analysis (reading code, tracing dependencies)
- Applying an already-grounded framework to data
- Mechanical execution of defined procedures

### Procedure (synthesized from all three frameworks)

**Phase 1: Scope** (from Rapid Review "Plan")
- Frame the research question: "What established frameworks exist for [topic]?"
- Define inclusion criteria: relevance to project context, actionable methodology
- Define exclusion criteria: pure theory without procedure, wrong domain

**Phase 2: Diverge** (from Double Diamond "Develop", parallel execution)

Branch A — Internal (brainstorm or explore, parameterized):
- **Brainstorm** when topic is prescriptive ("how should we X"): opus generates project-specific dimensions, constraints, desiderata
- **Explore** when topic is descriptive ("what do we currently do about X"): codebase exploration surfaces existing patterns

Branch B — External (Rapid Review "Identify" + "Evaluate"):
- Search for established frameworks, named methodologies, academic approaches
- Evaluate source relevance and applicability to project context
- Extract: framework names, component structures, scoring mechanics, known limitations

**Phase 3: Converge** (from Double Diamond "Deliver")
- Map internal dimensions onto external framework skeleton
- Adapt scoring criteria from external framework using project-specific evidence sources
- **Grounding quality assessment:** Explicitly flag one of:
  - **Strong** — Multiple established frameworks found, adapted with project-specific criteria
  - **Moderate** — One framework found with partial applicability, supplemented by internal analysis
  - **Thin** — No directly applicable framework found; output is project-derived with structural inspiration only
  - **None** — External search returned no relevant results; output is ungrounded internal reasoning only

**Phase 4: Output**
- Reference document with: research foundation (sources), adapted methodology, applied scoring/analysis
- Grounding quality label attached to output
- Sources section with links

### Parameterization

| Parameter | Options | Determines |
|-----------|---------|------------|
| Internal branch type | brainstorm / explore | Whether to generate new dimensions or surface existing patterns |
| Internal branch model | opus / sonnet | Cognitive complexity of internal analysis |
| Research breadth | narrow (1-2 searches) / broad (3-5 searches) | Tradeoff between token cost and coverage |
| Output format | reference document / skill body / decision document | Where the grounded methodology lands |

---

## Sources

- [Double Diamond Design Process](https://www.thefountaininstitute.com/blog/what-is-the-double-diamond-design-process)
- [Rapid Review Guide](https://guides.library.vcu.edu/rapidreview)
- [Rapid Review Definition](https://pmc.ncbi.nlm.nih.gov/articles/PMC10392303/)
- [Agentic Hallucination Mitigation](https://arxiv.org/html/2510.24476v1)
- [RICE vs WSJF](https://www.centercode.com/blog/rice-vs-wsjf-prioritization-framework)
- [13 Prioritization Techniques](https://www.ppm.express/blog/13-prioritization-techniques)
- [Cost of Delay without metrics](https://liminalarc.co/2017/06/cost-delay-project-management-2/)
- [ICE, RICE, WSJF backlog organization](https://hackernoon.com/ice-rice-wsjf-or-how-to-organize-your-backlog-effectively)
