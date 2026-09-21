# Verification of `plans/skill-reviews/review.md` — 2026-09-21

Checked against the working tree: `plugin/skills/review/SKILL.md` (231 lines,
unmodified today), `references/review-axes.md` (71),
`references/example-execution.md` (52), `references/common-scenarios.md` (27),
`plugin/fragments/review-requirement.md` (254).

**Line budget:** `review/SKILL.md` is allowlisted at ceiling **231** and measures
exactly 231. M8 is the budget source — moving the report template out frees ~81
lines, which funds every additive fix below. Apply M8 first.

Review tally: 2 critical, 8 major, 7 minor = 17 findings. My table carries 17.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | fixed | :4 is `allowed-tools: Read, Bash(git:*, diff:*)` — no `AskUserQuestion`. Step 1 (:34-42) now asks inline in numbered prose with a stated default ("1. The last N commits (default: 5)"), and :44-47 forbids the tool: "Never reach for `AskUserQuestion`. It renders the exchange as a picker…". The old :184 restatement is gone. |
| C2 | Critical | open-mechanical | :182-183 still "**Bash** for git commands only, **Read** for examining files, **Write** for review output", and `Write` is still absent from :4. `review-axes.md:35` ("Use `rg --files` (Bash) to verify each path exists") and :38 ("use `rg` via Bash") still need search through Bash, which :182 forbids — so an agent obeying the constraint silently skips the Runbook File References axis, whose :36-37 calls missing paths CRITICAL. The reviewer's severity mechanism ("`allowed-tools` grants rather than restricts", cited to CC 2.1.250 docs) is **not verifiable from this repo** — no in-repo document states it — so treat only the prose contradiction as established. |
| M3 | Major | open-mechanical | :3 is still the bare 8-word `Review in-progress changes for quality and correctness`, with no "Triggers on" or "Use when" and no exclusion. The name still collides with the built-in `code-review` and the scoped `plugin:review` entry. |
| M4 | Major | open-mechanical | :14-15 still "**Distinction:** This skill reviews work-in-progress. The built-in `/review` is for PR-focused reviews." No built-in `/review` exists in this environment's skill list; the built-ins are `code-review` (diff / PR number / branch / path, plus an effort level) and `security-review`. |
| M5 | Major | open-mechanical | :4 still `allowed-tools: Read, Bash(git:*, diff:*)` as a plain scalar. The parse outcome remains unverified — the reviewer did not run a parser and neither did I — but `diff:*` is verifiably unused: the body's diff calls are `git diff` at :53, :59-61, :66-67, :72. `runbook/SKILL.md:7` uses the same scalar form, so the shape is not unique to this skill. |
| M6 | Major | open-mechanical | :171 still `scratch/reviews/review-report-[timestamp].md`, repeated at `example-execution.md:39`. `.gitignore:5` still lists `/scratch/`, so output is uncommitted but unsanctioned — CLAUDE.md sanctions the harness scratchpad and project-local `tmp/`. :171-172 still joins the two paths with a bare "or" and no rule for choosing. |
| M7 | Major | open-mechanical | Two thirds still stale. :214-220 now reads `/design` → `/runbook` → `/build` → corrector → commit → complete, so the `/orchestrate` name and the three-type runbook claim are fixed ("per-phase typing: TDD + general" at :216 now matches D-30's abolition of `inline`). Still wrong: `/requirements` is absent though `CLAUDE.md` puts it at the head of the pipeline, the design→`/build` branch is unnamed, and :215-216 still hardcodes "Opus creates design document" / "Sonnet creates runbook", which no frontmatter sets. |
| M8 | Major | open-mechanical | The report template still occupies :86-146 — 61 of 231 lines, the largest block — and is inert until write time, while the analysis content sits in `review-axes.md` behind the single routing line at :77. The assessment criteria at :148-166 travel with it. |
| M9 | Major | open-mechanical | :189-190 (`example-execution.md`) and :192-194 (`common-scenarios.md`) still sit below §Constraints (:180), after the five-step process has finished. `common-scenarios.md` is analysis guidance and belongs beside :77; `example-execution.md` is orientation and belongs before step 1. |
| M10 | Major | open-mechanical | Half the finding is moot, half survives. The six-option scope list is gone — step 1 is now a four-row state table (:24-29) plus a three-option fallback (:37-42) whose option 3 is "Changes against a design document — name it". But step 2 Gather Changes (:49-73) still has no design-document branch and nothing says how to locate the design doc; `review-axes.md:12` still heads its section "(when design doc available)" without establishing availability. The skill still has no path to a plan directory, though :172 knows `plans/[plan-name]/` exists. |
| m11 | Minor | open-mechanical | Worse than recorded. `example-execution.md:5-11` still has the agent open with a five-option question — which step 1 now explicitly forbids at :21-22 ("Do not open with a question — the tree answers it in most cases"). The example no longer illustrates the procedure at all. |
| m12 | Minor | open-mechanical | `example-execution.md:39` still `Full review written to: scratch/reviews/review-report-2026-01-19-142530.md` — a literal dated path under the disputed location. Rides with M6. |
| m13 | Minor | open-design | :126-131 still mandates `## Positive Observations` / `[What was done well - be specific]` with two bullet slots. The reviewer itself grants this is not a tone-rule violation, so whether the section stays required is a style call, not a defect. |
| m14 | Minor | open-mechanical | :222-230 still summarises the required fields ("**Required:** Scope IN, Scope OUT, Changed files, Requirements summary / **Optional:** Prior state, Design reference") and then :230 points at `plugin/fragments/review-requirement.md` "for full template and rationale" — the same fragment the summary came from (`review-requirement.md:118-152` is the authority). |
| m15 | Minor | open-design | `review-axes.md:33-49` still carries two runbook-only axes ("when reviewing runbooks/plans"), loaded on every code review. Splitting the axes file is a structure choice, and the same 10-category count is asserted at :3. |
| m16 | Minor | open-mechanical | `common-scenarios.md:24` still "## Large changeset (1000+ lines)" with no basis. The sibling number at `review-requirement.md:13` ("≤5 net lines changed … across ≤2 files") is shared policy; the reviewer flagged it as possibly deliberate and I found nothing grounding it either — leaving it is defensible, marking it honest. |
| m17 | Minor | open-design | Still the only pipeline skill with no recall checkpoint: a grep for `Skill` or `recall` across `review/SKILL.md` and all three references returns nothing, while `review-axes.md:27-31` makes Project Standards an axis. Adding one needs `Skill` in `allowed-tools` and a decision about where the checkpoint sits — pipeline-level, not local. |

## Cross-file links

- C1 closes with formalize 3, requirements C2, proof M7.
- M6 and m12 are one defect in two files.
- M7's model assertions are the same class as requirements m7 ("Opus required"
  in prose where frontmatter carries no model field).
