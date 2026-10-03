# Item 2.9 — `plugin/fragments/review-requirement.md`

Requirements: m2, (c).

## Changes per bullet

- **§Execution Context, Changed files (m2, KD-6).** The field now names two
  forms. Under `/build` it is the list that
  `plugin/skills/build/scripts/changed-files.sh <job>` prints after `BASE:`
  (`--phase` at a phase boundary): the committed diff from the run's or phase's
  base to `HEAD`, minus the paths `verify-step.sh` exempts and the job's own
  `plans/<job>/` record. The working-tree form, `git diff --name-only <base>`,
  is for uncommitted work only. The old pointer to `phase-boundary.md` for the
  base is gone, since the script now resolves the base. The "never a bare
  `git diff --name-only`" and "must not be empty" sentences are kept.
- **Routing table, skill row (KD-5).** "Skill definitions" became "Skill
  definitions, their `references/` nodes, and shared instruction files kept
  outside a skill". It names the class, not edify's `plugin/fragments/`. The
  reviewer is still `plugin-dev:skill-reviewer`.
- **Routing table, design row (KD-5).** "Design documents →
  `edify:design-corrector` (opus)" became "The living design graph under
  `docs/` → `edify:corrector`". The Why column names `craft:design-doc-writing`
  as the criteria source in the dispatch prompt, in the agent row's form. It
  also says that a job's `plans/<job>/design.md` is a planning artifact reviewed
  by `edify:design-corrector`, so that agent is still findable from the table.
- **`craft`-absent fallback (KD-5).** The `plugin-dev` paragraph is now
  "When plugin-dev or craft is not installed". The `plugin-dev` sentences are
  unchanged. Added: without `craft`, the design-graph row keeps
  `edify:corrector` but loses its criteria source. The closing clause (separate
  marketplace plugin, check availability, note the fallback in the report) now
  covers both.

## Deviation — §UNFIXABLE Detection Protocol step 4 (orchestrator's extra scope)

Step 4 said reclassification is a fresh delegation, with "no continuation
mechanism available". That contradicts `finishing.md` §1 Structural proof,
`phase-boundary.md` §Review and `review-dispatch-template.md` §Report-only
variant, which resume the reviewer by name (`item-2-3.md`, `item-2-4.md`,
`item-2-5.md` flagged it). Step 4 now reads: resume the corrector with specific
guidance, by name (`SendMessage`) where the dispatch was named, as `/build`
names every dispatch. An unnamed dispatch cannot be resumed, so the caller
delegates again with the reclassification instructions in the prompt. The
second clause keeps the step true for callers that do not name their
dispatches (`/review`, and anything else that loads the fragment). "The
corrector" is kept as the step's word, because `finishing.md` §1 maps it ("Where
the protocol resumes the corrector for reclassification, resume the group's own
reviewer"). The delegation template's "Return filepath or error." is m12 and
was not touched.

## Judgement calls for review

- **`/build` §4.1's corrector uses the working-tree form, not `changed-files.sh`.**
  The outline says the working-tree form is "for `/review` only". But
  `SKILL.md` §4.1, as Item 2.1 left it (KD-1), dispatches the `item-N-M`
  corrector "scoped to this item's uncommitted changes", before the item's one
  commit. `changed-files.sh` lists committed work only, so it cannot serve that
  dispatch. So the text says the working-tree form is for uncommitted work
  only: `/review`, and `/build` §4.1's corrector. Writing "for `/review` only"
  would leave §4.1 with no stated form. If the reviewer reads the outline as
  binding, §4.1 needs a form of its own somewhere else.
- **Untracked files.** I added "It takes in uncommitted changes but never an
  untracked new file, so add those by name". `git diff` never lists untracked
  paths, and a §4.1 item that creates a file would otherwise send the corrector
  a list without that file.
- **"plans" left in the code row.** KD-5's `review-code` row is "code and tests,
  and the default for any file kind no row names", and `/build` never routes
  planning artifacts. The fragment's table also serves `/review`, and its
  §Production artifacts list keeps "Plans (runbooks)". Item 2.9's bullets do not
  name the code row, so it is unchanged. `/build` is unaffected, because
  `changed-files.sh` drops `plans/<job>/` and `finishing.md` §1 routes planning
  artifacts by artifact.
- **Path form.** The new `changed-files.sh` pointer uses the
  `plugin/skills/build/...` form that the replaced `phase-boundary.md` pointer
  used (outline §Scope OUT).

## Cross-references left for later items

- **Seam: `edify:corrector` rejects `design.md` (not owned by any item).**
  `plugin/agents/corrector.md` §Scope says it does not review "Design documents
  (use design-corrector)". Its §0 "Design document rejection" tells it to check
  whether a single-file scope "is `design.md` or in a `design` path", and if so
  to return `Error: Wrong agent type`. The new design-graph row (KD-5) sends
  `docs/design.md` to `edify:corrector`. A `review-design` group holding only
  `docs/design.md` would be refused. `corrector.md` is out of this job's scope
  (defect 21 owns its edits, and its allowlist ceiling is pinned). The
  rejection needs narrowing to `plans/<job>/design.md`, or KD-5 needs another
  reviewer. Flagged for the orchestrator and the deliverable review.
- `§Execution Context` anti-pattern (line ~141) still says "phase checkpoint",
  the term m15 renames to "phase boundary" in `tdd-auditor.md`. Not named by any
  item; noted only.
- `§UNFIXABLE Detection Protocol` validation's last bullet says "complete
  4-gate checklist" where the list above it has three gates. This is
  pre-existing, and no item names it. Noted only.
- `docs/`: no drift seen from this item for Items 2.12 and 2.14 beyond KD-5 and
  KD-6, which Item 2.14 records.

## Verification

- `just format`, then `just precommit` green: version consistency, cached
  tests, line limits (only the three allowlisted correctors reported), design
  links.
- Self-review of the uncommitted diff against Item 2.9's two bullets, KD-5 and
  KD-6. Also read against `finishing.md` §1 (routing, structural proof),
  `phase-boundary.md` §Review, `review-dispatch-template.md` §Report-only
  variant and §Example, `dispatch-composition.md` §Naming and resumption, and
  `SKILL.md` §4.1. Then read against `corrector.md` §0, which surfaced the seam
  above.
- 256 lines before, 264 after (`wc -l`, after `rumdl fmt`).
