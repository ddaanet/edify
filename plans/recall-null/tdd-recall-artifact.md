# TDD Recall Artifact: recall-null

Resolve ALL entries via `agent-core/bin/when-resolve.py` before starting cycles.

## Entry Keys

when testing CLI tools — Click CliRunner in-process, captures output and exit code
when writing red phase assertions — behavioral assertions, not structural (exit code alone insufficient)
when green phase verification includes lint — just check && just test before commit
when checking expected program state — boolean return not exception, EAFP state-query distinction
when designing cli tools for llm callers — stdin/stdout markdown, no quoting issues