- m16 is the same class as design m1, runbook M5, deliverable-review M2.
- C2's search-tool contradiction is the mirror of
  `build/references/review-dispatch-template.md:88`, which correctly records that
  `plugin-dev:skill-reviewer` has `Grep`/`Glob` and no `rg`.

## Exact edits for `open-mechanical`

### M8 first — it pays for everything else

Create `plugin/skills/review/references/report-template.md` holding SKILL.md
:84-166 verbatim (the `**Feedback structure:**` block and the `**Assessment
criteria:**` block), then in SKILL.md replace :84-166 with:

```
**Report format and assessment criteria:** Read
`references/report-template.md` and write the report by it.
```

Net: −81 lines in SKILL.md (231 → 150).

### `plugin/skills/review/SKILL.md`

**C2** — :182-183:

- old: `- **Bash** for git commands only, **Read** for examining files, **Write** for`
  `  review output`
- new: `- **Bash** for git commands and read-only search (`rg`, `rg --files`), **Read**`
  `  for examining files, **Write** for review output`

**M3** — :3:

- old: `description: Review in-progress changes for quality and correctness`
- new: `description: >-`
  `  Review in-progress changes for quality and correctness — uncommitted work,`
  `  recent commits, or partial branch work. Triggers on /review, "review my`
  `  changes", "review this work", "check my changes before commit". Not for a`
  `  finished plan's deliverables — that is /deliverable-review — and not for a`
  `  PR, which is the built-in code-review.`

