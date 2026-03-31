## 2026-03-18: Tmux verification mechanism — RESOLVED

**Resolution:** `claude -p` headless mode replaces tmux-based TUI interaction for plugin verification.

**Spike result:** `claude -p "list your available slash commands" --plugin-dir ./plugin` from a clean directory (no `.claude/`) returns all plugin skills. The `-p` flag runs non-interactively, bypasses Ink TUI entirely, outputs plain text. No tmux send-keys, no ANSI parsing, no readiness polling needed.

**Verification mechanism (applied to Steps 1.3, 6.1, 6.3):**
- **Skills (FR-1):** `claude -p "list your available slash commands" --plugin-dir ./plugin`
- **Agents (FR-1, FR-8):** `claude -p "list your available agents" --plugin-dir ./plugin`
- **Hooks (FR-1):** `claude -p "write test to /tmp/x" --plugin-dir ./plugin` — triggers `pretooluse-block-tmp.sh`
- **Clean-room test:** Run from `tmp/plugin-verify/` (no `.claude/`) to confirm `--plugin-dir` is the sole discovery path
- **Coexistence (FR-8):** Run from project root (has `.claude/agents/handoff-cli-tool-*.md`) to verify both sources
- **NFR-1 (dev reload):** Manual — edit skill, re-run check, confirm change visible. Only remaining manual step.

**Step 2.4:** Absorbed into Step 2.3 during /proof. Was a phase-boundary STOP, not a tmux issue.

**Prior art reviewed:**
- pchalasani/claude-code-tools (`tmux-cli`): execution marker pattern (`echo START; cmd; echo END:$?`) for reliable tmux output capture
- nielsgroen/claude-tmux: pattern-based readiness detection on `capture-pane` output
- ccbot: JSONL transcript file polling (avoids terminal scraping entirely)
- libtmux + pyte: Python tmux control with ANSI terminal emulation

These are available if tmux-based verification is ever needed (e.g., for interactive multi-turn test scenarios). For plugin loading verification, `-p` mode is sufficient and simpler.
