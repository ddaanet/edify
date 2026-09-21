# Brief triage — four inbox briefs against the current tree

2026-09-21. Read-only triage. Every classification rests on text quoted from the
tree at the paths named; where a brief's premise could not be checked from this
repository it says so.

## Two constraints that shape the classifications

`mechanical` means **no design fork** — clearly correct, small, reversible. It
does not mean one file: this repo couples a behaviour change to
`docs/design.md`, its `docs/references/` node, a `docs/decisions.md` line and a
`docs/changelog.md` entry (project `CLAUDE.md`, "Design Decisions"). Every
mechanical item carries that documentation cost on top of the edit named.

**No agent definition reads a fragment.**
`grep -rn "plugin/fragments" plugin/agents/*.md` returns nothing, and the only
pointers at `plugin/fragments/delegation.md` are `design-content-rules.md:187`,
`build/SKILL.md:218` and `dispatch-composition.md:90` — all read by the
*dispatcher*, never by the child. A rule a dispatched agent must obey has to
live in that agent's own definition.

---

## Brief A — `brief-cite-line-context-not-line-numbers.md`

| # | Proposal | Classification |
|---|---|---|
| A1 | `/design`'s outline guidance states the citation convention | needs-design (F-5) |
| A2 | Tighten `/runbook`'s bullet to the stable form only | **mechanical** (M1) |
| A3 | Frozen dated artifacts keep line numbers | already-done in effect |

### Verification

- **`/design` states no convention** — confirmed. A grep for `path:line`,
  `file:line`, `line number` and `enclosing symbol` across
  `plugin/skills/design/` returns nothing. `write-outline.md:154` specifies the
  outline's contents as "provenance, approach, key decisions, open questions,
  scope boundaries" and says nothing about how it points at code.
- **The `/runbook` bullet survived the `/build` rewrite** — confirmed at
  `plugin/skills/runbook/SKILL.md:99`, verbatim:
  "**Code-fix items enumerate affected call sites** (file:function or
  file:line)." The brief cites it as `:103`; it is now `:99` — its own citation
  rotted between filing and triage, which is the argument it was making.
- **A third emitter the brief did not name** —
  `plugin/fragments/token-economy.md:3`: "**Do NOT repeat file contents** - Give
  file references (path:line or path) instead". A general prose rule, so a more
  likely source of imitation than `/runbook`.
- **`runbook-corrector` needs no edit** — `:143` reads "**Code fix specificity**
  — Items targeting code enumerate affected call sites", with no form named. It
  enforces the enumeration without licensing `file:line`.
- **The exception holds, but incompletely** — review reports do carry
  `file:line` Location fields (`corrector.md:459,469,477,485`,
  `review/SKILL.md:105,114,123`, `deliverable-review/SKILL.md:118,142`). Under
  the brief's own exception those are write-time records and correctly keep
  numbers. But a deliverable-review finding is *consumed* by a later fix pass
  and routed to `/design` (D-60), i.e. read after the code may have moved. The
  brief does not address that case.
- **The claude-plugin-dev evidence** (`toolkit/release.sh:254` citing
  `:780-785`, the two `version-guard-test.sh` citations) —
  **could not confirm**; another repository, out of scope here.
- **Independent corroboration inside this repo** —
  `plans/provenance-reach-and-sweep/reports/deliverable-review.md:155-172` lists
  five stale reference sites found by a whole-tree sweep, including
  `tdd-slice.md:4`, `delegation.md:33`, `runbook/SKILL.md:78` and
  `review/SKILL.md:207`. Three of the five are `path:line` into live prose.

---

## Brief B — `brief-corrector-scope-and-escalation-resume.md`

| # | Proposal | Classification |
|---|---|---|
| B1 | Corrector fixes against runbook-level detail when the design supports it | **mechanical** (M2) |
| B2 | After an escalation, resume the reviewer that raised it | needs-design (F-6) |
| B3 | No new `/build` path for a "checkpoint fix" | already-done, nothing to remove |
| B4 | Mutation predictions are a lower bound ("at least this row") | **moot as stated** → F-2 |

### Verification

