# Session Handoff: 2026-03-04

**Status:** Plugin inventory complete; installation pending.

## Completed This Session

**Plugin repo mapping:**
- Repo `anthropics/claude-plugins-official` has 29 internal plugins (28 real + example-plugin) and 13 external plugins
- Internal: agent-sdk-dev, clangd-lsp, claude-code-setup, claude-md-management, code-review, code-simplifier, commit-commands, csharp-lsp, explanatory-output-style, feature-dev, frontend-design, gopls-lsp, hookify, jdtls-lsp, kotlin-lsp, learning-output-style, lua-lsp, php-lsp, playground, plugin-dev, pr-review-toolkit, pyright-lsp, ralph-loop, rust-analyzer-lsp, security-guidance, skill-creator, swift-lsp, typescript-lsp
- External: asana, context7, firebase, github, gitlab, greptile, laravel-boost, linear, playwright, serena, slack, stripe, supabase

**Already installed (14 plugins):**
- User scope: pyright-lsp, plugin-dev, superpowers, ralph-loop, pr-review-toolkit, claude-md-management, claude-code-setup, code-simplifier, context7
- Project scope (pytest-md): code-review, commit-commands, explanatory-output-style, feature-dev, hookify

**Remaining to install (16 internal):**
- agent-sdk-dev, clangd-lsp, csharp-lsp, frontend-design, gopls-lsp, jdtls-lsp, kotlin-lsp, learning-output-style, lua-lsp, php-lsp, playground, rust-analyzer-lsp, security-guidance, skill-creator, swift-lsp, typescript-lsp

**Installation mechanism:** `claude plugin install <name>@claude-plugins-official` (CLI) or `/plugin install <name>@claude-plugins-official` (interactive)

## In-tree Tasks

- [ ] **Explore Anthropic plugins** — Install remaining 16 plugins, explore code-review/security-guidance/feature-dev/superpowers for safety+security relevance, map against custom pipeline | sonnet | restart
  - Install command: `claude plugin install <name>@claude-plugins-official`
  - Focus: safety/security relevance per original task context
  - Overlap analysis started in prior session — see `plans/reports/safety-review-grounding.md` on main

## Blockers / Gotchas

- LSP plugins (11 of 28) require language server binaries installed on system — will show errors if binary missing
- "superpowers" plugin is installed but not listed in current repo — may have been renamed or removed
- Some plugins installed at project scope (pytest-md) — not active in this project

## Next Steps

Install remaining 16 plugins, then explore safety-relevant plugin content (code-review, security-guidance, feature-dev, superpowers).
