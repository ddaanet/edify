# 2026-08-14 — Decision records folded into one living design doc

The 23 files under `agents/decisions/` (~286KB) were folded into
`docs/design.md` and deleted. The fold triaged three ways: design rationale
moved into the design doc, live agent rules already covered by `CLAUDE.md` or
`memory/ddaanet/` were not duplicated, and content describing torn-down
subsystems was dropped rather than carried across.

Dropped subjects were verified absent from the tree first — the `analyze` and
`rules` CLI commands and `filtering.py`, the worktree CLI and its `session.md`
merge machinery, the memory-index validator and resolver, the retired autoformat
and recall-check hooks, and the CLAUDE.md fragment-ordering scheme.

The document follows the six-section format: functional requirements,
non-functional requirements, architecture, decisions, rejected alternatives,
changelog — with the resume affordances the project's living-design format adds
on top (status stamp, Now, status legend, and the split between limitations and
non-goals).
