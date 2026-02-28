---
name: userpromptsubmit-topic
model: sonnet
---

# UserPromptSubmit Topic Injection

**Context**: Ambient recall injection via UserPromptSubmit hook. When a user prompt contains keywords matching memory-index entries, resolve decision file sections and inject as additionalContext.
**Design**: `plans/userpromptsubmit-topic/outline.md`
**Requirements**: `plans/userpromptsubmit-topic/requirements.md`
**Status**: Ready
**Created**: 2026-02-28

---

## Weak Orchestrator Metadata

**Total Cycles**: 10

**Execution Model**: All cycles sonnet (TDD — phase-level model).

**Step Dependencies**: Sequential within phases; Phase 3 depends on Phases 1+2.

**Error Escalation**:
- Sonnet → User: Architectural ambiguity, test that can't be written with available infrastructure

**Report Locations**: `plans/userpromptsubmit-topic/reports/`

**Success Criteria**: Hook injects matched decision content as additionalContext on keyword-matching prompts. systemMessage shows matched triggers. No degradation of existing hook features.

**Prerequisites**:
- Flattened hook architecture in `userpromptsubmit-shortcuts.py` (verified: parallel accumulation, no early returns)
- `parse_memory_index()` returns `list[IndexEntry]` with `keywords: set[str]` (verified)
- `score_relevance()` accepts synthetic session_id (verified: no validation)
- Project-local `tmp/` exists and is gitignored (verified)

---

## Common Context

**Requirements (from design):**
- FR-1: Parse memory-index into keyword lookup (inverted index) — Cycle 1.1
- FR-2: Match prompt against keyword table, rank by score — Cycles 1.2, 1.3
- FR-3: Resolve matched entries to decision file content — Cycle 1.4
- FR-4: Cache inverted index with mtime invalidation — Cycles 2.1, 2.2
- FR-5: Integrate as parallel detector in hook — Cycles 3.1, 3.2, 3.3
- FR-6: Entry count cap (max 3) — Cycle 1.3
- FR-7: systemMessage with matched trigger lines + count header — Cycle 1.5

**Scope boundaries:**
- IN: Matching pipeline, caching, hook integration, unit + integration tests
- OUT: Sub-agent injection, memory-index generation, deep recall pipeline, calibration, code block filtering

**Key Constraints:**
- Single hook script architecture (C-1) — integrate into `userpromptsubmit-shortcuts.py`
- Dual-channel output (C-2) — additionalContext for agent, systemMessage for user
- 5s hook timeout shared with all features (NFR-1)
- Entry count cap bounds context budget (~150 rule budget before adherence degrades)
- Hook output must reinforce fragment instructions, never contradict (recency beats primacy)

**Recall (from artifact):**
- DO: Use `extract_keywords()` for prompt tokenization (same rules as index entries — stopword removal, lowercase, punctuation split)
- DO: Call `score_relevance()` with session_id="hook" (synthetic ID, no validation)
- DO: Use project-local `tmp/` for cache, NEVER `/tmp/` or `$TMPDIR`
- DO: Append to `context_parts`/`system_parts` accumulators (flattened parallel architecture)
- DO NOT: Use `resolve()` from when/resolver.py — it expects CLI query strings. Use `extract_section()` directly.
- DO NOT: Add early returns — all features fire in parallel, single output assembly at end
- systemMessage terminal constraint: ~60 chars after "UserPromptSubmit says: " prefix. Topic block is one entry in `system_parts` (hook joins with `" | "`).
- additionalContext is agent-only (system-reminder), systemMessage is user-only

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Dependencies:** Cycles are sequential within phases. Phase 3 depends on Phases 1 and 2. Cross-phase dependency declared per-cycle where applicable.

**Project Paths:**
- `src/claudeutils/recall/topic_matcher.py` — NEW: matching pipeline module
- `src/claudeutils/recall/index_parser.py` — READ: `parse_memory_index()`, `extract_keywords()` (promote from `_extract_keywords`)
- `src/claudeutils/recall/relevance.py` — READ: `score_relevance()`, `RelevanceScore`
- `src/claudeutils/when/resolver.py` — READ: `extract_section()` (promote from `_extract_section`)
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — MODIFY: add topic detector block
- `agents/memory-index.md` — READ: source data
- `tests/test_recall_topic_matcher.py` — NEW: unit tests
- `tests/test_ups_topic_integration.py` — NEW: hook integration tests

