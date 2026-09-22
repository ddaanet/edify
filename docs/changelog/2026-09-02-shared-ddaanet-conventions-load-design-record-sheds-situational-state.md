# 2026-09-02 — Shared ddaanet conventions load in every session; the design record sheds situational state

`CLAUDE.md` now imports `@memory/ddaanet/shared-claude.md`. That file declares
itself the always-in-context tier for every repo mounting the `ddaanet` memory
store — the scope between a repo's own conventions and `~/.claude/CLAUDE.md` —
but edify had never wired the import, so its standing defaults reached no
session here.

L-5 is retired rather than corrected. It recorded that `memory/MEMORY.md`
exceeded the loader cutoff, with a byte figure that went stale within days. A
measurement of a store that changes on every memory write is situational state,
not a design limitation, and neither the size nor the "the index is truncated"
claim belongs in a present-tense design record; the retirement pass it called
for is `/gitlore:index-audit`. Limitation IDs are referenceable, so the gap
stands rather than renumbering L-6.
