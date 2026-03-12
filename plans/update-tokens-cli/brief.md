# Brief: Update Tokens CLI

## Problem

`claudeutils tokens` requires a model argument (`{haiku,sonnet,opus}`) but there's no evidence of tokenization difference between models. Sonnet should be the default. Usage message needs updating to reflect current capabilities (accepts multiple files).

## Scope

- Make `sonnet` the default model argument (optional, not required)
- Update usage message to document multi-file support
- Verify tokenization produces identical results across model tiers (if not, document the difference)

## Success Criteria

- `claudeutils tokens file.py` works without specifying model (defaults to sonnet)
- Usage message accurately describes capabilities
