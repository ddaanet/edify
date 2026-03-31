# Text Matching, Scoring, and Keyword Lookup Patterns in Codebase

**Date:** 2026-02-28
**Scope:** Comprehensive survey of matching, scoring, and ranking algorithms across recall, when, and hook systems.

---

## Summary

The codebase implements four distinct text matching and scoring systems for different use cases:

1. **Keyword-based relevance scoring** (recall module) — Set intersection with normalization
2. **Fuzzy subsequence matching** (when module) — Modified fzf V2 algorithm with scoring
3. **Pattern matching guards** (UserPromptSubmit hook) — Regex-based detection with false-positive filtering
4. **Command routing** (PreToolUse hook) — Regex exact-match routing table

Each system has different performance characteristics, data structures, and use cases.

---

## Key Findings

### 1. Recall Module: Keyword-Based Relevance Scoring

**File:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/relevance.py`

**Approach:** Normalized keyword set intersection
**Scoring Formula:** `score = |intersection| / |entry_keywords|` (0.0 to 1.0 range)

**Function:** `score_relevance()`
```python
def score_relevance(
    session_id: str,
    session_keywords: set[str],
    entry: IndexEntry,
    threshold: float = 0.3,
) -> RelevanceScore:
    """Score relevance using normalized keyword overlap."""
    if not entry.keywords:
        score = 0.0
        matched = set()
    else:
        matched = session_keywords & entry.keywords
        score = len(matched) / len(entry.keywords)
    is_relevant = score >= threshold
    return RelevanceScore(...)
```

**Data Structures:**
- `IndexEntry`: Pydantic model with `keywords: set[str]` field
- `RelevanceScore`: Result model storing `score: float`, `is_relevant: bool`, `matched_keywords: set[str]`
- Input: `session_keywords` — set extracted from session text

**Performance:**
- **Time complexity:** O(n × m) where n=sessions, m=index entries, each scoring is O(1) set intersection
- **Threshold filtering:** Default 0.3 (entry must match 30% of its keywords from session)
- **Sorting:** Results sorted by score descending (highest relevance first)

**Function:** `find_relevant_entries()` — Batch scoring with filtering
```python
relevant = []
for entry in entries:
    score_result = score_relevance(session_id, session_keywords, entry, threshold)
    if score_result.is_relevant:
        relevant.append(score_result)
relevant.sort(key=lambda r: r.score, reverse=True)
return relevant
```

**Keyword Extraction:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/index_parser.py`

**Function:** `_extract_keywords()`
```python
def _extract_keywords(text: str) -> set[str]:
    """Extract keywords by tokenization and stopword removal."""
    tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())
    return {token for token in tokens if token and token not in STOPWORDS}
```

**Tokenization:**
- Split pattern: `[\s\-_.,;:()[\]{}\"'`]+` — whitespace, hyphens, underscores, punctuation
- Lowercased before stopword filtering
- 59-word stopword set (common articles, prepositions, auxiliaries)

**Stopword set includes:** a, an, the, is, are, be, have, for, from, to, at, in, on, with, and, or, not, etc.

**Use case:** Determine if an index entry (decision file reference) is relevant to a session topic.

---

### 2. When Module: Fuzzy Subsequence Matching

**File:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/when/fuzzy.py`

**Approach:** Modified fzf V2 algorithm with dynamic programming + gap penalties + boundary bonuses

**Scoring Constants:**
```python
MATCH_SCORE = 16
CONSECUTIVE_BONUS = 4
FIRST_CHAR_MULTIPLIER = 2
BOUNDARY_WHITESPACE = 10.0
BOUNDARY_DELIMITER = 9.0
BOUNDARY_CAMELCASE = 7.0
GAP_START_PENALTY = -3
GAP_EXTENSION_PENALTY = -1
WORD_OVERLAP_BONUS = 0.5
MIN_THRESHOLD_SINGLE_CHAR = 50.0
```

**Function:** `score_match(query, candidate) -> float`

**Algorithm stages:**

1. **DP Matrix Computation** `_compute_dp_matrix()`
   - Build matrix: `score[i][j]` = best score matching `query[0:i]` with `candidate[0:j]`
   - For each character match: base score + consecutive bonus + boundary bonus
   - Boundary types: whitespace (10.0), delimiter/-/_ (9.0), camelCase (7.0)
   - First character gets 2x multiplier

2. **Backtrace** `_get_match_positions()` — Find which positions in candidate matched query

3. **Gap Penalties** — Applied to all gaps between matched positions
   - Gap start: -3 points
   - Gap extension: -1 point per character

