# A/B Testing LLM Prompt Format Sensitivity: External Research

## Research Question

What established methods exist for measuring LLM behavioral differences from minor prompt wording variations, specifically for testing whether "how to verb" vs "how verb" affects agent recognition of index entries?

---

## Named Methodologies and Frameworks

### ProSA (Prompt Sensitivity Assessment)
- **Source:** EMNLP 2024 Findings
- **What it does:** Measures prompt sensitivity at the instance level (per-input, not per-dataset). Defines PromptSensiScore (PSS) metric. Uses decoding confidence to explain sensitivity mechanisms.
- **Key insight:** Sensitivity varies per-instance, not just per-dataset. Aggregating hides important variation.
- **Relevance:** The per-instance framing maps to our per-entry recognition problem. Some entries may be sensitive to format while others are not.
- **URL:** https://arxiv.org/abs/2410.12405

### FormatSpread
- **Source:** Sclar et al., ICLR 2024
- **What it does:** Algorithm that estimates min/max performance range across semantically equivalent prompt formats using Bayesian optimization. Works without model weight access (API-compatible).
- **Key finding:** Up to 76 accuracy points difference from formatting changes alone. Sensitivity persists across model scale, few-shot count, and instruction tuning.
- **Relevance:** Establishes that single-token formatting differences CAN produce large effects. Our "to" token hypothesis is within the class of variations they study.
- **URL:** https://arxiv.org/abs/2310.11324
- **Code:** https://github.com/msclar/formatspread

### IPS (Interaction-based Prompt Sensitivity)
- **Source:** OpenReview (under review)
- **What it does:** Game-theoretic interaction framework for fine-grained prompt sensitivity analysis. Quantifies changes in internal interactions when subtle prompt changes are introduced.
- **Relevance:** Theoretical framework for understanding WHY a change matters, not just whether it does.
- **URL:** https://openreview.net/forum?id=6fHZR6uxNa

### ChainForge
- **Source:** Harvard, CHI 2024
- **What it does:** Visual toolkit for prompt engineering and hypothesis testing. Supports A/B comparison across prompt variations, models, and settings. Built-in visualization of results across permutations.
- **Relevance:** Practical tool for running the comparison. Supports the paired-comparison design we need.
- **URL:** https://arxiv.org/abs/2309.09128
- **Tool:** https://www.chainforge.ai/

### Promptfoo
- **What it does:** CLI framework for evaluating prompts across models and variations. Matrix evaluation (prompt x model x test case). Supports custom assertions and metrics.
- **Relevance:** Could automate running test cases if we externalize the recognition task into a measurable format.
- **URL:** https://www.promptfoo.dev/

---

## Experimental Design Patterns

### 1. Paired Comparison (Within-Subject Design)

The standard approach for minor prompt variations. Same test cases evaluated under both conditions.

**Design:**
- Construct N test scenarios (tasks requiring index lookup)
- For each scenario, run with index format A ("how verb") and format B ("how to verb")
- Measure recognition outcome per entry per scenario
- Compare using paired statistical test

**Why paired:** Eliminates between-subject variance (task difficulty, entry relevance). Each entry serves as its own control.

### 2. Ablation Study Design

Isolate the single variable (presence/absence of "to" token) while holding everything else constant.

**Controls needed:**
- Same model, same temperature (0 for determinism, or fixed seed)
- Same system prompt, same task description
- Same index content (only format of trigger line varies)
- Same set of test tasks

**From the literature:** Researchers conduct ablation studies across multiple prompt configurations, with results showing that structural prompt components play a critical role (arxiv 2511.06227).

### 3. Repeated Trials with Statistical Testing

From tone-sensitivity research (arxiv 2512.12812):
- Apply each variant multiple times per test case
- Analyze using mean differences and pairwise t-tests with 95% CI
- Separates genuine effects from stochastic variation

**For our case:** At temperature 0, repetition should yield identical results (deterministic). At temperature > 0, multiple trials per (task, format) pair are needed.

### 4. Pooled Relevance Judgment (IR Methodology)

From Cranfield/TREC evaluation tradition:
- Establish ground truth: for each test task, which index entries SHOULD be recognized as relevant?
- Ground truth created by human expert judgment (not by the system under test)
- Measure recall = (entries recognized) / (entries that should have been recognized)
- Compare recall between format A and format B

