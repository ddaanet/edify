# Recall Artifact: when-resolve-fix

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## CLI conventions

when cli commands are llm-native — all stdout, no stderr, exit code signal
when writing error exit code — Click UsageError consolidates display+exit
when raising exceptions for expected conditions — custom types not ValueError

## Testing

when testing CLI tools — Click CliRunner in-process, isolated filesystem
when writing red phase assertions — behavioral verification, not just structure

## Deduplication

how deduplicate feedback entries — first-100-chars prefix key pattern

## Memory index

when writing memory-index trigger phrases — articles heading alignment with heading text