---

### Phase 1: Matching pipeline (type: tdd, model: sonnet)

Builds `src/claudeutils/recall/topic_matcher.py` — the complete matching pipeline from index construction through scoring, resolution, and output formatting. Tests in `tests/test_recall_topic_matcher.py`.

**API promotions folded into GREEN phases:**
- Cycle 1.1: promote `_extract_keywords` → `extract_keywords` in `index_parser.py` (update internal callers at lines 113, 138)
- Cycle 1.4: promote `_extract_section` → `extract_section` in `when/resolver.py` (update internal callers at lines 117, 225)

**Heading reconstruction:** `IndexEntry.key` stores trigger text without `/when` or `/how` prefix. Try both `## When {key}` and `## How to {key}` heading forms — `extract_section()` returns empty string on miss, so the fallback is free. If both miss, skip the entry (FR-3 silent-skip).

---

## Cycle 1.1: Build inverted index from parsed entries

**RED Phase:**

**Test:** `test_build_inverted_index_maps_keywords_to_entries`
**Assertions:**
- Given 3 `IndexEntry` objects: entry_a with keywords `{"recall", "system", "effectiveness"}`, entry_b with keywords `{"recall", "hook", "injection"}`, entry_c with keywords `{"commit", "message", "format"}`
- `build_inverted_index([entry_a, entry_b, entry_c])` returns `dict[str, list[IndexEntry]]`
- Assert `"recall"` key maps to list containing both entry_a and entry_b (length 2)
- Assert `"hook"` key maps to list containing only entry_b (length 1)
- Assert `"commit"` key maps to list containing only entry_c (length 1)
- Assert total unique keys == union of all entry keywords

**Expected failure:** `ImportError` or `AttributeError` — `build_inverted_index` does not exist yet

**Why it fails:** `topic_matcher.py` module not created

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_build_inverted_index_maps_keywords_to_entries -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/recall/topic_matcher.py` with `build_inverted_index()`.

**Behavior:**
- Iterate entries, for each keyword in `entry.keywords`, append entry to `index[keyword]`
- Return complete inverted index mapping

**Approach:** defaultdict(list), single pass over entries

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Create new module with `build_inverted_index(entries: list[IndexEntry]) -> dict[str, list[IndexEntry]]`
- File: `src/claudeutils/recall/index_parser.py`
  Action: Rename `_extract_keywords` → `extract_keywords` (public API). Update internal callers at lines 113 and 138.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_build_inverted_index_maps_keywords_to_entries -v`
**Verify no regression:** `just test`

---

## Cycle 1.2: Match prompt keywords to candidate entries

**RED Phase:**

**Test:** `test_match_prompt_returns_candidates_with_overlap`
**Assertions:**
- Given inverted index built from 3 entries (entry_a: recall/system keywords, entry_b: recall/hook keywords, entry_c: commit/message keywords)
- `get_candidates("how does the recall system work", inverted_index)` returns set of IndexEntry
- Assert result contains entry_a (keywords "recall" and "system" both match)
- Assert result contains entry_b (keyword "recall" matches)
- Assert result does NOT contain entry_c (no keyword overlap)
- Assert len(result) == 2

**Expected failure:** `AttributeError` — `get_candidates` does not exist

