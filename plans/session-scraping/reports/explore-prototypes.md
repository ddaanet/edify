# Exploration: Session Scraping Prototypes and Codebase Analysis

**Date:** 2026-02-25
**Scope:** Session format analysis, prototype code, data models, and reusable patterns

---

## Summary

Session scraping infrastructure exists in two forms: production parsing modules (`src/claudeutils/`) and proof-of-concept prototypes (`plans/prototypes/`, `scripts/scrape-validation.py`). The production code extracts feedback types (tool denials, interruptions, messages) and recursively walks agent trees. The prototypes demonstrate multi-project scanning, directive extraction (p:, d:), and git-session correlation. Key data structures use Pydantic models (FeedbackItem, ToolCall, SessionInfo) and handle JSONL session files with consistent error recovery patterns. Edge cases include malformed JSON, missing fields, content type variation (string vs. list), and agent file discovery.

---

## File Analysis

### 1. `/Users/david/code/claudeutils-wt/session-scraping-prototype/plans/prototypes/explore-sessions.py`

**Purpose:** Format exploration prototype — scans all ~/code/ projects to document session JSONL structure.

**Key Data Structures:**
- Session files stored in `~/.claude/projects/[ENCODED-PATH]/[UUID].jsonl`
- Encoded path format: `-Users-david-code` prefix, then project path with `/` → `-`
- Each line is a JSON object with: `type`, `subtype`, `message` (content), `timestamp`

**Parsing Pattern:**
```python
for line in session_file.read_text().splitlines():
    if not line.strip(): continue
    entry = json.loads(line)  # with decode error skip
    type_ = entry.get("type")
    subtype = entry.get("subtype")
```

**Content Extraction:**
- `message.content` can be string or list of dicts
- List items have `type` ("text", "tool_use", "tool_result")
- Text blocks: `block.get("text", "")`

**Entry Types Found:**
- `type: "user"` — user messages
- `type: "assistant"` — agent responses
- `type: "queue-operation"` — internal queue events
- Subtypes: not documented in this script but referenced

**Tool Usage Analysis:**
- Assistant content includes `tool_use` blocks with `name`, `input`, `id`
- Top tools: Read, Grep, Glob, Write, Bash, Edit, etc.

**Interrupt Detection:**
- Looks for `[Request interrupted by user]` pattern
- `queue-operation` entries may indicate interrupts

**Limitations:**
- Sample-based analysis (5 largest sessions)
- No handling of tool results (outcome tracking)
- Subtype field mentioned but not analyzed

---

### 2. `/Users/david/code/claudeutils-wt/session-scraping-prototype/scripts/scrape-validation.py`

**Purpose:** Extract pushback validation scenarios from sessions. Most complex prototype — demonstrates full session parsing with tool call correlation.

**Key Data Structures:**

```python
@dataclass
class ToolCall:
    name: str           # e.g. "Read", "Bash"
    tool_input: dict    # tool-specific args
    output: str         # tool result
    tool_use_id: str    # for correlation

@dataclass
class Turn:
    user_text: str
    assistant_text: str
    tool_calls: list[ToolCall]
```

**Parsing Strategy:**
- Streaming line-by-line JSON parsing
- Maintains state machine: track pending tool calls, match results to calls
- `Turn` = user message → assistant response (with tool calls) → tool results → next user

**Content Extraction Functions:**
```python
_extract_text(content: str | list[dict]) -> str
    # Handles both string and list formats

_parse_tool_results(content: list[dict]) -> dict[id -> text]
    # Finds tool_result blocks, extracts by tool_use_id

_process_assistant_content(content: list)
    # Extracts tool_use blocks, accumulates pending tools

_match_tool_results(msg_content, pending, completed) -> bool
    # Matches results to pending calls
```

**State Machine Pattern:**
1. User message: extract text, finalize previous turn, start new turn
2. User with tool_results: match results to pending calls (no new turn)
3. Assistant message: extract text, collect tool_use blocks into pending

**Scenario Matching:**
- Defines fingerprints (list of strings to find in order)
- `find_scenario_in_session()` scans turns for ordered fingerprints
- Returns matched turns or None

**Error Handling:**
- JSON decode failures tracked, reported at end
- Tool result limits: truncates to 1000 chars
- Missing tool_use_id or incomplete blocks logged as warnings

**Output Generation:**
- Markdown report rendering
- Tool calls formatted with input fields, output truncation
- Turn rendering with blockquoted assistant text

