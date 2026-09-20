# Review gate — skill definitions

Reviewer: `plugin-dev:skill-reviewer` (report-only; findings returned in
parts, fixes applied by the orchestrating session). Baseline
`1f54633b8bf3425a2c3cbd30bc9482049c216522`. Scope: the thirteen skill and
fragment files with content changes in this job — `design/SKILL.md`,
`route-to-execution.md`, `write-outline.md`, `research-protocol.md`,
`build/SKILL.md`, `tdd-slice.md`, `phase-boundary.md`, `finishing.md`,
`review-dispatch-template.md`, `deliverable-review/SKILL.md`,
`review/SKILL.md`, `runbook/SKILL.md`, `fragments/delegation.md`. Wrapping-only
changes from the reflow commit excluded.

## Findings

**Critical:** none.

**Major 1 — sibling pointers in `build/references/` used two incompatible
bases.** `finishing.md:10` (`../../fragments/…`), `route-to-execution.md`
(`../runbook/…`, `../build/…`) and `research-protocol.md` (`references/…`) are
relative to the skill's announced base directory; `tdd-slice.md:5`,
`phase-boundary.md:14` and `finishing.md:17` named a sibling bare
(`dispatch-composition.md`, `review-dispatch-template.md`), which resolves only
file-relative. `finishing.md` carried one of each. **Fixed** in commit
`d4e0a2b5`: the three bare names became `references/dispatch-composition.md`
and `references/review-dispatch-template.md`, per the outline's cross-cutting
rule (skill-base-relative).

**Minor 2 — `review/SKILL.md:230`** still carries the repo-relative
`plugin/fragments/review-requirement.md` in a "See … for full template"
sentence, six lines below the pointer this job rewrote. Pre-existing; belongs
to the repo-relative references job (outline §Scope OUT). **Left.**

**Minor 3 — `review-dispatch-template.md:3`, `:68`, `:90`** cited "`/build`
§6" for the structural proof and group routing, which now live in
`finishing.md` §1 (`/build` §6 is Escalation). **Fixed** in `d4e0a2b5`: all
three cite `finishing.md` §1.

**Minor 4 — `design/SKILL.md` `description:`** read capability → triggers →
capability. **Fixed** in `d4e0a2b5`: what it does (classifies, produces design
documents, routes by whether the work needs a runbook), then the triggers.

**Minor 5 — `design/SKILL.md` `allowed-tools`** omits `Edit` while
`write-outline.md:123` says "via Edit". Pre-existing and not a block:
`allowed-tools` pre-approves, it does not restrict
(`plugin-craft:skill-authoring`). **Left**, noted for the run summary.

**Hub length (measured):** `build/SKILL.md` 218, `design/SKILL.md` 285,
`review/SKILL.md` 231 against the ~200 guideline. The growth is the reflow's
honest count, not this job's content: `design/SKILL.md` went 175 → 285 lines
with word count 1738 → 1847 (+6%); its baseline carried 324–372-character
lines. Allowlisted with "no job yet".

## Design conformance

Every requirement checked and met: M-3 (preconditions bind by branch), M-5 and
KD-6 (the not-routable branch exists, with its return path), M-6 (`rg -n -U`
"per X" search returns zero hits across the thirteen files; every rewritten
site is an imperative Read; both citation sites name D-26 without "per"), m-1,
m-2, m-3, KD-2 (`deliverable-review/SKILL.md` step 2 is the bare-name call and
the verdict table verbatim; the script exists and is executable), KD-3 (three
branches, two discriminators, the second marked ungrounded, `test↔implementation`
dropped), KD-4 (`build/SKILL.md` §4, §4.3, §References and `tdd-slice.md`
agree on the `Slices:` trigger; both `/design` generate steps carry the
`runbook-format.md` Read), KD-5 (`description:`, four callers in the node's
scope sentence, §Downstream Consumers and §Routing out; the Phase 0 return
point; the `design.md`-exists branch corrected to C.5).

Cross-skill consistency: no instruction-subject second person in any body;
every stale-behaviour grep hit (`runbook`, `prose`, `type is`, `tdd`) judged
and found correct; every pointer written by this job resolves under the
skill-directory base after Major 1's fix.

Clean by name: `phase-boundary.md`, `tdd-slice.md`, `runbook/SKILL.md`,
`deliverable-review/SKILL.md`, `write-outline.md`, `research-protocol.md`,
`delegation.md`, `route-to-execution.md`, `design/SKILL.md`.

No UNFIXABLE.