**Why it fails:** Function not yet implemented in topic_matcher.py

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_match_prompt_returns_candidates_with_overlap -v`

**GREEN Phase:**

**Implementation:** Add `get_candidates()` to topic_matcher.py.

**Behavior:**
- Tokenize prompt text using `extract_keywords()` (same tokenization as index entries)
- For each prompt keyword, collect entries from inverted index
- Return union of all matched entries (deduplicated)

**Approach:** Set union over index lookups

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `get_candidates(prompt_text: str, inverted_index: dict[str, list[IndexEntry]]) -> set[IndexEntry]`
  Location hint: After `build_inverted_index()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_match_prompt_returns_candidates_with_overlap -v`
**Verify no regression:** `just test`

---

## Cycle 1.3: Score, rank, and cap candidates

**RED Phase:**

**Test:** `test_score_candidates_ranks_by_relevance_and_filters` (parametrized)

**Case 1 — ranking and threshold filtering:**
**Assertions:**
- Given 3 candidates: entry_high (4/5 keywords match prompt → score ~0.8), entry_mid (2/5 keywords match → score ~0.4), entry_low (1/10 keywords match → score 0.1)
- `score_and_rank(prompt_keywords, {entry_high, entry_mid, entry_low}, threshold=0.3)` returns list of `(IndexEntry, RelevanceScore)` tuples
- Assert len(result) == 2 (entry_low excluded, below 0.3)
- Assert result[0][0] == entry_high (highest score first)
- Assert result[1][0] == entry_mid

**Case 2 — entry count cap:**
**Assertions:**
- Given 5 candidates all scoring above 0.3 threshold
- `score_and_rank(prompt_keywords, candidates, threshold=0.3, max_entries=3)` returns list
- Assert len(result) == 3
- Assert all returned scores >= score of any excluded entry (top-3 by score)

**Expected failure:** `AttributeError` — `score_and_rank` does not exist

**Why it fails:** Function not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_score_candidates_ranks_by_relevance_and_filters -v`

**GREEN Phase:**

**Implementation:** Add `score_and_rank()` to topic_matcher.py.

**Behavior:**
- Call `score_relevance(session_id="hook", session_keywords=prompt_keywords, entry=entry, threshold=threshold)` for each candidate
- Filter to entries where `is_relevant == True`
- Sort descending by score
- Slice to `max_entries` if set

**Approach:** List comprehension → filter → sort → slice

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `score_and_rank(prompt_keywords: set[str], candidates: set[IndexEntry], threshold: float = 0.3, max_entries: int | None = None) -> list[tuple[IndexEntry, RelevanceScore]]`
  Location hint: After `get_candidates()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_score_candidates_ranks_by_relevance_and_filters -v`
**Verify no regression:** `just test`

---

## Cycle 1.4: Resolve matched entries with error-path coverage

**Prerequisite:** Read `src/claudeutils/when/resolver.py` lines 307-339 — understand `_extract_section_content()` and `_extract_section()` heading boundary detection

**RED Phase:**

**Test:** `test_resolve_entries` (parametrized)

**Case 1 — happy path:**
**Assertions:**
- Given a matched entry referencing decision file created in tmp_path with heading `## When Evaluating Recall System Effectiveness` and body text "Anti-pattern: Measuring..."
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns list of `ResolvedEntry`
- Assert len(result) == 1
- Assert result[0].content contains "Evaluating Recall System Effectiveness"
- Assert result[0].content contains "Anti-pattern"
- Assert result[0].source_file matches the decision file path

**Case 2 — missing file:**
**Assertions:**
- Given entry referencing nonexistent file path
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns empty list
- Assert len(result) == 0, no exceptions raised

**Case 3 — missing section:**
**Assertions:**
- Given entry referencing real file but with key that doesn't match any heading
- `resolve_entries([(entry, score)], project_dir=tmp_path)` returns empty list
- Assert len(result) == 0, no exceptions raised

**Expected failure:** `AttributeError` — `resolve_entries` does not exist

**Why it fails:** Function not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_resolve_entries -v`

**GREEN Phase:**

**Implementation:** Add `resolve_entries()` to topic_matcher.py. Promote `_extract_section` to public API.

**Behavior:**
- For each `(entry, score)` tuple:
  - Construct file path: `project_dir / entry.referenced_file`
  - Try heading `## When {entry.key}` first, then `## How to {entry.key}` if first returns empty
  - Call `extract_section(file_path, heading)` for content extraction
  - Skip entry if both headings return empty (silent skip per FR-3)
- Return list of ResolvedEntry (dataclass with content, source_file, entry fields)

**Approach:** Define `ResolvedEntry` dataclass. Loop with try-both-headings fallback.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Rename `_extract_section` → `extract_section` (public API). Update internal callers at lines 117 and 225.
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `ResolvedEntry` dataclass and `resolve_entries(entries: list[tuple[IndexEntry, RelevanceScore]], project_dir: Path) -> list[ResolvedEntry]`
  Location hint: After `score_and_rank()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_resolve_entries -v`
