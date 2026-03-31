# Problem: Ground How-Class Verb Form

## Context

The memory-format-grounding spec (S-C) prescribes bare imperative for how-class triggers:

```
/how [verb] [object]    — "format" not "to format"
```

The resolver (`resolver.py:196`) strips "to " prefix: `query.removeprefix("to ")`. So both query forms resolve identically. The index stores bare imperative; agents can query either way.

**Unvalidated assumption:** That bare imperative is the right *stored* form. The grounding report asserts this convention but doesn't measure whether agents naturally query with "how format X" or "how to format X", and whether the fuzzy matching scores differ between conventions.

## What Needs Grounding

1. **Agent query patterns** — How do agents actually invoke `/how`? Do they use bare imperative ("how format X"), infinitive ("how to format X"), or other forms? Extract from real session data via `session-scraper.py`.

2. **Fuzzy match score impact** — Given the 366-entry index with bare imperative triggers, compare `score_match("format runbook", "format runbook phase headers")` vs `score_match("to format runbook", "format runbook phase headers")`. The `removeprefix("to ")` normalizes before matching, but does the stored form matter for score quality?

3. **Heading alignment** — Decision file headings use "How to X" form (`_build_heading` adds "How to"). Index entries use bare imperative. The `_find_heading` does fuzzy fallback. Is there measurable friction in this translation?

## Tools

- `src/edify/when/fuzzy.py` — `score_match()`, `rank_matches()`
- `plans/prototypes/session-scraper.py` — `search` and `excerpt` commands for session data
- `agents/memory-index.md` — 366 entries, ~70 `/how` entries
- `src/edify/when/resolver.py` — resolution chain with `removeprefix("to ")`

## Success Criteria

- Empirical data on agent query verb form distribution (bare imperative vs infinitive vs other)
- Fuzzy match score comparison across verb forms for representative how-entries
- Recommendation: confirm bare imperative convention, switch to infinitive, or add normalization