**Limitations:**
- Fingerprint matching (basic string search, not semantic)
- Tool result truncation may lose context
- Assumes tool_use_id present in results (not guaranteed)

---

### 3. `/Users/david/code/claudeutils-wt/session-scraping-prototype/plans/prototypes/scrape-pending-directives.py`

**Purpose:** Extract `p:/pending:` directives from sessions across multiple projects.

**Multi-Project Scanning:**
```python
PROJECT_DIRS = [
    Path.home() / "code" / "claudeutils",
    wt_container / "claudeutils-wt" / "*",     # worktree siblings
    Path.home() / "code" / "claudeutils-*",    # legacy convention
]

def get_history_dir(project_dir: Path) -> Path:
    return Path.home() / ".claude" / "projects" / encode_project_path(str(project_dir))
```

**Directive Parsing:**
```python
PENDING_PATTERN = re.compile(r'^\s*(?:p|pending)\s*:\s*(.+)', re.IGNORECASE)
```
- Matches `p: <task description>` at line start
- Captures everything after colon as task description

**Task Name Extraction (from assistant response):**
```python
TASK_NAME_PATTERN = re.compile(r'\*\*(.+?)\*\*')      # bold text
TASK_LINE_PATTERN = re.compile(r'(?:task\s*name|name)\s*:\s*\*?\*?(.+?)\*?\*?\s*$')
```
- Tries bold text first (`**Task Name**`)
- Falls back to "task name:" or "name:" patterns
- Handles optional bold formatting around the name

**Turn Extraction Logic:**
- Scans for `type: "user"` entries
- Checks content (handles list and string formats)
- Finds next `type: "assistant"` within 5 entries
- Extracts response text (handles content arrays)

**Output Extraction:**
```python
scan_session(session_file: Path) -> list[dict]:
    # Returns per-directive entries:
    {
        "timestamp": entry.get("timestamp"),
        "user_text": truncated p: directive,
        "task_name": extracted task name,
        "session_file": UUID.jsonl,
        "response_preview": first 200 chars if no task_name,
    }
```

**Limitations:**
- Short window (next 5 entries) may miss task name if assistant talks first
- Task name extraction heuristics may fail on varied formats
- No validation that extracted name matches directive intent

---

### 4. `/Users/david/code/claudeutils-wt/session-scraping-prototype/plans/prototypes/correlate-pending-v2.py`

**Purpose:** Link `p:` directives to git task insertions via fuzzy text matching.

**Multi-Project Scanning:**
Same convention as scrape-pending-directives.py

**Directive Scraping:**
Reuses scrape-pending-directives pattern (inlined)

**Git History Analysis:**
```python
def get_all_insertions() -> list[dict]:
    git log --all --format=%H %aI --no-merges --follow -- agents/session.md
    # For each commit pair (curr, prev):
    #   Extract Pending Tasks section from both
    #   Find NEW tasks (in curr but not prev)
    #   Record insertion position (prepend/append/near-top/middle/near-bottom)

    # Filters out "Focused session" commits
    # Extracts task by index position and total count
```

**Insertion Position Heuristics:**
```python
idx = new_task_index
total = len(all_tasks)
if idx == 0: pos = 'prepend'
elif idx == total - 1: pos = 'append'
else:
    frac = idx / (total - 1)
    if frac <= 0.25: pos = 'near-top'
    elif frac >= 0.75: pos = 'near-bottom'
    else: pos = 'middle'
```

**Matching Algorithm:**
```python
def word_overlap(text1, text2) -> float:
    w1 = set(words_3plus_chars(text1.lower()))
    w2 = set(words_3plus_chars(text2.lower()))
    return len(w1 & w2) / len(w1 | w2)  # Jaccard similarity

def keyword_match(directive, task) -> float:
    # Extract words, skip common verbs/prepositions
    # Return: len(intersection) / min(set sizes)
```

**Scoring:**
- Compares directive text against candidates from same day ± 3 days
- Takes max(word_overlap, keyword_match) per candidate
- Threshold: score >= 0.15 to match
- Tracks batch_size per task insertion

**Edge Cases:**
- Missing timestamps: moved to "unmatched" list
- ValueError on date parsing: caught, moved to unmatched
- No candidates in date window: unmatched

**Limitations:**
- Fixed 4-day window (may miss delayed insertions)
- Heuristic threshold (0.15) not validated
- Jaccard vs keyword — takes max (may ignore legitimate weaker signal)
- Assumes one p: directive per task (batch inserts get distributed)

---

### 5. `/Users/david/code/claudeutils-wt/session-scraping-prototype/src/claudeutils/paths.py`

