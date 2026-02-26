# Session Scraping

## Requirements

### Functional Requirements

**FR-1: Multi-project session scanning**
Scan session JSONL files across all projects in `~/.claude/projects/`. Not limited to claudeutils — any project with session history is a valid source. Patterns evolved across multiple projects before crystallizing in claudeutils.

Acceptance criteria:
- Discovers all project directories in `~/.claude/projects/`
- Handles missing or empty history directories gracefully
- Scans both UUID session files and agent-*.jsonl files (agent files from orchestration sessions contain commit IDs and tool calls)
- Optional filtering by project path prefix (e.g., restrict to `~/code/` projects when needed)

**FR-2: Session timeline extraction**
Extract a chronological timeline per session with these entry types:

- **Timestamps** — on every extracted entry
- **User prompts** — human-authored messages (distinguished from tool_result messages, system injections, and command entries)
- **Skill/command invocations** — `/design`, `/commit`, `/requirements` etc. Detected via `<command-name>` XML tags in user string content. The skill body (injected as a subsequent `type=user` list entry) is suppressible content, same principle as C-1
- **Interactive tool outputs** — ExitPlanMode, AskUserQuestion, and similar tools where the output is a decision/choice, not just data
- **Interrupts** — `[Request interrupted by user]` signals
- **Tool calls with exit status** — tool name and success/failure by default. Tool input and output available via targeted per-call expansion by reference (not binary all-or-nothing toggle). Bash tool_calls that produce git commits carry the commit hash as metadata in the detail dict (`detail["commit_hash"]`) — not a separate entry type
- **Agent answers** — assistant text blocks

Acceptance criteria:
- Distinguishes human prompts from tool_result user entries, system-reminder injections, and command/skill entries
- Skill invocations show command name + args; skill body suppressed by default
- Tool calls show name + status in summary view; input/output expandable per-call by reference
- Commit hashes extracted from Bash output via pattern matching, attached as metadata on the tool_call entry
- Timeline is chronologically ordered by timestamp

**FR-3: Sub-agent aggregation**
Walk the session tree — main session plus direct sub-agents spawned via Task tool. Aggregate timeline entries and commit hashes across the tree. Tag each entry with its source (main session vs. agent slug/type).

Acceptance criteria:
- Discovers direct sub-agent files (agent-*.jsonl) for a session
- Each timeline entry identifies which agent produced it
- Commit hashes collected from all agents in the tree
- Single-level depth only (no recursive sub-sub-agents — claude does not nest agent spawning)

**FR-4: Git history correlation (post-processing)**
Correlate sessions with git history. The relationship is many-to-many: a commit may result from work spanning multiple sessions, a session tree may produce multiple commits, merge commits aggregate worktree branches with their own session histories.

Acceptance criteria:
- Given a session tree's extracted commit hashes, join against `git log` for metadata (diff stats, files changed, branch)
- Given a commit hash, trace back to which session(s) produced it
- Handles merge commits (constituent branches point to worktree session directories)
- Unattributed commits (manual, truncated output, lost sessions) identified as such

### Constraints

**C-1: Noise suppression with targeted expansion**
Session JSONL `progress` entries are ~85% of file size. Tool input/output and skill bodies are voluminous. The default view must suppress this noise — show tool name and status only, skill name and args only. Detailed content available via targeted per-call expansion by reference (given a tool call reference, show input, output, or both). Skill bodies expandable similarly. Not a binary all-or-nothing toggle — expanding all tool I/O reproduces the noise problem.

**C-2: Many-to-many session↔commit mapping**
No assumption of 1:1. Commits span sessions, sessions span commits. Orchestration sessions have sub-agents committing independently. The data model must represent this as a graph, not a bijection.

**C-3: Standalone prototype first**
Start as scripts in `plans/prototypes/` or `agent-core/bin/`. Integration into `src/claudeutils/` happens later — reuse existing infrastructure (`paths.py:encode_project_path`, `paths.py:get_project_history_dir`, agent tree walking pattern from `extraction.py`) but don't modify production modules yet.

### Out of Scope

- Real-time / streaming — retrospective only, operates on completed JSONL files
- Modify session files — read-only access to `~/.claude/projects/`
- Full-text search / indexing — stateless per invocation, no persistent database. Operates on raw JSONL each time
- Compaction handling — autocompact is disabled, handoff pattern keeps sessions short and complete
- Recursive sub-agent trees — claude does not spawn sub-sub-agents; single-level agent discovery is sufficient

### Dependencies

- `src/claudeutils/paths.py` — `encode_project_path()`, `get_project_history_dir()` for session file discovery
- Existing prototypes — `plans/prototypes/scrape-pending-directives.py` (multi-project pattern), `plans/prototypes/correlate-pending-v2.py` (git correlation pattern), `scripts/scrape-validation.py` (turn reconstruction with tool_use/tool_result pairing)

### References

- `plans/prototypes/requirements.md` — prior feature gap analysis for session extraction
- `plans/prototypes/explore-sessions.py` — format exploration prototype (1,108 sessions, entry type distribution, tool frequency)
- `scripts/scrape-validation.py` — most mature session parser (Turn/ToolCall dataclasses, tool_use/tool_result pairing)
