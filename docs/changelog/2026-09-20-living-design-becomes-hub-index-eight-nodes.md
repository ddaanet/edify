# 2026-09-20 — the living design becomes a hub, an index and eight nodes

`docs/design.md` had reached 1234 lines against a 400-line cap, carried on the
line-limit allowlist with the note "a split is due". Trimming could not close
that gap: past a few percent it starts removing the argument that stops a
settled decision from being re-litigated, which is the document's job.

The cut follows the seam that already existed, the `## Decisions` heading.
Everything above it — what the system is and how it is built, read while
building or debugging one component — stays in the hub. Everything below is the
argument index, read whole when weighing or adding a decision, and it moved:
`docs/decisions.md` carries one conclusion line per decision and every rejected
alternative by name, grouped by the node that argues it, and `docs/references/`
holds eight nodes carrying the arguments — `cli-and-package`, `testing`,
`pipeline-contracts`, `execution-routing`, `agent-instructions`,
`quality-gates`, `deliverable-review`, `project-configuration`. Node boundaries
are need-time: what a reader needs while changing one thing. §6.6 and §6.9
merged into one node because model choice and instruction structure are read
together and neither was cited from outside; every other node is one former
subsection. Rejected alternatives moved to the node whose decisions they
protect, under that node's own heading.

Nothing was renumbered and nothing was cut: the 112 identifier definitions
before the split are the 112 after, and the only tokens that left the moved text
are four `§7`/`§5.3` cross-references that became paths, with two more repointed
in the retained hub. The hub is 288 lines, the index 175, the largest node 224.
`docs/design.md` left the allowlist.

What the split does not buy on its own is the read: nothing in Claude Code loads
a node, so the hub's opening states the shape and `CLAUDE.md` carries a routing
table from what an agent touches to the node it reads first. Whether an
always-on instruction reliably causes that read is unestablished; the routing
table is the part with the best chance, because it matches the path the agent is
already looking at.
