# A slice's reports ride the commit whose work they report

**Decision:** my human partner, 2026-09-21. Recorded as D-86. **Scope:** the
four per-slice reports, plus the refactor, phase-boundary and review-gate
reports. `verify-step.sh` unchanged; no test covers this prose.

## What the real run showed

`plans/provenance-enforcement-and-routing/` had already executed the expected
rule by hand. Commits, with their full stats:

- `78206a83` Item 1.2/1 — `item-1-2-s1-{red,test-review,green}.md`,
  `plugin/bin/edify-review-range.sh`, `tests/test_review_range.py`
- `c30b7bc1` Item 1.2/1 code-review fixes — `item-1-2-s1-code-review.md`,
  `edify-review-range.sh`
- `45ad1184` Item 1.2/3 — `item-1-2-s3-{red,test-review}.md`,
  `tests/test_review_range.py`
- `f8d1e254` Item 1.2/4-8 — `item-1-2-s4-8-{red,test-review}.md`,
  `tests/test_review_range.py`
- `542ff17c` Item 1.10/8 — `item-1-10-s8-{red,test-review,green}.md`,
  `scripts/check_line_limits.sh`, `tests/test_line_limits.py`
- `50c35d61` Item 1.10/8 code-review fixes — `item-1-10-s8-code-review.md`,
  `scripts/check_line_limits.sh`

Three things the evidence settles beyond the brief's expectation:

1. **The expectation is confirmed exactly.** Every GREEN commit carries the
   slice's RED, test-review and GREEN reports with the tests and the
   implementation; every code-review report rides its own commit with that
   review's fixes. No report was ever committed alone, and no report was left
   behind.
2. **Two slices have no GREEN report at all** — `1.2/3` and `1.2/4-8`, the
   mutation-proven ones with no implementation left to write. Their commits
   carry RED and test-review reports plus tests, and they carry no code-review
   report either. So "the commit that adds the GREEN report" cannot be the only
   identification rule: `tdd-auditor` would return `blocked` on two of six
   slices. The rule as written falls back to the RED report for such a slice.
   (Whether a GREEN dispatch should run at all for a test-only slice is
   brief-triage D2 and stays open — see Open, below.)
3. **The job-level review gate did the same thing** — `a3a5304e`, `c5f99281`,
   `eeb06722` and `2832c42a` each commit one review-gate report, `2832c42a` with
   its fixes. `finishing.md` §1 never said to; it is the same hole one level
   out.

The identification command was verified against a real report:

```console
$ git log --diff-filter=A --format=%H \
      -- plans/provenance-enforcement-and-routing/reports/item-1-2-s1-green.md
78206a83c3a486e4ebda440f5493dd47c4540d6e
```

One hash, the correct commit.

## The rule as written

**D-86 — A report rides the commit whose work it reports, and names no hash.**

- The GREEN commit carries the slice's RED, test-review and GREEN reports with
  the tests and the implementation. RED and the test review leave their reports
  uncommitted for it; the corrector commits nothing.
- The orchestrator's after-the-slice commit **always happens** and carries the
  code-review report, with that review's fixes where there are any. Previously
  it was conditional on the review having changed something, which is what left
  the report untracked.
- Same shape one level out: `edify:refactor` commits its report with its
  refactoring; the phase-boundary and review-gate commits carry their
  corrector's report.
- Every committing dispatch stages the paths it names. Never `git add -A` or
  `git add .`.
- A report inside a commit cannot contain that commit's hash, so it contains
  none. The commit is resolved from the one that **adds** the report:
  `git log --diff-filter=A --format=%H -- <report path>`. For a slice with no
  GREEN report, the same query over its RED report.

## Files changed

Nothing staged or committed. `just format && just precommit` green: 348/349
passed, 1 xfail; the design-links check reports 86 decisions indexed, defined
once, conclusions matching, 8 nodes present.

### `plugin/agents/test-driver.md` (136 lines)

GREEN steps 5 and 6 swapped so the report exists before the commit.

- old 5 → "Commit once for the slice … What identifies the slice commit is the
  hash you record in the report."
- new 5 → "**Write the report before committing** … Record **no commit hash**:
  the report rides the commit it would name, and the orchestrator and the audit
  identify that commit as the one that adds this file."
- new 6 → "Stage by name the slice's tests, the implementation, and this slice's
  RED, test-review and GREEN reports — the RED and the test review left theirs
  uncommitted for this commit to carry. Never `git add -A` or `git add .` …"
