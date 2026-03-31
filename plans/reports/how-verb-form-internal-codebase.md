# Internal Codebase Exploration: How Verb Form Grounding

Exploration of the recall system's fuzzy matching engine, entry format, and resolver behavior to ground questions about the "how to X" vs "how X" format decision.

## Question 1: Fuzzy Matcher Behavior with Prefix Noise

### Finding: One-Token Prefix Causes Total Match Failure (0.0 Score)

The fuzzy matcher uses a modified fzf V2 scoring algorithm (DP matrix with gap penalties and boundary bonuses). When a query has a "to " prefix but the stored entry doesn't, matching fails completely:

- Query: "to write init files" → Entry: "write init files" → **Score: 0.0**
- Query: "write init files" → Entry: "write init files" → **Score: 353.5**

This is a real deficiency. The matcher exists to recover from imperfect recall, but it fails entirely when the agent happens to prepend "to" (natural in English phrasing).

**Root cause:** The DP matrix in `_compute_dp_matrix()` at `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py:50-87` requires all query characters to appear in the candidate in order. When the first character of the query is "t" (from "to") and the entry starts with "w" (from "write"), the DP initialization fails and returns 0.0 at line 172 of fuzzy.py:

```python
if base_score <= 0:
    return 0.0
```

The matcher has no tolerance for prefix noise — it requires a subsequence match of ALL query characters.

### The `removeprefix("to ")` Band-Aid

**Location:** `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py:196`

```python
# Strip leading "to " — cli.py splits "how to X" → query="to X".
# Safe to match lowercase only: callers always pass lowercase (memory-index
# entries use /how, cli.py lowercases the operator check, so "to " prefix
# is always lowercase when present).
query = query.removeprefix("to ")
```

**What it does:** The resolver removes the "to " prefix from the query BEFORE fuzzy matching. This transforms "to write init files" → "write init files", which then matches the stored entry.

**Why it exists:** The CLI parser at `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/cli.py:14-19` splits incoming commands like "how to X" into operator="how" and query="to X". The resolver receives "to X" and must strip it to match entries stored as bare imperatives ("X").

**Evidence the band-aid works:**
- With "to " prefix: `score_match("to write init files", "write init files") = 0.0`
- After removeprefix: `score_match("write init files", "write init files") = 353.5`
- Test coverage: `test_how_to_prefix_not_doubled()` in `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_resolver.py:230-262` verifies the band-aid handles "how to X" invocations correctly.

**The vulnerability:** This is a **fragile band-aid, not a robust solution**. It only handles the specific case of "to " prefix. If:
- An agent queries "how write" (omitting "to"), the band-aid doesn't apply, but the fuzzy matcher still works (no prefix).
- An agent queries "how please write" (extra prefix), the band-aid only strips "to " and leaves "please write", causing match failure.
- The fuzzy matcher itself fails on ANY prefix mismatch, not just "to ".

### Fuzzy Matcher Algorithm Details

**Algorithm:** Modified fzf V2 character subsequence matching with scoring.

**Input:** Query and candidate strings (both lowercased). Candidate must contain all query characters in order (contiguous or sparse).

**Scoring components** (`/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py:5-13`):
- `MATCH_SCORE = 16` — per matched character
- `CONSECUTIVE_BONUS = 4` — per consecutive matched character (after first)
- `FIRST_CHAR_MULTIPLIER = 2` — first query char bonus
- `BOUNDARY_WHITESPACE = 10.0` — match after space
- `BOUNDARY_DELIMITER = 9.0` — match after `/`, `-`, `_`
- `BOUNDARY_CAMELCASE = 7.0` — match at camelCase boundary
- `GAP_START_PENALTY = -3` — gap between matched chars
- `GAP_EXTENSION_PENALTY = -1` — per additional gap character
- `WORD_OVERLAP_BONUS = 0.5` — per shared word between query and candidate

**Test coverage:** `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_fuzzy.py` documents the algorithm with 11 tests including:
- `test_subsequence_match_scores_positive()` — verifies 0.0 for non-matches
- `test_boundary_bonuses_applied()` — whitespace > delimiter bonus
- `test_consecutive_match_bonus()` — consecutive matches score higher
- `test_gap_penalties_reduce_score()` — longer gaps reduce score
- `test_word_overlap_tiebreaker()` — whole-word overlap breaks ties
- `test_minimum_score_threshold()` — filters spurious single-char matches
- `test_prefix_word_disambiguates()` — query prefix "when" or "how" helps disambiguation (line 115-132)

