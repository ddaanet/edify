# Markdown and Token Tooling

Token counting, markdown cleanup, and formatter selection decisions.

## .Token Counting

### How to Pass Model As Cli Argument

**Decision:** Model is first positional argument in CLI, required parameter in functions

**Rationale:** Token counts vary by model; explicit model choice ensures accurate counts

**CLI Usage:** `edify tokens sonnet file.md`

**Implementation:** `count_tokens_for_file(path: Path, model: str)`

**Supported models:** haiku, sonnet, opus (short aliases preferred)

### How to Handle Model Alias Resolution

**Decision:** Hybrid approach - support Anthropic's official aliases directly, with runtime probing fallback for unversioned aliases

**Rationale:**

- Anthropic provides official aliases like `claude-sonnet-4-5` that auto-update to latest snapshots
- Power users can use full model IDs (`claude-sonnet-4-5-20250929`) or official aliases (`claude-sonnet-4-5`)
- Casual users can use simple aliases ("sonnet", "haiku", "opus") which resolve via runtime probing
- 24-hour cache avoids repeated API calls

**Implementation:**

1. **Pass-through**: If model starts with "claude-", use unchanged (no resolution needed)
2. **Unversioned alias resolution**: For simple aliases like "sonnet":
   - Check cache first (24-hour TTL in user config directory)
   - If cache miss/expired, query `client.models.list()` API
   - Filter models where ID contains the alias (case-insensitive)
   - Select latest by `created_at` timestamp
   - Cache full model list with timestamp
3. **Fallback**: If alias not found, pass through unchanged (API will error)
4. **Cache location**: Platform-appropriate user cache directory via `platformdirs`

**Cache format:**

```json
{
  "fetched_at": "2025-12-29T10:30:00Z",
  "models": [
    {"id": "claude-sonnet-4-5-20250929", "created_at": "2025-09-29T00:00:00Z"},
    ...
  ]
}
```

### How to Integrate With Anthropic Api

**Decision:** Use official Anthropic SDK with default environment variable handling

**Rationale:** SDK handles API details, retries, error types; avoid custom HTTP logic

**Implementation:** `tokens.py` module

**API Key:** `ANTHROPIC_API_KEY` environment variable (SDK default)

### When Counting Tokens In Empty Files

**Decision:** Return 0 for empty files without API call

**Rationale:** Avoid unnecessary API calls; empty content always has 0 tokens across all models

**Performance:** Reduces API usage for module development workflows

### When Expanding File Glob Patterns

**Decision:** Defer glob pattern expansion to future release

**Rationale:** Simplify initial implementation; users can use shell expansion if needed (e.g., `edify tokens *.md --model sonnet`)

**Future:** May add built-in glob support in later version

## .Markdown Cleanup Architecture

**Decision Date:** 2026-01-04

**Context:** Extend markdown preprocessor for Claude output patterns

### When Fixing Consecutive Emoji Lines

Claude generates markdown-like output that isn't always valid markdown:

1. Consecutive lines with emoji/symbol prefixes that should be lists
2. Code blocks with improper fence nesting
3. Metadata labels followed by lists needing indentation

These patterns break dprint formatting or produce suboptimal output.

### How to Clean Markdown Before Formatting

**Preprocessor approach:**

- Run markdown.py fixes BEFORE dprint formatting
- Fix structural issues while preserving content
- Error out on invalid patterns (prevent silent failures)

**Pipeline:**

```
Claude output → markdown.py (structure) → dprint (style) → final output
```

### .Design Decisions

#### When Extending Vs Creating Cleanup Functions

**Decision:** Extend `fix_warning_lines` for checklist detection, create new functions for code blocks and metadata indentation.

**Rationale:**

- Checklist detection is conceptually similar to existing warning line handling
- Code block nesting is fundamentally different (block-based vs. line-based)
- Metadata list indentation is a new pattern distinct from metadata blocks

**Alternatives considered:**

- Create all new functions → More code duplication
- Single mega-function → Harder to test and maintain

#### When Handling Invalid Markdown Patterns

**Decision:** Error out when inner fences detected in non-markdown blocks.

**Rationale:**

- Prevents dprint formatting failures downstream
- Makes issues visible immediately (fail fast)
- Invalid patterns indicate malformed Claude output that needs fixing

**Alternatives considered:**

- Silent skip → Hides problems, dprint fails later
- Auto-fix → Risk of corrupting code content