4. **Word Overlap Bonus** — Set intersection of whole words (not characters)
   - Bonus: 0.5 points per overlapping word
   - Acts as tiebreaker

5. **Threshold Gate** `_meets_minimum_threshold()`
   - Single-character queries: require word overlap OR score >= 50.0 (prevents noise)
   - Multi-character: accepted if any match found

**Example scoring flow:**
```
query="design", candidate="design decisions"
→ Exact prefix match in candidate
→ DP score: 16 + boundary bonus (10.0) + consecutive bonuses
→ Gap penalties: minimal
→ Word overlap: "design" matches → +0.5
→ Final score: high (exact match preferred)
```

**Function:** `rank_matches(query, candidates, limit=5) -> list[tuple[str, float]]`
- Scores all candidates
- Filters by score > 0
- Sorts descending by score
- Returns top N

**Data structures:**
- DP matrix: 2D list of floats, dimensions (len(query)+1) × (len(candidate)+1)
- Match positions: list of indices into candidate string
- Results: list of (candidate_string, score_float) tuples

**Use case:** Fuzzy matching of /when and /how triggers against user queries (e.g., user types "desig" → matches "design decisions").

---

### 3. When Module: Index Parsing and Trigger Routing

**File:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/when/resolver.py`

**Approach:** Multi-level prefix-based routing + fuzzy fallback

**Three resolution modes:**

1. **File routing:** `_resolve_file()` — Query starts with `..`
   - Exact filename match in decision directory
   - Returns file content
   - Error: lists available files as suggestions

2. **Section routing:** `_resolve_section()` — Query starts with `.`
   - Case-insensitive heading lookup across all decision files
   - Builds heading-to-files map once, then index lookup
   - Error: shows up to 10 available headings

3. **Trigger routing:** `_resolve_trigger()` — No prefix
   - Fuzzy match against trigger candidates using `fuzzy.rank_matches()`
   - Fuzzy engine: See Section 2 above
   - Resolution: find heading text, extract section, format with source reference

**Function:** `_get_suggestions()` — Simple sequential character matching (looser than fuzzy)
```python
def _get_suggestions(query: str, candidates: list[str], limit: int = 3) -> list[tuple[str, float]]:
    """Sequential character matching for suggestions (looser than main fuzzy)."""
    scored = []
    query_lower = query.lower()
    for candidate in candidates:
        candidate_lower = candidate.lower()
        matched = 0
        q_idx = 0
        for c in candidate_lower:
            if q_idx < len(query_lower) and c == query_lower[q_idx]:
                matched += 1
                q_idx += 1
        if matched > 0:
            scored.append((candidate, float(matched)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]
```

**Use case:** Resolve `/when` and `/how` commands to decision file content with three query styles.

---

### 4. UserPromptSubmit Hook: Pattern Guards and Continuation Parsing

**File:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/plugin/hooks/userpromptsubmit-shortcuts.py`

**Approach:** Tiered regex pattern matching with false-positive filtering

**Tier 1: Command shortcuts** — Exact string match on line
```python
COMMANDS = {
    "s": "[#status] List pending tasks...",
    "x": "[#execute] ...",
    "xc": "[execute, commit] ...",
    # ... 8 more commands
}
```
- Single-line exact match: first matching line wins
- No scoring (binary: match or no-match)

**Tier 2: Directive patterns** — Colon prefix with additive matching
```python
_DISCUSS_EXPANSION = "[DISCUSS] Evaluate critically, do not execute..."
_PENDING_EXPANSION = "[PENDING] Do NOT execute..."
# ... 3 more directives

DIRECTIVES = {
    "d": _DISCUSS_EXPANSION,
    "discuss": _DISCUSS_EXPANSION,
    "p": _PENDING_EXPANSION,
    # ... regex: r"^(\w+):\s+(.+)"
}
```
- Regex: `^(\w+):\s+(.+)` — word characters before colon
- Scans whole prompt, all matches fire (additive)
- Returns section content (directive line through next directive or EOF)

**Tier 2.5: Pattern guards** — Regex-based detection (additive with Tier 2)

Two regex patterns:

1. **Skill-editing pattern:**
```python
_EDIT_VERBS = r"(?:fix|edit|update|improve|change|modify|rewrite|refactor)"
_SKILL_NOUNS = r"(?:skill|agent|plugin|hook)"
EDIT_SKILL_PATTERN = re.compile(
    rf"(?:{_EDIT_VERBS}\b.*\b{_SKILL_NOUNS}|\b{_SKILL_NOUNS}\b.*\b{_EDIT_VERBS})",
    re.IGNORECASE,
)
```
- Triggers: edit verb + skill noun in any order
- Example matches: "fix the skill", "update hooks", "modify agent files"

2. **CCG (Claude Code Guide) platform keyword pattern:**
```python
CCG_PATTERN = re.compile(
    r"\b(?:hooks?|PreToolUse|PostToolUse|SessionStart|UserPromptSubmit"
    r"|mcp\s+server|slash\s+command|settings\.json|\.claude/|plugin\.json"
    r"|keybinding|IDE\s+integration|agent\s+sdk)\b",
    re.IGNORECASE,
)
```
- Detects Claude platform keywords
- 13 keywords: hooks, PreToolUse, PostToolUse, SessionStart, UserPromptSubmit, mcp server, slash command, settings.json, .claude/, plugin.json, keybinding, IDE integration, agent sdk

**Tier 3: Continuation parsing** — Multi-skill routing (lowest priority)

**Function:** `find_skill_references()` — Locate all `/skill` references with false-positive filtering

**Context-aware filtering** via `_should_exclude_reference()`:
1. **Precedence check:** Skill reference must be preceded by whitespace or line start
   - Excludes: quoted "/skill", file paths (plans/skill/), mid-word (foo/bar)
2. **Path check:** Exclude /skill-word/ or /skill/ patterns (directory paths)
3. **Line-prefix check:** Exclude lines starting with "note:" (meta-discussion)

**Function:** `parse_continuation()` — Two detection modes

Mode 3: Multi-line list pattern
```
/skill1 args
and
- /skill2 args
- /skill3 args
```

Mode 2: Inline prose with delimiters
- Delimiters: `, /` or `(?:\s+(?:and|then|finally)\s+/)`
- Example: `/skill1 args, /skill2 args` or `/skill1 args and then /skill2 args`

**Data structures:**
- Skill registry: dict mapping skill_name → {cooperative: bool, default-exit: list[str]}
- Continuation result: {current: {skill: str, args: str}, continuation: list[{skill, args}]}
- Cache: JSON file with paths, registry, timestamp for change detection

**Use case:** Expand workflow shortcuts in user prompts, detect editing tasks, platform questions, and multi-skill continuation chains.

---

### 5. PreToolUse Hook: Command Routing

**File:** `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/plugin/hooks/pretooluse-recipe-redirect.py`

**Approach:** Regex-based command routing with three matching functions

**Function: `_match_blocks()`** — Hard blocks (security/correctness)
```python
# python -c inline code
if re.match(r"python3?\s+-c\s", command):
    return _deny(...)

# rm index.lock (concurrent git access)
if re.search(r"rm\s.*index\.lock", command):
    return _deny(...)
```

**Function: `_match_python_uv()`** — Python invocation patterns
```python
# python3 -m <tool> → suggest bare <tool>
m = re.match(r"python3?\s+-m\s+(\S+)(.*)", command)

# python3 <script> → suggest bare <script>
m = re.match(r"python3?\s+(?!-)([\w./_-]+\.\w+)(.*)", command)

# uv run <command> → suggest bare <command>
m = re.match(r"uv\s+run\s+(.*)", command)
```

**Function: `_match_tool_wrappers()`** — Route to project wrappers
```python
if command == "ln" or command.startswith("ln "):
    # Suggest: just sync-to-parent

if command.startswith("git worktree "):
    # Suggest: claudeutils _worktree

if command.startswith("git merge ") or command == "git merge":
    # Suggest: claudeutils _worktree merge
```

**Main routing:** `_match()`
```python
def _match(command: str) -> dict | None:
    return (
        _match_blocks(command)
        or _match_python_uv(command)
        or _match_tool_wrappers(command)
    )
```

**Output format:** `permissionDecision: deny` with three message levels
- `permissionDecisionReason` — for agent and user
- `additionalContext` — agent-only detailed instruction
- `systemMessage` — user-facing summary (~60 chars)

**Data structures:**
- Command regex patterns: Compiled regex objects, no scoring (match/no-match)
- No ranking (first match in routing table wins)

**Use case:** Block low-level commands and route to wrappers that manage session state.

---

## Pattern Comparison Matrix

| System | Location | Approach | Scoring | Ranking | Data Struct | Use Case |
|--------|----------|----------|---------|---------|------------|----------|
| **Keyword Relevance** | recall/relevance.py | Set intersection | Normalized (0-1) | Score descending | set[str] | Entry relevance |
| **Fuzzy Match** | when/fuzzy.py | fzf V2 DP | Multi-stage float | Score descending | 2D matrix | Trigger matching |
| **Trigger Resolution** | when/resolver.py | 3-mode routing | Fuzzy for mode 3 | Prefix > fuzzy | dict/list | /when query |
| **Shortcuts** | UserPromptSubmit hook | Regex exact | N/A (binary) | Tier precedence | dict | Workflow expansion |
| **Pattern Guards** | UserPromptSubmit hook | Regex detection | N/A (binary) | Additive | regex | Context detection |
| **Continuation Parse** | UserPromptSubmit hook | Multi-mode regex | N/A (binary) | Mode precedence | registry dict | Multi-skill routing |
| **Command Routing** | PreToolUse hook | Regex match | N/A (binary) | Function order | compiled regex | Command blocking |

---

## Cross-File Patterns and Dependencies

### Keyword Extraction Pipeline

Flow: Raw text → `_extract_keywords()` → Tokenization → Stopword removal → `set[str]`

**Files:**
- Entry keywords: `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/index_parser.py` lines 72-87
- Relevance scoring: `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/relevance.py` lines 18-86

**Reuse:** Keyword extraction used in both old-format and new-format entry parsing.

### Fuzzy Engine Reuse

`fuzzy.rank_matches()` called by:
1. `when/resolver.py:_resolve_trigger()` — Fuzzy match trigger against candidates
2. `when/resolver.py:_find_heading()` — Fuzzy match heading text as fallback
3. `when/resolver.py:_get_suggestions()` — Looser sequential matching for error suggestions

### Entry Parsing Variants

Three entry formats supported by index_parser.py:

1. **New /when format:** `/when trigger | extra1, extra2`
2. **New /how format:** `/how trigger | extra1, extra2`
3. **Old format (deprecated):** `key — description`

Each has different keyword extraction source:
- New format: trigger + extras
- Old format: key + description

---

## Performance Considerations

### Recall Module (Keyword Relevance)

- **Set operations:** O(1) per lookup, O(n) for intersection
- **Batch scoring:** O(n × m) where n=sessions, m=entries
- **Threshold filtering:** Eliminates low-scoring entries before sorting
- **Sorting:** O(m log m) final sort of filtered results

### When Module (Fuzzy Matching)

- **DP matrix:** O(n × m) time and space where n=len(query), m=len(candidate)
- **Backtrace:** O(n) to extract match positions
- **Gap penalties:** O(positions_count) to calculate
- **Ranking:** O(k log k) where k=number of candidates
- **Single-char gate:** MIN_THRESHOLD (50.0) prevents expensive DP on every char

### UserPromptSubmit Hook (Pattern Matching)

- **Tier 1 (commands):** O(lines) scan with set lookup O(1)
- **Tier 2 (directives):** O(lines) regex scans, all matches fire
- **Pattern guards:** O(prompt_length) for each of 2 regex searches
- **Tier 3 (continuation):** Registry built once (cached), O(references) to find and parse
- **Cache validation:** Timestamps + file stat() calls (filesystem I/O)

### PreToolUse Hook (Command Routing)

- **Linear routing:** Each function tries regex match in order
- **First match wins:** Early exit on match (typical case: fast)
- **Script validation:** Path stat() call + file read first 2 bytes

---

## Tokenization and Normalization Details

### Recall Module Tokenization

**Split regex:** `[\s\-_.,;:()[\]{}\"'`]+`

**Splits on:**
- Whitespace: space, tab, newline
- Hyphens: -
- Underscores: _
- Punctuation: . , ; : ( ) [ ] { } " ' `

