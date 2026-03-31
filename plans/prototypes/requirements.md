# Prototypes — Session Extraction Feature Gap

## Context

The edify feedback pipeline (`discovery.py`, `parsing.py`, `extraction.py`, `filtering.py`) operates on a single project directory. It extracts feedback types (tool denials, interruptions, messages) but cannot:

- Scan across multiple project directories (worktrees)
- Extract specific directive types (`p:`, `d:`) from session transcripts
- Correlate session events with git history (task insertions, commits)
- Link sessions to commits (most interactive sessions include a commit)

## Current Prototypes

| Script | Location | Purpose |
|--------|----------|---------|
| `scrape-pending-directives.py` | `plans/prototypes/` | Extract `p:` directives from sessions across projects |
| `correlate-pending-v2.py` | `plans/prototypes/` | Match `p:` directives to git task insertions via fuzzy text similarity |
| `scrape-validation.py` | `scripts/` | Extract pushback scenario responses from sessions |
| `last-output` | `bin/` | Extract last assistant message from a session |

## Feature Gap

**FR-1: Multi-project session scanning**
Scan sessions across `~/code/edify`, `~/code/edify-wt/*`, and `~/code/edify-*`. The existing pipeline's `--project` flag accepts one directory. Three worktree location conventions exist.

**FR-2: Directive extraction**
Extract hook-processed directive types (`p:`, `d:`) from user messages. Current `parsing.py` only classifies tool denials, interruptions, and generic messages — no directive-type awareness.

**FR-3: Git history correlation**
Correlate session events (directives, commits) with git history (task insertions, commit hashes). The prototype `correlate-pending-v2.py` demonstrates: date-windowed matching + fuzzy text similarity to link `p:` directives to `session.md` task insertions.

**FR-4: Session-commit linkage**
Most interactive sessions include a commit. Link session IDs to git commits for traceability. Enables: "which session produced this task?" and "what was the p: directive that created this task?"

## Evidence (from this session)

Analysis of 30 `p:` directives across 337 sessions showed `p:`-originated tasks distribute evenly across insertion positions (34.5% prepend, 20.7% near-top, 17.2% middle, 13.8% near-bottom, 13.8% append) — distinct from the 61.5% prepend rate of workflow continuation tasks. This finding was only possible with the prototype scripts; the production pipeline cannot produce it.

## Integration Path

The prototypes use `edify.paths.encode_project_path` already. Natural integration points:
- `discovery.py` — add multi-project session listing
- `parsing.py` — add directive type detection
- `cli.py` — add `--projects` flag or auto-detect worktrees
- New module for git correlation (subprocess calls to `git log`, `git show`)
