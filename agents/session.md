# Session Handoff: 2026-03-09

**Status:** Original grounding scrapped after review. Corrected problem statement captured, ready for restart.

## Completed This Session

**Grounding review (discussion):**
- Scrapped `plans/reports/how-verb-form-grounding.md` — answered wrong questions
- Original report measured fuzzy self-matching (tautological) and query distribution (contaminated by index-driven retrieval)
- Identified two actual questions the grounding must answer (see pending task)

## In-tree Tasks

- [-] **Ground how verb form** — `/design plans/ar-how-verb-form/problem.md` | sonnet
  - Scrapped: report answered wrong questions (fuzzy self-matching, index-driven query distribution)
- [ ] **Restart grounding** — `/ground` | sonnet
  - Two questions:
    1. **Fuzzy matcher robustness**: prefix mismatch ("to" token) causes total match failure (0.0 scores). Matcher exists to recover from imperfect recall — failing on one-token prefix noise is a deficiency. `removeprefix` is a band-aid.
    2. **Agent recognition A/B**: does `how to <verb>` improve agent recognition of relevant entries during index scanning vs `how <verb>`? One token per entry (~70 tokens) cost. Test by varying index format and observing agent resolve success on real tasks.
  - Dead branches: fuzzy self-matching (tautological), query distribution (contaminated by index-driven retrieval), heading alignment (trivially true)
  - Prototypes in `plans/prototypes/` have reuse value for extraction

## Reference Files

- `plans/prototypes/` — extraction scripts, reusable for corrected analysis
- `src/claudeutils/when/fuzzy.py` — production fuzzy matcher (question 1)
- `src/claudeutils/when/resolver.py` — `removeprefix("to ")` band-aid at line 196

## Next Steps

Branch work continues — restart grounding with corrected problem statement.
