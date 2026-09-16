# plugin-dev:skill-reviewer on plugin/skills/review (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 to 4 pending.**

Files read: `SKILL.md`, `references/review-axes.md`, `references/example-execution.md`,
`references/common-scenarios.md`, and `fragments/review-requirement.md` (the only
fragment the skill routes through).

Measured (`wc`): `SKILL.md` 207 lines / 818 words; `review-axes.md` 65 / 371;
`common-scenarios.md` 27 / 154; `example-execution.md` 52 / 143. Description: 8 words.

## Critical

**C1. The skill mandates a tool the project forbids.** SKILL.md:20 says "Use
AskUserQuestion tool:" and :184 restates it as sanctioned. The always-loaded
`memory/ddaanet/shared-claude.md:22` says never to call it, and that file is imported
into the project CLAUDE.md, so it loads in every session where this skill fires. The
skill's own worked example already does the right thing:
`example-execution.md:5-11` asks in plain numbered prose. Fix: rewrite SKILL.md:18-32
as a numbered plain-prose question with a stated default, and reword :184.

**C2. The tool contract is self-contradictory and the stated constraint breaks a
mandatory review axis.** SKILL.md:4 grants Read and Bash only; :170 states "Bash for
git commands only, Read for examining files, Write for review output". So `Write` is
named as the output mechanism (also at :158) but absent from `allowed-tools`, and
worse, `review-axes.md:34` and `:36` require ripgrep through Bash to verify runbook
file paths and test function names, which :170 forbids. An agent obeying the
constraint silently skips the Runbook File References axis, whose own :35 calls
missing paths CRITICAL.

Severity mechanism: `allowed-tools` grants rather than restricts (per the
plugin-craft skill-authoring reference, verified against CC 2.1.250 docs), so the
missing `Write` entry costs a permission prompt, not a block. The blocking half is
the prose constraint at :170. Fix: add `Write` to the frontmatter and reword :170 to
permit read-only search commands alongside git.

## Major

**M3. The description carries no trigger clause, so the skill fires only on an
explicit slash invocation.** SKILL.md:3 is 8 words with no "Triggers on" or "Use
when". Every other edify skill names its trigger phrases. The name also collides with
the built-in code-review skill and the scoped `plugin:review` entry, so "review my
changes" has three candidates and this one offers no distinguishing signal. Fix:
append trigger phrases and an exclusion (not for a finished plan's deliverables,
which is `/deliverable-review`).

**M4. The distinguishing claim at SKILL.md:12 is stale.** It says "the built-in
/review is for PR-focused reviews", but no built-in `/review` exists in this session's
skill list; the built-ins are `code-review` (diff, PR number, branch or path, plus an
effort level) and `security-review`. Rewrite it against `code-review`.

**M5. The `allowed-tools` value is a comma-splitting hazard.** SKILL.md:4 reads
`allowed-tools: Read, Bash(git:*, diff:*)`. As a plain YAML scalar a consumer
splitting on commas yields `Read`, `Bash(git:*` and `diff:*)` rather than two
patterns. The reviewer did not run the parser, so the parse outcome is unverified;
what is verifiable is that the block-sequence form used by
`deliverable-review/SKILL.md:8-12` and `formalize/SKILL.md` is unambiguous. The same
form appears at `runbook/SKILL.md:6` (`Bash(rg:*, git:*)`). Separately, `diff:*`
grants the standalone diff binary, which the body never uses — it uses `git diff` at
:45, :51, :58, :63.

**M6. The report output path violates the project's temporary-files rule.**
SKILL.md:159 writes to `scratch/reviews/review-report-[timestamp].md`, repeated at
`example-execution.md:39`. CLAUDE.md sanctions exactly two locations, the harness
scratchpad and project-local `tmp/`. `scratch/` is gitignored (`.gitignore:5`), so
the output is not committed, but it is not sanctioned either. The runbook-scoped
alternative at :160 is fine; :158-160 joins the two with a bare "or" and gives no
rule for choosing.

