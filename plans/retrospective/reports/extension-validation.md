# Extension Validation: Search + Excerpt

## Search Command

**Test:** `search --project "/Users/david/code/edify-wt/pushback" --keyword "pushback" --keyword "sycophancy" --keyword "agreement momentum"`

**Result:** 780 entries across 24 sessions. All three keywords matched. Sessions span Feb 13-15, 2026. Output includes session_id (truncated), timestamp, matched keywords, hit count, and entry refs.

**Path handling:** Accepts real filesystem paths. Search function internally resolves to encoded directory names via `encode_project_path()`.

## Excerpt Command

**Test:** `excerpt <full-uuid> --project <path> --keyword "sycophancy" --window 3`

**Result:** 22 matching entries. Markdown output with:
- User prompts shown with full content
- Agent answers shown with full content
- Tool calls shown as summaries, with output detail for matched entries
- Match markers (`**>>**`) on target entries
- Overlapping windows merged correctly

**Path compatibility:** Both real paths (`edify-wt/pushback`) and decoded paths (`edify/wt/pushback`) resolve to the same encoded directory and work.

## Acceptance Criteria (FR-2)

- Session excerpts trimmed to relevant exchange: YES (window parameter controls context)
- Enough context to be readable standalone: YES (3-5 entry window shows conversation flow)
- Session ID and project dir included: YES (header of each excerpt)

## Limitations (acceptable for prototype)

- Search parses all matching session files on each invocation (no index). Acceptable for ~100 sessions per topic.
- Full UUID required for excerpt (scan output shows truncated). Topic agents will use search JSON output which includes full session_id.
- Hit count per session can be high (780 for pushback) — topic agents should use targeted keywords to narrow.