- RED step 6 old → "No commit — the uncommitted tests in the tree are the
  designed end state of this dispatch." new → "the uncommitted tests
  **and this report** are the designed end state of this dispatch; the slice's
  GREEN commit carries both."

### `plugin/skills/build/references/tdd-slice.md` (95 lines)

- §(a) old → "the tests stay uncommitted in the tree"; new → "the tests
  **and the report** stay uncommitted in the tree for the GREEN commit to
  carry".
- §(b) added → "The corrector commits nothing: its report joins the tests in the
  tree, and the GREEN commit carries it."
- §(c) old → "The GREEN report names the slice commit's hash." new → "The commit
  also carries the slice's three reports so far — RED, test review and GREEN —
  staged by name, never by a blanket add. So the GREEN report names no hash, and
  the slice commit is the commit that adds it:" followed by the fenced
  `git log --diff-filter=A` form. Fenced rather than inline so the 80-column
  reflow leaves the command intact.
- §After the slice 1 old → "**Commit the review fixes:** the corrector never
  commits. If (d) changed anything, commit it … Nothing to commit → go straight
  to verification." new → "**Commit the code review:** the corrector never
  commits, so this commit always happens … carrying (d)'s report and the fixes
  it applied, or the report alone where it changed nothing. Stage those paths by
  name. … a review whose report stayed uncommitted is what leaves that gate
  dirty."

### `plugin/agents/tdd-auditor.md` (219 lines)

- §Inputs old → "Each report names the commit it concerns." new → "No report
  names a commit hash — each rides the commit it concerns, so you identify that
  commit as the one that **adds** the report file."
- §Inputs git line old → "used only to confirm a commit a report names exists
  and to diff it: `git show`, `git diff`." new → "used only to resolve a report
  to its adding commit and to diff that commit: `git log --diff-filter=A`,
  `git show`, `git diff`."
- Check 2 old → "The GREEN report names exactly one commit … Identify the commit
  from the hash the GREEN report names." new → a fenced
  `git log --diff-filter=A` resolution, "More than one hash back, or none, is a
  violation", the RED-report fallback for a slice with no GREEN report, and
  "That commit carries the slice's tests, its implementation, and the slice's
  RED, test-review and GREEN reports … or a report of another slice riding
  along, is a violation."
- Check 2's two-commit paragraph kept true and made unconditional: old "That
  second one is expected wherever the code-review report accounts for it" → new
  "the orchestrator's commit of the code review — which always happens, since it
  carries the code-review report whether or not the review changed anything …
  and so is a code-review report that no commit adds."
- Check 4 old → "the refactor report names its own commit … Identify that commit
  from the refactor report." new → "Resolve it as the commit that adds
  `item-N-M-s<k>-refactor.md`."

### `plugin/skills/build/references/dispatch-composition.md` (105 lines)

- §Prompt contents 4 old → "a review dispatch commits nothing either — the
  orchestrator commits the fixes a corrector applied." new → "A committing
  dispatch stages the paths it names — its own report among them — and never
  `git add -A`. … the orchestrator commits the corrector's report, with the
  fixes it applied where there are any."
- §Prompt contents 5 added → "A report names no hash of the commit that carries
  it; whoever needs that commit resolves it with `git log --diff-filter=A` over
  the report's path."

This also closes, by reference, the gap `plans/skill-reviews/reports/`
`verify-orchestrate.md` M4 raised for a **general** item that is itself a
review: `build/SKILL.md` §4.2 routes such an item through this file, and §Prompt
contents 4 now states who commits the corrector's report.

### `plugin/skills/build/references/finishing.md` (78 lines)

- §1 added → "A corrector commits nothing, so commit each group's report
  yourself — with the fixes that reviewer applied where it applied any — staging
  those paths by name." Closes the job-level instance the real run performed
  without instruction.
- §3.2 old → "git serves only to confirm and diff the commit a report names."
  new → "git serves only to resolve a report to its adding commit and to diff
  that commit."

### `plugin/skills/build/references/phase-boundary.md` (24 lines)

old → "Otherwise commit and continue." new → "Otherwise commit and continue: the
corrector commits nothing, so that commit carries its report — with the fixes it
applied where there are any — and always happens."

### `plugin/agents/refactor.md` (222 lines)

