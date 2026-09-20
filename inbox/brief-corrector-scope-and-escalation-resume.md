## Brief: corrector scope against runbook detail, and resuming the reviewer after an escalation

2026-09-19

Arrived from the `handoff` plugin repo, which ran `/edify:orchestrate` (installed
plugin 0.2.0) over `plans/2026-09-18-directive-owns-the-procedure/runbook.md`.
This note ends handoff's involvement; nothing is tracked there. Sections are
named, not line-numbered; check each point against the current tree (the
execution skill may now be `build/`) before acting.

### Decisions

- **A corrector should fix against runbook-level detail when the design
  supports the fix.** An `Interfaces:` line or a test-hook literal the planner
  wrote is implementation detail, not a documented design decision. The
  corrector applies the fix and reports it as a deviation, so the orchestrator
  records a list revision in the runbook. It escalates (UNFIXABLE) only when the
  fix conflicts with the design itself (`design.md` / `outline.md`).
- **After an escalation, resume the reviewer that raised it.** Once my human
  partner decides, the orchestrator `SendMessage`s the decision to the same named
  corrector, which applies the fix inside its own scope. The orchestrator does
  not apply the fix itself, and does not widen the next phase reviewer's scope
  to cover it: phase scoping is context management.
- **No new orchestrate path.** Escalate → human decides → resume the reviewer
  is enough; my human partner resists adding a named "checkpoint fix" path,
  which the tdd-auditor had recommended.
- **Runbook mutation predictions are a lower bound.** Write "this mutation reds
  at least this row", not "this row alone reds". Twice in one run the exact
  claim was wrong, because a pre-existing row sat in the same predicate cell or
  an earlier branch returned before the mutated line was read; each time the
  executor had to correct the runbook in place.

### Constraints

- The corrector's UNFIXABLE taxonomy (`agents/corrector.md`, "UNFIXABLE
  Subcategory Codes") has U-ARCH "conflict with a documented design decision"
  and U-DESIGN "multiple valid approaches". Nothing there distinguishes the
  design record from the runbook's own wording, so a corrector gives both the
  same weight.
- The "at least" wording belongs wherever runbooks are authored and reviewed
  (runbook skill, `runbook-corrector`), not only in the executor.

### Rejected approaches

- Widening the next phase-boundary corrector's scope to cover a fix made
  between phases: it breaks phase scoping, which exists to bound context.
- The orchestrator applying an approved fix inline, tests first and
  self-reviewed. This is what the run did; nobody but the orchestrator
  reviewed the commit.

### Additional context

The case: the Phase 3 corrector found that the closing line the checkpoint
prints ("End on one line: `Ready to /compact`.") could be appended to a reply
still asking for memory approval. It marked this out of scope because the
runbook's `Interfaces:` said `closing_directive` "opens with `End on one line`".
Its report: "changing it is a spec decision, not a correction." It offered two
options, so the finding also looked like U-DESIGN. The outline said only that both producers print "an
instruction to end the reply on the named line", and it already reworded a
sibling instruction to "refer to everything printed above it" for the same
reason. So the fix ("Once everything above is done, end on one line: …")
was design-consistent, and the second option (let the skill text or the
dogfood run cover it) was not a real alternative. Sources in the handoff repo:
`plans/2026-09-18-directive-owns-the-procedure/reports/phase-3-corrector.md`
("Observations for the orchestrator"), `reports/tdd-audit.md`
("Recommendations"), and the runbook's blockquotes under Items 2.1 and 3.1.