**Purpose:** Path encoding utilities — map absolute paths to Claude history directory names.

**Key Functions:**

```python
def encode_project_path(project_dir: str) -> str:
    """Convert /Users/david/code/foo to -Users-david-code-foo"""
    if project_dir == "/":
        return "-"
    return project_dir.rstrip("/").replace("/", "-")

def get_project_history_dir(project_dir: str) -> Path:
    """Return ~/.claude/projects/[encoded-path]/"""
    return Path.home() / ".claude" / "projects" / encode_project_path(project_dir)
```

**Encoding Logic:**
- Root `/` → `-`
- All others: leading and trailing `-` from `/` replacement (e.g., `/a/b/` → `-a-b`)
- Absolute path requirement (validates, raises ValueError if relative)

**Reuse Points:**
- All prototypes and production code use this (or inline equivalent)
- Natural integration point for multi-project scanning
- Session IDs: UUID format, directly concatenated (no encoding needed)

---

### 6. `/Users/david/code/claudeutils-wt/session-scraping-prototype/src/claudeutils/extraction.py`

**Purpose:** Recursive feedback extraction with agent tree walking.

**Recursive Tree Pattern:**

```python
def extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]:
    history_dir = get_project_history_dir(project_dir)
    feedback = []

    # Extract from main session
    session_file = history_dir / f"{session_id}.jsonl"
    if session_file.exists():
        feedback.extend(_extract_feedback_from_file(session_file))

    # Find and recursively process sub-agents
    agent_files = find_related_agent_files(session_id, project_dir)
    for agent_file in agent_files:
        agent_feedback, agent_id = _process_agent_file(agent_file)
        feedback.extend(agent_feedback)

        # RECURSION: Process agents spawned by this agent
        if agent_id:
            feedback.extend(extract_feedback_recursively(agent_id, project_dir))

    return sorted(feedback, key=lambda x: x.timestamp)
```

**Sub-Agent Discovery:**
- Defined elsewhere (`find_related_agent_files()`)
- Returns list of `agent-*.jsonl` files by session ID
- Used to build full tree

**Output:**
- Flat list of FeedbackItem objects
- Sorted by timestamp (preserves tree structure in time)
- Aggregates across all depth levels

**Limitations:**
- No cycle detection (assumes acyclic tree)
- No depth tracking (could be added for analytics)
- All feedback mixed (no origin tracking beyond agent_id in FeedbackItem)

---

### 7. `/Users/david/code/claudeutils-wt/session-scraping-prototype/plans/prototypes/requirements.md`

**Purpose:** Prior feature gap analysis document — frames integration strategy.

**Feature Matrix:**

| Feature | Current Pipeline | Prototypes | Evidence |
|---------|------------------|-----------|----------|
| Multi-project scanning | Single project | ✓ scrape-pending-directives.py | All worktree conventions |
| Directive extraction (p:, d:) | Message types only | ✓ scrape-pending-directives.py | Regex-based p: matching |
| Git correlation | None | ✓ correlate-pending-v2.py | Fuzzy matching, position heuristics |
| Session-commit linkage | None | ✓ Embeds in correlate | git log -S, commit dates |

**Integration Points:**
- `discovery.py` — add `list_sessions_multiproject()`
- `parsing.py` — add directive type detection
- `paths.py` — already handles multi-project encoding
- New module: git correlation (subprocess git operations)

**Reuse Opportunities:**
- `encode_project_path()` already exists
- Turn/ToolCall dataclasses (scrape-validation.py) → production models
- State machine pattern (turn parsing) → extraction.py enhancement

---

## Cross-Cutting Patterns

### Session File Format

**Location:** `~/.claude/projects/[ENCODED-PATH]/[UUID].jsonl`

**Entry Structure:**
```json
{
  "type": "user|assistant|queue-operation",
  "timestamp": "2026-02-25T12:34:56Z",
  "sessionId": "uuid-string",
  "agentId": "uuid-string (if sub-agent)",
  "slug": "slug-string (if worktree)",
  "message": {
    "content": "string | [ {type, text/tool_use_id/input/...} ]"
  },
  "toolUseResult": { "agentId": "...", ...} (if sub-agent result)
}
```

### Content Type Handling

All parsing code must handle dual format:

**String Content:**
```python
if isinstance(content, str):
    return content
```

**List Content:**
```python
if isinstance(content, list):
    texts = [item.get("text", "") for item in content if item.get("type") == "text"]
    return " ".join(texts)
```