**Source:** Stanford IR textbook, Ch. 8 (https://nlp.stanford.edu/IR-book/pdf/08eval.pdf)

---

## Statistical Methods for Detecting Small Effects

### McNemar's Test (Primary Recommendation)

**Why it fits:** Binary paired data (recognized/not recognized, same entry under two conditions). Focuses specifically on discordant pairs (cases where the two formats disagree).

- Null hypothesis: format A and format B have equal recognition rates
- Test statistic based on entries that flip (recognized in A but not B, or vice versa)
- Does not require normal distribution assumption
- Power depends on number of discordant pairs, not total pairs

**Sample size for McNemar's test:** With 63 entries and ~10 test tasks = 630 paired observations. If the discordant rate is low (say 5% = ~32 discordant pairs), power may be limited. Need discordant proportion > ~8% for adequate power at alpha=0.05.

**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2902578/

### Fisher's Exact Test (Small Sample Fallback)

When discordant pair count is very small (< 25), McNemar's chi-squared approximation is unreliable. Fisher's exact test on the 2x2 discordant table is more appropriate.

### Effect Size: Cohen's g (for McNemar)

Measures the degree to which discordant pairs favor one condition over the other:
- g = 0.05 (small), g = 0.15 (medium), g = 0.25 (large)
- With 63 entries x 10 tasks: detectable effect depends on discordance rate

### Bootstrap Confidence Intervals

Non-parametric alternative when distributional assumptions are questionable:
- Resample (task, entry) pairs with replacement
- Compute recognition rate difference for each resample
- Report 95% CI for the difference

---

## Handling the "Silent Failure" / Counterfactual Problem

This is the core methodological challenge: recognition failure is the absence of an action (agent doesn't invoke an entry), making it invisible in normal operation.

### Approach 1: Controlled Task Design with Known Relevant Set

**Design ground truth tasks** where the correct set of relevant entries is predetermined:
- Create tasks that unambiguously require specific index entries
- Measure recall (what fraction of the relevant set was actually invoked)
- Silent failure becomes measurable: entry X was relevant but not invoked

**This is the IR evaluation approach.** The key is constructing tasks with clear ground truth.

### Approach 2: Forced Selection / Explicit Recognition Task

**Externalize the implicit recognition** into an explicit task:
- Present the agent with the index and a task description
- Ask it to LIST which entries are relevant (not to use them, just identify them)
- Eliminates the "silent" aspect entirely — non-selection is visible

**Trade-off:** Tests a different behavior (explicit listing vs organic recognition during task execution). May not capture the same cognitive process.

### Approach 3: Instrumented Observation

- Log all index entries the agent references, quotes, or invokes during task execution
- Compare invocation sets between format A and format B for each task
- Requires instrumentation (tool call logging, or structured output format)

### Approach 4: Perturbation-Based (from FormatSpread)

- Inject format variation as a perturbation
- Measure output stability (does the set of recognized entries change?)
- No need for ground truth — measures sensitivity directly

---

## Sample Size Guidance

### From the Literature

- **FormatSpread:** Evaluated across standard benchmarks (hundreds to thousands of test cases). Used Bayesian optimization to reduce the number of format variants needed (~20 formats sufficient to estimate the performance range).
- **Tone sensitivity study:** Used multiple trials per condition (typically 5-10 repetitions) with statistical testing.
- **ProSA:** Evaluated on standard NLP benchmarks with thousands of instances.

### For Our Specific Problem

Parameters:
- 63 index entries
- Single binary variation ("how verb" vs "how to verb")
- Need to construct test tasks

**Power analysis for McNemar's test:**
- With 63 entries and 1 task: 63 paired observations. Underpowered unless effect is very large.
- With 63 entries and 10 tasks: 630 paired observations. Adequate for medium effects IF tasks are sufficiently varied.
- With 63 entries and 20 tasks: 1260 paired observations. Good power for small effects.

**Key constraint:** Test tasks must be independent and varied. Reusing similar tasks inflates the apparent sample size without adding information. Each task should exercise a different subset of the index.

**Practical minimum:** 10-15 diverse test tasks, yielding 630-945 paired observations. This gives adequate power for medium effect sizes (g > 0.15) on McNemar's test.

---

## Index Contamination Problem

Our specific challenge: the agent reads the index before querying, so its query form is influenced by the index format. The literature addresses this:

### From FormatSpread / ProSA

These frameworks assume the prompt format IS the independent variable being manipulated. They don't face contamination because the prompt IS the treatment.

**Our situation is different:** The index format is the treatment, but the agent's behavior is mediated by reading the index. This creates a confound:
- Agent reads "how to verb" format -> may copy "how to" pattern in its reasoning
- Agent reads "how verb" format -> may copy "how" pattern

**This is not a bug in our experiment — it IS the experiment.** The question is whether the format affects recognition, and the mechanism may well be through the agent's processing of the format. The contamination IS the signal.

### Recommendation: Two-Level Design

1. **Level 1 (Index scanning):** Does the agent correctly identify relevant entries when scanning the index? (Forced selection task — Approach 2 above)
2. **Level 2 (Organic use):** Does the format affect actual invocation during real tasks? (Controlled task with instrumentation — Approach 1+3 above)

Level 1 isolates recognition. Level 2 measures end-to-end behavioral impact.

---

## Practical Applicability to Our Problem

### What maps directly:
- **Paired comparison design** — same entries, same tasks, two formats. Standard approach.
- **McNemar's test** — binary recognition outcome, paired data. Correct statistical test.
- **Ground truth construction** — we can create tasks with known-relevant entry sets (IR methodology).
- **Forced selection task** — simplest way to make silent failure visible.

### What needs adaptation:
- **Sample size** — most literature uses hundreds/thousands of test cases. Our 63 entries constrain this. Compensate with more test tasks.
- **Contamination framing** — literature treats prompt format as exogenous. Our format is endogenous (agent reads it). Reframe as feature of the design, not a confound.
- **Effect granularity** — literature measures aggregate accuracy. We need per-entry analysis (which specific entries are affected?). ProSA's instance-level approach is the closest match.

### Recommended Design for Our Case:

1. Construct 15-20 test tasks with predetermined relevant entry sets (3-5 relevant entries each)
2. Run each task twice: once with "how verb" index, once with "how to verb" index
3. Temperature 0 for determinism
4. Measure per-entry recognition (binary: invoked or not)
5. McNemar's test on the full (entry x task) observation matrix
6. Supplement with forced-selection variant (ask agent to list relevant entries explicitly)
7. Report both aggregate effect and per-entry breakdown

---

## Sources

- [ProSA: Assessing and Understanding the Prompt Sensitivity of LLMs](https://arxiv.org/abs/2410.12405) — EMNLP 2024 Findings
- [Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design (FormatSpread)](https://arxiv.org/abs/2310.11324) — ICLR 2024
- [Benchmarking Prompt Sensitivity in Large Language Models](https://arxiv.org/html/2502.06065v1) — PromptSET dataset
- [Evaluating and Explaining Prompt Sensitivity Using Interactions (IPS)](https://openreview.net/forum?id=6fHZR6uxNa)
- [ChainForge: A Visual Toolkit for Prompt Engineering and LLM Hypothesis Testing](https://arxiv.org/abs/2309.09128) — CHI 2024
- [Does Tone Change the Answer? Evaluating Prompt Tone Sensitivity](https://www.arxiv.org/pdf/2512.12812) — repeated trials + t-tests methodology
- [Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs](https://arxiv.org/pdf/2509.01790)
- [Statistical Design of Prompt Testing](https://www.statology.org/statistical-design-prompt-testing/) — Statology
- [Evaluation in Information Retrieval](https://nlp.stanford.edu/IR-book/pdf/08eval.pdf) — Stanford IR textbook, Ch. 8
- [McNemar's Test for Paired Binary Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC2902578/)
- [A/B Testing for LLM Prompts: A Practical Guide](https://www.braintrust.dev/articles/ab-testing-llm-prompts) — Braintrust
- [Promptfoo: Test Your Prompts](https://www.promptfoo.dev/docs/intro/)
- [A Practical Guide for Evaluating LLMs and LLM-Reliant Systems](https://arxiv.org/html/2506.13023v1)
