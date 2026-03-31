# Requirements: Precommit Python3 Redirect Hook

## Functional Requirements

| ID | Pattern | Action | Notes |
|----|---------|--------|-------|
| FR-1 | `python3 <path>` / `python <path>` | Soft redirect → `<path>` | Validate: exists, executable, has shebang |
| FR-2 | `python3 -m <tool>` / `python -m <tool>` | Soft redirect → `<tool>` | Strip prefix, no per-module validation |
| FR-3 | `python3 -c "..."` / `python -c "..."` | Hard block → write prototype to `plans/prototypes/` | Captures unmet tooling need |
| FR-4 | `uv run <command>` | Soft redirect → `<command>` | .venv active in sandbox |
| FR-5 | `rm ... index.lock` | Hard block | Absorb from pretooluse-block-rm-lock.sh |
| FR-6 | Post-implementation | Remove "Script invocation" rule from CLAUDE.md | Hook enforces mechanically |

## Architecture

- **Consolidate** FR-1–5 + existing patterns (ln, git worktree, git merge) into `plugin/hooks/pretooluse-recipe-redirect.py`
- **Delete** `plugin/hooks/pretooluse-block-rm-lock.sh` after absorption
- **Update** `.claude/settings.json` to remove block-rm-lock hook entry
- **Routing table** with per-pattern action type:
  - Soft redirect: `additionalContext` message, exit 0
  - Hard block: stderr message, exit 2

## Action Types

- **Soft redirect** (additionalContext): Agent sees suggestion, can follow or override. Used for FR-1, FR-2, FR-4, existing ln/git-worktree/git-merge.
- **Hard block** (exit 2): Tool call prevented. Used for FR-3, FR-5.

## Scope

**IN:**
- Pattern matching and routing in pretooluse-recipe-redirect.py
- Consolidation of block-rm-lock.sh
- settings.json hook registration update
- CLAUDE.md rule removal

**OUT:**
- submodule-safety.py (different pattern class — cwd validation, dual-mode)
- New CLI commands in claudeutils
- Test infrastructure for hooks