**No test for prefix noise recovery.** The test suite does not include "to " prefix mismatch scenarios, which is the reported deficiency.

## Question 2: Index Entry Format and Agent Recognition

### Current Index Format: Bare Imperatives

All 63 `/how` entries are stored in bare imperative form (no "to" prefix):

```
/how <verb> <object...>
```

**Examples from memory-index.md** (`/Users/david/code/edify-wt/ar-how-verb-form/agents/memory-index.md:26-451`):
- `/how output errors to stderr`
- `/how configure script entry points`
- `/how format token count output`
- `/how write init files`
- `/how encode file paths`
- `/how format runbook phase headers`
- `/how prevent skill steps from being skipped`
- `/how chain multiple skills together`

**Full list of 63 /how entries:**
```
/how output errors to stderr
/how configure script entry points
/how format token count output
/how write init files
/how encode file paths
/how resolve history directories
/how extract session titles
/how format session titles
/how detect trivial messages
/how order feedback extraction
/how validate session uuid files
/how parse first line metadata
/how resolve agent ids to sessions
/how extract agent ids from sessions
/how handle optional field defaults
/how filter user prompt submit hooks
/how format runbook phase headers
/how prevent skill steps from being skipped
/how format batch edits efficiently
/how pass model as cli argument
/how handle model alias resolution
/how integrate with anthropic api
/how clean markdown before formatting
/how order markdown processing steps
/how detect markdown line prefixes
/how indent nested markdown lists
/how review delegation scope template
/how dispatch corrector from inline skill
/how inject context with rule files
/how make skills discoverable
/how compose agents via skills
/how recall sub-agent memory
/how augment agent context
/how split test modules
/how apply mock patches correctly
/how test markdown cleanup
/how validate migration conformance
/how define feedback type enum
/how manage cyclomatic complexity
/how architect feedback pipeline
/how build reusable filtering module
/how detect noise in command output
/how categorize feedback by keywords
/how deduplicate feedback entries
/how merge templates safely
/how name session tasks
/how wrap a discussion session
/how integrate tdd workflow
/how document three stream planning
/how checkpoint runbook execution
/how structure phase grouped runbooks
/how verify commits defense in depth
/how design with outline first approach
/how format runbook outlines
/how chain multiple skills together
/how end workflow with handoff and commit
/how expand outlines into phases
/how use review agent fix all pattern
/how transmit recommendations inline
/how name review reports
/how write green phase descriptions
/how implement domain validation
```

### Entry Format Decision: Bare Imperatives (Not "How to X")

**Design decision location:** `/Users/david/code/edify-wt/ar-how-verb-form/agents/decisions/workflow-advanced.md` references entry format at line 357-362, but the specific decision about "how X" vs "how to X" is not documented in the decisions directory.

**Evidence from behavior:**
- Index parser expects bare triggers: `trigger = rest.strip()` at `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/index_parser.py:60`
- Resolver reconstructs heading with "to": `"How to {capitalized}"` at `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py:302-303`
- Test case explicitly verifies bare trigger + "to" heading reconstruction at `test_trigger_fuzzy_heading_match_how_operator()` (test_when_resolver.py:157-185)

**Heading reconstruction behavior:**
When resolving, the bare trigger "configure script entry points" is reconstructed as heading text "How to Configure Script Entry Points" for lookup in decision files. This decouples index storage (bare) from user-facing document headings (with "to").

### Agent Recognition During Index Scanning

There is NO test or documented analysis of how agents recognize "how" entries during index scanning vs. "how to" recognition. The prototype scripts focus on parsing agent output, not agent input behavior:

- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-extract.py` — extracts queries agents PRODUCE
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-scores.py` — measures fuzzy match scores for different query forms

Neither script tests whether agents more readily recognize and query "how to X" vs "how X" entries when scanning the index for relevant triggers.

## Question 3: Entry Count and Token Cost

### Total /how Entries: 63

