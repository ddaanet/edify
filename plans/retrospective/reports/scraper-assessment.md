# Scraper Assessment: Capabilities vs Requirements

## Working Capabilities

**scan** — Lists all projects with session counts. Works across all ~136 project directories without prefix. Returns decoded paths (lossy: dashes become slashes). Full UUIDs needed for downstream commands.

**parse** — Parses single session JSONL into timeline entries. Classifies: user_prompt, skill_invocation, tool_call, tool_interactive, interrupt, agent_answer. Content truncated to 200 chars with detail expansion via `--expand tN` or `--all-detail`. Works correctly.

**tree** — Aggregates main session + sub-agent files into unified timeline. Extracts commit hashes from Bash tool outputs. Re-numbers refs globally. Works correctly.

**correlate** — Joins session commit hashes against git history. Identifies attributed/unattributed commits, merge parent provenance. Works correctly.

## Gaps Against Requirements

### Gap 1: No content search across sessions (blocks FR-2)

Current workflow requires parsing sessions one-by-one to inspect content. No command to search keyword(s) across multiple sessions/projects and return matching session IDs + entry refs.

**Needed:** `search` command — given project directories and keywords, scan sessions for keyword matches in entry content/detail, return session_id + project_dir + matching entry refs.

**Scale:** ~980 sessions across ~130 directories. Per-topic searches target 1-30 project directories (50-100 sessions each). Must parse JSONL content, not just filenames.

### Gap 2: No excerpt extraction (blocks NFR-2)

Parse produces full timeline. No way to extract a window of N entries around a specific ref (e.g., 5 entries before/after t42) as a standalone markdown excerpt.

**Needed:** `excerpt` command — given session_id + project + entry ref(s) or keyword match, extract conversation window as blog-ready markdown. Trim to relevant exchange per NFR-2.

### Gap 3: Path mapping ambiguity (usability issue, not blocker)

`scan` decodes `-Users-david-code-edify-wt-pushback` as `/Users/david/code/edify/wt/pushback` (lossy). `parse`/`tree`/`correlate` need the real filesystem path `/Users/david/code/edify-wt/pushback`. Workaround: use `encode_project_path()` with the real path. Not blocking but complicates scripting.

**Mitigation for search command:** Accept encoded dir names or real paths; use `encode_project_path()` internally.

## Assessment Conclusion

Gaps 1 and 2 need implementation (steps 1.2, 1.3). Gap 3 is a usability issue addressable within the new commands. Existing scan/parse/tree/correlate stages are solid — extensions build on `parse_session_file()` and `build_session_tree()` internals.
