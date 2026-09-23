# Brief triage — my human partner's calls

2026-09-23. Closes the triage in `brief-triage.md`. Item ids are that report's.
Every mechanical item below is applied in the tree; the jobs named are on
`.claude/handoff-todo.md`.

## Applied

- **M1** was already in the decided form: enclosing symbol, a quoted fragment
  only where the symbol holds more than one site. `deliverable-review/SKILL.md`
  now asks for the same form in findings, since a fix pass reads them later.
- **M3** — the GREEN report carries the gate verdict: the precommit recap line
  and the `tmp/.test-sentinel` hash.
- **M10** — the RED report carries a `Fixtures tried and rejected` heading;
  `None` is a valid entry.
- **F-1** was already settled by D-86 before this triage was read: the report
  rides the slice commit and names no hash.
- **F-6** — after a decision on an UNFIXABLE with no design impact, the
  orchestrator applies or delegates the fix and resumes `phase-P-corrector`
  to review it; recorded in `phase-boundary.md`.
- The hub sentence still naming `subagents/` transcripts as the missing-report
  fallback (M8's defect) is rewritten.
- Three fragments read by nothing — `claude-config-layout.md`,
  `execution-routing.md`, `workflows-terminology.md` — are deleted.

## Routed to a job

- **tdd-slice job** — M4 (skip artifacts for dispatches (b) and (d)), M5 (a
  superseded review fix still commits its report), M9 (test-only slice: the
  orchestrator runs the gate and commits inline and writes the same report;
  the record is what matters, not the dispatch), F-12 (a named form for a red
  taken under a stated mutation, with what the RED report shows and the test
  review checks).
- **git-hygiene hooks job** — M11 as agent-scoped `PreToolUse` deny hooks on
  the executors, following `prohibitions`' shape (deny with a recovery
  message), plus one prose line; `prohibitions` already covers whole-tree
  `git add`. Confirm the agent-frontmatter `hooks:` field with one
  `claude-code-guide` query first. The corrector copy rides defect 21.
- **defect 21** — M2, M7, F-4 (a machine-shaped report head, merged with the
  feeds-back-into-design brief's grouping), the corrector half of M11.
- **context-triggered handoff job** — F-3 reframed: not a phase-boundary rule
  but a harness script reading the session transcript's last `usage` at each
  dispatch return, routing to the handoff plugin's clear-and-resume past 150k
  (soft, or when the next phase is non-trivial) or 200k (hard). The brief's
  percentage is gitlore's and stays ungrounded here.
- **sweep-exit-condition job** — F-5, where the citation convention lands in
  `/design`.

## Dropped

- **F-2** no mutation-gate field in the runbook format; the corrector's
  mutation run stays optional judgement.
- **F-7** a first-class orchestrator agent buys only a bounded tool list over
  a general-purpose agent loading `edify:build`; C-C with it.
- **F-8** pre-empted by M1. **F-9** reviewer judgement, no mandated probe.
  **F-10** a short report head does what a roll-up dispatch would.
  **F-11** a report-only commit; the gate recap goes in the phase corrector's
  report, which the boundary already commits.

The four briefs stay in `inbox/` until the jobs that read them are done.
