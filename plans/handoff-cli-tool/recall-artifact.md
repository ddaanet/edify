# Recall Artifact: Session CLI Tool

## Planning-Relevant Entries

- `when designing cli tools for llm callers` — stdin/stdout markdown, no quoting, section-based parsing
- `when cli commands are llm-native` — all stdout, exit code signal, no stderr, `**Header:** content` format
- `when cli error messages are llm-consumed` — facts only, STOP directive for data-loss, no suggestions
- `when writing error exit code` — consolidate display+exit, `_fail()` pattern, `Never` return type
- `when adding error handling to call chain` — context at failure site, display at top level
- `when checking expected program state` — `_git_ok()` boolean pattern, not exception-based
- `when writing CLI output` — no destructive suggestions, agents follow instructions literally
- `when placing quality gates` — gate at commit chokepoint, scripted mechanical check
- `when splitting validation into mechanical and semantic` — script for deterministic, agent for judgment
- `when choosing script vs agent judgment` — non-cognitive deterministic operations get scripted
- `when testing CLI tools` — Click CliRunner, in-process, isolated filesystem
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path, mock only for error injection
- `when extracting git helper functions` — `_git(*args)` pattern, subprocess reduction
- `when tracking worktree tasks in session.md` — two-section model, static classification, no moves
- `when choosing task status markers` — checkbox notation, dagger for failed, hyphen for canceled

## Implementation-Relevant (for step files, not recall)

Deferred to step-level context: mock patching details, test structure patterns, fixture conventions.
