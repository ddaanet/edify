# Skill Optimization Grounding

**Grounding:** Moderate — 1 directly applicable framework family (prompt compression), supplemented by extensive internal analysis. External research provides the compression taxonomy and differential budget concept; internal analysis provides the project-specific segmentation and prioritization.

## Research Foundation

### External Frameworks

**LLMLingua (Microsoft Research, EMNLP'23 / ACL'24)**
Coarse-to-fine prompt compression using a small language model to identify and remove unimportant tokens. Key contribution: **budget controller** with differential compression ratios by content type.

| Content type | Compression rate | Rationale |
|---|---|---|
| Instructions | 10-20% | Preserve clarity, high attribution |
| Examples/demonstrations | 60-80% | High redundancy, model already knows patterns |
| Questions/queries | 0-10% | Critical intent, minimal compression |

Achieves up to 20x compression with minimal performance loss. The budget controller concept is the most transferable element — not the automated tool itself (which targets API-level compression, not instruction authoring).

**ProCut (2025)**
LLM-agnostic framework that segments prompt templates into "semantically meaningful units" and prunes low-utility components via attribution estimation. 78% token reduction while maintaining or slightly improving task performance.

Key insight: **segmentation before pruning**. Identify meaningful units first, then measure each unit's contribution to output quality. Prune bottom-up from lowest-attribution units.

**Practical Engineering Consensus (multiple sources)**
Manual optimization patterns with broad agreement across practitioners:

- **Conditional inclusion** — only load sections relevant to current invocation
- **Prompt caching alignment** — static content at top, variable content at bottom (cached tokens 75% cheaper)
- **Structured formatting** — bullets/tables over prose (denser tokenization)
- **Instruction referencing** — register instructions once, reference by identifier
- **Semantic summarization** — condense redundant content, preserve essential semantics

**Agentic-Specific (arxiv 2502.02533, arxiv 2512.08769)**
Multi-agent prompt optimization research finds:

- "One agent, one tool" simplifies prompting and eliminates tool-selection noise
- Shorter, well-scoped inputs yield sharper responses than massive context windows
- Separate agent memories reduce input tokens per step
- The prompt is the primary "optimizable component" in agent systems

## Adapted Methodology

### Framework: Segment → Attribute → Compress

Adapted from ProCut's segment-then-prune approach, using LLMLingua's budget controller for differential compression, with project-specific segmentation from internal analysis.

### Step 1: Segment

Classify every block of skill content into one of these categories (derived from internal D-1 through D-13 analysis):

| Category | Definition | Examples |
|---|---|---|
| **Core rules** | Behavioral constraints that prevent high-severity failures | Carry-forward verbatim rule, NEVER create other sections, only-commit-when-asked |
| **Mechanical instructions** | Exact tool invocations, platform workarounds | Separate Bash calls, subshell pattern, heredoc syntax |
| **Conditional paths** | Instructions for rarely-triggered execution branches | Consolidation flow, submodule handling, plan-archive, multi-handoff merge |
| **Redundant content** | Rules restated from always-loaded context (CLAUDE.md, fragments) | Error suppression, secrets, task format, vet proportionality |
| **Examples** | Worked demonstrations of rules or formats | Good/bad handoff, commit message examples, haiku task examples |
| **Guidelines** | Quality heuristics that improve but don't constrain output | Preserve specifics, omit verbose details, target 75-150 lines |
| **Reference loads** | Content requiring runtime Read calls | Gitmoji index, template.md, good-handoff.md |
| **Framework overhead** | Continuation protocol, section headers, design comments | Tail-call chain logic, HTML comments, structural markdown |
| **Sequential tool calls** | Steps that issue serial tool calls where parallel calls would work | Handoff `wc -l` + `learning-ages.py` as two sequential calls; commit `just precommit` then `git status -vv` |

### Step 2: Attribute (compression budget per category)

Adapted from LLMLingua's budget controller. Rates express target compression (0% = keep all, 100% = remove all).

