# How Verb Form: External Research

Research on how "how to X" vs "how X" affects fuzzy string matching and LLM/IR recognition.

## 1. Fuzzy String Matching and Function Words

### Character-level algorithms (Levenshtein, Jaro-Winkler)

**Levenshtein distance** counts minimum single-character edits (insert, delete, substitute). Adding "to " to a string adds 3 edit operations. For short strings like "how verb" (8 chars) vs "how to verb" (11 chars), that's a normalized distance of ~0.27 — enough to drop below typical similarity thresholds (0.8+).

**Jaro-Winkler** adds a prefix bonus for strings sharing a common prefix (up to 4 chars, scaling factor 0.1). Formula: `JW = Jaro + (L * P * (1 - Jaro))`. Both "how verb" and "how to verb" share prefix "how " (4 chars max), so the prefix bonus is identical. The divergence after position 4 ("t" vs first char of verb) creates character transposition mismatches in the Jaro base calculation, reducing similarity.

**Key finding:** Neither algorithm has stopword awareness. "to" is treated as 2-3 characters of noise, not as a semantically empty function word. The project's fzf-based matcher (subsequence DP + gap penalties) is similarly character-level — "to " creates gap penalties between matched characters.

Sources:
- [Jaro-Winkler vs Levenshtein in AML Screening](https://www.flagright.com/post/jaro-winkler-vs-levenshtein-choosing-the-right-algorithm-for-aml-screening)
- [Jaro-Winkler distance - Wikipedia](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
- [Jaro Winkler vs Levenshtein Distance (Medium)](https://srinivas-kulkarni.medium.com/jaro-winkler-vs-levenshtein-distance-2eab21832fd6)

### Token-based algorithms (TF-IDF cosine, BM25)

**TF-IDF cosine similarity** naturally handles "to" via IDF weighting — "to" appears in most documents, gets near-zero IDF weight, contributes negligibly to the similarity vector. Adding or removing "to" barely changes the cosine score.

**BM25** similarly downweights high-frequency terms through IDF. The "to" token would have minimal impact on retrieval scores.

**Short-string caveat:** For very short strings (3-5 tokens), even low-IDF tokens occupy a larger fraction of the vector. One source notes that for short string matching, articles and function words "are worth keeping around for matching, since titles may differ by only an article word, although we want to place less weight on them."

Sources:
- [Fuzzy String Matching at Scale (Medium)](https://medium.com/tim-black/fuzzy-string-matching-at-scale-41ae6ac452c2)
- [TF-IDF and Cosine Similarity (Medium)](https://medium.com/@mifthulyn07/comparing-text-documents-using-tf-idf-and-cosine-similarity-in-python-311863c74b2c)

### Project-specific: fzf V2 subsequence matcher

The project's `score_match()` in `fuzzy.py` uses character-subsequence DP with gap penalties. For "how to verb" (candidate) matched against "how verb" (query):
- All query chars found as subsequence: yes (h-o-w-[gap: " to "]-v-e-r-b)
- Gap penalty for skipping " to ": `GAP_START_PENALTY(-3) + GAP_EXTENSION_PENALTY(-1) * 3 = -6`
- Word overlap bonus: "how" and "verb" match (0.5 each = 1.0)

For "how verb" (candidate) matched against "how to verb" (query):
- Query "how to verb" has "to" which must match somewhere in "how verb"
- "t" not found after "w" in "how verb" — **complete match failure, score 0.0**

This is the asymmetry identified in session.md: querying with "to" against a candidate without "to" can cause total failure, not just degraded scores.

## 2. LLM Sensitivity to Prompt Wording Variations

### Research findings

**Magnitude of sensitivity:** LLMs show up to 76 accuracy points difference from formatting changes in few-shot settings (LLaMA-2-13B). GPT-3.5-turbo varies up to 40% on code translation depending on prompt template. Larger models (GPT-4, Claude) are more robust but not immune.

**What matters:** Research identifies sensitivity to:
- Template format (plain text vs Markdown vs JSON vs YAML)
- Example ordering (>40% accuracy shift from reordering)
- Morphological, syntactic, and lexico-semantic features
- Label format (even random labels outperform no labels)

**What's less studied:** The specific effect of a single function word ("to") in an otherwise identical short phrase. Most research examines structural formatting changes (template, ordering) rather than within-phrase function word presence. The closest analogue is morphological/syntactic variation research, which confirms these matter but doesn't isolate the "to" infinitive marker specifically.

**Robustness scaling:** Sensitivity persists even with increased model size, more few-shot examples, or instruction tuning — though absolute magnitude decreases with model capability.

Sources:
- [Does Prompt Formatting Have Any Impact on LLM Performance? (arXiv)](https://arxiv.org/html/2411.10541v1)
- [Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design (ICLR 2024)](https://openreview.net/forum?id=RIu5lyNXjT)
- [The Profound Impact of Prompt Variations (Substack)](https://thebigdataguy.substack.com/p/the-profound-impact-of-prompt-variations)
- [Evaluating the Sensitivity of LLMs to Prior Context (arXiv)](https://arxiv.org/pdf/2506.00069)

### RAG-specific findings

Query format affects RAG pipeline performance at the retrieval stage (embedding similarity) and the generation stage (prompt interpretation). HyDE and Query2Doc expand queries with pseudo-documents to improve retrieval, suggesting that raw query form matters enough to warrant reformulation.

Sources:
- [Enhancing RAG: A Study of Best Practices (arXiv)](https://arxiv.org/abs/2501.07391)
- [RAG Comprehensive Survey (arXiv)](https://arxiv.org/html/2506.00054v1)

## 3. Information Retrieval Treatment of Function Words

### Historical trend

IR systems moved from large stop lists (200-300 terms) to small stop lists (7-12 terms) to no stop list. Modern web search engines generally do not use stop lists. The word "to" appears on virtually all historical stop lists (it's among the most frequent English words).

### Why stop lists shrank

IDF weighting (and BM25's saturation function) naturally downweight high-frequency terms, making explicit stop lists redundant. Removing stopwords can harm phrase queries ("to be or not to be") and proximity-based retrieval.

### Impact quantification

Stopword removal reduces index size by 30-50%. For retrieval quality, the effect is mixed: removal improves precision for keyword-heavy queries but can hurt recall for natural language queries where function words carry structural meaning ("how to" signals intent differently than "how").

### "To" as infinitive marker

"To" occupies a unique position: it's a high-frequency function word (stopword candidate) but also an infinitive marker carrying grammatical information. In "how to configure X", "to" signals procedural intent. In "how configure X", the intent is still recoverable from context but the grammatical signal is absent.

No research was found specifically isolating the infinitive "to" from other stopword effects. The closest finding: IR research on query reformulation shows that function word removal aids keyword extraction but can lose intent signals.

Sources:
- [Stanford IR Book: Dropping Common Terms (Stop Words)](https://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html)
- [Stopword Removal Impact on IR for Code-Mixed Data (Springer)](https://link.springer.com/article/10.1007/s42979-023-01942-7)
- [Effects of Stop Words Elimination for Arabic IR (arXiv)](https://arxiv.org/pdf/1702.01925)

## 4. Synthesis: Implications for the Two Grounding Questions

### Question 1: Fuzzy matcher robustness to prefix mismatch

Character-level matchers (including the project's fzf-based algorithm) have no mechanism to handle function words specially. The "to" prefix causes:
- **Asymmetric failure:** Query with "to" against candidate without "to" → match failure (0.0)
- **Degraded score:** Query without "to" against candidate with "to" → gap penalties reduce score

Token-based matchers (TF-IDF, BM25) handle this naturally via IDF downweighting. The project's word-overlap bonus (0.5 per matching word) partially compensates but doesn't address the subsequence match failure.

**Established approaches:** Stopword stripping before matching, token-level matching instead of character-level, or hybrid approaches (token match for ranking, character match for typo tolerance).

### Question 2: Agent recognition during index scanning

Research confirms LLMs are sensitive to prompt wording, but the specific "how to X" vs "how X" difference is:
- Smaller than the variations studied (template changes, example reordering)
- In a domain (short trigger phrases in an index) where research is sparse
- Likely model-dependent (larger models more robust)

The strongest external signal: IR research showing "to" carries grammatical intent (procedural signal). An LLM scanning an index might benefit from "how to" as a clearer procedural marker, but this is inference from IR principles, not direct measurement. The session.md correctly identifies this as requiring an A/B behavioral test, not a literature-derived answer.

## Limitations

- No research found isolating single-function-word effects in fuzzy matching
- LLM prompt sensitivity research focuses on structural changes, not within-phrase word presence
- IR stopword research is corpus-level, not short-string-level
- The project's specific algorithm (fzf V2 subsequence) has no academic literature on stopword sensitivity
- All synthesis for the grounding questions is inference from adjacent findings, not direct evidence
