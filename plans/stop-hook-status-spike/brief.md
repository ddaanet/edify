# Brief: Stop hook status display

## 2026-03-13: Spike results

Spike tested Stop hook `systemMessage` for displaying `_status` output directly to user without agent mediation.

**Findings (all positive):**
- `systemMessage` works on Stop hooks — user sees output in terminal
- Multi-line ANSI-colored output renders cleanly
- Leading newline + ANSI reset (`\033[0m`) escapes the dim "Stop says:" styling
- Colors tested: bold green (Next), cyan (command), dim (metadata), yellow (bullet), bold yellow (Restart)

**Mechanism:** Agent outputs trigger string ("Status.") as last line → Stop hook detects via `grep` on `last_assistant_message` → hook runs `edify _status` → returns `systemMessage` with output → user sees it directly.

**Production integration:** Deferred to status CLI implementation (Phase 2 of handoff-cli-tool). Hook script prototype in `tmp/spike-stop-hook/`.

**Open question:** `block` + `systemMessage` interaction untested — would enable auto-continuation after status display.
