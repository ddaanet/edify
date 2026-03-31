# A/B Test Methodology for Index Format Effects on Agent Behavior

**Date:** 2026-03-09

**Objective:** Document existing internal infrastructure for testing whether index entry format (`how to <verb>` vs `how <verb>`) affects agent recognition of relevant entries during index scanning and resolution.

## Summary

The project has substantial existing infrastructure for session analysis and agent behavior measurement through the session scraper pipeline and multiple specialized prototype scripts for extracting how-verb queries. However, there is **no existing task replay or agent simulation framework**—testing would require running real agent tasks and comparing outcomes across variants. The fuzzy matcher has full test coverage; the session scraper can identify which `/how` queries agents use but cannot directly measure recall success without external annotation. Building A/B test infrastructure requires:

1. Index variant generation (two versions of memory-index.md)
2. Task selection and isolation
3. Outcome measurement (reconciliation success rate, agent recognition during scanning)
4. Statistical reporting

## 1. Existing Test Infrastructure for Recall

### 1.1 Unit Tests for Fuzzy Matching

**File:** `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_fuzzy.py`

The fuzzy matcher has comprehensive unit test coverage:
- **Test patterns:** Subsequence matching, boundary bonuses, consecutive match bonuses, gap penalties, word-overlap tiebreaker, minimum score thresholds
- **Coverage:** Tests verify that matching behavior is deterministic across different query/candidate pairs
- **Limitations:** Tests measure matching accuracy in isolation—they don't simulate agent recognition during index scanning or measure whether matched entries are semantically relevant

The fuzzy matcher implementation (`/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py`) uses modified fzf V2 scoring with:
- Consecutive character bonuses
- Boundary bonuses (whitespace=10, delimiter=9, camelcase=7)
- Gap penalties
- Word-overlap tiebreaker
- Minimum threshold filter (50.0 for single-char queries)

**Relevance to A/B test:** The fuzzy matcher is fixed—it applies equally to both variants. Tests confirm it works correctly, but don't measure how index format affects agent behavior.

### 1.2 Recall CLI and Resolution Tests

**Files:**
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_cli_resolve.py` — Tests `_recall resolve` command with artifact mode and argument mode
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_artifact.py` — Tests artifact parsing (Entry Keys section)
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_cli_check.py` — Tests validity checks on recall artifacts
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_cli_integration.py` — End-to-end resolution tests

**Test patterns:** These test the plumbing (file reading, parsing, fuzzy matching) but use mocked resolver (`mock_resolve.side_effect = [...]`) rather than real index data. They verify exit codes, content deduplication, null entry handling—structural correctness, not behavioral measurement.

**Limitation:** No tests measure whether agents recognize entries during task execution or whether index format changes affect discovery.

### 1.3 Recall Integration Tests

**File:** `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_integration.py`

- Marked with `@pytest.mark.e2e`
- Creates synthetic index and session JSONL, runs tool call extraction, topic extraction, relevance scoring
- **Limitation:** Purely synthetic—doesn't measure real agent behavior against real indices

### 1.4 Tool Call Extraction

**File:** `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_tool_calls.py`

Tests extraction of tool calls from session JSONL:
- Reads Skill tool invocations with `skill="how"` from session files
- Parses input parameters, tracks timestamps and session IDs
- **Relevance:** Can identify which `/how` queries agents issued in past sessions, but cannot measure whether entries were recognized or resolution succeeded

## 2. Session Scraper and Analysis Pipeline

**File:** `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/session-scraper.py` (1020 lines)

### 2.1 Six-Stage Pipeline Architecture

The session scraper provides a production-quality pipeline for analyzing Claude Code session histories:

1. **Stage 1 (Scan):** List all projects and sessions across `~/.claude/projects/`
   - Output: SessionFile list with project paths, session IDs, file types (uuid or agent)

