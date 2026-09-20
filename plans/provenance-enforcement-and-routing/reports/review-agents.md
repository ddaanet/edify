# Review gate — agent definitions (Item 1.1)

Scope: `plugin/agents/outline-corrector.md`, `plugin/agents/design-corrector.md`,
whole files as shipped. Baseline `1f54633b8bf3425a2c3cbd30bc9482049c216522`;
content change `a11008a6`, reflow `f375c9d9`.

Requirements: M-1, M-2, M-3 via KD-1 and KD-4
(`plans/provenance-enforcement-and-routing/outline.md`).

**Verdict: no Critical, Major or Minor defects. No edits applied.**

## Checks

### KD-1 — the repair table

Exactly seven rows plus header and separator (lines 142–150 of
`outline-corrector.md`, 211–219 of `design-corrector.md`). Row-for-row match
against KD-1's table in the outline, wording included.

Three invariants present and complete: never write a `Base:` obtained any way
other than the verbatim copy (`git log`, `git merge-base`, `HEAD` all named as
recomputation); never overwrite a `Derived from:` that is present; every value a
`TODO` replaces is quoted in the report.

### Shared block byte-identical

Extracted `- **Repair by what you found**` through `quoted in the report.` from
both files and diffed: **identical**, no differences. The reflow wrapped the two
copies the same way — both blocks sit at the same two-space list-continuation
indent, so MD013 produced the same break points.

Worth recording: `a11008a6` shipped the invariant paragraph with a code span
split across lines (`` `git `` / `` log` ``), which would have rendered as
literal backticks. `f375c9d9`'s reflow moved `git log` onto one line and
repaired it. Not a defect in the shipped state.

### Detection bullets unchanged

Compared the four `Derived from:` / section bullets in each file against the
baseline blob. Identical content in both files; the only differences are line
breaks introduced by the reflow. The `design-corrector.md` bullets keep their
no-trailing-period house style, the `outline-corrector.md` ones keep theirs.

### Semantic consistency with the detection bullets

- "Naming only the report → Major" (bullet) against "`TODO` in `Base:` only;
  leave `Derived from:` as found" (table): consistent. The bullet sets severity,
  the table sets the repair; neither asks the agent to rewrite the
  `Derived from:` the bullet objects to. This is M-1's fix — the old
  "`TODO` placeholder in both fields" bullet is what wrote `TODO` over a correct
  `Derived from:`.
- "A recomputed base → Critical" (bullet) against "copy the prior `Base:`
  verbatim; report Critical if it differed" (table): consistent, and this is
  M-2 — the corrector now performs the verbatim copy it had already verified,
  while the Critical report survives.
- "Missing → Major" for an absent section against "add it, `TODO` in both
  fields": consistent, severity and repair are orthogonal.
