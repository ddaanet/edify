# How Verb Form Grounding Report

**Grounding:** Moderate

Two questions about the recall system's `/how` entry format: fuzzy matcher robustness to prefix noise, and agent recognition of entry format during index scanning.

## Research Foundation

**Internal branch:** `plans/reports/how-verb-form-internal-codebase.md` — codebase exploration of fuzzy matcher, resolver, index format, and test coverage.

**External branch:** `plans/reports/how-verb-form-external-research.md` — fuzzy matching algorithms, LLM prompt sensitivity, IR stopword treatment.

---

## Question 1: Fuzzy Matcher Robustness to Prefix Noise

### Framework Mapping

Character-level fuzzy matching algorithms (Levenshtein, Jaro-Winkler, fzf-style subsequence) have no mechanism for function-word awareness. "to" is 2-3 characters of noise, not a semantically empty particle. This is a well-understood limitation in the string matching literature.

Token-level algorithms (TF-IDF cosine, BM25) handle function words naturally via IDF downweighting — high-frequency terms like "to" contribute negligibly to similarity scores.

The project's fzf V2 subsequence matcher (`fuzzy.py`) is character-level. It requires all query characters to appear as a subsequence in the candidate. "to write X" queried against stored "write X" fails completely (0.0 score) because "t" from "to" has no match position after "w" in "write".

### Adaptations

The `removeprefix("to ")` band-aid at `resolver.py:196` pre-normalizes queries before matching. This transforms "to write X" → "write X" before the matcher sees it. It works for the specific "to " case but:

- Doesn't generalize to other prefix noise ("please write X", "can you write X")
- Addresses a symptom (query has "to") rather than the cause (matcher has zero tolerance for prefix mismatch)
- Is asymmetric: only needed because entries store bare imperatives

**Established approaches from external research:**
- Pre-normalization (current approach, extend to more patterns)
- Token-level matching (eliminate character-level prefix sensitivity entirely)
- Hybrid: token match for ranking, character match for typo tolerance

### Finding

The matcher's prefix failure is a real deficiency — confirmed by both codebase evidence (0.0 scores) and external research (character-level matchers have no stopword mechanism). The fix is an engineering choice between extending pre-normalization or upgrading to token-level matching. The entry format question ("how to X" vs "how X") is orthogonal — whichever format is chosen, the matcher should tolerate the other form gracefully.

**Implication for verb form decision:** Changing entries from "how X" to "how to X" does not fix the matcher. An agent querying "write init files" against stored "to write init files" would hit the same 0.0 failure in reverse. The fix belongs in the matcher or pre-normalization layer, not the entry format.

---

## Question 2: Agent Recognition During Index Scanning

### Framework Mapping

LLM prompt sensitivity research confirms models respond differently to wording variations — up to 76 accuracy points for formatting changes (template, example ordering). However:

- Studied variations are structural (Markdown vs JSON, example reordering), not within-phrase function word differences
- The "how to X" vs "how X" difference is a single function word in a short trigger phrase — smaller magnitude than anything in the literature
- No research isolates the infinitive "to" marker's effect on LLM recognition

IR research provides the closest analogue: "to" as infinitive marker carries grammatical intent (procedural signal). "How to configure X" signals procedure more explicitly than "how configure X". But this is a retrieval/parsing signal, not an LLM in-context recognition signal.

### Adaptations

No external framework directly applies. The question reduces to: does an LLM scanning a flat index of 63 `/how` entries more reliably recognize relevant entries when they read "how to verb" vs "how verb"?

**What external research suggests (inference, not evidence):**
- Larger models (Claude Sonnet/Opus) are more robust to minor wording variations
- The grammatical completeness of "how to X" may provide a marginally clearer procedural signal
- At 63 entries with ~490 tokens total, the ~63 token cost of adding "to" is negligible

**What external research cannot answer:**
- Whether the recognition difference is measurable in practice
- Whether it matters given the structured invocation paths (agents use `/how` CLI, not freeform scanning)
- Whether the current bare imperative format causes actual recognition failures

### Finding

External research cannot ground this question. The session.md conclusion stands: this requires an empirical A/B behavioral test, not literature-derived reasoning. The test design: vary index format, observe agent resolve success on real tasks, measure difference.

**Practical consideration from internal branch:** The recall system has two retrieval paths:
1. **CLI invocation** (`/how write init files`) — agent copies or adapts a trigger from the index. Format matters only if the agent's adaptation introduces "to" (handled by `removeprefix` band-aid).
2. **Spontaneous recognition** — agent recognizes a relevant entry while scanning the index during a task. This is where format might matter, but no data exists on how often this path fires or whether it's affected by verb form.

---

## Grounding Assessment

**Quality label: Moderate**

- Q1 (fuzzy matcher): One applicable framework area (character-level vs token-level matching) with clear applicability. The deficiency is well-characterized and the fix space is established. **Strong** for this sub-question.
- Q2 (agent recognition): No directly applicable research. Inference from adjacent findings (LLM prompt sensitivity, IR stopword effects) only. **Thin** for this sub-question.
- Combined: Moderate — one question well-grounded, one requiring empirical measurement.

**Searches performed:**
- Fuzzy string matching stopword sensitivity
- LLM prompt sensitivity wording variation / RAG retrieval prompt format
- Information retrieval infinitive marker / query reformulation function words
- String similarity algorithm prefix handling / Jaro-Winkler prefix bonus
- LLM in-context learning format sensitivity

**Gaps:**
- No research on single-function-word effects in subsequence matching
- No LLM studies on within-phrase function word presence (vs structural formatting changes)
- No IR research specific to short trigger phrases (3-6 words)

## Sources

### Primary
- Stanford IR Book: [Dropping Common Terms](https://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html) — stopword treatment in IR systems, IDF as natural downweighting mechanism
- [Prompt Formatting Impact on LLM Performance (arXiv 2411.10541)](https://arxiv.org/html/2411.10541v1) — up to 76pt accuracy variation from formatting changes
- [LLM Sensitivity to Spurious Features (ICLR 2024)](https://openreview.net/forum?id=RIu5lyNXjT) — sensitivity to morphological, syntactic, lexico-semantic features

### Secondary
- [Jaro-Winkler vs Levenshtein in AML Screening](https://www.flagright.com/post/jaro-winkler-vs-levenshtein-choosing-the-right-algorithm-for-aml-screening) — algorithm comparison, prefix bonus mechanics
- [Fuzzy String Matching at Scale](https://medium.com/tim-black/fuzzy-string-matching-at-scale-41ae6ac452c2) — TF-IDF for short string matching, IDF weighting
- [Stopword Removal Impact on IR (Springer)](https://link.springer.com/article/10.1007/s42979-023-01942-7) — stopword effects on retrieval quality

### Internal
- `plans/reports/how-verb-form-internal-codebase.md` — fuzzy matcher algorithm, removeprefix band-aid, index format inventory
- `plans/reports/how-verb-form-external-research.md` — full external research with synthesis