- **The taxonomy gap is real** — `plugin/agents/corrector.md:47` gives U-ARCH as
  "Fix would violate an architectural invariant or conflict with a documented
  design decision" and `:48` gives U-DESIGN as "Multiple valid approaches exist
  and the choice has non-trivial downstream consequences". Neither distinguishes
  the design record from the runbook's own wording.
- **One half is already right** — the investigation gate at `corrector.md:77`
  reads "2. Design deferral: not found in design.md", naming the design record
  and not the runbook. The gate already points at the right artifact; only the
  taxonomy prose is silent. That makes B1 a wording fix, not a mechanism change.
  D-27 ("Reviewers fix everything and escalate the rest",
  `docs/decisions.md:62`) already supports the direction.
- **The escalation path ends at the escalation** — `phase-boundary.md:19`:
  "UNFIXABLE → STOP and escalate." Nothing says what happens after my human
  partner decides. The *mechanism* exists: `dispatch-composition.md:81`
  ("Resumption is `SendMessage` to that name") and the phase reviewer is named
  `phase-P-corrector`. `build/SKILL.md:145-149` already resumes a named agent,
  but only for mechanical remediation.
- **B2 is a fork, not a mechanical edit** — the brief reports it as my human
  partner's own call in another repository's session, which cannot be verified
  against its own source from here, and it adds a step to the escalation
  contract (D-40, escalation has three tiers).
- **B4's target does not exist.** `grep -cin "mutation\|mutate"` returns **0**
  for `runbook/SKILL.md`, `runbook-format.md` and `runbook-corrector.md`.
  edify's runbook format has no gate field and no mutation prediction: a tdd
  item carries `Slices:` with test names and stated assertions
  (`runbook-format.md:32-48`) and nothing else. So B4 is not a wording
  tightening — it proposes **introducing** a mutation-gate field. The only
  mutation mechanism in the tree is `corrector.md:418-422`, an
  "**(optional, once)**" mutated-SUT run in the code review, and its wording is
  already lower-bound-shaped: "Report whether every test redded; a test that
  stayed green detects absence but not wrongness." It makes no per-row
  prediction, so the failure B4 describes cannot arise from edify's own text.

---

## Brief C — `brief-orchestrate-context-cost-and-tdd-process.md`

| # | Proposal | Classification |
|---|---|---|
| C-A | Phase-boundary split as the scheduled path | needs-design (F-3) |
| C-C | Move the standing dispatch preamble into `delegation.md` | needs-design (F-7); premise false |
| C-D | A machine-shaped verdict head on corrector reports | needs-design (F-4) |
| C-E | Delegate RED/GREEN roll-up, never corrector reports | prohibition already-done; rest F-10 |
| C-2.1 | A gate verdict in every GREEN report | **mechanical** (M3); mtime does not map |
| C-2.2 | GREEN lists every test file that *sources* the script | belongs-elsewhere (bats-shaped) |
| C-2.3 | Mutation proof in an independent review | already-done; optional→required is F-2 |
| C-2.4 | No skipped per-slice reviews for a "small" item | **mechanical** (M4), = D1 |
| C-2.5 | A superseded review fix still commits its report | **mechanical** (M5) |
| C-2.6 | A committed `reports/phase-N-gate.md` | artifact F-11; gate recap **mechanical** (M6) |
| C-3a | "One commit per slice" vs "the report cites that commit" | **verified defect** → F-1 |
| C-3b | Resolve a runbook's `file:NNN` before dispatch | half is M1; rest F-8 |
| C-x | `$TMPDIR`-unset mutation incidents | guards **mechanical** (M7); script needs-design |

### Verification

- **C-A: `resuming.md` is still recovery-framed** — 13 lines, titled "Resuming
  After a Context Ceiling or a Kill", and `phase-boundary.md:19` ends "Otherwise
  commit and continue" with no handoff or clear. The nearest existing decision
  is D-25 ("Planning and execution run in different sessions"), which does not
  cover splitting *within* execution.
- **C-A's figures are not grounded for edify.** 35–55%, and 15–24M billed
  against 84M, are gitlore's replay of its own measured series, with category
  attribution self-declared at ±15%. Nothing here measures edify. The
  *mechanism* — a block added at call k is re-sent on every later call, so cost
  grows with the square of session length — is a property of the API, not of
  gitlore, and needs no re-measuring. The savings do.
