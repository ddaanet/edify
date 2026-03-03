# Deliverable Review: session-scraping

**Date:** 2026-03-02
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `plans/prototypes/session-scraper.py` | 628 |

Note: `plans/session-scraping/reports/review.md` (corrector review) is a ceremony artifact, not a deliverable. `agents/session.md` and `agents/learnings.md` are session management.

Inventory script returned 0 files — the prototype existed before the branch (modified, not created). Inventory derived from `git diff 5179dc2e..HEAD`.

**Design conformance summary:** 6/6 data models implemented. 4/4 pipeline stages implemented. 4/4 CLI commands present. Two FR acceptance criteria unimplemented (agent file scanning in Stage 1, merge commit tracing in Stage 4).

## Critical Findings

1. **FR-4 merge commit parent tracing not implemented** — `correlate_session_tree()` (line 475-522)
   - Design requirement: FR-4 AC "Handles merge commits (constituent branches point to worktree session directories)." Key Decision 4: "inspect `git log --merges` parents, map parent branches to worktree session dirs via encoded path convention."
   - Current behavior: merge commits are correlated like regular commits (hash lookup, metadata retrieval). Parent branch → worktree session tracing is completely absent.
   - Impact: Sessions producing merge commits get basic correlation, but the worktree branch provenance chain is lost. Cannot answer "which worktree sessions contributed to this merge?"

## Major Findings

1. **Scanner doesn't enumerate agent-*.jsonl files** — `scan_projects()` (line 99-129)
   - Design requirement: FR-1 AC "Scans both UUID session files and agent-*.jsonl files." Stage 1 spec: "List UUID session files + agent-*.jsonl files per project."
   - Current behavior: only UUID files returned (`UUID_RE.match(f.stem)` on line 120). `SessionFile.file_type` supports `Literal["uuid", "agent"]` but no agent entries are ever created by the scanner.
   - Mitigation: Stage 3 (`build_session_tree`) discovers agent files independently via the subagents directory. Pipeline works end-to-end. Gap affects `scan` command completeness only.

2. **Silent error suppression in unattributed commit scan** — `correlate_session_tree()` (line 515-516)
   - `except subprocess.CalledProcessError: pass` silently swallows git log failure for unattributed commit detection.
   - Contrast: `_git_commit_info()` (line 444-445) correctly prints warning to stderr on CalledProcessError (fixed by corrector). This occurrence was missed.
   - Impact: if git log fails (bad repo path, corrupt index), unattributed commits silently return empty. User sees "Unattributed (recent 50): 0" with no indication of failure.

## Minor Findings

**Error handling:**
- JSON decode errors in parser skipped without logging (line 184-185). Recall guidance ("When Handling Malformed Session Data"): "Skip malformed entries, log warnings." No warning emitted.

**Design alignment:**
- `subtype: "tool_result"` check per Key Decision 1 implemented via content structure inspection (`_has_tool_results`) rather than explicit subtype field check. Functionally equivalent — tool_result entries always have tool_result blocks in content — but deviates from design's explicit mention of `subtype` field.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: Project directory enumeration | Covered | `scan_projects()` lines 99-129 |
| FR-1: Path decoding | Covered | `_decode_project_path()` lines 91-96 (lossy, documented) |
| FR-1: Prefix filtering | Covered | `scan_projects(prefix=...)` lines 105-116 |
| FR-1: UUID + agent file listing | **Partial** | UUID only; agent files absent from scanner (Major #1) |
| FR-2: 6 entry types | Covered | `EntryType` enum, all branches in `parse_session_file` |
| FR-2: User prompt classification | Covered | Key Decision 6 categories all implemented |
| FR-2: Skill invocation detection | Covered | `<command-name>` tag parsing, lines 346-367 |
| FR-2: Tool call/result correlation | Covered | `pending_tools` state machine, lines 166-292 |
| FR-2: Interactive tool outputs | Covered | `INTERACTIVE_TOOLS` frozenset, line 32 |
| FR-2: Interrupt detection | Covered | String + list formats, lines 297-310, 335-345 |
| FR-2: Commit hash extraction | Covered | `_extract_commit_hash()` + `GIT_COMMIT_MARKERS`, lines 154-160 |
| FR-2: Noise suppression (C-1) | Covered | Content summary + `--expand`/`--all-detail` |
| FR-3: Sub-agent discovery | Covered | `build_session_tree()` subagents dir, lines 400-415 |
| FR-3: Source tagging | Covered | `agent_source` field, `cur_agent` tracking |
| FR-3: Commit hash collection | Covered | `commit_hashes` set in SessionTree, lines 387-394 |
| FR-4: Git metadata lookup | Covered | `_git_commit_info()`, lines 427-472 |
| FR-4: Forward/reverse index (C-2) | Covered | `session_commits` + `commit_sessions` dicts |
| FR-4: Merge commit tracing | **Missing** | Not implemented (Critical #1) |
| FR-4: Unattributed commits | Covered | Last 50 commits check, lines 498-516 |
| C-3: Prototype scope | Covered | Single script, no production module changes |
| CLI interface | Covered | Click group with scan/parse/tree/correlate |

## Summary

- **Critical:** 1 (merge commit parent tracing unimplemented)
- **Major:** 2 (scanner agent file gap, silent error suppression)
- **Minor:** 2 (JSON parse logging, subtype field check style)
