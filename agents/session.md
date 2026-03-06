# Session Handoff: 2026-03-06

**Status:** Plugin exploration complete. All 28 internal plugins installed and analyzed.

## Completed This Session

**Plugin repo mapping (prior session):**
- Repo `anthropics/claude-plugins-official` has 29 internal plugins (28 real + example-plugin) and 13 external plugins
- Internal: agent-sdk-dev, clangd-lsp, claude-code-setup, claude-md-management, code-review, code-simplifier, commit-commands, csharp-lsp, explanatory-output-style, feature-dev, frontend-design, gopls-lsp, hookify, jdtls-lsp, kotlin-lsp, learning-output-style, lua-lsp, php-lsp, playground, plugin-dev, pr-review-toolkit, pyright-lsp, ralph-loop, rust-analyzer-lsp, security-guidance, skill-creator, swift-lsp, typescript-lsp
- External: asana, context7, firebase, github, gitlab, greptile, laravel-boost, linear, playwright, serena, slack, stripe, supabase

**Plugin installation (post server migration):**
- Reinstalled all 28 internal plugins at project scope (prior user-scope installs lost to migration)
- Re-enabled hookify and feature-dev (were disabled)
- Confirmed `superpowers` absent from official repo — not available

**Safety/security plugin exploration:**
- security-guidance: PreToolUse hook with 8 web/JS patterns (eval, innerHTML, GitHub Actions injection, pickle, os.system). Session-scoped dedup, blocks first occurrence.
- hookify: Declarative rule engine via `.local.md` files. Events: bash/file/stop/prompt. Actions: warn/block. Ships 4 examples.
- code-review: 5 parallel Sonnet agents for PR review with confidence scoring (>=80 threshold). GitHub-integrated.
- feature-dev: 7-phase interactive dev workflow with 3 agents (explorer/architect/reviewer). Interactive paradigm vs our autonomous pipeline.

**Overlap analysis:** Complementary, not redundant. Official plugins cover web-specific security patterns; our pipeline covers LLM-specific behavioral safety (S-1 through S-6, C-1 through C-3). Full report: `plans/reports/anthropic-plugin-exploration.md`

**Technique extraction (discussion):**
- False positive exclusion list for vet/corrector (from code-review confidence scoring pattern)
- Skill description optimization loop (from skill-creator eval framework)
- Brief written to `plans/active-recall/brief.md` — plugin report as Phase 6 extraction pipeline test target

## In-tree Tasks

- [x] **Explore Anthropic plugins** — Install remaining 16 plugins, explore code-review/security-guidance/feature-dev/superpowers for safety+security relevance, map against custom pipeline | sonnet | restart

## Worktree Tasks

- [ ] **Vet false positives** — Add "do NOT flag" taxonomy to vet/corrector agent prompts: pre-existing issues, OUT-scope items, pattern-consistent style, linter-catchable. From code-review plugin confidence scoring pattern. | sonnet
- [ ] **Skill description evals** — Adopt skill-creator eval loop for skill descriptions: generate trigger/non-trigger queries, 60/40 train/test split, measure triggering accuracy, iterate. Scripts in skill-creator plugin. | sonnet

## Blockers / Gotchas

- LSP plugins (11 of 28) require language server binaries installed on system — will show errors if binary missing
- `superpowers` plugin confirmed absent from official repo

## Reference Files

- `plans/reports/anthropic-plugin-exploration.md` — Full exploration report with overlap analysis
- `plans/reports/safety-review-grounding.md` — Prior safety framework grounding (on main)

## Next Steps

Branch work complete.