- Row "`Derived from:` absent, `Base:` present" against invariant 2 ("never
  overwrite a `Derived from:` that is present"): no conflict, the row's
  precondition is absence.
- The `Critical Constraints` section of both files still carries "Never
  `git rev-parse HEAD` to supply a `Base:`" — consistent with invariant 1, and
  not contradicted by the verbatim-copy row (a copy is not a rev-parse).

### Every row is an Edit-reachable action

`add it`, `TODO` in one or both fields, and `copy the prior `Base:` verbatim`
are all `Edit` operations on the artifact; the copy's input needs `Read` of the
prior artifact and the reachability tests need `Bash`. Both agents grant
`Read`, `Write`, `Edit`, `Bash`, `Skill`. No row asks for a tool the agent
lacks.

### Third invariant's placement

Stated at the end of the repair block, in the Provenance criteria — i.e. where
the agent decides what it replaced, not in the report-format template. The
criterion permits "at least where the agent will meet it", and this is the point
at which the replaced value is still in hand; the report template's
`Fix: [What was changed]` field is where it lands. Accepted as-is; noted in case
a later dedup pass moves the block.

### KD-4 — the new outline-corrector criterion

`plugin/agents/outline-corrector.md:96-100`, last bullet under **Clarity:**.

- Heading fit: Clarity is the right home — the defect it names is
  underspecification ("specific enough that two executors would write the same
  test"), which is the same class as the neighbouring "Key decisions are
  explicit, not implicit". Feasibility was the plausible alternative; Clarity is
  at least as good and the bullet is the only one in its section that states a
  severity, which is how the file already marks a criterion that carries one.
- Severity: Major. Consistent with its neighbours' explicit severities —
  Cross-Component Interface Compatibility flags Major, Provenance flags Major
  for a missing section. A slice that cannot be dispatched RED is the same
  weight.
- Citation form: "Read `runbook-format.md` in the `runbook` skill's
  `references/` … and its §\"Assertion quality\"". Bare filename plus skill
  name, no repo-relative `plugin/…` path — the accepted form under the outline's
  cross-cutting rule. Verified the target exists and the heading is real:
  `plugin/skills/runbook/references/runbook-format.md:87` is
  `## Assertion quality (tdd items)`.

### Reflow damage

- Table rows untouched: all nine KD-1 lines are single physical lines in both
  files, and the three example tables in `outline-corrector.md` (lines 168–172,
  182–186, 252–256, 262–265) are intact. `tables` is off in `.rumdl.toml`.
- Split code spans: none. Every line in both files has an even number of
  backticks (fenced-code markers excluded). The `rg -n '\*\*$|`$'` sweep
  returned 105 hits across the two files; each was judged and every one is a
  *closing* marker — bold section labels (`**Tool Usage:**`), fence lines, or a
  line ending in a closed code span (`… only route to `Base:``). No opening
  marker sits at end of line.
- Split bold markers: none. Every line has an even number of `**` runs.

### Frontmatter and agent-definition criteria (`plugin-dev:agent-development`)

- `name`: `outline-corrector`, `design-corrector` — lowercase-hyphen, in range,
  alphanumeric ends. Valid.
- `model`: `opus` in both. Not `inherit`, which the skill recommends by default;
  deliberate here under the repo's dispatch rule (reviewer one rung above the
  implementer). No finding.
- `color`: `cyan` / `magenta` — distinct, and cyan-for-review matches the
  skill's guidance.
- `tools`: exactly the five each body uses. `Skill` is used by both for the
  `edify:recall` call; `Bash` for `git merge-base` and `rg --files`; `Write` for
  the review report. Least-privilege satisfied, nothing granted unused.
- System prompt: second person throughout, role / responsibilities / process /
  output format / edge cases all present in both.
- `description`: both use the repo's block-scalar "Triggering examples:" shape
  rather than the skill's prose "Typical triggers include …" plus a
  "When to invoke" body section. **Observation, not a finding, and not fixed** —
  it is the convention across the whole corrector family (`corrector.md`,
  `runbook-corrector.md`, `tdd-auditor.md` alike), it predates the baseline,
  Item 1.1 does not touch it, and converting two of four would fragment the
  family. Belongs with pilfer defect 21 (corrector-family dedup) if it is taken
  up at all.

### Line counts

450 (`outline-corrector.md`) and 460 (`design-corrector.md`), both over the
400-line soft cap. Both allowlisted at exactly those ceilings in
`scripts/check_line_limits.allow:18-19` against "pilfer defect 21
(corrector-family dedup)". Reported, not shrunk, per instruction. Note the
ceilings are exact: any further growth of either file turns the gate red, which
is KD-7's stated design.

### Formatter

```
rumdl fmt --check -q --no-cache plugin/agents/outline-corrector.md plugin/agents/design-corrector.md
→ exit 0
```

## git diff --stat

Against the baseline, for the two files in scope:

```
 plugin/agents/design-corrector.md  | 154 ++++++++++++++++++++++++++-----------
 plugin/agents/outline-corrector.md | 114 +++++++++++++++++++--------
 2 files changed, 192 insertions(+), 76 deletions(-)
```

The bulk of that churn is `f375c9d9`'s 80-column reflow. The content change
(`git diff a11008a6^ a11008a6`) is 34 insertions and 2 deletions across the two
files.

No working-tree changes were made by this review, so `git diff --stat` for the
two files is empty.
