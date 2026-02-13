# Architecture

Module structure, path handling, data models, and general architectural decisions.

## .Module Architecture

### How to Write Init Files

**Minimal init:**

**Decision:** Keep `src/claudeutils/__init__.py` empty (1 line)

**Rationale:** Prefer explicit imports from specific modules over package-level re-exports for clarity

**Impact:** Users must import from specific modules:

```python
from claudeutils.models import FeedbackItem
from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
```

### When Placing Helper Functions

**Private helpers cohesion:**

**Decision:** `_extract_feedback_from_file()` in `parsing.py`, `_process_agent_file()` in `discovery.py`

**Rationale:** Keep helpers close to their callers for cohesion; extract only when complexity exceeds limits

**Impact:** Clear module boundaries, easier to understand data flow

### When Splitting Large Modules

**Decision:** Split large files by functional responsibility (models, paths, parsing, discovery, extraction, cli)

**Rationale:** Maintain 400-line limit while preserving logical grouping

**Impact:** 6 source modules + 6 test modules, all under limit

## .Path Handling

### How to Encode File Paths

**Path encoding:**

**Decision:** Simple `/` → `-` character replacement with special root handling (`"/"` → `"-"`)

**Rationale:** Matches Claude Code's actual encoding; simple and reversible

**Implementation:** `paths.py:encode_project_path()`

### How to Resolve History Directories

**Decision:** Use `~/.claude/projects/[ENCODED-PATH]/` as standard location

**Rationale:** Matches Claude Code storage convention

**Implementation:** `paths.py:get_project_history_dir()`

## .Content Parsing

### How to Extract Session Titles

**Decision:** Handle both string and array (text blocks) content formats

**Rationale:** Claude Code sessions use both formats depending on content type

**Implementation:** `parsing.py:extract_content_text()`

- String content: return directly
- Array content: find first `type="text"` dict and extract `text` field
- Default: return empty string

### How to Format Session Titles

**Decision:** Replace newlines with spaces, truncate to 80 chars with "..." suffix

**Rationale:** Display constraint (terminal width), readability

**Implementation:** `parsing.py:format_title()`

## .Filtering Logic

### How to Detect Trivial Messages

**Decision:** Multi-layer filter - empty, single-char, slash commands, keyword set

**Algorithm:**

1. Strip whitespace
2. Check if empty → trivial
3. Check if single character → trivial
4. Check if starts with `/` → trivial
5. Check if lowercase matches keyword set → trivial
6. Otherwise → substantive

**Rationale:** O(1) set lookup, case-insensitive exact matching only

**Keywords:**
`{"y", "n", "k", "g", "ok", "go", "yes", "no", "continue", "proceed", "sure", "okay", "resume"}`

### How to Layer Feedback Extraction

**Decision:** Type filter → error check → interruption check → trivial filter

**Rationale:** Tool denials and interruptions take priority over trivial filtering to preserve important feedback

**Implementation:** `parsing.py:extract_feedback_from_entry()`

## .Session Discovery

### How to Validate Session Uuid Files

**Decision:** Validate session files with regex `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$`

**Rationale:** Filter out agent files (agent-*.jsonl) and other non-session files

**Implementation:** `discovery.py:list_top_level_sessions()`

### When Sorting Glob Results

**Decision:** Use `sorted(history_dir.glob("*.jsonl"))` instead of raw glob

**Rationale:** Glob doesn't guarantee file order; tests require predictable results

**Impact:** Consistent ordering across runs

### How to Parse First Line Metadata

**Decision:** Parse only first JSONL line for session metadata (title, timestamp)

**Rationale:** Session metadata is in first entry; avoids reading entire file

**Performance:** O(1) per session file

## .Agent Processing

### How to Resolve Agent Ids To Sessions

**Decision:** Agent IDs become session IDs for child agents

**Example:** Main session "main-123" has agent "a1", agent "a1" has agent "a2"

- Recursion: `main-123` → `find_related_agents("main-123")` → agent `a1`
- Next level: `a1` → `find_related_agents("a1")` → agent `a2`
- Result: All feedback from main-123, a1, a2 combined

**Rationale:** Matches Claude Code's actual architecture where agents spawn child agents

**Impact:** True tree recursion without special tracking

### How to Extract Agent Ids From Sessions

**Decision:** Extract `agentId` from first line when processing agent files

**Rationale:** Agent ID is consistent throughout file; avoids repeated extraction

**Implementation:** `discovery.py:_process_agent_file()`

## .Error Handling

### When Handling Malformed Session Data

**Decision:** Skip malformed entries, log warnings, continue processing

**Examples:**

- Empty files → skip
- Malformed JSON → log warning, skip entry
- Missing sessionId field → treat as non-match
- Non-existent history dir → raise FileNotFoundError

**Rationale:** Partial data better than complete failure; user can investigate warnings

### How to Handle Optional Field Defaults

**Decision:** Use `.get(field, default)` for optional fields (sessionId, agentId, slug)

**Rationale:** Pydantic handles None values; graceful handling of missing data

**Implementation:** Throughout `parsing.py` and `discovery.py`