#### How to Order Markdown Processing Steps

**Decision:**

```python
1. fix_dunder_references        # Line-based
2. fix_metadata_blocks          # Line-based
3. fix_warning_lines            # Line-based (extended)
4. fix_nested_lists             # Line-based
5. fix_metadata_list_indentation # Line-based (new)
6. fix_numbered_list_spacing    # Spacing (after structure)
7. fix_markdown_code_blocks     # Block-based (last)
```

**Rationale:**

- Line-based fixes before block-based (avoid interference)
- Spacing fixes after structural changes
- Code block nesting last (operates on complete structure)

**Alternatives considered:**

- Random order → Some fixes would break others
- All new fixes at end → Spacing issues with numbered lists

#### How to Detect Markdown Line Prefixes

**Decision:** Generic prefix detection (any consistent non-markup prefix), not hard-coded patterns.

**Rationale:**

- Handles current patterns (✅, ❌, [TODO], etc.)
- Adapts to new patterns Claude might generate
- Reduces maintenance (no pattern list to update)

**Alternatives considered:**

- Whitelist specific prefixes → Brittle, needs updates
- No grouping logic → Each pattern needs separate fix

#### How to Indent Nested Markdown Lists

**Decision:** 2 spaces for nested lists.

**Rationale:**

- Standard markdown convention
- Matches dprint default formatting
- Consistent with existing codebase style

**Alternatives considered:**

- 3 spaces → Not standard
- 4 spaces → Too much nesting, harder to read

### When Evolving Markdown Processing

**Evolution to dprint plugin:**

Current preprocessor is a separate step. Ideally, this should be a dprint plugin that runs during formatting. Benefits:

- Single-pass processing
- Better integration with dprint configuration
- Cleaner toolchain

**Migration path:**

1. Keep preprocessor functional (backwards compatibility)
2. Develop dprint plugin with same logic
3. Test plugin thoroughly
4. Deprecate preprocessor, migrate users
5. Remove preprocessor once plugin is stable

## .Markdown Formatter Selection

### When Choosing Markdown Formatter Tool

**Remark-cli chosen:**

**Decision Date:** 2026-01-07

**Decision:** Use remark-cli as markdown formatter, not Prettier or markdownlint-cli2.

**Rationale:**

| Criterion | Prettier | markdownlint-cli2 | remark-cli (chosen) |
|-----------|----------|-------------------|---------------------|
| Primary Purpose | Formatter | Linter only | Formatter |
| Idempotent | ❌ No (documented bugs) | ❓ N/A | ✅ Yes |
| CommonMark Compliance | ⚠️ Mostly | ✅ Yes | ✅ 100% |
| Nested Code Blocks | ⚠️ Issues | ❓ Unclear | ✅ Correct |
| YAML Frontmatter | ⚠️ Strips comments | ✅ Yes | ✅ Exact preservation |
| Configuration | 2 options | 60+ lint rules | 17+ format options |

**Prettier issues disqualifying it:**
- Non-idempotent: Multiple documented bugs (empty sub-bullets, mid-word underscores, lists with extra indent)
- YAML frontmatter: Strips comments, breaks on long lists
- Nested code blocks: Inconsistent backtick reduction
- Limited configurability

**markdownlint-cli2 limitations:**
- Not a comprehensive formatter (only fixes rule violations)
- No idempotency guarantee

**remark-cli advantages:**
- Idempotent by design with fixed configuration
- 100% CommonMark compliance via micromark
- Handles nested code blocks correctly per spec
- Preserves YAML frontmatter exactly (doesn't parse or modify)
- Highly configurable (17+ formatting options)
- Active maintenance by unified collective
- 150+ plugin ecosystem

**Test Results:** Both Prettier and remark-cli passed test corpus validation (3 runs, idempotent). However, Prettier has documented edge cases that fail in production use.

**Configuration chosen:**
```json
{
  "settings": {
    "bullet": "*",
    "fence": "`",
    "fences": true,
    "rule": "*",
    "emphasis": "*",
    "strong": "*",
    "incrementListMarker": true,
    "listItemIndent": "one"
  },
  "plugins": [
    "remark-gfm",
    "remark-frontmatter",
    "remark-preset-lint-consistent"
  ]
}
```

**Reference:** Decision based on comprehensive evaluation (2026-01-07) comparing Prettier, markdownlint-cli2, and remark-cli across CommonMark compliance, idempotency, configuration options, and test corpus validation