**M7. The workflow stages list (SKILL.md:191-197) is stale on three counts and
asserts model assignments it cannot support.** It omits `/requirements`, which
`docs/design.md:139` and CLAUDE.md both put at the head of the pipeline; omits the
design-to-inline branch named on the same line; describes runbook typing as "per-phase
typing: TDD + general" while `runbook-format.md:14` gives `(type: tdd|general|inline)`
and `docs/design.md:143` confirms three; and hardcodes "Opus creates design document"
and "Sonnet creates runbook", which no frontmatter sets, since a skill runs in
whatever model the session runs. It also conflicts with CLAUDE.md's dispatch default
and with `docs/design.md:520`, which pins runbook review at opus.

**M8. Progressive disclosure is inverted.** The output report template occupies
SKILL.md:74-134 — 61 of 207 lines, the largest block — and is inert boilerplate
needed only at write time, while the analysis content lives in `review-axes.md`
behind a single routing line at :68. Move the template to
`references/report-template.md` and route from step 4, which also lets the assessment
criteria at :136-154 travel with it.

**M9. Two of the three references are routed from the wrong place.** SKILL.md:176
points at `example-execution.md` and :178 at `common-scenarios.md`, both below the
Constraints section, after the five-step process has finished.
`common-scenarios.md` is analysis guidance (secrets, multi-concern changes, pattern
violations, already-committed work, large changesets) and belongs at step 3 beside
:68; `example-execution.md` is orientation and belongs before step 1.

**M10. One scope option has no procedure behind it.** SKILL.md:31 offers "Design
conformity" as option 6, but step 2 (:42-64) supplies gather commands for the other
five only and never branches for it. Nothing says how to locate the design document,
and `review-axes.md:12` heads its Design Conformity section "when design doc
available" without saying how availability is established. The skill has no path to a
plan directory either, though :160 knows `plans/[plan-name]/` exists.

## Minor

**m11. The worked example lists five scope options** (`example-execution.md:5-11`)
while SKILL.md:25-32 lists six; design conformity is missing. Fix with M10.

**m12. The example hardcodes volatile content**: `example-execution.md:39` carries a
literal dated path under the disputed `scratch/` location.

**m13. The report template mandates praise unconditionally** (SKILL.md:114-119, two
bullet slots, "be specific"). A code review is a different audience from a chat
reply, so not a direct violation of the tone rule, but forcing the section means it
gets filled when there is nothing to say.

**m14. The execution-context requirement is stated twice**: SKILL.md:201-204
summarises the fields, then :206 points at `fragments/review-requirement.md` for the
"full template and rationale" — the same fragment the summary came from
(`review-requirement.md:85-102` is the authority).

**m15. Two of the ten review axes apply only to runbooks**
(`review-axes.md:32-43`, both headed "when reviewing runbooks/plans") and load on
every code review.

**m16. An ungrounded operational threshold**: `common-scenarios.md:24` keys guidance
to "Large changeset (1000+ lines)" with no basis. The same class of number appears at
`review-requirement.md:10` (≤5 net lines across ≤2 files), though that fragment is
shared policy and may be deliberate.

**m17. This is the only pipeline skill with no recall checkpoint.** Grepping for
recall matches inline, proof, requirements, runbook, design, orchestrate and recall
itself, not review — yet `docs/design.md:139` lists review as the in-progress quality
gate, and Project Standards is an axis (`review-axes.md:26-30`).

## Checked and clean

`review-axes.md:3` claims a 10-category checklist and there are exactly 10
second-level headings. No second-person constructions in SKILL.md or the three
references. All internal path references resolve. `user-invocable: true` matches the
convention. Secrets handling is consistent between SKILL.md:174 and
`common-scenarios.md:4-7`. SKILL.md:182-189, separating this skill from the corrector
agent, is the strongest writing in the file and matches D-28 (`docs/design.md:465-477`).

## Suggested order

C1 and C2 first, since both make the skill instruct behaviour the project forbids or
that defeats its own checks. Then M3 and M4 together as one discoverability pass.
Then M7, M8 and M9 as a single restructuring pass, since moving the template also
moves the reference pointers. The rest are independent.
