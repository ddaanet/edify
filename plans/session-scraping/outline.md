# Session Scraping — Design Outline

## Approach

Standalone prototype scripts in `plans/prototypes/` that import from `src/claudeutils/` for reusable infrastructure (paths, content extraction, agent tree walking). New data models as Pydantic BaseModels. Pipeline architecture: scan → parse → aggregate → correlate.

**Constraint C-3 compliance:** No modifications to `src/claudeutils/` modules. All new code lives in prototype scripts. Production integration is a separate future task.

## Pipeline Architecture

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐
│  Scanner  │───→│  Parser  │───→│ Aggregator│───→│ Correlator│
│ (FR-1)   │    │ (FR-2)   │    │ (FR-3)    │    │ (FR-4)    │
└──────────┘    └──────────┘    └───────────┘    └───────────┘
     │               │                │                │
  SessionFile    TimelineEntry    AgentTree      CorrelatedSession
  discovery      extraction       assembly       + CommitInfo
```

### Stage 1: Scanner (FR-1)
- Enumerate `~/.claude/projects/*/` directories
- Decode encoded paths back to project directories
- Filter by optional path prefix (e.g., `~/code/`)
- List UUID session files + agent-*.jsonl files per project
- Output: list of `SessionFile(path, project_dir, file_type: uuid|agent, session_id)`

### Stage 2: Parser (FR-2)
- Stream JSONL line-by-line per session file
- Extract timeline entries with 7 types:
  - `user_prompt` — human messages (exclude tool_result user entries, system-reminder injections, command entries)
  - `skill_invocation` — `/design`, `/commit`, etc. Detected via `<command-name>` tags in user string content. Subsequent user list entry containing skill body tagged as suppressible detail
  - `tool_call` — tool name + exit status (input/output suppressed by default, expandable per-call by reference). Bash calls producing git commits carry `detail["commit_hash"]`
  - `tool_interactive` — ExitPlanMode, AskUserQuestion tool outputs (decision content)
  - `interrupt` — `[Request interrupted by user]` signals
  - `agent_answer` — assistant text blocks
  - `timestamp` — implicit on all entries (not a separate type)
- Commit hash extraction: scan Bash tool_result content, attach as `detail["commit_hash"]` on the tool_call entry (not a separate entry type)
- Tool_use/tool_result correlation via tool_use_id (state machine from scrape-validation.py)
- Output: `list[TimelineEntry]` per session file

### Stage 3: Aggregator (FR-3)
- Given a top-level session UUID, discover direct sub-agent files (agent-*.jsonl)
- Single-level only — no recursive walking (claude does not spawn sub-sub-agents)
- Tag each entry with source: `(session_id, agent_type: main|agent, agent_slug)`
- Merge + sort by timestamp across main session + direct agents
- Collect all commit hashes from tree into a set
- Output: `SessionTree(root_session_id, entries: list[TimelineEntry], commit_hashes: set[str])`

### Stage 4: Correlator (FR-4)
- Take commit hashes from SessionTree
- Run `git log` for metadata per hash (author, date, message, diff stats, files changed, branch)
- Build reverse index: commit_hash → set[session_id]
- Build forward index: session_id → set[commit_hash]
- Handle merge commits: identify constituent branches, trace to worktree session dirs
- Identify unattributed commits (in git log but no session match)
- Output: `CorrelationResult(session_commits: dict, commit_sessions: dict, unattributed: list)`

**No fuzzy matching.** FR-4 specifies joining on extracted commit hashes, not text similarity. The correlate-pending-v2.py fuzzy matching approach is for directive↔task matching (different problem).

## Data Models

```python
class EntryType(StrEnum):
    USER_PROMPT = "user_prompt"
    SKILL_INVOCATION = "skill_invocation"
    TOOL_CALL = "tool_call"
    TOOL_INTERACTIVE = "tool_interactive"
    INTERRUPT = "interrupt"
    AGENT_ANSWER = "agent_answer"

class TimelineEntry(BaseModel):
    timestamp: str  # ISO 8601
    entry_type: EntryType
    session_id: str
    agent_source: str | None  # None for main session, agent slug/type for sub-agents
    content: str  # summary text (prompt text, tool name+status, commit hash, etc.)
    detail: dict | None  # expandable detail (tool input/output, full commit info)

class SessionFile(BaseModel):
    path: Path
    project_dir: str
    file_type: Literal["uuid", "agent"]
    session_id: str

class SessionTree(BaseModel):
    root_session_id: str
    project_dir: str
    entries: list[TimelineEntry]
    commit_hashes: set[str]
    agent_ids: list[str]  # all agents in tree, for reference

class CommitInfo(BaseModel):
    hash: str
    author: str
    date: str
    message: str
    files_changed: int
    insertions: int
    deletions: int
    branch: str | None

class CorrelationResult(BaseModel):
    session_commits: dict[str, list[CommitInfo]]  # session_id → commits
    commit_sessions: dict[str, list[str]]  # commit_hash → session_ids
    unattributed: list[CommitInfo]  # commits with no session match
```

## Key Decisions

**1. User prompt detection**
- `type: "user"` entries where content is NOT a tool_result (no `tool_result` blocks in content list)
- Exclude system-reminder injections: check for `<system-reminder>` prefix in content
- Exclude `subtype: "tool_result"` entries (user entries carrying tool output back)

**2. Commit hash extraction**
- Scan Bash tool_result content for commit hash patterns
- Pattern: `[a-f0-9]{7,40}` in context of git commit output (near "create mode", "file changed", branch name)
- Avoid false positives: require git commit output context markers, not bare hex strings
- Attached as `detail["commit_hash"]` on the `tool_call` entry — not a separate entry type
- Aggregator collects via `entry.detail.get("commit_hash")` into `SessionTree.commit_hashes`

**3. Noise suppression with targeted expansion (C-1)**
- `TimelineEntry.content` = summary only (e.g., "Bash: success", "/design plans/session-scraping/requirements.md")
- `TimelineEntry.detail` = expandable content (tool input/output, skill body) — populated but not rendered by default
- Each tool call gets a stable reference (sequential index within timeline, e.g., `t42`)
- CLI: request detail by reference for specific calls, not binary all-or-nothing toggle
- Skill invocations: command name + args in content, skill body (19KB+) in detail

**4. Many-to-many data model (C-2)**
- Two dictionaries (forward + reverse index), not a bijective map
- Graph structure emerges from the index: sessions share commits, commits span sessions
- Merge commits: inspect `git log --merges` parents, map parent branches to worktree session dirs via encoded path convention

**5. Module organization (C-3)**
- Single script entry point: `plans/prototypes/session-scraper.py`
- Internal modules if >400 lines: split by stage (scanner, parser, aggregator, correlator)
- Imports from `src/claudeutils/`: `paths.encode_project_path`, `paths.get_project_history_dir`, `parsing.extract_content_text`
- Does NOT import: `extraction.py` (reimplements single-level agent discovery with TimelineEntry output)

**6. Classifying user-type entries**
Four distinct categories within `type: "user"` entries:
- **Skill/command:** string content containing `<command-name>` tags → `skill_invocation`
- **Skill body injection:** list content where first text block starts with "Base directory for this skill" → suppressible detail attached to preceding skill_invocation
- **System injection:** string content starting with `<system-reminder>` → suppressed (not a timeline entry)
- **Tool result:** list content containing `tool_result` type blocks → suppressed (tool output, not user action)
- **True prompt:** string content or list with only `text` blocks, no command/system-reminder markers → `user_prompt`

## Scope Boundaries

**IN:**
- Multi-project session enumeration
- Timeline extraction (7 entry types) with noise suppression and targeted per-call expansion
- Single-level sub-agent aggregation with source tagging
- Git correlation via extracted commit hashes
- CLI interface for running the pipeline

**OUT:**
- Production module modifications (C-3)
- Real-time/streaming (retrospective only)
- Full-text search/indexing (stateless per invocation)
- Compaction handling (not relevant — autocompact disabled)
- Fuzzy text matching for correlation (commit hashes are exact)
- Interactive TUI or web interface

## Open Questions

None — requirements are well-specified, prototypes demonstrate all key patterns, data models are straightforward Pydantic.
