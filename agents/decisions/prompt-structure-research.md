# Prompt Structure Research

Distilled from prompt-composer design (Dec 2025). Original research in `plans/prompt-composer/` (git history).

---

## When Ordering Fragments In CLAUDE.md

LLMs exhibit **strong primacy bias** — content at the beginning of context receives disproportionate attention. Secondary **recency bias** exists at the end. Middle content has weakest influence ("lost in the middle").

**Practical implications:**
- Critical rules → document START (primacy position)
- Guidance/preferences → document END (recency position)
- Important but non-critical → middle (weakest position, contains bulk of content)
- Distribution heuristic: ~20% critical / ~60% important / ~20% guidance

**Sources:**
- [Serial Position Effects of LLMs (2024)](https://arxiv.org/html/2406.15981v1)
- [Exploiting Primacy Effect](https://arxiv.org/html/2507.13949)
- [Positional Bias in Financial Decision-Making](https://arxiv.org/html/2508.18427)

**Note:** The 20/60/20 distribution is a heuristic from organizational change management ([ResearchGate](https://www.researchgate.net/publication/270824843_The_20-60-20_rule)), not empirically validated for LLMs. Treat as reasonable starting point.

---

## When Formatting Rules For Adherence

Bullet points outperform prose for discrete task adherence. Connected ideas requiring context benefit from paragraph format.

**Format by content type:**

| Content Type | Best Format | Rationale |
|-------------|-------------|-----------|
| Discrete rules | Bullets | Higher task adherence |
| Connected concepts | Prose paragraphs | Cohesion needed |
| Critical rules | Visually salient markers (⚠️, bold) | Attention capture |
| Examples | Code blocks | Pattern matching |

**Source:** [Effect of Selection Format on LLM Performance (arXiv 2025)](https://arxiv.org/html/2503.06926)

---

## When Writing Rules For Different Models

Different model classes benefit from different instruction density:

| Model Class | Characteristics | Instruction Style |
|------------|----------------|-------------------|
| Opus | Handles complex/detailed prompts, catches nuances | Concise prose, trust inference |
| Sonnet | Handles clear prompts well, balanced | Clear bullets with context |
| Haiku | Needs precise, scoped tasks | Explicit steps, ⚠️ markers, DO NOT examples |

**Source:** [Claude Model Family (Anthropic)](https://www.anthropic.com/news/claude-3-family)

**Expansion ranges:** Same semantic content requires different rule counts:
- Strong (Opus): 3-5 rules per module
- Standard (Sonnet): 8-12 rules per module
- Weak (Haiku): 12-18 rules per module

---

## When Too Many Rules In Context

LLM adherence degrades with excessive rules. Empirical observation: adherence collapses >200 rules. Claude system prompt consumes ~50, leaving ~150 for user rules.

**Counting approach:** Marker-based counting (`[RULE:Tn]`) is unambiguous — the generator defines what constitutes a rule, not a parser heuristic.

---

## When Loading Context For Llm Processing

LLMs only read explicitly provided context. No inherent behavior to load additional files. Context files require explicit reading instructions or `@` references.

**Source:** [Effective Context Engineering for AI Agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## .When Evaluating Prompt Structure Tools

No existing tool combines position bias optimization + model-specific variants + rule budgeting. Closest matches:
- **Airia Prompt Layering** — modular composition but no tiering/budgeting (commercial only)
- **Langfuse** — basic composition via references, open source, but no ordering/variants
- **General platforms** (PromptLayer, LangSmith, Bedrock) — versioning/evaluation only

**Source:** `plans/prompt-composer/existing-tools-research.md` (full analysis)

---

## .When Applying Prompt Research

The fragment system (`agent-core/fragments/` + CLAUDE.md `@` references) solves modular composition. Remaining opportunities:
- ~~**Position optimization** — order fragments/rules by criticality (primacy/recency)~~ **Done** (Feb 2026)
- ~~**Token budget tracking** — formal counting to prevent context bloat~~ **Done** (Feb 2026)
- **Model-specific variants** — if haiku execution quality becomes a problem

---

## .How to Order Fragments By Position Bias

CLAUDE.md sections ordered by position bias research (primacy strongest, recency secondary, middle weakest).

**Zone classification:**

| Zone | Section | Fragments | Rationale |
|------|---------|-----------|-----------|
| PRIMACY | Core Behavioral Rules | communication, execute-rule, delegation | Session-defining: interaction model, modes, shortcuts, core principle |
| EARLY-MID | Documentation Structure | session.md, learnings.md, jobs.md, memory-index | Informational scaffolding, progressive discovery |
| MIDDLE | Operational Rules | error-handling, review-requirement, token-economy, commit-skill-usage, no-estimates, code-removal, tmp-directory | Important policies, not session-defining |
| RECENCY | Reference & Tooling | bash-strict-mode, sandbox-exemptions, claude-config-layout, design-decisions, project-tooling, tool-batching | Reference material, "how to work" (fresh before action) |

`workflows-terminology` stays at absolute primacy (line 1) as entry point.

**Token budget:** ~15k tokens heuristic (well under 30k threshold). Measured by `agent-core/bin/context-budget.py`.

**Future:** If adherence issues emerge in specific zones, consider further reordering within zones or promoting individual fragments.
