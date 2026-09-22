# Classification — proof verdict prompt

**Requirements-clarity gate**

- **Requirements source:** user request (project todo item, my human partner's
  wording)
- **Completeness:** each FR has a concrete mechanism — Y (propose a verdict in
  prose with its reason; show the amended item on a proposed revision; read the
  verdict from a free-form reply; one clarifying question on ambiguity). Each
  NFR has a measurable criterion — Y (forced verdict per item survives;
  accumulate-then-apply-as-batch survives; all four verdicts stay expressible;
  `SKILL.md` stays under its 200-line cap after the 80-column reflow).
- **Routing:** proceed to triage.

**Classification block**

- **Classification:** Simple
- **Implementation certainty:** High — a prose rewrite of one section of a skill
  body plus its reference file. No new mechanism; the replacement form is the
  one `docs/references/agent-instructions.md` D-78 already specifies for
  elicitation.
- **Requirement stability:** High — the change and its invariants are stated in
  the request; scope is the `proof` skill and the docs that describe it.
- **Behavioral code check:** No. No functions, no logic paths, no conditional
  branches — markdown prose under `plugin/skills/` only.
- **Work type:** Production — it changes how the `/proof` gate elicits
  dispositions from my human partner.
- **Artifact destination:** agentic-prose (`plugin/skills/proof/`), with an
  investigation tail in `docs/` (changelog entry, one design-node paragraph).
- **Evidence:** both triage axes high and no behavioral code puts this at
  Simple; the artifact-destination table puts `plugin/skills/` at agentic-prose,
  which routes identically. Recall surfaced `memory/line-caps.md` (the 200-line
  `SKILL.md` cap is a hard gate; never satisfy it by shaving prose) and
  `memory/style-edit-briefs.md` (a load-bearing em-dash survives an edit pass).
  Design nodes read: `agent-instructions.md` D-61/D-62/D-78,
  `quality-gates.md` D-48/D-50/D-52/D-53.

**Author-corrector coupling**

Author change: `proof`'s verdict prompt. Coupled corrector: none — `/proof` is
itself the T3/T6 gate that follows a corrector, and no corrector reviews the
`proof` skill body. Update needed: no.