**M4** — :14-15:

- old: `**Distinction:** This skill reviews work-in-progress. The built-in `/review` is`
  `for PR-focused reviews.`
- new: `**Distinction:** This skill reviews work-in-progress in the main session. The`
  `built-in `code-review` targets a diff, PR, branch or path at a chosen effort`
  `level; `security-review` is its security counterpart.`

**M5** — :4:

- old: `allowed-tools: Read, Bash(git:*, diff:*)`
- new: `allowed-tools:`
  `  - Read`
  `  - Write`
  `  - Bash(git:*)`
  (block-sequence form as at `deliverable-review/SKILL.md:8-13`; `diff:*` dropped
  as unused, `Write` added per C2)

**M6** — :170-172:

- old: `**Write review to file:**`
  `- Path: `scratch/reviews/review-report-[timestamp].md` or`
  `- Path: `plans/[plan-name]/reports/review-report.md` (if part of runbook)`
- new: `**Write review to file:**`
  `- Reviewing a plan's work → `plans/[plan-name]/reports/review-report.md``
  `- Otherwise → project-local `tmp/review-report-[timestamp].md` (gitignored)`

**M7** — :214-220:

- old the six numbered stages
- new: `1. `/requirements` — capture requirements`
  `2. `/design` — triage and design; routes to `/runbook` or straight to `/build``
  `3. `/runbook` — decompose into phases of typed items`
  `4. `/build` — execute the planned work, runbook or not`
  `5. corrector — review and fix changes before commit`
  `6. `/commit-commands:commit` — commit changes`
  (model assignments dropped: a skill runs in whatever model the session runs)

**M9** — move :189-190 (`**Example execution:**` …) to immediately before
`### 1. Determine Scope` at :19, and move :192-194 (`**Common scenarios:**` …)
to immediately after the axes routing line at :77-80.

**M10** — add a design-document branch to step 2, after :73:

- new: ```` **For a design document:** ````
  ```` ```bash ````
  ```` ls plans/*/design.md plans/*/outline.md   # locate the plan's artifact ````
  ```` git diff HEAD                              # changes to judge against it ````
  ```` ``` ````
  and amend `review-axes.md:12`:
  - old: `## Design Conformity (when design doc available)`
  - new: `## Design Conformity (when the caller named a design doc, or step 2 located one)`

**m14** — delete :224-228 (the `**Required:**` / `**Optional:**` summary lines),
keeping :222-223 and :230:

- result: `When delegating to corrector, Read `../../fragments/review-requirement.md`` 
  `and include the scope context it specifies — §Execution Context is the`
  `authority for the field list and the rationale.`

### `plugin/skills/review/references/example-execution.md`

**m11 + m12** — rewrite :3-15 so the agent infers scope instead of asking, and
:39 so the path is not volatile:

- :3-15 old: the `/review` → five-option question → "Uncommitted changes" exchange
- new: `**User:** `/review``
  ``
  `**Agent:** "Reviewing uncommitted changes, 5 files — the tree is dirty and`
  `nothing is ahead of main.`
- :39 old: `Full review written to: scratch/reviews/review-report-2026-01-19-142530.md`
  new: `Full review written to: tmp/review-report-<timestamp>.md`

### `plugin/skills/review/references/common-scenarios.md`

**m16** — :24:

- old: `## Large changeset (1000+ lines)`
- new: `## Large changeset (1000+ lines — ungrounded threshold, needs calibration)`