2. **Stage 2 (Parse):** Parse single JSONL session into ordered TimelineEntry list
   - Extracts: User prompts, assistant answers, tool calls, skill invocations, interrupts
   - Deduplicates and numbers refs globally
   - **Capability:** Can identify `/how` queries issued by agents

3. **Stage 3 (Tree):** Aggregate main session + direct sub-agent files into SessionTree
   - Builds commit hash set from Bash tool results
   - Discovers agent files in `<history_dir>/<session-id>/subagents/`

4. **Stage 4 (Correlate):** Join session commits against git history
   - Maps commits to sessions, identifies unattributed commits
   - Traces merge commit parents to worktree session directories

5. **Stage 5 (Search):** Cross-project keyword search in session histories
   - Case-sensitive/insensitive matching
   - Returns SearchHit with context snippet

6. **Stage 6 (Excerpt):** Extract conversation windows around matches
   - Markdown output with before/after context
   - Useful for manual review of agent behavior around `/how` invocations

### 2.2 Capabilities for A/B Testing

**Can do:**
- Identify which sessions issued `/how` queries (Stage 2 + 5)
- Extract query text and classify into verb forms (Stage 2)
- Build session trees with commit provenance
- Locate task contexts by keyword/ref

**Cannot do:**
- Measure whether recall resolution succeeded in past tasks
- Determine which index entries agents recognized during scanning
- Replay tasks against modified indices
- A/B-compare outcomes across variants

**Session entry content limits:** Stores first 200 chars of agent answers in `TimelineEntry.content`, full text in `TimelineEntry.detail["full_text"]`. Large conversations are truncated.

## 3. Prototype Scripts for How-Verb Analysis

**Files in `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/`:**

### 3.1 How-Verb-Form Query Extraction

**`how-verb-form-extract.py`** (222 lines)
- Scans all sessions for `/how` invocations (text patterns + Skill tool calls)
- Classifies verb forms: bare (imperative), infinitive ("to X"), gerund ("-ing")
- Outputs: Count by form, examples per form, most common leading verbs
- **Limitation:** Extracts observed queries but doesn't measure resolution success

**`how-verb-form-skill-calls.py`** (110 lines)
- Extracts **only** Skill tool invocations of `/how` (cleaner signal than text patterns)
- Deduplicates by (query, session)
- Same verb form classification as above
- **Reuse value:** Cleanest extraction method; can be adapted to feed into A/B framework

**`how-verb-form-cli.py`** (122 lines)
- Extracts `/how` from CLI/Bash tool invocations (`_recall resolve`, `edify _when resolve`)
- Same verb form classification
- **Reuse value:** Identifies CLI-level resolution patterns

### 3.2 Fuzzy Matching Behavior Analysis

**`how-verb-form-scores.py`** (117 lines)

Measures fuzzy match scores across verb forms for a fixed set of 20 how-entries:
```python
HOW_ENTRIES = [
    "format runbook phase headers",
    "split test modules",
    "write init files",
    # ... 17 more
]
```

**Tests:**
- Self-match scores: bare vs "to+bare" vs gerund vs (to+bare with stripping)
- Cross-entry ranking: does verb form change top match?
- Raw "to" penalty: what if resolver didn't strip "to "?

**Key findings from prototype execution:**
- `removeprefix("to ")` band-aid at line 196 in `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py` masks the real problem
- Fuzzy matcher scores "to X" lower than bare "X", but band-aid makes them equivalent post-stripping
- **Relevance to A/B test:** Illustrates the core problem being tested—how format affects matching

**Limitation:** Tests fuzzy matcher in isolation, not agent behavior during index scanning.

### 3.3 Other Analysis Scripts

- **`score.py`** — General-purpose scoring framework (reusable for metric calculation)
- **`extract-design-metrics.py`** — Extracts metrics from design sessions
- **`agent-duration-analysis.py`** — Measures agent execution times
- **`collect-delegation-overhead.py`** — Measures overhead from task delegation

**Reuse potential:** Score calculation, metric extraction, and session parsing patterns can be adapted for A/B framework.

