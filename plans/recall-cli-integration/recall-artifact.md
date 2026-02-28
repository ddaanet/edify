# Recall Artifact: Recall CLI Integration

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

when cli commands are llm-native — _recall is underscore-prefixed, LLM-native (stdout markdown, exit codes)
when writing error exit code — Click _fail pattern, Never return type
when checking expected program state — boolean returns for check subcommand
when designing cli tools for llm callers — structured markdown output, no quoting issues
when cli error messages are llm-consumed — facts only, STOP directive for unrecoverable
when testing CLI tools — Click CliRunner, in-process, isolated filesystem
when writing red phase assertions — behavioral verification, not structural
when preferring e2e over mocked subprocess — real git repos for diff subcommand tests
when writing recall artifacts — keys only, downstream resolve, no staleness
when anchoring gates with tool calls — _recall resolve is the canonical gate anchor
how recall sub-agent memory — bash transport, when-resolve.py resolution
when adding error handling to call chain — layer separation: context at site, display at top
