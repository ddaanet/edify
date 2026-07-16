## Temporary Files

**Use the harness scratchpad for throwaway files; use project-local `tmp/`
when a temp file should stay with the repo.**

- Claude Code provides a per-session scratchpad directory (its path is given
  in the system prompt, under `/tmp/claude-*/`). It is sandbox-writable and
  session-isolated — use it for intermediate results, scratch scripts, and
  work that does not belong in the project.
- Use project-local `<project-root>/tmp/` when a temp file needs to be
  inspectable within the repo or to outlive the session; it is gitignored.
- Do not scatter temp files into arbitrary system locations outside those
  two.