### Graceful Degradation

**JSON Decode Failures:**
- Skip line, continue
- Count and report at end (optional)
- No exception propagation

**Missing Fields:**
- `.get()` with defaults
- Check `isinstance()` before accessing nested fields
- Return None or empty collection, not error

**Malformed Entries:**
- Logger warnings, not exceptions
- Validation: check `isinstance()` before each access

### Data Models (Pydantic)

**FeedbackItem:**
```python
timestamp: str              # ISO 8601
session_id: str             # UUID
feedback_type: FeedbackType # enum: TOOL_DENIAL, INTERRUPTION, MESSAGE
content: str                # user input or error message
agent_id: str | None        # sub-agent reference
slug: str | None            # worktree slug
tool_use_id: str | None     # tool denial linkage
```

**ToolCall:**
```python
tool_name: str              # "Read", "Bash", etc.
tool_id: str                # tool_use id from entry
input: dict                 # tool-specific args
timestamp: str              # ISO 8601
session_id: str             # UUID
```

**SessionInfo:**
```python
session_id: str             # UUID
title: str                  # extracted from first message
timestamp: str              # ISO 8601
```

### Regex Patterns (Common)

**UUID Session File:**
```python
r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
```

**Directive Matching:**
```python
r'^\s*(?:p|pending)\s*:\s*(.+)'          # p: directive
r'^\s*(?:d|discuss)\s*:\s*(.+)'          # d: directive (future)
```

**Task Line Extraction:**
```python
TASK_PATTERN = re.compile(r'^- \[[ x>]\] \*\*(.+?)\*\*')  # Session.md format
BOLD_TEXT = re.compile(r'\*\*(.+?)\*\*')                  # Generic bold
```

### Error Recovery Patterns

**File Read:**
```python
try:
    with path.open() as f:
        lines = f.read().strip().split('\n')
except OSError:
    return []  # Empty result, not error
```

**JSON Parse:**
```python
try:
    entry = json.loads(line)
except json.JSONDecodeError:
    # Log and continue, or count and report
    continue
```

**Nested Access:**
```python
content = entry.get("message", {}).get("content", "")
if isinstance(content, list):
    # proceed
```

### State Tracking Patterns

**Turn Assembly (scrape-validation.py):**
- `pending_tools: dict[tool_use_id -> ToolCall]` — incomplete calls
- `turn_tools: list[ToolCall]` — completed calls for current turn
- `current_user: str | None` — signals turn boundary
- `assistant_parts: list[str]` — accumulates text blocks

