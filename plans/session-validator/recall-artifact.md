# Recall Artifact: Session Validator

Resolve entries via `claudeutils _recall resolve` — do not use inline summaries.

## Entry Keys

when splitting validation into mechanical and semantic — scripted deterministic checks vs agent judgment
when placing quality gates — commit chokepoint, scripted mechanical enforcement
when testing CLI tools — Click CliRunner in-process, not subprocess
when preferring e2e over mocked subprocess — real git repos tmp_path, mock only error injection
when choosing script vs agent judgment — non-cognitive deterministic → script
when adding a new variant to an enumerated system — grep downstream enumeration sites
when finding project root in scripts — CLAUDE.md marker not agents/
when writing error exit code — single call _fail pattern, not display+exit
when triaging behavioral code changes as simple — moderate minimum for new functions