**Example:** "user-prompt/submit: keyword_match" → {user, prompt, submit, keyword, match}

**Stopword handling:** After tokenization, filter using 59-word set (case-insensitive)

### When Module Case Normalization

All matching is **case-insensitive:**
- Query lowercased: `query.lower()`
- Candidate lowercased: `candidate.lower()`
- Comparison happens on lowercased strings
- Original case preserved in returned results

**Example:** Query "DESIGN" matches candidate "design decisions" (case ignored).

### UserPromptSubmit Hook Normalization

- **Command matching:** Exact case-insensitive set lookup (strips and compares)
- **Directive key matching:** Lowercase-only regex capture, case-insensitive in DIRECTIVES dict
- **Regex patterns:** Case-insensitive flags (`re.IGNORECASE`)

---

## Edge Cases and Thresholds

### Keyword Relevance

- **Empty keywords:** Entry with no keywords scores 0.0 (unrelevant)
- **Default threshold:** 0.3 (entry must match 30% of its keywords)
- **Exact scoring:** 1.0 only if all entry keywords found in session

### Fuzzy Matching

- **Single-char query gate:** Requires score >= 50.0 OR word overlap > 0
  - Prevents "a" matching every candidate
  - Word overlap acts as escape hatch (e.g., query="a", candidate="analyze" matches if "a" is a word)