**Verify no regression:** `just test`

---

## Cycle 1.5: Format dual-channel output

**RED Phase:**

**Test:** `test_format_output_produces_context_and_system_parts`
**Assertions:**
- Given 2 ResolvedEntry objects:
  - entry_1: content="## When Evaluating...\nAnti-pattern: ...", source_file="agents/decisions/operational-practices.md", entry with key="evaluating recall system effectiveness"
  - entry_2: content="## When Too Many Rules...\nLLM adherence degrades...", source_file="agents/decisions/prompt-structure-research.md", entry with key="too many rules in context"
- `format_output([entry_1, entry_2])` returns `TopicMatchResult`
- Assert `result.context` contains "When Evaluating" AND "When Too Many Rules" (both sections)
- Assert `result.context` contains "Source: agents/decisions/operational-practices.md" (attribution)
- Assert `result.system_message` starts with "topic (N lines):"
- Assert `result.system_message` contains "evaluating recall system effectiveness"
- Assert `result.system_message` contains "too many rules in context"
- Assert `format_output([])` returns `TopicMatchResult` with empty context and empty system_message

**Expected failure:** `AttributeError` — `format_output` and `TopicMatchResult` do not exist

**Why it fails:** Not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_format_output_produces_context_and_system_parts -v`

**GREEN Phase:**

**Implementation:** Add `TopicMatchResult` dataclass and `format_output()` to topic_matcher.py.

**Behavior:**
- `TopicMatchResult`: dataclass with `context: str` and `system_message: str`
- Context format: Each resolved entry as "heading\ncontent\nSource: file_path", joined with `\n\n`
- System message format: `"topic (N lines):\ntrigger1\ntrigger2"` where triggers are entry keys (with pipe extras if present from original index entry). N = total lines in context.
- Empty input → empty strings in both fields

**Approach:** String formatting with line counting

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `TopicMatchResult` dataclass and `format_output(resolved: list[ResolvedEntry]) -> TopicMatchResult`
  Location hint: After `resolve_entries()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_format_output_produces_context_and_system_parts -v`
**Verify no regression:** `just test`

---

**Light checkpoint** after Phase 1: `just dev` + verify `topic_matcher.py` exports `match_topics()` entry point (added in Phase 3 integration — at this point verify module structure is clean and all 5 functions exist).

---

### Phase 2: Index caching (type: tdd, model: sonnet)

Adds caching layer to `topic_matcher.py` so repeated prompts don't re-parse memory-index.md. Cache stored in project-local `tmp/` per D-4.

---

## Cycle 2.1: Cache build and store

**Prerequisite:** Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 393-478 — understand existing continuation registry cache pattern (hash generation, mtime validation, silent failure)

**RED Phase:**

**Test:** `test_cache_stores_index_to_project_tmp`
**Assertions:**
- Given a valid memory-index file in tmp_path, and project_dir = tmp_path (with `tmp/` subdir created)
- `get_or_build_index(index_path, project_dir)` returns `(entries, inverted_index)` tuple
- Assert `entries` is list of IndexEntry with len > 0
- Assert `inverted_index` is dict with string keys
- Assert exactly one file matching `tmp/topic-index-*.json` exists in project_dir
- Assert that file loads as valid JSON
- Assert JSON contains "entries" key (list) and "inverted_index" key (dict) and "timestamp" key (float)

**Expected failure:** `AttributeError` — `get_or_build_index` does not exist

**Why it fails:** Caching layer not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_cache_stores_index_to_project_tmp -v`

**GREEN Phase:**

**Implementation:** Add `get_or_build_index()` with cache-write logic to topic_matcher.py.

**Behavior:**
- Generate cache path: `project_dir / "tmp" / f"topic-index-{hash}.json"` where hash = SHA256 of `str(index_path) + str(project_dir)`
- On cache miss: call `parse_memory_index(index_path)` → `build_inverted_index(entries)` → serialize to JSON → write cache file
- Create `tmp/` subdir if needed (`mkdir(parents=True, exist_ok=True)`)
- Silent failure on cache write error (degrade gracefully)
- Serialization: IndexEntry needs JSON-compatible form (convert sets to sorted lists for JSON, reconstruct on load)

