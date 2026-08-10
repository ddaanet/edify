# Data Validation and Quality

Data models, code quality standards, and feedback processing pipeline.

## .Data Models

### When Choosing Pydantic For Validation

**Pydantic for validation:**

**Decision:** Use Pydantic BaseModel for all data structures (SessionInfo, FeedbackItem)

**Benefits:**

- Automatic type validation
- ISO 8601 timestamp validation
- JSON serialization with `model_dump(mode="json")`
- Clear field definitions

**Impact:** Type safety at runtime, not just static analysis

### How to Define Feedback Type Enum

**Decision:** Use StrEnum for feedback types (MESSAGE, TOOL_DENIAL, INTERRUPTION)

**Rationale:** Type-safe string constants, clear intent, better than string literals

**Impact:** IDE autocomplete, validation errors for invalid types

## .Code Quality

### When Docstring Formatting Conflicts

**Decision:** Accept docformatter wrapping as the source of D205 violations when docstring first line exceeds 80-char limit.

**Issue:** When a docstring summary exceeds 80 characters, docformatter wraps the first line, which triggers ruff D205 (blank line required between summary and description).

**Example:**
```python
# Original (E501 - line too long):
"""Convert consecutive **Label:** lines to list items and indent following lists."""

# Docformatter wraps first line to fit 80 chars:
"""Convert consecutive **Label:** lines to list items and indent following
lists.
"""
```

This triggers ruff D205 because docformatter doesn't add the blank line that ruff expects after a multi-line summary.

**Solution:** Shorten docstring summaries to fit within 80 characters (docformatter's wrap-summaries limit), preventing the wrap and avoiding the D205 violation.

**Rationale:** docformatter handles docstring reformatting (which ruff doesn't do). The wrap-summaries setting exists for readability. The conflict is expected but surprising when the first line should be shortened.

**Don't do:** Ignore D205 globally or disable docformatter.

### How to Manage Cyclomatic Complexity

**Complexity management:**

**Decision:** Extract helper functions when cyclomatic complexity exceeds limits

**Examples:**

- `_extract_feedback_from_file()` extracted from main extraction logic
- `_process_agent_file()` extracted to handle agent file processing

**Rationale:** Ruff/pylint complexity checks enforced at build time; refactor rather than suppress

### When Tempted To Suppress Linting

**Decision:** Fix linting issues properly instead of using `# noqa` suppressions

**Rationale:** Suppressions hide problems; proper fixes improve code quality

**Examples:**

- G004: Use lazy % formatting for logging
- E501: Split long lines properly
- C901/PLR0912: Extract helper functions

### When Adding Strict Type Annotations

**Decision:** Full type annotations in strict mypy mode

**Rationale:** Catch bugs early, self-documenting code, IDE support

**Impact:** Zero runtime overhead, significant development-time benefit

## .Feedback Processing Pipeline

### How to Architect Feedback Pipeline

**Feedback processing:**

**Decision:** Three-stage pipeline: `collect` → `analyze` → `rules`

**Rationale:** Mirrors the exploratory workflow in tmp-\* scripts; each stage builds on previous output

**Data flow:**

- `collect`: Batch extract from all sessions → JSON array of FeedbackItem
- `analyze`: Filter noise, categorize → Statistics summary
- `rules`: Stricter filter, deduplicate → Rule-worthy items for manual review

### How to Build Reusable Filtering Module

**Decision:** Create `filtering.py` module with reusable `is_noise()` and `categorize_feedback()` functions

**Rationale:** Both `analyze` and `rules` need noise filtering; DRY principle

**Impact:** Filtering module implemented first; other features depend on it

### How to Detect Noise In Command Output

**Decision:** Multi-marker detection with length threshold

**Markers (return True if present):**

- Command outputs: `<command-name>`, `<bash-stdout>`, `<bash-input>`, `<local-command-stdout>`
- System messages: `Caveat:`, `Warmup`, `<tool_use_error>`
- Error outputs: `Exit code`, `error: Recipe`

**Length threshold:** < 10 characters (configurable for `rules`)

**Rationale:** Based on analysis of 1200 feedback items; these patterns dominated noise

### How to Categorize Feedback By Keywords

**Decision:** Keyword-based category assignment with priority order

**Categories and keywords:**

| Category     | Keywords                                 |
| ------------ | ---------------------------------------- |
| instructions | don't, never, always, must, should       |
| corrections  | no, wrong, incorrect, fix, error         |
| code_review  | review, refactor, improve, clarity       |
| process      | plan, next step, workflow, before, after |
| preferences  | prefer, i want, make sure, ensure        |
| other        | (default)                                |

**Rationale:** Simple O(1) keyword matching; categories derived from feedback summary analysis

### How to Deduplicate Feedback Entries

**Decision:** First 100 characters as dedup key, case-insensitive

**Rationale:** Handles repeated feedback across sessions; 100 chars captures intent while allowing variation in endings

**Implementation:** Track seen prefixes in set; skip items with already-seen prefix

### When Filtering For Rule Extraction

**Decision:** `rules` applies additional filters beyond `analyze`

**Additional filters:**

- Skip questions: starts with "How ", "claude code:"
- Skip long items: > 1000 characters (too context-specific)
- Higher min length: 20 chars (vs 10 for analyze)

**Rationale:** Rule extraction needs higher signal-to-noise; context-specific feedback isn't generalizable

