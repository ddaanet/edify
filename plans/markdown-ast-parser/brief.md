# Brief: Markdown AST Parser

## Problem

Multiple markdown consumers in the codebase use regex-based line-by-line parsing with ad-hoc fence tracking. Each consumer reimplements structure detection (headings, lists, code blocks, thematic breaks) with different edge-case handling:

- **prepare-runbook.py:** `extract_cycles` (regex for `## Cycle X.Y:` + `_fence_tracker`), `split_cycle_content` (`---` splitting + `**Bootstrap:**` marker detection), `extract_sections` (line-by-line H2 detection)
- **session validation** (`src/claudeutils/validation/session_structure.py`): `parse_sections` (heading detection), `check_task_section_lines` (list item regex for task metadata)
- **task_parsing.py:** Regex for `- [ ] **Name** — command | model | restart` with sub-item detection
- **handoff-cli-tool S-4 parser** (planned): new session.md parser for read/write operations

Each has its own fence-boundary handling. prepare-runbook.py has `strip_fenced_blocks` and `_fence_tracker`. Session validation has none (vulnerability to fenced headings in session.md — currently unlikely but not prevented).

## Architecture

Two-stage pipeline:

1. **Preprocessor (existing):** Fix LLM structural errors before parsing. The `markdown_*_fixes.py` modules handle: bold-as-heading, incorrect backtick fencing, list spacing, metadata blocks. Known bug: multi-line inline code spans (xfail in `test_full_pipeline_remark[02-inline-backticks]`).

2. **Standard parser (new):** Parse corrected markdown into AST. Candidates: `markdown-it-py` (CommonMark-compliant, extensible, Python), `mistune` (fast, pure Python). Traversal replaces all regex structure detection.

**Consumer migration:**

| Consumer | Current | After |
|----------|---------|-------|
| prepare-runbook.py cycles | regex + _fence_tracker | AST heading nodes → cycle boundaries |
| prepare-runbook.py split | `---` string search | AST thematic_break nodes |
| session validation sections | line-by-line heading detection | AST heading tree |
| task parsing | regex for list items with inline formatting | AST list_item → checkbox → strong → code nodes |
| handoff-cli-tool S-4 | (not yet built) | Built directly on AST from start |

**List item structure example (task entries):**

```markdown
- [ ] **Task name** — `command` | model | restart
  - Plan: foo | Status: outlined
  - Note: some context
```

Current: regex with capture groups and sub-item heuristics.
After: list_item node → paragraph with checkbox, strong, code inline nodes. Sub-items as nested list. Metadata extraction from typed AST nodes, not string pattern matching.

## Prerequisite

Fix the preprocessor xfail (multi-line inline code spans). The standard parser needs well-formed markdown as input. The preprocessor's job is to guarantee this.

## Scope Considerations

- **Dependency addition:** `markdown-it-py` or `mistune` becomes a project dependency. Both are pure Python, well-maintained, available on PyPI.
- **Migration order:** Build shared parser utility first. Migrate consumers one at a time (session validation → prepare-runbook.py → handoff-cli-tool). Each migration is independently testable.
- **handoff-cli-tool coupling:** S-4 (session.md parser) is designed but not built. Building it directly on AST avoids building a regex parser then rewriting it. The AST parser plan should ship before handoff-cli-tool runbook execution.
- **prepare-runbook.py coupling:** The `---` splitting and Bootstrap detection just added (bootstrap-tag-support) would be rewritten. This is acceptable — the current implementation is functional, the rewrite improves it.

## Evidence

- bootstrap-tag-support: `split_cycle_content` added another `---`-dependent split, compounding fragility
- `_fence_tracker` pattern duplicated across consumers
- xfail `test_full_pipeline_remark[02-inline-backticks]` — preprocessor bug blocking full pipeline
- handoff-cli-tool outline S-4: designs a new regex-based parser for session.md that would be immediately superseded by AST approach

## Classification Hint

Complex — new dependency, cross-cutting migration across multiple consumers, preprocessor bug fix prerequisite. Production artifact destination. Multiple phases: parser utility, preprocessor fix, consumer migrations. Blocks handoff-cli-tool S-4 (parser design changes).

## Ordering Consideration

This plan should be evaluated against handoff-cli-tool timeline. If handoff-cli-tool is the priority, the S-4 parser could be built on AST from the start (making this plan a prerequisite for handoff-cli-tool), or built with regex first (making this plan a follow-up rewrite). The prerequisite ordering avoids throwaway work.
