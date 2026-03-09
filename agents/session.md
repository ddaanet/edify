# Session Handoff: 2026-03-09

**Status:** Format grounding spec refined. Blocked on two subtree deliveries (ar-how-verb-form, ar-threshold-calibration).

## Completed This Session

**Memory Format Grounding (S-C):**
- Executed `/ground` skill — parallel diverge-converge research
- Internal branch: codebase pattern inventory of 366 entries, trigger taxonomy, when/how resolver analysis, index structure metrics (file: `plans/reports/memory-format-internal-codebase.md`)
- External branch: cognitive science (encoding specificity, CBR predictive indexing, ACT-R), educational psychology (Bloom's revised, conditional/procedural), hierarchical RAG, faceted classification, LLM agent memory (MemGPT/Letta, A-MEM), Dublin Core metadata (file: `plans/reports/memory-format-external-research.md`)
- Convergence: Strong grounding — 3 independent frameworks validate trigger format, 2 taxonomies validate when/how distinction (file: `plans/reports/memory-format-grounding.md`)

**Format Spec Refinements (discussion session):**
- D-1 (suspended): "how to" vs "how" verb form — requires grounding via fuzzy match scores, agent query logs, retrieval accuracy. Not a design decision until measured.
- D-2 (withdrawn): "when planning" anti-pattern rejected — contradicts "broadest applicable verb" convention. Existing "outcome framing" drift covers the real issue.
- D-3 (applied): Index format changed to md lists, dropped `/` prefix, lowercase operators. Separates storage format from CLI invocation syntax.
- D-4 (applied): All validation rules promoted to error. Agents ignore warnings. Ungrounded thresholds kept but marked for calibration, not deferred.
- D-5 (applied): LLM conditional knowledge deficit stated as motivating problem in §1. Internal evidence: 304/367 when-class entries, ~3% spontaneous recall, structured pipelines compensate.
- D-6 (applied): All thresholds user-configurable with feedback pipeline. Five thresholds identified for calibration against 366-entry dataset.

## In-tree Tasks

- [x] **AR Format Grounding** — `/ground` | opus

## Worktree Tasks

- [ ] **Ground how verb form** → `ar-how-verb-form` — `/design` | sonnet
  - Measure fuzzy match scores ("how format X" vs "how to format X"), extract agent query patterns via session scraper, observe retrieval accuracy
  - Tools: `fuzzy.py` score_match, `session-scraper.py`, 366-entry index
  - Retrieval accuracy requires agent behavior observation, not just script execution
- [ ] **Calibrate thresholds** → `ar-threshold-calibration` — `/orchestrate` | sonnet
  - Measure distributions for all 5 thresholds against 366-entry dataset, set at natural breakpoints, implement user-configurable defaults with feedback pipeline
  - Thresholds: keyword overlap %, specificity range, keyword count, content words, discriminating count
  - Human judgment needed for "is this a true duplicate" / "is this over-specific" labeling

## Reference Files

- `plans/reports/memory-format-grounding.md` — format specification (primary deliverable, consumed by S-G, S-K, S-E, S-D)
- `plans/reports/memory-format-internal-codebase.md` — codebase pattern inventory (audit evidence)
- `plans/reports/memory-format-external-research.md` — framework research (audit evidence)
- `plans/active-recall/outline.md` — parent design outline (S-C context)

## Next Steps

Blocked on subtree delivery. After both worktrees merge back, apply measurement results to spec and merge branch to main.