| Category | Compression | Rationale |
|---|---|---|
| Core rules | 0% | High-severity, keep regardless. These are load-bearing defensive rules. |
| Mechanical instructions | 20-30% | Consolidate duplicates (e.g., "separate Bash calls" stated 3x → 1x). Keep at execution site. |
| Conditional paths | 70-80% | Extract to on-demand reference files. Replace with 1-line trigger + Read instruction. |
| Redundant content | 80-100% | Remove if always-loaded provides identical rule. Keep 1-line cross-reference if removal feels risky. |
| Examples | 50-60% | Keep examples for project-specific patterns (commit density). Remove examples of obvious patterns (imperative mood). |
| Guidelines | 30-40% | Condense bullet lists. Replace multi-line guidance with dense single-line rules. |
| Reference loads | Varies | Template: inline structure, eliminate Read. Gitmoji: keep full Read — inlining a subset creates a knowledge ceiling (agent picks from subset, unaware better matches exist in the full index). Sub-agent delegation considered but overhead (agent spawn + context) exceeds the Read cost. Optimization path is CLI tool (embeddings + cosine similarity), not inlining or delegation. |
| Framework overhead | 50% | Remove design comments. Compact continuation protocol. Keep H3 step headers (retrieval anchors). |
| Sequential tool calls | 30-50% | Restructure skill steps so independent tool calls batch into single messages. Reduces round-trip overhead without changing content. |

### Step 3: Apply compression techniques per category

**Technique mapping:**

| Technique | Applies to | Description |
|---|---|---|
| **Delete** | Redundant content | Remove entirely; always-loaded context provides the rule |
| **Consolidate** | Mechanical instructions | Merge duplicated statements into single occurrence |
| **Extract** | Conditional paths | Move to reference file; replace with trigger + Read |
| **Inline** | Reference loads | Embed critical subset directly; lazy-load remainder |
| **Condense** | Guidelines, examples | Rewrite as dense single-line rules or minimal examples |
| **Defer** | CLI-bound operations | Mark as "eliminated when CLI tool ships" — don't compress instructions that will be removed entirely |
| **Batch** | Sequential tool calls | Restructure step instructions so independent calls appear in a single message (parallel execution) |

### Step 4: Validate

After applying compression:

1. **Adherence test:** Run the optimized skill through representative scenarios (normal handoff, multi-handoff, handoff+commit chain, submodule commit, WIP commit). Check for behavioral regressions.
2. **Token measurement:** Count tokens before/after using `wc -l` as proxy (actual tokenization varies, but line count correlates).
3. **Failure mode check:** For each removed or condensed block, verify the failure mode it prevents is still covered (either by always-loaded context or by remaining skill content).

## Application to Handoff + Commit Skills

### Handoff Skill (330 lines)

**Segment inventory:**

| Category | Lines | Specific blocks |
|---|---|---|
| Core rules | ~40 | Carry-forward verbatim (41-46), allowed sections (94-101), no commits as pending (132-136), no fresh Write (54) |
| Mechanical instructions | ~15 | wc -l command (222-225), learning-ages.py invocation (180-181) |
| Conditional paths | ~55 | Consolidation flow (179-215), plan-archive (229-235), multi-handoff merge (48-54), invalidation check (170-177) |
| Redundant content | ~20 | Task naming/format (56-65, restates execute-rule.md), learnings format (142-154, restates learnings.md header) |
| Examples | ~35 | Haiku task examples (67-90), preserve specifics list (108-127) |
| Guidelines | ~20 | Target 75-150 lines (103-107), context preservation principles (277-298) |
| Reference loads | ~10 | Template.md reference, example reference |
| Framework overhead | ~15 | Continuation protocol (309-318), additional resources section (320-330) |

**Estimated reduction:** ~80-100 lines achievable through conditional path extraction (~45 lines), redundancy removal (~15 lines), example condensation (~15 lines), guideline compression (~10 lines). Target: ~230-250 lines.

### Commit Skill (237 lines)

**Segment inventory:**

| Category | Lines | Specific blocks |
|---|---|---|
| Core rules | ~15 | Only-commit-when-asked (18-21), precommit gate (123), no error suppression constraint |
| Mechanical instructions | ~45 | Separate Bash calls (3 occurrences), subshell pattern (145-147), heredoc syntax, stage/commit/verify steps |
| Conditional paths | ~25 | Submodule handling (128-149), vet gate branches (96-113), context mode split |
| Redundant content | ~20 | Error suppression (202), secrets (204), heredoc (201) — all in system prompt. Vet gate partially restates vet-requirement.md |
| Examples | ~40 | Commit message examples (70-86), context gathering commands (229-237) |
| Guidelines | ~10 | Message style rules (60-68) |
| Reference loads | ~5 | Gitmoji index reference |
| Framework overhead | ~10 | HTML comment (92-94), continuation frontmatter |

