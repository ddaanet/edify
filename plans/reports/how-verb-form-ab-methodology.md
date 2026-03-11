# A/B Testing Methodology for How-Verb-Form: Grounding Report

**Grounding:** Strong

Established methodologies exist for measuring LLM behavioral differences from minor prompt wording variations. The three objections raised against feasibility (silent failure, contamination, low stakes) each have methodological answers.

## Research Foundation

**Internal branch:** `plans/reports/how-verb-form-ab-methodology-internal.md` — existing test infrastructure, session scraper capabilities, prototype scripts, infrastructure gaps.

**External branch:** `plans/reports/how-verb-form-ab-methodology-external.md` — named frameworks (ProSA, FormatSpread, ChainForge), experimental designs, statistical methods, silent failure approaches.

---

## Framework Mapping

### Objection 1: Silent Failure → Forced Selection Task

**General principle:** When the behavior under test is implicit (agent silently not recognizing an entry), externalize it into an explicit task. IR evaluation methodology (TREC/Cranfield tradition) establishes this: construct tasks with known-relevant entry sets, measure recall as fraction recognized.

**Forced selection design:** Present the agent with the index and a task description. Ask it to LIST which entries are relevant — don't ask it to use them. Non-selection becomes visible data, not silent absence.

**Project application:** Construct 15-20 task descriptions (drawn from real session contexts via session scraper). For each task, human annotates which of 63 entries are relevant (ground truth). Run under both index formats. Measure per-entry recognition as binary (listed / not listed).

### Objection 2: Contamination → It IS the Signal

**General principle:** When the treatment (index format) is read by the subject (agent) before the measured behavior (recognition), the reading-processing chain is not a confound — it's the mechanism being tested. FormatSpread (ICLR 2024) treats prompt format as the independent variable precisely because the model processes the format before producing output.

**Project application:** The agent reads "how to write init files" or "how write init files" in the index, then decides whether it's relevant to the task. If the format affects that decision, that's the result. The concern about "agents copying triggers they just read" applies to query generation (how the agent phrases a `/how` command), not to recognition (whether the agent identifies an entry as relevant).

### Objection 3: Low Stakes → ProSA Instance-Level Analysis

**General principle:** Aggregate effects can be small while instance-level effects are large. ProSA (EMNLP 2024) shows sensitivity varies per-instance — some inputs are highly sensitive to format while others are not. A small aggregate effect may hide a subset of entries where format matters substantially.

**Project application:** The 63 entries are heterogeneous. Some have distinctive verbs ("architect", "deduplicate"), others have common verbs ("write", "format", "handle"). Format sensitivity likely varies by entry. Instance-level analysis reveals which specific entries benefit from "to", even if the average effect is small.

---

## Recommended Experimental Design

### Design: Paired Forced Selection

1. **Task construction:** Extract 15-20 real task contexts from session history (session scraper Stage 6). Select tasks that exercised different parts of the index.
2. **Ground truth:** Human annotates 3-5 relevant entries per task from the 63 `/how` entries.
3. **Index variants:** Generate two versions of `memory-index.md` — variant A (current: `how <verb>`), variant B (`how to <verb>`). All other content identical.
4. **Execution:** For each (task, variant) pair, prompt the agent: "Given this task, which `/how` entries from the index are relevant? List them." Temperature 0.
5. **Measurement:** Per-entry binary recognition (listed / not listed). 63 entries × 15 tasks × 2 variants = 1890 observations.

### Statistical Analysis

**Primary test:** McNemar's test on the paired binary outcomes. Focuses on discordant pairs (entries recognized under one format but not the other).

**Sample size:** 15 tasks × 63 entries = 945 paired observations per format. Adequate for medium effects (Cohen's g > 0.15). If discordant rate is low (< 5%), use Fisher's exact test.

**Supplementary:** Per-entry breakdown — which entries flip between formats? Instance-level analysis (ProSA-inspired) to identify format-sensitive entries.

### Controls

- Same model, temperature 0 (deterministic)
- Same system prompt, same task description text
- Only the index trigger format varies
- Task presentation order randomized (mitigate position effects)

---

## Infrastructure Requirements

### Exists (reusable)

- Session scraper: task context extraction (Stage 6)
- How-verb-form prototypes: verb form classification, query extraction
- Index parser: read current index entries
- Fuzzy matcher tests: baseline measurement

### Needs building

- **Index variant generator:** Parse `memory-index.md`, transform `/how <verb>` ↔ `/how to <verb>`, validate equivalence. Small script.
- **Task selector:** Use session scraper to find sessions with `/how` invocations, extract task contexts, deduplicate. Adapts existing prototype.
- **Ground truth annotation:** Human labels relevant entries per task. Manual, one-time effort.
- **Forced selection harness:** Prompt template + result parser. Runs agent with each (task, variant) pair, collects listed entries.
- **Analysis script:** McNemar's test, per-entry breakdown, effect size calculation. Standard statistics.

### Does NOT need building

- Task replay infrastructure (forced selection is simpler and more direct)
- Agent simulation framework (real agent invocation suffices)
- Instrumented observation (explicit listing replaces implicit measurement)

---

## Grounding Assessment

**Quality label: Strong**

Two established frameworks directly applicable:
- **FormatSpread / ProSA** (ICLR 2024, EMNLP 2024): Named methodologies for measuring LLM sensitivity to prompt format variations, including instance-level analysis
- **TREC/Cranfield evaluation** (IR tradition): Ground truth construction, recall measurement, paired comparison — standard methodology for exactly this class of problem

The forced selection design eliminates the silent failure problem entirely. The contamination reframing (treatment = mechanism, not confound) is established in the prompt sensitivity literature. McNemar's test is the standard statistical method for paired binary outcomes.

**Gaps:**
- No research specifically tests single-function-word effects in index-scanning tasks (our specific scenario)
- Sample size is constrained by entry count (63) — compensated by task count
- Forced selection measures explicit recognition, which may differ from organic recognition during task execution (acknowledged trade-off)

## Sources

### Primary
- [ProSA: Prompt Sensitivity Assessment (EMNLP 2024)](https://arxiv.org/abs/2410.12405) — instance-level sensitivity, PromptSensiScore metric
- [FormatSpread: Quantifying Sensitivity to Spurious Features (ICLR 2024)](https://arxiv.org/abs/2310.11324) — format perturbation methodology, Bayesian optimization for format space
- [Evaluation in Information Retrieval (Stanford IR Book, Ch. 8)](https://nlp.stanford.edu/IR-book/pdf/08eval.pdf) — ground truth construction, recall measurement, pooled relevance judgment
- [McNemar's Test for Paired Binary Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC2902578/) — statistical method for discordant pair analysis

### Secondary
- [ChainForge: Visual Toolkit for LLM Hypothesis Testing (CHI 2024)](https://arxiv.org/abs/2309.09128) — practical A/B comparison tooling
- [Promptfoo](https://www.promptfoo.dev/) — CLI framework for prompt evaluation
- [Does Tone Change the Answer? (arXiv 2512.12812)](https://www.arxiv.org/pdf/2512.12812) — repeated trials + statistical testing methodology

### Internal
- `plans/reports/how-verb-form-ab-methodology-internal.md` — existing infrastructure inventory
- `plans/reports/how-verb-form-ab-methodology-external.md` — full external research
