## 2026-03-14: Tmux verification mechanism unresolved — blocks Phase 1 execution

**Gap:** Steps 1.3, 2.4, 6.1, and 6.3 all reference "standard tmux interaction" / "same tmux verification mechanism as Step 1.3" for validating plugin loading inside a live Claude session. This mechanism was flagged as an unresolved design dependency during runbook outline /proof (and again during corrector review). The designated resolution point was "pre-Phase-1 spike or during Phase 1 expansion" — neither occurred.

**What's missing:** Step 1.3 has skeleton tmux commands (new-window, send-keys, capture-pane) but doesn't specify:
- How to send commands to the Claude session interactively (e.g., how to type `/help` into the running claude process via tmux)
- How to parse/verify structured output from capture-pane
- How to handle the Claude process startup delay reliably

**Required before Phase 1 execution:** Design the spike. Options:
- Pre-Phase-1 spike step that validates the tmux approach works and documents the interaction pattern
- Or accept manual validation for checkpoints 1.3, 2.4, 6.1, 6.3 (human runs and eyeballs output) and simplify step instructions accordingly

**If proceeding without redesign:** Steps 1.3, 2.4, 6.1, 6.3 are manual verification checkpoints — the agent runs the tmux commands, captures output, and reports to orchestrator for human judgment. The "STOP and report" instruction already in those steps is consistent with this.
