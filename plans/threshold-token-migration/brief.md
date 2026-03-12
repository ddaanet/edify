# Brief: Threshold Token Migration

## Problem

All size thresholds (decision files, learnings, source code) use line counts. Token counts are more semantically correct:
- Decision files have no line wrapping — one line = one paragraph. Line count drastically underestimates size.
- Source code file size limits exist for context management (how much context the agent loads per Edit), not complexity. Token count directly measures what's being optimized.
- Learnings.md "80 lines" limit exists because it loads into every session via CLAUDE.md @-reference. Real constraint is context window budget.

Token counting infrastructure exists (`token_cache.py`, `tokens.py`). Local tokenizer available via anthropic SDK — no network dependency.

## Scope

- Audit all line-based thresholds across validation code and prose fragments
- Convert to token-based equivalents with calibrated values
- Expected blast radius: current thresholds calibrated against line counts need recalibration, especially decision files where line count ≪ token count

## Dependencies

- Token CLI default model (pending: update-tokens-cli) — if tokenization varies by model, threshold values depend on which tokenizer. Expected to be negligible.

## Success Criteria

- All size thresholds use token counts instead of line counts
- Threshold values calibrated against actual file sizes (not converted mechanically from line counts)