**Estimated reduction:** ~50-70 lines achievable through redundancy removal (~15 lines), mechanical instruction consolidation (~10 lines), conditional path extraction (~15 lines), example condensation (~15 lines). Target: ~170-190 lines.

### Combined savings estimate

| Metric | Before | After | Reduction |
|---|---|---|---|
| Handoff SKILL.md | 330 lines | ~240 lines | ~27% |
| Commit SKILL.md | 237 lines | ~180 lines | ~24% |
| Runtime Reads eliminated | 2 calls + 157 lines | 1 call + 77 lines | ~50% |
| Template.md | 80 lines (Read) | ~20 lines (inlined) | 75% |
| Gitmoji index | 77 lines (Read) | 77 lines (Read, kept) | 0% (deferred to CLI tool) |
| Tool-call round-trips | Sequential per step | Batched where independent | ~2-4 fewer round-trips per invocation |

**Important:** These are prose instruction optimizations independent of the CLI tool tasks. When Handoff CLI and Commit CLI ship, the mechanical instruction sections (~60 lines handoff, ~45 lines commit) become eliminable — a further ~20% reduction each.

## Grounding Assessment

**Quality label:** Moderate

**Evidence basis:**
- LLMLingua's budget controller concept (differential compression by content type) directly applicable
- ProCut's segment-then-prune methodology maps cleanly onto the internal dimension analysis
- No established framework specifically addresses "LLM skill document optimization" — this is an adapted application
- Practical engineering consensus (conditional inclusion, structured formatting) is well-established but not formalized as named methodology

**Searches performed:**
- "LLM prompt optimization token efficiency compression methodology 2025 2026" → LLMLingua, CompactPrompt
- "prompt compression framework methodology reduce tokens maintain performance" → ProCut, compression taxonomy
- "instruction optimization LLM system prompt token reduction best practices" → practical engineering patterns
- "optimizing AI agent system prompts token efficiency agentic workflows 2025" → multi-agent design, SupervisorAgent
- Fetched: portkey.ai token efficiency guide, sandgarden.com prompt compression taxonomy

**Gaps:**
- No empirical data on adherence degradation from compression of LLM skill instructions specifically
- Compression rates are heuristic (adapted from automated compression research to manual editing)
- No framework for measuring "defensive rule attribution" — the severity × frequency classification is ungrounded (internal analysis only)

## Sources

- [LLMLingua (Microsoft Research)](https://www.microsoft.com/en-us/research/blog/llmlingua-innovating-llm-efficiency-with-prompt-compression/) — Primary. Budget controller concept, differential compression ratios by content type.
- [LLMLingua GitHub](https://github.com/microsoft/LLMLingua) — Primary. Implementation details, compression methodology (EMNLP'23, ACL'24).
- [ProCut: LLM Prompt Compression via Attribution Estimation](https://arxiv.org/html/2508.02053) — Primary. Segment-then-prune methodology, 78% token reduction.
- [CompactPrompt: Unified Pipeline](https://arxiv.org/html/2510.18043v1) — Secondary. Self-information scoring, n-gram abbreviation. 2.35x reduction.
- [Portkey: Optimize Token Efficiency](https://portkey.ai/blog/optimize-token-efficiency-in-prompts/) — Secondary. Practical techniques: batch prompt, skeleton-of-thought, concise engineering.
- [Sandgarden: Prompt Compression](https://www.sandgarden.com/learn/prompt-compression) — Secondary. Taxonomy: filtering, distillation, encoding, budget-aware compression.
- [Prompt Compression for LLM Cost Reduction (MLMastery)](https://machinelearningmastery.com/prompt-compression-for-llm-generation-optimization-and-cost-reduction/) — Secondary. Overview of compression categories.
- [Token Optimization for AI Agents (Elementor)](https://medium.com/elementor-engineers/optimizing-token-usage-in-agent-based-assistants-ffd1822ece9c) — Secondary. Agentic-specific strategies.
- [Multi-Agent Design: Optimizing with Better Prompts](https://arxiv.org/html/2502.02533v1) — Secondary. Prompt as primary optimizable component in agent systems.
- [Agents At Work: 2026 Playbook](https://promptengineering.org/agents-at-work-the-2026-playbook-for-building-reliable-agentic-workflows/) — Secondary. Context management, prompt caching for agents.