**Session Scanning:**
- `entries: list[dict]` — full JSONL load or streaming
- Most code streams (iterate, don't buffer all)

**Project Enumeration:**
```python
for d in PROJECT_DIRS:
    history_dir = get_project_history_dir(d)
    if not history_dir.exists(): continue
    for session_file in history_dir.glob("*.jsonl"):
        if not UUID_PATTERN.match(session_file.name): continue
        # process
```

---

## Edge Cases and Limitations

### Malformed Content

**Issue:** Content field can be incomplete or corrupted
```json
{"message": {"content": []}}        // empty list
{"message": {"content": ""}}        // empty string
{"message": {}}                     // missing content
{"message": {"content": null}}      // null content
```

**Current Handling:**
- Empty/None: return empty string or skip
- Missing: `.get()` with default
- Type check before iteration (isinstance)

**Gap:** No validation of content structure (e.g., missing "type" field in list items)

### Tool Result Linkage

**Issue:** tool_use_id in tool_result must match pending tool_use

**Current Handling (scrape-validation.py):**
- State machine maintains `pending_tools` dict keyed by tool_use_id
- When tool_result found, lookup by id and move to completed

**Gap:**
- No error if tool_result id not in pending (silent drop)
- Assumes tool_use_id always present
- Tool results can arrive out of order if JSON entries reordered

### Content Type Variations

**Issue:** `content` field has multiple formats
```python
content: str                        // agent message text
content: list[dict]                 // structured (tool_use, tool_result, text)
```

**Current Handling:**
- Check `isinstance(content, str)` first
- If list, iterate and match by type field
- Extraction helpers handle both

**Gap:**
- Some code assumes list format without checking
- Tool result matching only works in list format
- No union type enforcement

### Missing Agent ID in Results

**Issue:** Sub-agent spawned but result doesn't include agentId
```json
{
  "toolUseResult": {}        // missing agentId
}
```

**Current Handling (discovery.py):**
```python
if isinstance(tool_result, dict) and "agentId" in tool_result:
    agent_id = tool_result["agentId"]
```

**Gap:** Silent drop if missing agentId — no warning logged

### Circular Agent References

**Issue:** Agent A spawns B, B spawns A (creates cycle)

**Current Handling (extraction.py):**
- No cycle detection
- Would recurse indefinitely

**Gap:** Requires external safeguard (max depth, visited set)

### Date Parsing in Correlation

**Issue:** Timestamp format varies or missing
```python
"timestamp": "2026-02-25T12:34:56Z"       // ISO 8601
"timestamp": "2026-02-25"                 // date only
"timestamp": ""                           // empty
```

**Current Handling (correlate-pending-v2.py):**
```python
dt = datetime.strptime(d["date"], "%Y-%m-%d")
# catches ValueError, moves to unmatched
```

**Gap:** Only parses YYYY-MM-DD format (extracted from ISO string by slice [:10])

---

## Key Design Decisions (Prototypes)

**1. Streaming JSON Parsing**
- All code line-by-line, not bulk load
- Handles large files (1000+ entries)
- Errors don't block further parsing

**2. Fuzzy Matching for Correlation**
- Word overlap + keyword match (max of two)
- Threshold 0.15 empirically chosen (not validated)
- Date window ±3 days (also heuristic)
- Acknowledges uncertainty vs. perfect matching

**3. Regex-Based Extraction**
- Simple patterns (p:, d:, task name patterns)
- No semantic understanding
- Fast, no model dependency

**4. Recursive Tree Walking**
- Depth-first via recursion
- Flat output (loses tree structure but gains sort by timestamp)
- Agent ID chain preserved in FeedbackItem.agent_id

**5. Position-Based Heuristics**
- Task insertion position (prepend/append/near-top/etc.)
- Categorical not continuous (easier to reason about)
- Binning at 25% and 75% thresholds

---

## Reusable Code Inventory

### Production Code (src/claudeutils/)

**Already Available:**
- `paths.py:encode_project_path()` — path encoding (used by all prototypes)
- `paths.py:get_project_history_dir()` — history directory lookup
- `models.py:FeedbackItem` — feedback data model
- `models.py:FeedbackType` — feedback type enum
- `parsing.py:extract_content_text()` — dual-format content handling
- `parsing.py:extract_feedback_from_entry()` — single-entry feedback extraction
- `discovery.py:list_top_level_sessions()` — session listing for one project
- `discovery.py:find_sub_agent_ids()` — agent tree discovery from toolUseResult
- `discovery.py:find_related_agent_files()` — agent file lookup by session ID
- `extraction.py:extract_feedback_recursively()` — full tree extraction

**Gaps (from prototypes):**
- Multi-project session listing (discovery.py needs enhancement)
- Directive type detection (parsing.py needs new function)
- Turn-based parsing with tool correlation (new, or extract from scrape-validation.py)
- Git history correlation (new module)

### Prototype Code (plans/prototypes/, scripts/)

**Can Be Promoted:**
- `scrape-validation.py:ToolCall, Turn` — dataclasses, reusable models
- `scrape-validation.py:extract_turns()` — state machine pattern
- `scrape-pending-directives.py:PENDING_PATTERN` — regex
- `correlate-pending-v2.py:word_overlap(), keyword_match()` — matching functions
- `explore-sessions.py:block_types, interactive_tools` — analysis patterns

**Should Remain Prototypes:**
- Fingerprint-based scenario matching (S1-S4 validation)
- Fuzzy text correlation (not production-ready, threshold unvalidated)
- Ad-hoc analysis scripts (one-time, specific purpose)

---

## Recommendations for Design Phase

**Data Flow:**
1. Multi-project session enumeration (scanner)
2. Per-session parsing (entry-by-entry extraction)
3. Directive classification (p:, d:, etc. types)
4. Tool call correlation (optional, for detailed analysis)
5. Git correlation (optional, for traceability)

**Confidence Levels:**
- Session format: HIGH (explored across 1,108 sessions)
- Feedback extraction: HIGH (production code works)
- Agent tree walking: HIGH (production code works)
- Directive extraction: MEDIUM (regex-based, format variations possible)
- Git correlation: LOW (prototypes demonstrate feasibility, thresholds not validated)

**Integration Strategy:**
- Extend `discovery.py` for multi-project and directive support
- Promote ToolCall/Turn models if tool correlation needed
- New git module if correlation required (keep separate from parsing)
- Validate fuzzy matching thresholds on labeled dataset before production

