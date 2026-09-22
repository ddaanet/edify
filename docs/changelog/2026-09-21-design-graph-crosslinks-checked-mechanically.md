# 2026-09-21 — the design graph's crosslinks are checked mechanically

Splitting `docs/design.md` into a hub, an index and eight nodes made two
invariants hand-breakable: a `D-<n>` with no index line, and an index conclusion
drifting from its node's. `scripts/check_design_links.sh` pins both, plus
`Argued in` resolution, in the root `justfile` only — a consuming project has no
`docs/decisions.md`. The hub stays unpinned: its conclusions carry no ID.
