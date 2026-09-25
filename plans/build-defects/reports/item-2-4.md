# Item 2.4 — `plugin/skills/build/references/review-dispatch-template.md`

Status: **applied.**

Requirements: inline M1, m15, M2, m16, m6.

## Per bullet

- **Changed files as an explicit list (M2, KD-1).**
  - §Template: the `git diff --name-only <baseline commit hash>` command became a
    list placeholder, one line per file in the artifact group, named as its
    share of `finishing.md` §1 step 1's list — the same wording Item 2.3 gave
    `finishing.md` §1's scope sentence.
  - §Example: the command became the skill group's five files. `scripts/verify-step.sh`,
    in the example's Scope IN, is left out on purpose: it is a script, so it
    belongs to the code group, which shows a group's share rather than the
    whole diff.
- **`**Constraints:**` block (M2).** Added to §Template and §Example, before the
  fix/report/return lines, with the bullet `review-requirement.md` §Execution
  Context's delegation template carries. The §Report-only variant replaces only
  the closing three lines and the recall line, so it inherits the block; the
  "closing three lines" count still holds (fix/report line, blank, return line).
- **Agent-definition criteria (m16).** A placeholder criteria line for
  agent-definition groups only, naming the `plugin-dev:agent-development`
  criteria: frontmatter validity, trigger description quality, tool access
  minimality, system-prompt structure. Checked against that skill: its
  §Frontmatter Fields, §Validation Rules (identifier, description, system
  prompt) and the tools "least privilege" best practice.
- **Report path and return lines defer (M1, m15, KD-2).** In §Template both
  became placeholders citing `dispatch-composition.md` §Prompt contents. The
  §Example instantiates the rule: report path under `review-skill`, return "the
  report path on success, or `blocked: <reason>`", and UNFIXABLE marked inside
  the report. The §Report-only variant's closing paragraph now writes to "the
  group's report path (§Field Rules)" instead of restating the path.
- **§Field Rules, Report path (M1).** Now "Report path and return contract":
  `dispatch-composition.md` §Prompt contents is the one rule for both, under the
  dispatch name `review-<group>`. The structural-proof sentence is kept.
- **Constraint bullet (m6).** The D-26 routing paragraph became "implementation
  changes only. Planning artifacts route as `finishing.md` §1 says, not through
  this template." `finishing.md` §1 keeps the one copy (checked).

## Pointers checked

- `dispatch-composition.md` §Prompt contents item 5 holds the report-path rule
  and the return contract. It does not yet name `review-<group>` in §Naming, nor
  the report-only exception or UNFIXABLE-inside-the-report; Item 2.5 adds all
  three, after which this file's pointers land in full.
- `finishing.md` §1 step 1 is the baseline diff line; its planning-artifact
  paragraph is intact.

## Noticed, not changed

The §Example is a skill-definition group (`review-skill`) dispatched through
the fix-capable §Template, while `review-requirement.md` routes skill
definitions to the report-only `plugin-dev:skill-reviewer`. It is correct only
under the plugin-dev-absent fallback. Not in this item's findings; left as is.