## 4. Infrastructure Gaps

### 4.1 No Task Replay Capability

**Current limitation:** Cannot re-execute a past task with a modified index.

**What would be needed:**
- Extract task definition (user prompts, context, goal)
- Freeze index variant
- Re-run task with agent
- Record outcomes

**Existing tools that could support this:**
- Session scraper can extract task context via Stage 6 (excerpt)
- Tool call extraction can identify which `/how` queries were issued
- But no framework exists to re-run tasks or measure success automatically

### 4.2 No Ground Truth for "Recognition Success"

**Current limitation:** Can extract that an agent issued `/how query X`, but cannot directly measure whether:
- Resolution succeeded
- Entry was relevant to the task
- Agent recognized the entry during index scanning

**What would be needed:**
- Manual annotation: tasks × recall entries → relevance labels
- Or: Indirect measurement via proxy (reconciliation success rate)
- Or: Agent trace data (which entries agent read, which it selected)

**Existing proximity:** Tool call extraction (test_recall_tool_calls.py) can identify when agents invoked specific tools, but not whether those were caused by index entry recognition.

### 4.3 Index Variant Generation

**Current state:** No infrastructure exists to generate `memory-index.md` variants.

**What would be needed:**
- Parsing script to read current index
- Transformation functions (convert `how <verb>` → `how to <verb>` or vice versa)
- Validation that variants have identical entry counts and coverage

## 5. Recommended A/B Test Framework Design

### 5.1 Architecture

```
├── A/B Framework
│   ├── index-variants.py
│   │   ├── Load memory-index.md
│   │   ├── Generate variant A (current: `how <verb>`)
│   │   ├── Generate variant B (experimental: `how to <verb>`)
│   │   └── Validate equivalence
│   │
│   ├── task-selection.py
│   │   ├── Scan session histories
│   │   ├── Identify tasks that invoked `/how`
│   │   ├── Classify by agent type, task length, recall complexity
│   │   └── Select diverse sample for testing
│   │
│   ├── task-replay.py
│   │   ├── Extract task context via session scraper
│   │   ├── Freeze index variant A or B
│   │   ├── Spawn agent with fixed seed, same prompts
│   │   ├── Record: reconciliation success, `/how` queries issued, entries resolved
│   │   └── Compare outcomes across variants
│   │
│   └── analysis.py
│       ├── Aggregate results: success rate by variant
│       ├── Statistical test: (success_rate_B - success_rate_A) significant?
│       ├── Analyze `/how` query patterns (bare vs infinitive by variant)
│       └── Report: findings, effect size, sample size
```

### 5.2 Measurement Approach

**Behavioral questions for A/B test:**

1. **Fuzzy matcher robustness:** Does one-token prefix noise (`to` token) cause total match failure?
   - **Proxy measurement:** Reconciliation success rate on variant B vs A
   - **Direct measurement:** Force `/how to` queries, measure non-zero scores

2. **Agent recognition:** Does `how to <verb>` improve agent recognition during index scanning vs `how <verb>`?
   - **Measurement:** In variant B, do agents issue more `/how` queries naturally?
   - Or: Do agents issue the same queries but with higher success rate?

**Outcome metrics:**
- **Reconciliation success:** % of `/how` queries that resolved without error
- **Query volume:** Average `/how` queries per task
- **Query success rate:** (successful / attempted) per task
- **Verb form distribution:** bare vs infinitive vs gerund per variant

## 6. Existing Code Reusable for A/B Framework

### 6.1 From Session Scraper

- **`parse_session_file()`** — Parse JSONL to TimelineEntry list (line 187)
- **`build_session_tree()`** — Aggregate with sub-agents (line 415)
- **`extract_excerpts()`** — Get task context by ref/keyword (line 733)
- **`_entry_full_text()`** — Extract searchable text from entries (line 628)

**Import path:** `from plans.prototypes.session_scraper import parse_session_file, build_session_tree`

