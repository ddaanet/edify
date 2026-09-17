## Brief: deliverable-review produces findings and nothing owns consuming them

2026-09-17

Arrived from the `handoff` plugin repo, after working a two-layer
deliverable-review's fix list across several sessions.

### The gap

`skills/deliverable-review/SKILL.md` ends with:

> Report severity counts only. No merge-readiness language — the user reads
> severity counts and decides what to act on. The report is the deliverable; the
> skill does not queue follow-up work or record lifecycle state.

That boundary is defensible for the *review*. The consequence is that the
review's output is handed to a session with no guidance on working it, and two
failure modes follow reliably. Both are about the report's shape, so the fix
belongs in the design of the report rather than in a new skill.

### Failure 1 — the severity sort is the wrong working order

A report arrives sorted by severity, and that sort invites working Majors first
and sweeping Minors after. That re-enters the same function, docstring or
paragraph twice, re-derives the same context, and produces two commits where the
second is unreviewable without the first.

Findings that touch the same region belong in one pass regardless of tier.
Severity decides what gets **dropped** when the list is too long; it does not
decide the order of what stays.

Suggested: have the report carry a co-location grouping alongside the severity
grouping — the same findings indexed by file or region — or say plainly in the
report's closing section that severity is a triage axis and not a work order.

### Failure 2 — a two-layer review's counts are two scales spliced

Where a code reviewer and a prose reviewer each produce a list, the merged
"24 Minor" is two thresholds concatenated. The prose reviewer's bar for minor is
a sentence that could be tighter; the code reviewer's is a branch dead to the
suite. Nothing in the merged list announces that.

Reading the count as one population invites two errors: treating the whole tail
as cosmetic because most of it is, and estimating the pass from the total rather
than from the substantive subset.

Suggested: carry the reviewer of origin on each finding, and report counts per
reviewer as well as merged.

### Failure 3 — closure is finding-granular, defects are site-granular

A finding that names two places gets one fix pass, one commit message naming the
finding, and one status line reading closed — while one of the two places is
still open. The residual leaves no trace in any of those artifacts, because
every closure signal in the workflow is emitted per finding.

Observed twice in one job: a finding about a tagged union's unknown-key handling
was closed at the action-object level with the payload level still open, and
recorded as done until a later audit reopened it; a sibling finding about an
emptiness predicate had the same shape from the other direction, with a second
route found later and deliberately attached to the same finding so the eventual
pass could not close one and leave its twin.

Suggested: have a finding that names N sites say so structurally — a site list
the fix pass can be checked against — so that closing it is N checks rather than
one judgement. This is the piece that most clearly feeds back into the report's
design rather than into a consumer's discipline.

### Additional context

A related hazard, stated so a consumer does not rediscover it: a fix-status
audit, a plan, a changelog entry and a commit message are all write-time records
— true when written and never revised as the code moves past them. That is what
makes them evidence of reasoning at the time, and it is why none of them answers
"is this finding open now". In the job above, an audit file still read one
finding as "open (residual)" and its sibling as "deferred" hours after both
landed. The file was not wrong; it was not about now.

No change is proposed to the `handoff` repo, and nothing here asks
`deliverable-review` to take on lifecycle state — only to shape the report so a
consumer can work it without inferring the shape.
