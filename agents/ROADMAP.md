# Roadmap

Future enhancement ideas for edify.

## Markdown Formatter Survey ✅

**Status:** Complete (2026-01-07)

**Decision:** remark-cli selected and migrated

**Reference:** `agents/decisions/architecture.md` - Markdown Formatter Selection section

## Session Summary Extraction

**Goal:** Extract a summary of a session for process compliance analysis.

**Output format:**

- Tool uses (without full inputs/outputs)
- User inputs
- Key assistant outputs
- Timeline of interactions

**Use case:** Analyze whether agents followed expected workflows, identify deviations
from standard procedures.

## Additional Output Formats

**Goal:** Support different output formats beyond JSON.

**Potential formats:**

- Pretty-printed JSON with indentation
- CSV format for spreadsheet analysis
- Markdown format for human-readable reports

## Filtering Options

**Goal:** Allow users to filter extracted feedback.

**Potential filters:**

- `--type` - Filter by feedback type (message, tool_denial, interruption)
- `--since` / `--until` - Date range filtering
- `--agent` - Filter by agent ID
- `--exclude-trivial` - Hide filtered-out trivial messages in output

## Generate Claude Agents from Role Description

**Goal:** Generate complete agent wrapper files from high-level role descriptions.

**Input:** Natural language description of agent purpose, capabilities, constraints.

**Output:**

- Role YAML config (target_class, rule_budget, modules, enabled_tools)
- Composed system prompt
- Optional: Claude Code wrapper script

**Use case:** Rapid prototyping of new agent types without manual module composition.

## Command-Based MCP for Shell Execution

**Goal:** Evaluate MCP as lightweight alternative to Bash tool for simple shell
commands.

**Context:** Tool descriptions are included per-enabled-tool, not in system prompt. The
Bash tool description is ~65 lines + ~95 lines for git commit/PR instructions. A
command-based MCP could provide shell execution without this overhead.

**Research questions:**

- What is the token overhead of MCP tool definitions vs system tool descriptions?
- Can an MCP provide sandboxed execution equivalent to Bash tool?
- Use case: `just *` commands, simple build/test invocations

**Tradeoffs:**

- MCPs are reputed to be token-heavy (need measurement)
- System tools don't offer another shell escape hatch (likely intentional for
  sandboxing)
- MCP would need equivalent safety guarantees

**Measurement:** Use `edify tokens` command to compare tool description overhead

## Claude Wrapper Generator (plan-claude-wrapper.md)

**Goal:** Create a plan for generating Claude Code wrapper configurations.

**Scope:**

- Analyze existing Claude Code wrapper patterns
- Define wrapper template structure
- Specify customization points (model, tools, hooks)
- Integration with module composition system
