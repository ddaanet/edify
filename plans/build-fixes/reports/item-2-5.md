# Item 2.5 — `plugin/skills/build/references/review-dispatch-template.md`

Requirements: Major 1, m4, m11, m19.

## Changes per bullet

- **§Field Rules, Baseline (Major 1).** "Read back from `tmp/build-baseline`
  (written at `/build` §2 by `git rev-parse HEAD` before edits)" became the
  `BASE:` that `plugin/skills/build/scripts/changed-files.sh <job>` prints —
  the one `finishing.md` §1 step 1 took. It is still substituted as the hash
  itself. The design-phase sentence now follows KD-1: the base is the parent
  of the run's first item-report commit, so what `/design` committed before
  execution lies outside the diff. The old reason ("taken after the entry gate
  has confirmed a clean tree") described the deleted capture.
- **§Report-only variant, UNFIXABLE (m4).** "Mark a blocker
  "UNFIXABLE: [description]"" became a paragraph asking for:
  - the subcategory code, each glossed in one clause from `corrector.md`'s
    taxonomy table — U-REQ, U-ARCH or U-DESIGN;
  - an investigation summary of the three gates (Scope OUT, design deferral,
    codebase patterns) with a conclusion;
  - the DEFERRED rule for an issue in Scope OUT or deferred by the design.

  These are exactly what `review-requirement.md` §UNFIXABLE Detection Protocol
  validates per issue. The glosses are inline because the report-only reviewer
  cannot be assumed to reach `plugin/agents/corrector.md` from a consumer repo.
- **§Report-only variant, blocked (m19).** The prompt now ends: "If you cannot
  review at all, reply `blocked: <reason>` instead of findings." The paragraph
  after the block tells the calling session that such a reply carries no
  findings and leaves no report, and sends it to `references/escalation.md`.
- **§Example (m11).** A new lead paragraph says the example shows the
  fix-capable §Template for a skill-definition group, which is what that group
  takes when `plugin-dev` is not installed and the skill row falls back to
  `edify:corrector`. With `plugin-dev` installed, the group takes
  `plugin-dev:skill-reviewer` and the §Report-only variant.
- **Cross-reference from Item 2.4 (reclassification).** The paragraph after
  the report-only block now says that an UNFIXABLE failing validation goes back
  to this reviewer, `review-<group>`, resumed by `SendMessage`. Its reply comes
  in parts and the session rewrites the report. This is the wording of
  `finishing.md` §1 Structural proof.

## Judgement calls for review

- **Where a `blocked:` reply goes.** The outline allows the return but does not
  say what the caller does with it. I pointed it at `references/escalation.md`,
  the node for "a dispatch that … returned an unexpected result", since a
  report-only reviewer that cannot review leaves the gate with no report for
  the structural proof. No new procedure is added.
- **Subcategory glosses inline.** They restate three rows of `corrector.md`'s
  table in one clause each. The alternative — "see `plugin/agents/corrector.md`"
  — names a repo path an installed plugin's reviewer may not resolve (the
  repo-relative-paths job is outline §Scope OUT).

## Cross-references left for later items

- `review-requirement.md` §UNFIXABLE Detection Protocol step 4 still says
  reclassification is a fresh delegation with "no continuation mechanism
  available", against the resume by name here, in `finishing.md` and in
  `phase-boundary.md`. No item names it. Already flagged in `item-2-3.md` and
  `item-2-4.md`.
- The routing table's skill row and its `plugin-dev` fallback paragraph, which
  the §Example lead relies on: Item 2.9 keeps the fallback and adds the `craft`
  one.

## Verification

- `just format`, then `just precommit` green (version consistency, cached
  tests, line limits — only the three allowlisted correctors reported — and
  design links).
- Self-review of the uncommitted diff against Item 2.5's bullets, KD-1, and
  `finishing.md` §1 and §2 as Item 2.4 left them.
- 151 lines before, 170 after (`wc -l`, after `rumdl fmt`).
