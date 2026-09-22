# 2026-09-17 — `/inline` and `/orchestrate` merge into `/build`; continuation passing retires

One execution skill now takes whatever planning produced — a proofed
`runbook.md`, a `design.md` or `outline.md` with no runbook, or a task from its
own invocation — and runs one lifecycle over all of them. `/inline` and
`/orchestrate` are deleted.

The split had partitioned on whether a runbook existed, and it charged for that
twice. Two skills carrying one lifecycle drifted: three different definitions of
a clean tree between them, so a run that wrote a memory file tripped the entry
gate on a state the post-item gate was documented to tolerate; and two
descriptions of the same reviewer's tool list, both wrong, each in its own way.
`plugin-dev:skill-reviewer` holds Read, Grep and Glob, and both skills told it
to fix issues and write a report — it can do neither, so every skill-definition
review silently produced nothing and the structural-proof Read then blocked on
the missing file. The seam also invited the belief that simple work needs a
different *skill* rather than a lighter path through one. `/build` is a lean
hub: the once-firing steps — phase boundary, finishing the job — are opt-in
reference nodes, so a session in the middle of a multi-session run loads only
what it hits.

The phase type `inline` goes with it. It meant "the executor does this one
itself", which is a decision a planner takes a stage too early; `/build` decides
delegation per item at dispatch time, by the batching rule. Types are now `tdd`
and `general`. `inline-plan.md` is removed as an artifact kind rather than
renamed — it was an `outline.md` with the architecture section empty, named
after its consumer — which collapses `/design`'s Simple and agentic-prose
branches into one route producing an `outline.md`.

Continuation passing retires in the same pass. Skills chained through a
`[CONTINUATION: ...]` suffix with tail-calls and a frontmatter `cooperative:`
declaration; the machinery over-compensated for agents that could not chain
unaided, which is no longer the failure mode. `/design` and `/runbook` now name
the next command and stop, and `plugin/fragments/continuation-passing.md` is
deleted. Its successor — handoff-and-continue, conditioned on context usage — is
a different mechanism and is not preserved as an extension point here.