**Count:** 63 `/how` entries in `/Users/david/code/edify-wt/ar-how-verb-form/agents/memory-index.md`

**Token cost estimate:**
The claim "~1 token per entry" is approximate. At average trigger length of ~6 words per entry:
- 63 entries × ~6 words/entry × ~1.3 tokens/word ≈ **490 tokens**

The "~1 token per entry" framing likely refers to the marginal cost of adding one entry (operator "/how" + minimal trigger), not the full cost of all 63 entries. A one-token-per-entry addition would be ~63 tokens, which is closer to the "~70 tokens" mentioned in session.md.

### Context: Total Index Size

- Total entries: 367 (304 /when + 63 /how)
- Index format: One line per entry (operator + trigger + optional extras)
- Full memory-index.md size: ~10KB of markdown (lines 1-451)

The index is loaded via CLAUDE.md `@`-reference, making it persistent in all agent contexts.

## Test Coverage Summary

**Prefix mismatch scenarios NOT covered:**
- Query with "to " prefix where entry is bare (handled by removeprefix band-aid)
- Query without "to " where fuzzy should tolerate prefix mismatch
- Query with extra prefixes or noise (not handled)

**Scenarios covered:**
- Exact match: `test_subsequence_match_scores_positive()` ✓
- Sparse match: handled in multiple tests ✓
- Boundary bonuses: `test_boundary_bonuses_applied()` ✓
- "how to" prefix handling: `test_how_to_prefix_not_doubled()` ✓
- Cross-operator matching: `test_cross_operator_matching()` ✓

**Gap:** No systematic test of fuzzy matcher's robustness to prefix variations (beyond the "to " special case).

## Key Findings Summary

1. **Fuzzy matcher is brittle on prefix mismatch:** Zero score (0.0) for "to write X" vs "write X" is system failure mode, not graceful degradation.

2. **The removeprefix band-aid works but is fragile:** Handles the specific "to " prefix but doesn't solve the underlying fuzzy matcher deficiency. Any other prefix variation (extra words, noise) will cause 0.0 scores.

3. **All entries stored as bare imperatives:** 63 /how entries use "write X", "format Y" format with no "to" prefix.

4. **Heading reconstruction adds "to" at display time:** Index stores bare "configure script entry points", decisions file has heading "How to Configure Script Entry Points", agent sees the full heading when resolving.

5. **No empirical data on agent recognition:** The impact of entry format ("how X" vs "how to X") on agent recognition during index scanning is untested and undocumented.

6. **Token cost: ~490 tokens for all 63 entries (~1 token marginal per new entry added).**

## File References

### Fuzzy Matcher
- Algorithm: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py:1-220`
- DP matrix: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py:50-87`
- Scoring: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py:141-196`
- Tests: `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_fuzzy.py:1-172`

### Resolver and removeprefix Band-Aid
- Resolver: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py:1-340`
- removeprefix: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py:177-236` (called at line 196)
- Heading reconstruction: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py:297-304`
- Tests: `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_resolver.py:230-262`

### CLI Entry Point
- CLI split behavior: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/cli.py:14-19`
- Operator stripping: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/cli.py:14-19`

### Index and Entries
- Index file: `/Users/david/code/edify-wt/ar-how-verb-form/agents/memory-index.md:1-451`
- /how entries: `/Users/david/code/edify-wt/ar-how-verb-form/agents/memory-index.md:26-451` (63 entries)
- Index parser: `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/index_parser.py:1-90`

### Prototype Analysis Scripts
- Query extraction: `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-extract.py:1-222` (analyzes verb forms in agent output)
- Score analysis: `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-scores.py:1-117` (measures fuzzy scores for different query forms)

## Design Notes

**For grounding discussion:**

Question 1 (Fuzzy matcher robustness) is answered: The matcher fails on prefix noise (0.0 score), the band-aid only covers "to ", and this is a system deficiency worth addressing at the matcher level (tolerance for prefix mismatch) rather than with format changes.

Question 2 (Index format A/B test) requires empirical observation: Does agent recognition improve if entries are stored as "how to X" instead of "how X"? This needs a behavioral A/B test where agents scan the index under both formats and we measure how often they recognize and invoke relevant entries, not a script-based analysis.
