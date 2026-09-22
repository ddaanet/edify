# 2026-09-21 — `/proof` proposes a verdict instead of polling for one

Every item `/proof` presented ended with
`Verdict? (a)pprove (r)evise (k)ill (s)kip`. D-78 had already retired that shape
in its `AskUserQuestion` form across `review`, `requirements` and `formalize` —
an option list bounds what the user can say, which defeats elicitation — but the
enforcement was omission from `allowed-tools`, and an inline menu written in the
skill body is not a tool call, so `proof` kept the defect in the one skill whose
entire job is elicitation. The reply a four-letter menu invites is one
character; the gate wants a judgement.

The loop now reads the item, proposes the verdict it thinks the item deserves
with the reason for it, and on a proposed revision writes out the amended item
so the reply lands on concrete wording rather than on a request to produce some.
The disposition comes from the free-form reply: agreement takes the proposal,
any of the four verdicts is reachable however it is phrased, and a reply that
settles nothing costs **one** clarifying question — never a guessed verdict, and
never the next item until this one's verdict is recorded. A second unsettled
answer is discussion, not a third question, so the sub-loop absorbs it and ends
by proposing a verdict again.

Nothing the letter menu was carrying is lost. The forced verdict per item was
never the menu's doing — it is the rule that no item advances undisposed, and it
survives verbatim, with "never a guessed verdict" closing the hole a
conversational reply opens. Verdicts still accumulate in-memory and still apply
as one batch at the terminal action; no edit happens during iteration.

The reply-mapping detail lives in `proof/references/item-review.md` §Verdict
Capture rather than in the hub, which sits under its 200-line cap with nothing
to spare. That is a budget decision, not an importance one: the hub carries the
rule, the reference carries the cases.

`docs/design.md` FR-16 — validate an artifact item-by-item with forced verdicts
— is unchanged and still true. D-78's conclusion still names `AskUserQuestion`
alone, and the node now records the norm behind it by user ruling: plain
conversation is the default for every skill, with no position taken on
interaction mechanisms that do not exist yet.
