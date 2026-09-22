# 2026-08-10 — Sub-agent capability claims re-probed

Several long-standing claims about sub-agents were measured false. Sub-agents
have the `Skill` tool, receive `CLAUDE.md` and `memory/MEMORY.md` natively, and
can spawn sub-agents via `Agent`; there is no `Task` tool at any level (D-72).

The rule that execution agents never review their own work survived the
falsification, but as policy rather than capability limit — it holds *because*
an execution agent is now technically able to review its own work and must not
(D-28).
