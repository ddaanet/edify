# Recall Artifact: Session Scraping

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

how encode file paths — path encoding for session file discovery
how resolve history directories — ~/.claude/projects/ storage convention
how extract session titles — handles both string and array content formats
how detect trivial messages — multi-layer filter for noise suppression
how validate session uuid files — regex filter for session vs agent files
how resolve agent ids to sessions — recursive agent tree walking
how extract agent ids from sessions — agentId from first line of agent files
when handling malformed session data — skip malformed, log warnings, continue
how architect feedback pipeline — three-stage collect/analyze/rules pipeline
how detect noise in command output — multi-marker detection with length threshold
how build reusable filtering module — is_noise() and categorize_feedback() DRY
how deduplicate feedback entries — first 100 chars as dedup key
when temporal validation required for analysis — git history correlation for feature availability
when recovering agent outputs — script extraction from task output files
when measuring agent durations — duration_ms not timestamp delta, sleep detection
when analyzing sub-agent token costs — total_tokens decomposition, cache hits
when choosing feedback output format — text default, json for piping
when designing cli tools for llm callers — structured markdown stdin/stdout
how configure script entry points — pyproject.toml [project.scripts]
when writing CLI output — no destructive suggestions, agents follow instructions
when writing error exit code — consolidate display+exit, _fail() pattern
when capturing requirements from conversation — capture over interview mode
when placing helper functions — keep close to callers for cohesion
when splitting large modules — by functional responsibility, 400-line limit
when choosing pydantic for validation — BaseModel for all data structures
how define feedback type enum — StrEnum for type-safe string constants
