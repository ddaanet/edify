# Classification: design-routing-and-provenance

Two items, both surfaced by **explicit bundling** — the task frame's
`Remaining` section folds both into this `/design` invocation.

## Item A — collapse the execution-readiness gate

- **Classification:** Moderate
- **Implementation certainty:** High — the two gate copies are located
  (`references/write-outline.md` §Outline Sufficiency Gate,
  `references/write-design.md` §C.5) and the collapse target is a shared
  reference node. No architectural alternatives in play.
- **Requirement stability:** High — scope is the gate text and its inbound
  references; the decision it encodes (`/runbook` or `/build`) is unchanged.
- **Behavioral code check:** No. Agentic prose only; no functions, logic paths
  or conditional branches.
- **Work type:** Production — delivers a corrected procedure that agents follow.
- **Artifact destination:** agentic-prose (`plugin/skills/design/`), with
  investigation-destination edits to `docs/design.md` and `docs/changelog.md`.
- **Evidence:** Moderate rather than Simple on file count — five files, not
  one. `feedback-stale-claims-survive-reference-sweeps` supplies the core
  finding: the `/build` merge repointed this gate's *references* without
  re-deriving its *claims*, so "scope fits single-session capacity" survived
  as text and is now contradicted by `plugin/skills/build/SKILL.md` §5.

## Item B — record the deliverable-review and initial commit base

- **Classification:** Moderate
- **Implementation certainty:** High — a new section in the artefact contract,
  with one inheritance rule (a second-pass artefact copies the prior base
  rather than taking a fresh `HEAD`).
- **Requirement stability:** High — the consumer is named and its current
  behaviour verified (`plugin/skills/deliverable-review/SKILL.md:31`
  establishes the review range "known from context or asked of the user").
- **Behavioral code check:** No. Prose contract change.
- **Work type:** Production.
- **Artifact destination:** agentic-prose (`plugin/skills/design/`,
  `plugin/skills/deliverable-review/`, `plugin/agents/`).
- **Evidence:** `design-content-rules.md` §References already occupies the
  "backward-looking provenance" slot but holds a reading list; a git ref that
  a later command substitutes into `git diff` is a different kind of value.

## Routing

Both items are Moderate with destination agentic-prose, so both take the same
route: outline → `/proof` → commit → `/build`. They batch into one
`outline.md` — they change the same skill's artefact contract and their edits
land in overlapping files.
