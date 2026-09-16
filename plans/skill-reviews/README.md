# Skill reviews — edify plugin, 2026-09-16

One report per skill, from `plugin-dev:skill-reviewer`, one agent per skill, four at
a time. The reviewer has no Write tool, so each report arrived in its reply and was
saved here by the calling session. Message delivery cuts a reply at roughly 4000
characters; the first four reviewers were cut and resent in parts, the rest were told
to chunk up front. Line cites are the reviewers' own and are **unverified** by the
calling session, except where a reviewer says it ran a command.

| Skill | Critical | Major | Minor |
|---|---|---|---|
| inline | 3 | 7 | 17 |
| formalize | 3 | 5 | 5 |
| design | 3 | 6 | 7 |
| deliverable-review | 3 | 7 | 9 |
| orchestrate | 2 | 8 | 9 |
| proof | 2 | 9 | 6 |
| recall | 2 | 5 | 5 |
| requirements | 2 | 6 | 10 |
| review | 2 | 8 | 7 |
| runbook | 2 | 7 | 8 |
| ground | 0 | 6 | 8 |
| **total** | **24** | **74** | **91** |

## Cross-cutting

- **`AskUserQuestion` is mandated by four skills and forbidden by the always-loaded
  conventions** (formalize, proof, review, requirements). One decision settles all
  four: a stated exception for user-facing pipeline skills, or a rewrite to numbered
  prose questions with stated defaults.
- **`docs/` does not ship with the plugin**, yet skills cite `docs/design.md` as
  operative content (deliverable-review C2 hardcodes a dead citation into every
  consumer's report; formalize C2 is the same class for the CLI path).
- **A bare `/proof` is ambiguous across three installed skills** and is invoked that
  way at every call site (proof M1, runbook M9, design).
- **Ungrounded operational thresholds** appear unmarked in deliverable-review (M2),
  runbook (M5), review (m16), formalize (7) and design (m1), while siblings mark the
  same numbers as needing calibration.
- **Progressive disclosure is inverted** in review (M8), requirements (M6) and
  formalize (8): the largest block is boilerplate, the reasoning content sits behind
  one routing line or is linked from the last bullet.
- **The recall contract is diverged from in three places** (proof M4 drops the
  plan-dir half; requirements m3 and runbook re-invoke where the contract says to run
  the loaded procedure inline).
- **Skills disagree with the fragments they route through** on reviewer routing,
  dirty-tree remediation and halt conditions (orchestrate M6, M7, M8), and on recall
  precedence (recall M5).
- **Two skills state a required model in prose** where frontmatter carries no model
  field (requirements m7, review M7).

## Decisions these reviews surface

1. `AskUserQuestion`: exception or rewrite.
2. deliverable-review: is the skill terminal, or do findings route on (its C3, against
   D-58 and D-60)?
3. recall: does the index Read come back (its C1, against D-48)? The answer decides
   three of its steps and how much of `gitlore:recall` edify still duplicates.
4. Are `inline` phases real? Nothing in orchestrate reads the type token
   (runbook C2).
5. `/design` → `/inline` handoff: who commits, and where does the baseline come from
   (inline C1)?
