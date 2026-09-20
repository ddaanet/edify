## Brief: orchestrate context cost, and TDD process gaps two audits found

2026-09-18

Arrived from the `gitlore` plugin repo, which ran `/edify:orchestrate` over two
runbooks (`index-edit-propagation`, `tier-arrival-review-minors`), measured the
orchestrator sessions' context, and had `edify:tdd-auditor` audit both. This
note ends gitlore's involvement; nothing is tracked there.

**Anchor drift.** Everything below was observed against the *installed* plugin,
whose execution skill is `orchestrate`. This repo's tree now carries
`plugin/skills/build/` instead; the sections named map to `SKILL.md` §4.5 and
`references/{phase-boundary,resuming,dispatch-composition,tdd-slice}.md`.
Sections are named, not line-numbered. Check each item against the current
tree before acting — some may already be settled.

### Part 1 — context cost of an orchestrator session

Source: `/Users/david/code/gitlore/plans/2026-09-10-orchestrate-context-analysis.md`
(439 lines; method, per-category shares and the falsified hypotheses are there).
Context size per API call is exact (`message.usage`); attribution to categories
is modelled, ±15%. The flagship session billed 84,268,347 input tokens, peaking
at 419,100; 98% of that was cache reads, so the *monetary* ranking differs from
the token ranking and no price multiplier was applied.

- **A. Split the run across sessions at phase boundaries — 35–55%.** The
  dominant cost is no category: a block added at call *k* is re-sent on every
  later call, so cost grows with the square of session length. Replaying the
  measured series with a 20K-token re-prime per session: 2 sessions −35%,
  3 −48%, 4 −55%. Phase-sized sessions measured 15–24M billed against 84M for
  one that ran three phases. The resume-after-ceiling procedure is a *recovery*
  path; the change is to make it the *scheduled* path at the phase boundary,
  after the checkpoint commit — hand off, clear, resume. Split only there, so
  no in-flight slice is lost.
- **C. Move the standing dispatch preamble out of the prompt — ~1.9%.** ~15% of
  prompt characters repeat across dispatches: working directory, `CLAUDE.md`
  paths, "Commit nothing", recall-artifact path. Extend "Context by path, never
  by content" to them via `plugin/fragments/delegation.md`. Keep behavioural
  *overrides* of the agent's own definition ("Commit nothing") in the prompt if
  there is any doubt the fragment is read.
- **D. A specified verdict head on corrector reports — up to ~10%.** Corrector
  reports are 69% of report bytes. Make the opening a complete, machine-shaped
  head — verdict, files changed, findings reported-not-applied with section
  pointers, list-revision suggestions — so the orchestrator reads ~1KB and
  pages into one section. Risk, stated plainly: a head that omits a finding is
  a silent summariser failure moved earlier. The head must *point at* sections,
  never replace them.
- **E. Delegate RED/GREEN roll-up; never corrector-report reading — ~2–3%.**
  RED and GREEN reports are 189KB of 747KB and carry per-test output the
  orchestrator does not act on. Pass/fail counts plus a commit hash are
  verifiable against `git log` and a re-run, so a bad summary is detectable. A
  corrector summary is not.

Not forwarded: **B** (re-reading reports the formatter rewraps) is caused by
gitlore's own `just format-docs` wrap set; **F** lists things measured and not
worth doing — precommit output (1.3% of peak), agent return messages (0.8%),
trimming the base prompt from inside the skill. "Dispatch prompts prepared in
files, referenced by path" was **falsified** as stated; do not re-propose it
without reading that section.

### Part 2 — process rules the audits asked for

Sources: `plans/index-edit-propagation/reports/tdd-audit.md` and
`plans/tier-arrival-review-minors/reports/tdd-audit.md` under
`/Users/david/code/gitlore/`.

1. **A gate verdict in every GREEN report** — gate path, mtime, and the input
   it postdates. Eleven of nineteen slices in one run had no auditable evidence
   the suite was green at commit.
2. **GREEN reports list every test file that sources the changed script**, not
   a grep for changed strings.
3. **A guard's mutation proof runs in an independent test review.** The author
   proving their own guard is weaker evidence, even when a corrector repeats it.
4. **No skipped per-slice reviews for a "small" item.** The one item run
   without them shipped a Major test regression to the checkpoint. If the
   orchestrator substitutes its own check, it writes that down as a report file.
5. **One slice per commit**; a superseded review fix still commits its report,
   with a line saying so.
6. **A committed `reports/phase-N-gate.md`** at each phase boundary holding the
   gate's recap line, the tip sha and the gate mtimes, so "green at phase
   boundary" is audited rather than asserted in a handoff.

### Part 3 — two contradictions in the dispatch contract

- **A report cannot cite its own commit.** "One commit per slice, report
  included" plus "cite the commit sha in the report" is impossible.
  `references/tdd-slice.md` still says both: "commits once per slice" and "The
  GREEN report names the slice commit's hash". Executors resolve it with an
  extra commit, a parent sha, or an amend loop, and the auditor reads each as a
  defect. The dispatch decides: the report rides the slice commit and cites no
  sha, or it is its own commit by construction **and `tdd-auditor` is told so**.
- **A runbook's `file:NNN` goes stale once an earlier phase edits the file.**
  Runbooks name tests by `@test` name and code by function; the orchestrator
  resolves any `:NNN` to a name against the current tree before composing a
  dispatch. Belongs in `/runbook`'s item rules and in dispatch composition.

### Constraints

- A recurring incident worth a design look, offered without a recommendation:
  five reviews ran mutations with `$TMPDIR` unset (unmutated run read as a
  mutant, stacked mutants, a backup written to `/`). Each recovered by
  `git checkout --`, safe only because the subject had no uncommitted edits.
  The audit suggested a mutate-and-run script that refuses a dirty target and
  verifies an empty `git diff` afterwards.
- A brief's recommendation is input, not a decision. The savings figures are
  one repository's sessions.