**Approach:** Follow continuation registry pattern. Hash via hashlib.sha256.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `get_or_build_index(index_path: Path, project_dir: Path) -> tuple[list[IndexEntry], dict[str, list[IndexEntry]]]` with cache helper functions
  Location hint: After `format_output()`, before entry point

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_cache_stores_index_to_project_tmp -v`
**Verify no regression:** `just test`

---

## Cycle 2.2: Cache hit and invalidation

**RED Phase:**

**Test:** `test_cache_behavior` (parametrized)

**Case 1 — cache hit avoids reparsing:**
**Assertions:**
- Call `get_or_build_index(index_path, project_dir)` twice with same inputs
- Monkeypatch `parse_memory_index` in topic_matcher module to track call count
- Assert `parse_memory_index` called exactly once (second call uses cache)

**Case 2 — cache invalidation on mtime change:**
**Assertions:**
- Call `get_or_build_index(index_path, project_dir)` once (builds cache)
- Modify source file: append a newline to index_path (changes mtime)
- Call `get_or_build_index(index_path, project_dir)` again
- Monkeypatch `parse_memory_index` call count across both builds
- Assert `parse_memory_index` called twice total (cache invalidated, rebuilt)

**Expected failure:** Cache hit test may pass trivially if GREEN implementation doesn't load from cache yet, or fail on monkeypatch setup

**Why it fails:** Cache read + mtime validation not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_cache_behavior -v`

**GREEN Phase:**

**Implementation:** Add cache-read and mtime-validation logic to `get_or_build_index()`.

**Behavior:**
- On cache file exists: load JSON, check if source file mtime > cache timestamp
- If source newer: invalidate (delete cache), rebuild
- If source same or older: reconstruct entries + inverted_index from cached JSON
- Reconstruct IndexEntry objects from JSON (convert sorted lists back to sets for keywords)

**Approach:** `os.path.getmtime()` for mtime comparison. JSON round-trip with set↔list conversion.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add cache-read path to `get_or_build_index()` — load JSON, validate mtime, reconstruct or invalidate
  Location hint: Beginning of `get_or_build_index()`, before cache-miss path

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_cache_behavior -v`
**Verify no regression:** `just test`

---

**Light checkpoint** after Phase 2: `just dev` + verify cache file creation in `tmp/`.

---

### Phase 3: Hook integration (type: tdd, model: sonnet)

Integrates topic matching into `agent-core/hooks/userpromptsubmit-shortcuts.py` as a parallel detector block. Tests in `tests/test_ups_topic_integration.py`.

**Phase-specific recall:** "when mapping hook output channel audiences" — additionalContext agent-only, systemMessage user-only. "when writing hook user-visible messages" — terminal constraint ~60 chars for content.

**xfail integration test:** At phase start, write xfail test for full hook → topic injection pipeline. Remove xfail at cycle 3.1 GREEN.

**Prerequisite:** Read existing hook integration test patterns in `tests/` — check for `main()` import patterns, stdin mocking, env variable setup.

---

## Cycle 3.1: Topic detector block in hook

**Prerequisite:** Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 874-958 — understand `main()` structure, accumulator pattern, output assembly. Read existing test patterns for hook invocation.

**RED Phase:**

**Test:** `test_hook_topic_injection_produces_additional_context`
**Assertions:**
- Set up fixture: memory-index file with 2 entries under a decision file heading, corresponding decision file with matching section headings and body content, all in tmp_path
- Monkeypatch environment: set `CLAUDE_PROJECT_DIR` to tmp_path (or equivalent path resolution)
- Monkeypatch stdin with JSON `{"prompt": "how does the recall system work"}`
- Invoke hook `main()` (capture stdout)
- Parse JSON output
- Assert `output["hookSpecificOutput"]["additionalContext"]` contains resolved decision content (section body text)
- Assert `output["systemMessage"]` contains "topic" and trigger key text

**Expected failure:** Output contains no topic-related content — hook doesn't call topic matcher yet

**Why it fails:** Topic detector block not added to `main()`

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_hook_topic_injection_produces_additional_context -v`

**GREEN Phase:**

**Implementation:** Add topic injection detector block and `match_topics()` entry point.