### 6.2 From How-Verb Prototypes

- **`classify_verb_form()`** — Classify bare/infinitive/gerund (how-verb-form-extract.py, line 46)
- **Query extraction patterns** — JSONL parsing for `/how` tool calls (how-verb-form-skill-calls.py, lines 42-80)
- **Score calculation** — Fuzzy match scoring across variants (how-verb-form-scores.py, lines 41-112)

**Note:** These are prototype scripts—not in src/edify/, so reuse requires copying or refactoring into library code.

### 6.3 From Recall Infrastructure

- **`parse_index()`** — Read memory-index.md (`src/edify/when/index_parser.py`)
- **`fuzzy.rank_matches()`** — Rank candidates for a query (`src/edify/when/fuzzy.py`)
- **`score_match()`** — Single query-candidate score (`src/edify/when/fuzzy.py`, line ~50)

**Import path:** `from edify.when.index_parser import parse_index` and `from edify.when.fuzzy import rank_matches, score_match`

## 7. Testing Infrastructure Summary

| Component | File/Path | Type | A/B-Ready? | Notes |
|-----------|-----------|------|-----------|-------|
| **Fuzzy Matcher** | `tests/test_when_fuzzy.py` | Unit tests | Yes (fixed) | Deterministic; use as measurement baseline |
| **Recall Resolution** | `tests/test_recall_cli_resolve.py` | CLI tests | Partial | Tests plumbing; mocked resolver, not real behavior |
| **Session Parser** | `plans/prototypes/session-scraper.py` | Pipeline tool | Yes | Can extract task context and `/how` queries |
| **How-Verb Analysis** | `plans/prototypes/how-verb-form-*.py` | Extraction | Yes | Can classify verb forms; extract query patterns |
| **Index Parser** | `src/edify/when/index_parser.py` | Library | Yes | Read variants for comparison |
| **Task Replay** | (None exists) | — | No | Needs to be built |
| **Agent Simulation** | (None exists) | — | No | Needs to be built; depends on Claude Code API |
| **Ground Truth** | (None exists) | — | No | Needs manual annotation or proxy definition |

## 8. Implementation Priorities

**High-value, low-effort:**
1. Refactor verb form classification into `src/edify/` (reuse from prototypes)
2. Add index variant generator (parse + transform + validate)
3. Add task selector (use session scraper to find `/how`-heavy tasks)

**Medium-effort, high-value:**
4. Build task replay harness (extract context, invoke agent, record outcomes)
5. Implement reconciliation success metric

**Lower priority (blocked on infrastructure):**
6. Statistical significance testing (requires sample of 20-50 tasks minimum)
7. Agent trace analysis (would require instrumenting agent behavior)

## 9. Files Referenced

### Core Recall/When Infrastructure
- `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/fuzzy.py` — Fuzzy matcher
- `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/resolver.py` — Resolution with "to " band-aid (line 196)
- `/Users/david/code/edify-wt/ar-how-verb-form/src/edify/when/index_parser.py` — Index parsing

### Tests
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_when_fuzzy.py` — Fuzzy matcher tests
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_cli_resolve.py` — Resolution tests
- `/Users/david/code/edify-wt/ar-how-verb-form/tests/test_recall_tool_calls.py` — Tool call extraction

### Prototype Scripts (Reusable)
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/session-scraper.py` — Session analysis pipeline
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-extract.py` — Query extraction
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-skill-calls.py` — Clean skill-level extraction
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-scores.py` — Fuzzy score analysis
- `/Users/david/code/edify-wt/ar-how-verb-form/plans/prototypes/how-verb-form-cli.py` — CLI-level query extraction

### Supporting Infrastructure
- `/Users/david/code/edify-wt/ar-how-verb-form/agents/session.md` — Session context with problem statement and prototype references
- `/Users/david/code/edify-wt/ar-how-verb-form/agents/learnings.md` — Section on "When grounding recall system behavior" (definitions of meaningful measurement)
