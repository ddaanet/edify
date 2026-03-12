# Brief: Markdown Migration

## Problem

Three loosely coupled concerns are tangled together by shared infrastructure gaps: markdown structure detection uses ad-hoc regex, token counting lacks a clean importable API despite having a cache, and operational thresholds are hardcoded in prose fragments. Each degrades independently but they share a migration surface (markdown files are what gets parsed, counted, and threshold-checked).

## Sub-problems

### 1. Parser — regex-based structure detection

Multiple consumers reimplement markdown structure detection with regex:

- `session_structure.py`: `parse_sections` via `SECTION_PATTERN` regex, no fence tracking
- `task_parsing.py`: `TASK_PATTERN`, `COMMAND_PATTERN`, `WORKTREE_MARKER_PATTERN` regexes for list item metadata
- `prepare-runbook.py`: `extract_cycles` with `_fence_tracker`, `split_cycle_content` with `---` splitting
- `markdown_parsing.py`: segment-based parser with fence tracking, YAML prolog detection — already a structural parser but outputs `Segment` objects, not an AST

**Coupling to markdown-ast-parser:** This sub-problem is fully subsumed by the markdown-ast-parser plan. See Relationship section below.

### 2. Token cache API — exists but underexposed

`token_cache.py` implements a complete SQLite-backed cache (SQLAlchemy, md5-keyed, model-aware, LRU via `last_used`). `tokens.py` integrates it in `count_tokens_for_files`. The cache works.

What's missing:
- No CLI command exposes cached counting (only `claudeutils tokens` exists, unclear if it uses cache)
- No bulk/directory counting API
- No cache management (eviction, stats, invalidation)
- The deferred import in `tokens.py:194` (`from claudeutils.token_cache import ...`) suggests the integration was added incrementally

**Independence:** This sub-problem is fully independent of the parser and threshold work. Can ship separately.

### 3. Thresholds — hardcoded in prose and validation code

Operational thresholds scattered across files:
- `learnings.md`: "Soft limit: 80 lines" (prose instruction, not enforced programmatically)
- `validation/learnings.py`: `MAX_WORDS = 7` (learning key length)
- `validation/decision_files.py`: `CONTENT_THRESHOLD = 2` (substantive line count)
- `runbook/SKILL.md`: file count thresholds marked "(ungrounded — needs calibration)"
- Various fragment files: line limits, size warnings in prose

Two distinct types:
- **Programmatic thresholds** (Python constants): could be extracted to a config module
- **Prose thresholds** (instructions in .md files): can't be programmatically enforced without parsing the prose — making this dependent on the parser

**Independence:** Programmatic threshold extraction is independent. Prose threshold migration depends on having a parser that can locate and potentially rewrite threshold values in markdown — tightly coupled to the parser sub-problem.

### Coupling analysis

| Sub-problem | Depends on parser? | Depends on token cache? | Independent? |
|---|---|---|---|
| Parser | N/A | No | Subsumed by markdown-ast-parser |
| Token cache API | No | N/A | Yes — ship independently |
| Programmatic thresholds | No | No | Yes — ship independently |
| Prose thresholds | Yes (needs AST to locate) | Possibly (token-based limits) | No — blocked on parser |

## Current State

**Parser infrastructure:**
- `markdown_parsing.py`: Segment-based parser (processable vs protected zones). Handles fences, YAML prologs. Used by the markdown preprocessor pipeline (`markdown.py`, `markdown_block_fixes.py`, `markdown_list_fixes.py`, `markdown_inline_fixes.py`).
- Validation modules: Independent regex parsers in `session_structure.py` and `task_parsing.py`, no shared parsing layer.
- Preprocessor xfail: `test_full_pipeline_remark[02-inline-backticks]` — multi-line inline code span bug.

**Token cache:**
- `token_cache.py`: Complete implementation — `TokenCache` class, `TokenCacheEntry` ORM model, `cached_count_tokens_for_file`, `get_default_cache`. Uses `platformdirs` for cache location.
- `tokens.py`: Public API with model resolution, file counting, bulk counting. Cache integration via deferred import.

**Thresholds:**
- All hardcoded. No central config. Prose thresholds are instructions to the agent, not programmatic enforcement.

## Relationship to markdown-ast-parser

The markdown-ast-parser plan fully subsumes this plan's parser sub-problem. It specifies:
- Two-stage pipeline: preprocessor (existing `markdown_*.py` fixes) then standard parser (`markdown-it-py` or `mistune`) producing AST
- Consumer migration: session validation, task parsing, prepare-runbook, handoff-cli-tool S-4
- Prerequisite: fix preprocessor xfail first

This plan should **not** include parser work. The parser sub-problem is markdown-ast-parser's scope. What remains in this plan:
- Token cache API improvements (independent)
- Programmatic threshold extraction (independent)
- Prose threshold migration (blocked on markdown-ast-parser delivering an AST)

The residual scope is small enough to question whether this plan justifies its own existence vs being absorbed into other work (token cache improvements into a CLI batch, threshold extraction into a code-quality sweep).

## Dependencies

- **markdown-ast-parser** — subsumes parser sub-problem; prose threshold migration blocked on AST availability
- **codebase-sweep** — threshold extraction overlaps with its "mechanical refactoring" scope
- **handoff-cli-tool** — S-4 parser decision affects migration order (AST-first vs regex-first)

## Success Criteria

- Token cache has CLI exposure (count with cache stats, bulk directory counting)
- Programmatic thresholds extracted to a single config module with named constants
- Prose thresholds catalogued with migration path (post-AST)
- No parser work duplicated from markdown-ast-parser

## References

- `src/claudeutils/token_cache.py` — existing cache implementation
- `src/claudeutils/tokens.py` — token counting API
- `src/claudeutils/markdown_parsing.py` — segment parser (preprocessor infrastructure)
- `src/claudeutils/validation/session_structure.py` — regex-based section parsing
- `src/claudeutils/validation/task_parsing.py` — regex-based task metadata parsing
- `plans/markdown-ast-parser/brief.md` — AST parser plan (subsumes parser sub-problem)
- `agents/decisions/markdown-tooling.md` — formatter selection and token counting decisions