**Behavior:**
- `match_topics(prompt_text: str, index_path: Path, project_dir: Path, threshold: float = 0.3, max_entries: int = 3) -> TopicMatchResult` — top-level entry point wrapping full pipeline: `get_or_build_index` → `get_candidates` → `score_and_rank` → `resolve_entries` → `format_output`
- In hook `main()`: after pattern guards (line ~928), before continuation parsing (line ~930):
  - Determine memory-index path and project_dir from environment
  - Call `match_topics(prompt, index_path, project_dir)`
  - If result has non-empty context: append `result.context` to `context_parts`
  - If result has non-empty system_message: append `result.system_message` to `system_parts`
  - Wrap in try/except (silent failure — topic injection should never break the hook)

**Approach:** Import topic_matcher at top of hook file. Environment-based path resolution.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `match_topics()` top-level entry point
  Location hint: End of module, before `if __name__`
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Add import of `match_topics` from `claudeutils.recall.topic_matcher`. Add detector block between pattern guards and continuation parsing sections.
  Location hint: After line 928 (CCG_PATTERN block), before line 930 (Tier 3 continuation)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_hook_topic_injection_produces_additional_context -v`
**Verify no regression:** `just test`

---

## Cycle 3.2: Additive with existing features

**RED Phase:**

**Test:** `test_topic_injection_additive_with_commands`
**Assertions:**
- Same fixture setup as 3.1 (memory-index + decision files in tmp_path)
- Monkeypatch stdin with JSON `{"prompt": "s\nhow does recall work"}` (command "s" on first line + topic keywords on second)
- Invoke hook `main()` (capture stdout)
- Parse JSON output
- Assert `output["hookSpecificOutput"]["additionalContext"]` contains BOTH command expansion text (from "s" shortcut) AND topic decision content
- Assert `output["systemMessage"]` contains command expansion AND topic trigger info (both features visible)

**Expected failure:** Test should pass if parallel architecture works correctly. If it fails, accumulation logic has a bug.

**Why it fails:** If it fails — interference between command expansion and topic injection in accumulator logic

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_additive_with_commands -v`

**GREEN Phase:**

**Implementation:** No new code expected — the parallel accumulation architecture handles additive behavior. Both command expansion and topic injection append to `context_parts`/`system_parts` independently.

**Behavior:**
- If test passes immediately: confirms parallel architecture works. Mark cycle complete.
- If test fails: debug accumulation logic — check for early returns, overwriting, or conditional exclusions between features.

**Changes:**
- None expected. Debug-only if test fails.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_additive_with_commands -v`
**Verify no regression:** `just test`

---

## Cycle 3.3: No-match passthrough

**RED Phase:**

**Test:** `test_topic_injection_silent_on_no_match`
**Assertions:**
- Same fixture setup as 3.1 (memory-index + decision files in tmp_path)
- Monkeypatch stdin with JSON `{"prompt": "hello world"}` (no matching keywords for any index entry)
- Invoke hook `main()` (capture stdout)
- Assert either: (a) no output at all (complete pass-through, exit 0), or (b) if other features match, output contains no topic-related content in additionalContext or systemMessage
- Specifically: if output exists, assert "topic" not in `output.get("systemMessage", "")`

**Expected failure:** Test should pass if `match_topics()` correctly returns empty result on no matches

**Why it fails:** If it fails — `match_topics()` injects content even with no keyword overlap, or raises an exception

**Verify RED:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_silent_on_no_match -v`

**GREEN Phase:**

**Implementation:** Ensure `match_topics()` returns empty `TopicMatchResult` when no candidates score above threshold. Hook checks for non-empty before appending.

**Behavior:**
- `format_output([])` returns `TopicMatchResult(context="", system_message="")`
- Hook: `if result.context:` guard before appending to `context_parts`
- Hook: `if result.system_message:` guard before appending to `system_parts`

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Verify `match_topics()` returns empty result on no matches (may already work from format_output empty-input handling)
- File: `agent-core/hooks/userpromptsubmit-shortcuts.py`
  Action: Verify guard conditions on result before appending (may already be in place from 3.1)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_ups_topic_integration.py::test_topic_injection_silent_on_no_match -v`
**Verify no regression:** `just test`

---

**Full checkpoint** after Phase 3: `just dev` + review accumulated changes + verify dual-channel output in integration tests.
