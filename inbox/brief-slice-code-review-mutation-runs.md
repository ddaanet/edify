## Brief: the slice code review mutates what green added, not once and optionally

2026-10-08

From sandbox-lies, after a `/edify:build` run of its `sandbox-lies-review-fixes-2`
job in which my human partner made per-slice mutation runs binding partway
through. Nothing is tracked in sandbox-lies after this note. Sections are named,
not line-numbered.

### The gap

`plugin/skills/build/references/tdd-slice.md`, step **(d) Code review**, and
`plugin/agents/corrector.md`, **Code review** item 2 ("Mutated-SUT run
(optional, once)"), allow a single optional mutation per slice. Red-phase
evidence covers only what the red tests name. Three kinds of behaviour stay
unproven:

- **What GREEN added beyond the red tests**: an extra branch, guard or fallback
  the implementer wrote to make the tests pass.
- **Tests written after their code**: pins and regression cases, which have no
  red phase.
- **Behaviour whose fixture changed between RED and GREEN**: the red seen
  before the change no longer proves anything.

### Evidence (sandbox-lies, bats suites)

- **The first build** used the current optional rule. A slice review passed a
  test whose fixture held three masked names where two already met the
  threshold, so the slash case it named was vacuous. A later deliverable review
  ran 39 mutations, and dropping `/?` from the matcher left the suite green.
  That became a Major.
- **The second build** ran under the binding rule below:
  - A Phase 3 review's mutations survived twice. A BSD-stub case could not
    detect a GNU-only `grep -qP`, and another could not detect a dropped `wc`
    padding strip. Both cases were rebuilt until the mutation went red.
  - A slice reviewed before the rule existed was mutated at the end-of-build
    review. One mutation survived: when `sed` failed partway, the probe kept
    its partial output and reported `found` for an id it never checked. A
    Major, fixed with a test that fails under that mutation.
  - A slice code review ran nine mutations. One equivalent mutant exposed dead
    code, which was removed.
  - Other slices: 8 of 8 mutations went red, with nothing to fix.
- The build's tdd-audit then recommended that a reviewer also mutate every line
  of its own fixes.

### Decision (from my human partner, for the run above)

The slice code review mutates, one mutation per behaviour:

- every behaviour in the GREEN diff that no RED report names;
- every test written after its code;
- every behaviour whose fixture changed between RED and GREEN.

It skips a behaviour whose RED report shows the test failing on its assertion
against the unchanged code, with the fixture unchanged since. Procedure:

- Run only the slice's own test files, one process at a time.
- Mutate in place and prove the mutation landed. Restore by inverting the edit,
  then check that `git diff` shows only the intended changes.
- When a mutation survives, the fixture or test is fixed, and the same mutation
  going red proves the fix.
- The report gets a table: behaviour | mutation | red or survived (and fixed).

Cost observed: about 3–5 single-file runs per slice. That was affordable on a
2GB box run sequentially.

### Conflicts to resolve in edify (edify's call)

- **Fixing a surviving mutation means editing a test, which code review cannot
  do.** In `tdd-slice.md` (d), scope IN is the implementation files, and
  `corrector.md` says "OUT: the tests (never edit them here)". In the run, the
  reviewers fixed tests anyway. Options: allow test edits at (d) only for a
  surviving mutation, proved by that mutation going red; or return the
  survivor to a test-review pass.
- **`corrector.md` and `tdd-slice.md` disagree on restoring.** `corrector.md`
  says "save the SUT … restore", while `tdd-slice.md` says "never restore from
  a copy" and restore by inverting the edit. The `craft:test-discipline`
  genuine-red node sides with inverting.
- **The tdd-audit's recommendation** (mutate every line of the reviewer's own
  fixes) belongs in the same step, if adopted.

### Additional context

- The reports are in sandbox-lies at
  `plans/sandbox-lies-review-fixes-2/reports/` (`phase-3-review.md`,
  `item-1-1-sB-code-review.md`, `item-2-1-s1-code-review.md`,
  `review-code-tests.md`, `tdd-audit.md`). Each has its mutation table.
