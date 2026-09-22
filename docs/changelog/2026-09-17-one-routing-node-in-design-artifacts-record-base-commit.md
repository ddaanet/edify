# 2026-09-17 — one routing node in `/design`; artifacts record their base commit

`/design` stated the execution-routing decision twice — once in
`write-outline.md`'s Outline Sufficiency Gate, once in `write-design.md`'s C.5 —
and the copies had drifted. Wording differed; the prose branch's hard-gate
qualifier existed in only one; and, substantively, one copy exempted the prose
path from the readiness criteria while the other bound it. The two copies routed
differently on the same input, which is what a second copy costs.
`references/route-to-execution.md` now states the decision once, under a name
that says what it decides: **does this work need a runbook?**, not whether the
session can execute it. "Execution readiness" and "direct execution" are retired
from `/design` with the branch they named; `/build` §4.1 keeps the second phrase
for a different thing, inline rather than delegated dispatch. Single-session
capacity was a criterion on both copies and contradicted `/build` §5, which
provides for a run spanning several sessions — the residue of the retired
in-session execution path, true only while the design session did the work. The
surviving criteria split in two, because the flat list was hiding that:
preconditions, which bind every branch including prose and send a failure back
to *design*; and runbook discriminators, which send it to `/runbook`. The
Exploration branch drops its "and design resolved all questions" conjunct — read
literally it bounced every spike back to design, since a spike exists to answer
a question.

Separately, every `/design` artifact now carries a `## Provenance` section
naming the review it derives from and the commit its deliverable starts at
(D-80). `/edify:deliverable-review` built its range from context or by asking,
so a second design-to-deliverable pass reviewed only the fixes — the original
base was gone from context by then, and nothing in the narrowed review looked
wrong. The inheritance rule is the whole mechanism: a second-pass artifact
copies `Base:` from the artifact it supersedes and never recomputes it. The
correctors enforce it after the fact and are barred from supplying a base
themselves, since a computed one is the recomputation. The same change makes
that consumer take `design.md` *or* `outline.md`, whichever exists; it had named
`design.md` alone, so nothing from the agentic-prose route — which produces only
an outline — was reviewable at all.
