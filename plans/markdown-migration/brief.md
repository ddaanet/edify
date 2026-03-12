**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Markdown Migration

## Problem

Current markdown handling is fragile — custom regex parsing, hardcoded thresholds, no AST representation. Three coupled sub-problems:

- **Lenient markdown parser:** Project files use non-standard markdown (nested task lists with metadata, mixed heading levels, inline directives). Standard parsers reject or mangle these. Need a parser that handles project conventions while producing a usable AST.

- **Token counting API + sqlite cache:** Token counting (`src/claudeutils/tokens.py`) makes API calls per file. Need a caching layer (sqlite, consistent with project's sqlalchemy convention) and a clean API that other tools can import.

- **Threshold migration:** Hardcoded thresholds scattered across skills and fragments (learnings.md soft limit 80 lines, session.md size warnings, etc.). Need configuration-driven thresholds that can be tuned without editing prose.

## Dependencies

- Related plan: markdown-ast-parser (briefed) — may overlap or subsume the parser sub-problem
- Token cache partially exists: `src/claudeutils/token_cache.py` (sqlite via sqlalchemy)

## Open Questions

- Does markdown-ast-parser plan cover the lenient parser need, or is it a different scope?
- Should thresholds live in a config file, or in the artifacts they govern (e.g., frontmatter)?

## Success Criteria

- Design resolves overlap with markdown-ast-parser plan
- Architecture for parser that handles project markdown conventions
- Token cache API designed (may extend existing token_cache.py)