- **Empty query:** Returns 0.0
- **Query longer than candidate:** Returns 0.0 (impossible to match)
- **Minimum threshold:** 0.0 (any match with positive score accepted) unless single-char gate applies

### When Module Routing

- **Ambiguous heading:** Error if same heading exists in multiple files
- **Missing file:** Lists available files (up to 10) in error message
- **Missing section:** Falls back to fuzzy heading match within file

### UserPromptSubmit Hook

- **Fence detection:** Code blocks skipped (directives inside fenced blocks ignored)
- **Note: prefix exclusion:** Lines starting with "note:" are meta-discussion, not skill invocations
- **Path pattern exclusion:** /skill-word/ patterns treated as directory paths, not invocations
- **Whitespace requirement:** /skill must be preceded by whitespace (prevents mid-word matches)

### PreToolUse Hook

- **Script validation:** Checks file exists, executable (stat mode & 0o111), has shebang (#!)
- **index.lock:**  Indicates concurrent git access — suggests retrying instead of deleting

---

## Data Structures Summary

### Pydantic Models (Data Validation)

**IndexEntry** (recall/index_parser.py):
```python
class IndexEntry(BaseModel):
    key: str
    description: str
    referenced_file: str
    section: str
    keywords: set[str]
```

**RelevanceScore** (recall/relevance.py):
```python
class RelevanceScore(BaseModel):
    session_id: str
    entry_key: str
    score: float
    is_relevant: bool
    matched_keywords: set[str]
```

**WhenEntry** (when/index_parser.py):
```python
class WhenEntry(BaseModel):
    operator: str
    trigger: str
    extra_triggers: list[str]
    line_number: int
    section: str
```

### Collections

- **Sets:** Keywords (fast membership test, automatic dedup)
- **Dicts:** Skill registry (skill_name → metadata), heading_to_files (heading → files)
- **Lists:** Candidates for ranking, tool_calls sequence (order matters), match positions
- **2D list:** DP matrix for fuzzy scoring (index: [query_idx][candidate_idx])

---

## Integration Points

### Recall → Index Parser

```python
entries = parse_memory_index(index_file)  # Returns list[IndexEntry]
for entry in entries:
    score = score_relevance(session_id, session_keywords, entry)
```

Keywords extracted once at parse time, reused in scoring.

### When → Fuzzy

```python
entries = parse_index(index_file)
trigger_candidates = [e.trigger for e in entries]
matches = fuzzy.rank_matches(query, trigger_candidates, limit=1)
```

Triggers extracted to list, scored via fuzzy, top match resolved to decision file.

### UserPromptSubmit → Continuation Parsing

```python
registry = build_registry()  # Collects all skills (cached)
parsed = parse_continuation(prompt, registry)
if parsed:
    context = format_continuation_context(parsed)
```

Registry built once per session, used to find and validate skill references.

---

## Recommendations for UserPromptSubmit Topic Injection

Based on this analysis, the following patterns are relevant for implementing trigger-matching in UserPromptSubmit topic injection:

1. **Keyword-based filtering:** Use `recall/relevance.py` model for determining which memory-index entries are relevant to the user's topic
2. **Fuzzy trigger matching:** Leverage `when/fuzzy.py` to match user text against known triggers with tolerance
3. **False-positive filtering:** Follow UserPromptSubmit hook pattern (context-aware filtering in `_should_exclude_reference()`) to avoid matching in irrelevant contexts
4. **Regex guard patterns:** Use compiled regex with `re.IGNORECASE` for efficient pattern detection (low overhead)
5. **Tokenization:** For keyword extraction, reuse `/Users/david/code/claudeutils-wt/userpromptsubmit-topic/src/claudeutils/recall/index_parser.py:_extract_keywords()` to ensure consistency with recall system
6. **Caching:** Follow UserPromptSubmit hook cache pattern (hash-based path, timestamp validation) to avoid redundant computation
7. **Ranking:** Multi-stage scoring (fuzzy score primary, word overlap secondary tiebreaker) provides both precision and recall