- **C-C's precondition is false.** `plugin/fragments/delegation.md` is read by
  no dispatched agent (see the constraint above), so moving the standing
  preamble there moves it where no child reads it. `dispatch-composition.md:14`
  already says "Context by path, never by content" and `:26-28` already carries
  the commit-nothing overrides — the duplication the brief measured is between
  the *prompt* and text the child never sees.
- **C-D: the gap is real** — `corrector.md:437-450` opens the report with
  `## Summary` "[2-3 sentence overview]" plus "**Overall Assessment**: [Ready /
  Needs Minor Changes / Needs Significant Changes]". Prose; no files-changed
  list, no reported-not-applied list, no list-revision suggestions. The head
  buys token economy and not correctness: the blocking check is a grep
  (`review-requirement.md:212`, "Use `rg` (Bash) to search for `UNFIXABLE`"),
  which works without a head. The brief's own stated risk — a head that omits a
  finding — is a silent-summariser failure moved earlier.
- **C-E: the prohibition is already the tree's shape** — the orchestrator reads
  corrector reports itself at `finishing.md:40-43` and `build/SKILL.md:145`, and
  nothing delegates roll-up. The verification claim holds: a GREEN report's
  commit hash is required at `test-driver.md:70`, so counts plus a hash are
  checkable against `git log`.
- **Incidental verified defect** — `finishing.md:68` tells `tdd-auditor` to use
  "the session's `subagents/` transcripts as fallback where a report is
  missing". Reading a subagent transcript is forbidden by the shared convention
  (full JSONL, overflows the window); the documented remedy is to resume the
  named agent for its report (`dispatch-composition.md:81`). → M8.
- **C-2.1: gap confirmed, mechanism wrong.** `test-driver.md:56` runs
  `just precommit`, `:58-60` sends its warnings to the report, `:68-72` lists
  the report's contents — commit hash, tests run, the order they passed. No gate
  verdict. But the brief prescribes "gate path, mtime, and the input it
  postdates", and edify's sentinel is content-hash based: `justfile:150`
  `local sentinel="tmp/.test-sentinel"`, `:158` compares `"$(cat "$sentinel")"`
  to `$current_hash` by string equality. There is no mtime to cite.
- **C-2.3 is already structurally satisfied** — RED is `edify:test-driver`, the
  mutation run is in the code review by `edify:corrector`
  (`corrector.md:418-422`), and D-28 already forbids an execution agent
  reviewing its own work. The residual is only that the run is "(optional,
  once)".
