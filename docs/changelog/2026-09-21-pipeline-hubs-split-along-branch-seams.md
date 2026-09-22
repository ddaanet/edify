# 2026-09-21 — the pipeline hubs split along branch seams

`/build`, `/design` and `/requirements` were the three `SKILL.md` files still
carried on `scripts/check_line_limits.allow` with the note "no job yet" — 218,
277 and 354 lines against the 200-line hub cap (NFR-1, D-69). All three are now
under it and off the allowlist, along with
`docs/superpowers/design/plugin-transition-evaluation.md`, which was trimmed of
the four directives it evaluated that have since been executed.

The split rule that produced them, which is not the obvious one: the cost being
managed is the *number of extra Reads a single run makes*, not the number of
files. A skill is cut one node per **branch**, never one node per topic — a
branch that is not taken costs nothing, whereas a topic split makes one path
open three files in sequence. Where a body no longer fits under the cap even
after the conditional branches are extracted, the remainder goes into a single
node read once at its earliest point of need, rather than into several read at
each. Every pointer states the condition under which its node is read, so the
node is neither opened speculatively nor skipped when it is required.

What that produced:

- **`/build`** — the error branch became `references/escalation.md`, absorbing
  `references/resuming.md`: post-item remediation, the two-level escalation
  model's cases, and resumption after a kill are one branch and now one Read.
  The trailing References recap went, since every node is already named inline
  with its trigger.
- **`/design`** — triage became `references/triage.md`: the two axes, the work
  type and artifact-destination tables, multi-item decomposition and the
  classification gate. A resumed `design.md` or `outline.md` never classifies,
  so those paths now read nothing they do not use; a fresh job pays one Read for
  all of it. Routing stayed in the body, so no route gained a Read.
- **`/requirements`** — `references/elicit-mode.md` is the branch; the extract
  path never opens it. `references/formats-and-exit.md` is the single node the
  cap forced: the recall artifact, the gap-fill question template, the
  `requirements.md` format, the skill-dependency table and the exit routing, all
  read once at the recall pass, which is the first of them to be needed.

Reads per run are unchanged or lower on every path except the two the cap
forced: a fresh `/design` job and any `/requirements` run each pay one more.
