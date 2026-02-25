# Diagnostic: when-resolve.py Double-"to" and Cross-Operator Matching

**Date:** 2026-02-25
**Trigger:** `/recall all` and `/design` triage recall — 6 consecutive resolution failures
**Severity:** Blocks all `/how` entry resolution and cross-operator batch recall

## Bug 1: Double "to" Prefix

**Reproduction:**
```bash
agent-core/bin/when-resolve.py "how to prevent skill steps from being skipped"
# Error: No match for 'to prevent skill steps from being skipped'
```

**Root Cause:**

`cli.py:24` splits on first space: `"how to prevent..."` → operator=`"how"`, query=`"to prevent..."`.

`resolver.py:213-214` prepends operator prefix:
```python
operator_prefix = "how to" if operator == "how" else operator
query_with_operator = f"{operator_prefix} {query}"
# Result: "how to to prevent skill steps from being skipped"
```

Double "to" — one from user input, one from operator mapping.

**Code path:**
```
cli.py:24     _parse_operator_query("how to prevent...") → ("how", "to prevent...")
resolver.py:213  operator_prefix = "how to"
resolver.py:214  query_with_operator = "how to to prevent..."  ← BUG
resolver.py:220  fuzzy.rank_matches("how to to prevent...", candidates) → no match
resolver.py:223  _handle_no_match("to prevent...", candidates, "how")
```

**Fix:** Strip leading "to " from query in `_resolve_trigger` when operator is "how":
```python
if operator == "how" and query.startswith("to "):
    query = query[3:]
```

Location: `resolver.py` between lines 212-213 (before operator_prefix construction).

## Bug 2: Cross-Operator Matching Failure

**Reproduction:**
```bash
agent-core/bin/when-resolve.py "when prevent skill steps from being skipped"
# Error: No match for 'prevent skill steps from being skipped'
# Did you mean:
#   /when prevent skill steps from being skipped   ← it KNOWS the answer!
```

**Root Cause:**

The entry is `/how prevent skill steps from being skipped` but the caller uses `"when"` prefix. In `_resolve_trigger`:

- Query built: `"when prevent skill steps from being skipped"`
- Candidate built: `"how to prevent skill steps from being skipped"` (from the /how entry)
- `fuzzy.rank_matches` scores this low — prefix `"when"` vs `"how to"` creates gap penalties and word mismatch that drops below threshold
- `_get_suggestions` (looser sequential char matcher) finds it → shows in "Did you mean" → but the strict `rank_matches` rejects it

**Why this matters:** The design skill's triage recall invokes `when-resolve.py "when <trigger>"` for all entries without knowing whether each is `/when` or `/how`. Batch recall breaks for all `/how` entries when called with `"when"` prefix.

**Fix:** Match on trigger text only, stripping operator prefix from both query and candidates:

```python
# Instead of matching "when X" against "how to Y":
# Match "X" against "Y" (bare triggers)
trigger_candidates = [e.trigger for e in entries]
matches = fuzzy.rank_matches(query, trigger_candidates, limit=1)
```

Then map the matched trigger back to its entry (already have `_load_matched_entry` pattern, needs adaptation for bare-trigger matching).

Location: `resolver.py:212-226` — replace operator-prefixed matching with trigger-only matching.

**Trade-off:** Operator prefix currently helps disambiguate entries with same trigger but different operators. Check if any such collisions exist in memory-index.md before removing prefix from matching.

## Affected Files

- `src/claudeutils/when/resolver.py` — `_resolve_trigger()` lines 194-265
- `src/claudeutils/when/cli.py` — `_parse_operator_query()` lines 14-26 (optional, fix can be in resolver)

## Test Files

- `tests/test_when_cli.py` — CLI integration tests (CliRunner)
- `tests/test_when_resolver.py` — resolver unit tests (tmp_path fixtures)

## Existing Test Coverage

- `test_trigger_fuzzy_heading_match_how_operator` — tests `/how` resolution with correct invocation (`"how", "configure script entry points"`) — passes because no "to" in query
- No test for `"how to X"` input form (Bug 1)
- No test for cross-operator matching (Bug 2)

## Recommended TDD Approach

### Cycle 1: Double-to fix
- RED: Test `resolve("how", "to prevent skill steps from being skipped", ...)` — expects resolution, currently fails
- GREEN: Strip "to " prefix in `_resolve_trigger`
- REFACTOR: Check if cli.py should also strip (defense in depth)

### Cycle 2: Cross-operator matching
- RED: Test `resolve("when", "prevent skill steps from being skipped", ...)` where entry is `/how prevent skill steps from being skipped` — expects resolution, currently fails
- GREEN: Match on bare triggers, map back to entry
- REFACTOR: Verify no trigger collisions across operators, simplify `_handle_no_match` and `_load_matched_entry`

## Collision Check

Before implementing Bug 2 fix, verify no trigger text collisions:
```bash
grep -oP '/(when|how) \K[^|]+' agents/memory-index.md | sort | uniq -d
```
If any trigger appears under both `/when` and `/how`, bare-trigger matching needs disambiguation logic.