- **C-2.6: no such artifact** — `phase-boundary.md` has no `phase-N-gate.md`.
  Separately, `verify-step.sh:31` prints a bare `echo "CLEAN"`, which the shared
  convention already condemns ("A quiet gate signs off with the list of checks
  that passed — never a bare 'OK' or 'Green'").
- **C-3a is a live defect, sharper than the brief states.** Both strings are
  present: `tdd-slice.md:28` "commits once per slice" and `:29` "The GREEN
  report names the slice commit's hash". `test-driver.md:61-72` resolves the
  ordering — commit at step 5, report written at step 6 — so the report is
  **not** in the slice commit. Nothing then commits it: `tdd-slice.md:39-42`
  covers only the code review's fixes, `:52-55` only the `runbook.md` edits.
  `build/SKILL.md:131-139` then runs `verify-step.sh` after every GREEN, and
  that script tolerates only ` M memory` (`verify-step.sh:9`) — so the untracked
  GREEN report yields `DIRTY`, exit 1, and the §4.4 remediation path fires after
  **every** GREEN dispatch. A guaranteed spurious remediation loop, not a
  documentary ambiguity.
- **C-3b** — `runbook-format.md` names tests by test name and targets by path
  only; no `:NNN` appears in the format or its example. The one place licensing
  `file:line` is `runbook/SKILL.md:99`, i.e. M1. The resolve-before-dispatch
  half is absent from `dispatch-composition.md` and adds a step per dispatch.
- **C-x** — `corrector.md:418-422` says "save the SUT, mutate it in place ...
  restore" with no dirty-target refusal and no post-restore verification. The
  file carries no `tmp/`-versus-`/tmp/` rule either (`grep -in "tmp\|TMPDIR"`
  hits only report paths at `:434` and `:594`), while `test-driver.md:95` does.

---

## Brief D — `brief-orchestrate-delegated-run-findings.md`

| # | Proposal | Classification |
|---|---|---|
| D1 | A skipped dispatch leaves an artifact | **mechanical** (M4), = C-2.4 |
| D2 | A GREEN report even for a test-only slice | **mechanical** (M9) |
| D3 | "Fixtures tried and rejected" as a RED heading | **mechanical** (M10) |
| D4 | A mechanism-claim probe in the code-review prompt | needs-design (F-9) |
| D5 | A sweep's gate defeats the shared refusal mechanism | needs-design (F-2), with B4 |
| D-o1 | A first-class orchestrator agent holding `Agent` | needs-design (F-7) |
| D-o2 | One opus delegate ≈ one heavy phase | field evidence for C-A (F-3) |
| D-o3 | Non-ordinary reds have no named form | needs-design (F-12) |
| D-o4 | Nothing forbids `git stash` / `reset` / blanket `add` | **mechanical** (M11) |
| D-o5 | "Stop on anything needing a decision" conflates two | needs-design, with F-3 |

### Verification

- **D1: the precedent is where the brief says.** `build/SKILL.md:172-183` —
  `Write(plans/<job>/reports/review-skip.md)`, required to state "what changed,
  why review adds no value for this specific change, and what verification was
  performed instead", and "**Skip is not confidence-gated:**". Verbatim.
  `tdd-slice.md` (all 55 lines read) has **no** skip provision for dispatch (b)
  or (d).
- **D2: the assumption is where the brief says.** `tdd-slice.md:24-29` — "(c)
  GREEN ... Makes the tests pass one at a time ... carrying tests and
  implementation together"; `test-driver.md:52-54` — "Pick one failing test,
  implement the minimal growth that passes it". Both presuppose an
  implementation. Two existing rules argue against the orchestrator executing
  such a slice itself: D-28 ("execution agents never review their own work") and
  `build/SKILL.md:113` ("Review is **not** the executor's judgement").
- **D3: confirmed present and confirmed incomplete.** `test-driver.md:37-38` —
  "**A test that passes has named itself vacuous.** Report it as such; do not
  delete or weaken it — the test review decides." Nothing asks for the discarded
  attempt: `grep -in "reject\|discard\|attempt"` over `test-driver.md` hits only
  `:81` ("after 2 implementation attempts"). Note the asymmetry — the *reviewer*
  already holds the vacuous-red taxonomy (`corrector.md:395-409`: "A bare
  negative", "A fallback supplying the rule's answer", "An isolation fixture
  with nothing to leak", "Fixture unreachable from the write path") while the
  author is told only to report a passing test.
- **D4: confirmed absent.** `review-dispatch-template.md:33-38` review criteria
  and `corrector.md:413-425` code-review criteria carry no probe instruction.
  The brief's own constraint bites here: the 5:1 comment-to-code ratio is a
  property of a shell deliverable, and edify's deliverable is almost entirely
  prose, so the ratio is plausibly worse — but that is an inference,
  **ungrounded** either way.
- **D5: same absent target as B4.** No mutation gate exists in the runbook
  format (count 0, verified twice). `corrector.md:418-419` already aims the
  optional run at "the plausible-but-forbidden implementation the slice exists
  to rule out", close to the shared-mechanism idea, but no N-scenario sweep
  concept exists anywhere.
- **D-o1: confirmed.** `grep -n "^tools:" plugin/agents/*.md` — not one of the
  eleven definitions lists `Agent`. The skill has it (`build/SKILL.md:8`
  `allowed-tools: Agent, ...`), so the orchestrating layer is whichever session
  invokes the skill. The proposed frontmatter form
  `tools: Agent(edify:test-driver, …)` — a parenthesised per-agent restriction —
  **could not confirm**; no example exists in this tree.
- **D-o3: confirmed, and a hard stop today.** `test-driver.md:33` requires
  "every test fails on its assertion — a wrong value or an absent raise, never
  `ImportError` or `AttributeError`"; `tdd-slice.md:13` repeats it; and
  `tdd-slice.md:20-21` makes it the test review's mechanical first check ("every
  listed test FAILED on an assertion — none PASSED, none ERROR"). A slice that
  cannot take an ordinary red has no legal form and fails that check.
- **D-o4: confirmed absent.**
  `grep -rn "git stash\|git reset\|git add -A\|git add \."` over `plugin/`
  returns nothing.
- **D-o5: confirmed.** `build/SKILL.md:185-204` lists escalation triggers and
  routes a context ceiling to `resuming.md`, but nothing tells a delegate how to
  distinguish a genuine fork from a self-describing ceiling handoff.

---

## Overlaps

**Between the briefs.** D1 and C-2.4 are the same edit. C-A, D-o2 and D-o5 are
one design question. B4 and D5 are one design question. B1 and C-D both touch
the corrector's contract. C-3b and A2 are the same edit.

**With the pending jobs.**

- **(a) sweep exit conditions / review scoping.** D1/C-2.4 is the same shape one
  rung down: a skip artifact *is* an exit-condition record. And
  `plans/provenance-reach-and-sweep/reports/deliverable-review.md:155-172`
  already found five stale reference sites by a whole-tree sweep, three of them
  `path:line` into live prose — brief A's convention would have prevented those
  three. Design A1 with (a).
- **(b) scoping a TDD GREEN dispatch in `tdd-slice.md`.** Four items land in
  that same 55-line file: D2 (test-only slices), D-o3 (non-ordinary reds), F-1
  (where the GREEN report is committed) and M4 (skip artifacts). One job;
  `tdd-slice.md` is the shared mutable file, so they cannot run in parallel.
- **(c) pilfer defect 21, corrector-family dedup.** The UNFIXABLE taxonomy is
  already duplicated — `corrector.md:44-48` and
  `review-requirement.md:203-205, 222` — and the report-head shape across
  `corrector.md:437-500`, `runbook-corrector.md:212` and
  `review/SKILL.md:105-123`. B1 (M2) and C-D (F-4) should ride the dedup job
  rather than precede it, or they get applied twice.
- **(d) `brief-review-feeds-back-into-design.md`.** C-D and (d) are both
  report-shape changes with the same consumer; (d)'s "reviewer of origin" and
  "site list per finding" belong in the same head C-D specifies. Brief A's
  exception also bears on (d): a finding's `file:line` Location is a write-time
  record that a later fix pass reads as if live, which is (d)'s third failure
  seen from the citation side.

---

## Mechanical edits ready to apply

Each is one clearly-correct reversible change with no design fork. The
documentation coupling named at the top applies to all of them.

- **M1** — `plugin/skills/runbook/SKILL.md:99`. Replace
  `(file:function or file:line)` with the stable form only: enclosing symbol
  plus a quoted distinctive fragment, and say why (a line number is invalidated
  by the edits the item itself prescribes). Closes A2 and half of C-3b.
- **M2** — `plugin/agents/corrector.md:47-48`. Say in U-ARCH that a documented
  design decision means `design.md` / `outline.md`, not the runbook's own
  wording, and that a fix against runbook-level detail the design supports is
  applied and reported as a deviation. Closes B1.
- **M3** — `plugin/agents/test-driver.md:68-72`, GREEN report contents. Require
  a gate verdict line. Do **not** copy the brief's "mtime" — cite
  `tmp/.test-sentinel`'s hash and the run that wrote it, per `justfile:150-169`.
- **M4** — `plugin/skills/build/references/tdd-slice.md`. Add a skip provision
  for dispatches (b) and (d), modelled on `build/SKILL.md:172-183`: an absent
  dispatch writes `plans/<job>/reports/item-N-M-s<k>-<test|code>-review-skip.md`
  stating what was in scope, why it is empty and what was verified instead; not
  confidence-gated. Closes D1 and C-2.4.
- **M5** — `tdd-slice.md`, "After the slice" step 1. A review fix superseded by
  a later one still commits its report, with a line saying so. Closes C-2.5.
- **M6** — `plugin/skills/build/scripts/verify-step.sh:31`. Replace
  `echo "CLEAN"` with a recap naming the checks that passed (clean tree,
  `just precommit`). Exit codes unchanged, so no call site changes.
- **M7** — `plugin/agents/corrector.md:418-422`. The mutated-SUT run gains two
  inline guards: refuse a target with uncommitted changes, and verify
  `git diff --quiet` after the restore. Add the missing `tmp/`-not-`/tmp/` rule,
  matching `test-driver.md:95`.
- **M8** — `plugin/skills/build/references/finishing.md:68`. Drop "the session's
  `subagents/` transcripts as fallback"; replace with resuming the named agent
  for its report (`dispatch-composition.md:81`).
- **M9** — `tdd-slice.md` §(c). Name the test-only slice: a slice whose
  production change is already in place still runs the GREEN dispatch and still
  writes its report with the gate result and the commit hash. Closes D2.
- **M10** — `plugin/agents/test-driver.md`, RED step 5. Require a report heading
  for fixtures tried and rejected, and why. Closes D3.
- **M11** — `plugin/agents/{artisan,test-driver,refactor,corrector}.md`, Tool
  Usage. Forbid `git stash`, `git reset` and blanket `git add`; stage named
  paths only. Four files, because no agent definition reads a fragment. Closes
  D-o4.

M4, M5 and M9 all edit `tdd-slice.md`; apply them in one pass, under job (b)'s
scope.

---

## Forks for my human partner

- **F-1 — where a slice's GREEN report is committed.** Not a documentary
  ambiguity: as written the report is untracked when `build/SKILL.md` §4.4 runs
  `verify-step.sh`, so the DIRTY remediation path fires after every GREEN
  dispatch. Either the report rides the slice commit and cites no sha, or it is
  its own commit by construction and `tdd-auditor` is told so. The second is the
  cheaper fix against `test-driver.md:61-72` as written.
- **F-2 — does a mutation gate enter the runbook format at all?** B4 and D5 both
  presuppose one and edify has none. Sub-questions: an N-scenario sweep
  defeating the shared refusal mechanism; "at least this row" lower-bound
  wording; whether `corrector.md:418`'s run stops being optional. The last has a
  cost per slice.
- **F-3 — is the phase-boundary split the scheduled path?** Bundles C-A, D-o2
  and D-o5. The quadratic re-send mechanism is an API property and needs no
  re-measuring; the 35–55% is gitlore's and is **ungrounded for edify**.
  Deciding it also gives the context-ceiling return a named form, which is what
  D-o5 wants.
- **F-4 — the corrector report's head.** Design with job (d) and after job (c)'s
  dedup, since the shape is duplicated across three files.
- **F-5 — where the citation convention lands in `/design`,** and whether it
  binds a review report's `Location` field. `design-content-rules.md` is the
  content-rules node. Design with job (a).
- **F-6 — resume the reviewer after a human decision on an UNFIXABLE.** Worth
  one line of confirmation first: brief B reports this as my human partner's own
  call in another repository's session, unverifiable from here.
- **F-7 — a first-class orchestrator agent.** Bundles D-o1 and C-C, since both
  turn on which text a dispatched child actually loads. The proposed
  `tools: Agent(...)` per-agent restriction syntax is unverified.
- **F-8 — resolve a runbook's `:NNN` to a name before composing a dispatch.**
  Adds a step per dispatch; largely pre-empted by M1.
- **F-9 — the mechanism-claim probe:** required per new claim, or reviewer
  judgement. Mandating it is unbounded work.
- **F-10 — delegated RED/GREEN roll-up.** The prohibition half is already the
  tree's shape; only the new dispatch is a decision.
- **F-11 — a committed `reports/phase-N-gate.md`.** Adds a commit per phase; the
  gate-output half is M6 and can land without it.
- **F-12 — a named form for a non-ordinary red.** Today such a slice fails
  `tdd-slice.md:20-21`'s mechanical first check. Blocked with job (b).

**Not carried forward:** C-2.2 (GREEN lists every test file that *sources* the
changed script) is bats-shaped; edify's suite is pytest and the brief names no
analogue. Brief C's items B and F were already withheld by its author.
