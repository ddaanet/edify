# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When analyzing sub-agent token costs
- Anti-pattern: Treating `total_tokens` from CLI `<usage>` as fresh input cost. The field sums all token types (cache reads + writes + fresh) without decomposition. Sub-agent per-turn cache breakdown isn't in session JSONL — only main session assistant messages carry `cache_read_input_tokens`/`cache_creation_input_tokens`.
- Correct pattern: Use main session first-turn `cache_creation_input_tokens` to measure system prompt size (~43K tokens p50). Use minimal-work agents (≤3 tool uses) for fixed overhead proxy. For actual $ cost with cache breakdown, use litellm proxy with SQLite spend logging.
- Evidence: 709 Task calls analyzed. Minimal-work agents: 35.7K total_tokens p50. Main session cache hit rate: 94-100% after warmup. No cross-agent caching signal in token-per-tool-use ratios (median 1.09).
## When adding a new variant to an enumerated system
- Anti-pattern: Updating only the authoritative definition section (type table, contract) but not downstream sections that enumerate existing variants. Leaves binary tdd/general language in 8+ locations across 3 skills.
- Correct pattern: After updating the authoritative definition, grep all affected files for existing variant names (e.g., "tdd.*general", "both TDD and general") and update every enumeration site. Skill-reviewer catches these as propagation gaps.
- Evidence: Skill-reviewer found 1 critical (Phase 0.75 outline generation wouldn't produce inline phases), 3 major (description triggering, When to Use, Phase 1 expansion branch missing), 4 minor enumeration sites — all in runbook/SKILL.md alone.
## When comparing file versions across branches
- Anti-pattern: Using `wc -l` equality to conclude files are identical. Same line count does not mean same content — entries can be added/removed/replaced while maintaining count.
- Correct pattern: Diff content, not counts. `git diff <base>..<branch> -- <file>` or compare actual text. Line count is a size metric, not an identity check.
- Evidence: Learnings.md had 62 lines on both merge base and branch → concluded "no changes." Post-merge found 36 genuine new entries from the branch.
## When compressing session tasks
- Anti-pattern: Reducing task descriptions to one-liners during session compression. Contextual notes (insights inputs, scope expansions, discussion conclusions, domain boundaries) exist only in session task notes — plan artifacts (requirements.md, design.md) don't contain them.
- Correct pattern: Before compressing, classify each sub-item: (a) duplicates plan artifact content → safe to trim, (b) contextual-only (insights, scope decisions, validation approaches) → must preserve. Only trim category (a).
- Evidence: Compression at `0418cedb` lost detail from 12 tasks. Recovery required `git show` against pre-compression commit. Handoff CLI lost domain boundaries + learnings flow + gitmoji validation; orchestrate evolution lost ping-pong TDD agent pattern; 7 backlog tasks reduced to stubs.
## When CLI command fails and raw commands are denied
- Anti-pattern: Decomposing a failed CLI tool into its constituent git commands for diagnostics. Each raw command is denied, but the denial is parsed as a permission obstacle rather than a routing signal. Variants feel novel ("different command, different purpose") but are the same class: raw git in a project that denies them.
- Correct pattern: After CLI failure, retry with escalated flags (`--force`) before attempting raw commands. If `--force` isn't available, check `--help` for diagnostic subcommands. The deny list is a routing signal, not a permission obstacle — it means "use the wrapper."
- Evidence: 7 denied `git worktree`/`git branch` commands before using `claudeutils _worktree rm --force`, which succeeded immediately. The `--force` flag existed for exactly this broken-state scenario.
## When Edit tool reports success but changes don't persist
- Anti-pattern: Trusting Edit tool "success" confirmation after Bash has modified the file. The tool reports success but the write doesn't persist — silently dropped.
- Correct pattern: Use Write tool for files that need guaranteed writes, especially after Bash commands (sed, git mv) have touched the file in the same session. Also: git mv and sed on tracked files require `dangerouslyDisableSandbox: true`.
- Evidence: Multiple Edit calls returned "success" on cli.py but cat confirmed no changes. Write tool succeeded on first attempt.
## When editing skill files
- Anti-pattern: Modifying skill `description` frontmatter without loading the platform skill guide first. Wrote action-first descriptions for 17 skills, then had to revert all 17 — `git checkout HEAD -- path/` would have been one command.
- Correct pattern: Load `/plugin-dev:skill-development` before editing any skill file. The guide mandates "This skill should be used when..." (third-person with trigger phrases). `.claude/rules/skill-development.md` references the skill but doesn't inline the constraint. The H1 heading (not `description`) is what Claude Code displays in the skill picker — fix generic `<Name> Skill` titles there.
- Evidence: 17 description edits + 17 reverts in same session. User noted git would have been cheaper.