Step 6 old → commit first, then "Name the commit hash in your report … that is
how the audit finds it", with `git add <the files you changed>`. new → "Write
your report first … then stage the files you changed together with it",
`git add <the files you changed> plans/<job>/reports/item-N-M-s<k>-refactor.md`,
and "Name **no commit hash** in the report — it rides the commit it would name,
and the audit finds that commit as the one that adds the report file."

### `plugin/skills/build/SKILL.md` (218 lines — unchanged count)

§4.4 old → "a slice's code review once its fixes are committed" new → "a slice's
code review once its commit lands". Shorter than the original, so the file stays
at its 218-line ceiling. No other edit; the file never stated the old contract.

### `docs/design.md` (344 lines, +5)

§5.3, two paragraphs:

- old → "after the per-slice code review the orchestrator commits the
  corrector's fixes … A slice's own commit is the implementer's, made in GREEN
  mode." new → "commits the corrector's report and whatever fixes it applied …
  That commit therefore always happens, even where the review changed nothing. A
  slice's own commit is the implementer's, made in GREEN mode, and it carries
  the slice's RED, test-review and GREEN reports along with the tests and the
  implementation (D-86)."
- old → "The auditor keys on the hash the GREEN report names … Git serves only
  to confirm the named commit exists and to diff it." new → "No report names a
  hash, since each rides the commit it would name; the auditor resolves a commit
  as the one that **adds** its report (`git log --diff-filter=A`). … Git serves
  only to resolve a report to its adding commit and to diff that commit."

### `docs/references/pipeline-contracts.md` (314 lines, +36)

D-86 added before §Rejected alternatives, in the bolded-lead shape: the rule,
the `git log --diff-filter=A` form fenced, the RED-report fallback under D-84,
the defect it settles, the six commits from the real run as grounding, the
rejected alternative (a commit of its own per report), and the accepted
tradeoffs (a `git log` per resolution; a report amended after its commit lands
needs a second commit that `--diff-filter=A` will not return).

### `docs/decisions.md` (181 lines, +2)

Index line under §Pipeline contracts:

```markdown
- **D-86** — A report rides the commit whose work it reports, and names no hash
  (the commit is resolved from `git log --diff-filter=A` over the report path).
```

The node conclusion "A report rides the commit whose work it reports, and names
no hash" is a prefix of it, as `check_design_links.sh` requires; the check now
reports 86 decisions.

### `.claude/handoff-todo.md`

The "Where a slice's GREEN report is committed (brief-triage F-1)" bullet
removed from §Open decisions.

### `docs/changelog.md` (400 lines — at cap, see Open)

The 2026-09-21 TDD-audit entry absorbed the new rule rather than taking a
heading of its own: both come from the same audit of the same run, and a
separate entry did not fit. Heading retitled "what the TDD audit changed:
slice-scoped GREEN, mutation proof, report commits", with a closing paragraph on
D-86. The sentence "Where a GREEN report is committed stays open and was
deliberately not touched here" was removed, being now false.

To free the lines, today's four 2026-09-21 entries were compressed — wording
only, no fact dropped: the crosslinks entry (a decision index → an index,
breakable by hand → hand-breakable, dropped "to match on"), the TDD entry's
first two paragraphs merged, the recall entry's first paragraph reordered so the
long inline code span breaks more cheaply, and the ruff entry's tail rephrased.
No entry dated earlier than 2026-09-21 was touched.

## Open

- **`docs/changelog.md` is now at exactly 400 of its 400-line cap.** It fits and
  the gate passes, but a file parked at its cap has stopped emitting the signal,
  and the per-date split already recorded in `.claude/handoff-todo.md`
  §Remaining ("split it per date before the next design-significant entry") is
  now overdue rather than upcoming. I did not split it — out of this task's
  scope.
- **A test-only slice's missing GREEN report** (brief-triage D2, and the reason
  D-86 needs a RED-report fallback). Two of the six audited slices produced no
  GREEN report and no code-review report at all. D-86 accommodates that rather
  than deciding it; whether a mutation-proven slice should still get a GREEN
  dispatch is still open.
- **Nothing mechanically checks the rule.** `verify-step.sh` catches the symptom
  — an uncommitted report leaves the tree dirty — one dispatch late, and only if
  it runs. There is no check that a commit adding a report also carries the work
  that report describes.
- **A report amended after its commit lands** resolves to its original adding
  commit, not the amendment. Recorded as an accepted tradeoff in D-86; no
  instance of it exists in the audited run.
