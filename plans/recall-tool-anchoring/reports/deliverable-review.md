# Deliverable Review: recall-tool-anchoring

**Date:** 2026-02-24
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | +/- | Net |
|------|------|-----|-----|
| Code | agent-core/bin/recall-check.sh | +20/-0 | +20 |
| Code | agent-core/bin/recall-resolve.sh | +46/-0 | +46 |
| Code | agent-core/bin/recall-diff.sh | +28/-0 | +28 |
| Code | agent-core/hooks/pretooluse-recall-check.py | +43/-0 | +43 |
| Agentic prose | agent-core/agents/design-corrector.md | +4/-3 | +1 |
| Agentic prose | agent-core/agents/outline-corrector.md | +1/-1 | 0 |
| Agentic prose | agent-core/agents/runbook-outline-corrector.md | +1/-1 | 0 |
| Agentic prose | agent-core/skills/design/SKILL.md | +6/-2 | +4 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +3/-1 | +2 |
| Agentic prose | agent-core/skills/review-plan/SKILL.md | +2/-2 | 0 |
| Agentic prose | agent-core/skills/deliverable-review/SKILL.md | +1/-1 | 0 |
| Agentic prose | agent-core/skills/orchestrate/SKILL.md | +1/-1 | 0 |
| Configuration | .claude/settings.json | +10/-0 | +10 |
| Agentic prose | .claude/agents/crew-recall-tool-anchoring-p1.md | +161/-0 | +161 |
| Agentic prose | .claude/agents/crew-recall-tool-anchoring-p4.md | +161/-0 | +161 |
| **Total** | **15 files** | **+488/-12** | **+476** |

**Design conformance:** All 6 In-scope items produced. Crew agents are orchestration infrastructure (prepare-runbook.py output), not production deliverables.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**M1. recall-resolve.sh:26 — `%` vs `%%` parameter expansion (robustness)**

`${line% — *}` uses shortest-suffix match. For a line containing multiple ` — ` sequences (e.g., `when foo — bar — annotation`), only the last ` — annotation` would be stripped, leaving `when foo — bar` as the trigger. Using `%%` (longest-suffix match) would strip from the first ` — ` onward.

Current recall-artifact format has exactly one ` — ` per line, so no functional impact. Prototype script (D-2: throwaway) — fix would benefit any future format with compound annotations.

**M2. runbook/SKILL.md frontmatter — missing recall-diff.sh in allowed-tools (conformance)**

`allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)` — Phase 0.75 now calls `agent-core/bin/recall-diff.sh` but the Bash pattern list doesn't include it. Non-blocking: the skill runs in the main session where settings.json `Bash(agent-core/bin/recall-*:*)` permission applies. Frontmatter doesn't declare the dependency.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| Reference manifest format for recall-artifact.md | Covered | plans/recall-tool-anchoring/recall-artifact.md (16 entries) |
| recall-check.sh (exists?) | Covered | agent-core/bin/recall-check.sh (20 lines) |
| recall-resolve.sh (expand references → content) | Covered | agent-core/bin/recall-resolve.sh (46 lines) |
| recall-diff.sh (what changed since last update?) | Covered | agent-core/bin/recall-diff.sh (28 lines) |
| PreToolUse hook on Task (soft warning) | Covered | agent-core/hooks/pretooluse-recall-check.py (43 lines) |
| D+B restructure: read-side gates (6 gates, 6 files) | Covered | review-plan, deliverable-review, orchestrate skills + 3 corrector agents |
| D+B restructure: write-side gates (3 gates, 2 files) | Covered | design/SKILL.md (A.5, C.1), runbook/SKILL.md (Phase 0.75) |
| Permission registration in settings.json | Covered | `Bash(agent-core/bin/recall-*:*)` in permissions.allow |
| Hook registration in settings.json | Covered | PreToolUse matcher "Task" → pretooluse-recall-check.py |

**Missing:** None.
**Unspecified:** Crew agents (p1, p4) — justified orchestration infrastructure.

## Review Detail

### Code (4 files, 137 lines)

**recall-check.sh** — Correct. `set -euo pipefail`, arg check, existence check (-f), non-empty check (-s), distinct error messages. Matches D-3 spec.

**recall-resolve.sh** — Correct. Parses manifest (strips ` — ` annotations), skips blanks/comments, detects `when`/`how` prefix, delegates to `when-resolve.py`. Exit 0 on empty triggers (valid artifact, no entries). Verified functional during this review session. See M1 for `%` vs `%%` edge case.

**recall-diff.sh** — Correct. `date -r` for mtime (POSIX-portable), `git log --since` for changes, excludes artifact itself from output. `|| true` on grep pipeline is acceptable per error-handling fragment (expected no-match case).

**pretooluse-recall-check.py** — Correct. Reads JSON from stdin, extracts `tool_input.prompt`, regex `r"plans/([^/]+)/"` for job name, `os.path.exists` for artifact check. Uses `additionalContext` (warning, not blocking) per D spec. Graceful exception handling on JSON parse failure.

### Agentic Prose (10 files)

**Read-side D+B restructure (6 gates):** All converted from "Read recall-artifact.md if present" to `Bash: agent-core/bin/recall-resolve.sh <path>`. Tool-anchored — can't get content without calling the script. Lightweight fallback (memory-index + when-resolve.py) preserved for artifact-absent case. "Proceed without it" anti-pattern eliminated in all instances (orchestrate/SKILL.md was the last holdout).

**Write-side D+B restructure (3 gates):** All converted from "Recall re-evaluation: Re-evaluate..." to `Bash: agent-core/bin/recall-diff.sh <job-name>`. Tool provides data (changed files list), judgment remains with consumer (which entries to add/remove). Consistent format across design A.5, design C.1, runbook Phase 0.75.

**Recall-artifact.md (reference manifest):** 16 entries, each with trigger phrase + ` — ` annotation. Heading line correctly skipped by recall-resolve.sh. All triggers resolve successfully (verified by running recall-resolve.sh during this review). Trigger phrases align with memory-index entries (corrector fixed `how to X` → `how X` alignment in final review).

### Configuration (1 file)

**settings.json:** Permission `Bash(agent-core/bin/recall-*:*)` covers all three scripts with wildcard. Hook registered under PreToolUse with matcher "Task". Path uses `$CLAUDE_PROJECT_DIR` variable for portability. No conflicts with existing hooks.

### Cross-Cutting

- **Path consistency:** All 9 gates reference correct script paths. Settings.json permission pattern covers all scripts. Hook path in settings matches actual file.
- **API contract alignment:** recall-resolve.sh takes `<artifact-path>` (full path) — all read-side callers pass full path. recall-diff.sh takes `<job-name>` — all write-side callers pass job name. Consistent.
- **Naming convention:** `recall-*.sh` prefix for scripts, `pretooluse-*.py` for hook. Follows existing project conventions.
- **Agent tool access:** All 3 corrector agents have unrestricted `Bash` in their tools list — can call recall-resolve.sh. Settings.json permission additionally enables main-session calls.
- **Gate count verification:** 6 read-side + 3 write-side = 9 gates across 8 files. Matches design claim.

## Summary

- **Critical:** 0
- **Major:** 0
- **Minor:** 2
