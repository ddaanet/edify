# Brief — a tdd slice spec enumerates a guard predicate's boundary states

From a gitlore session, 2026-09-24. Input for `skills/runbook/references/runbook-format.md`; the choice is yours.

## Observation

One tdd item, two slices, run through `/edify:orchestrate` with RED → test review → GREEN → code review per slice and a phase corrector. RED discipline held throughout: every test failed on its named assertion, and both test reviews reproduced the red before editing. Yet three of the four review passes found a MAJOR correctness defect in code that had gone green, and every one was a boundary state of a single file-predicate guard (`[ -s "$file" ]`): the file present and empty; present and all-whitespace; present before the run and consumed by a step inside it that then failed. Each shipped in a commit before any test saw it, and was caught by a reviewer instructed to probe empirically.

The cause is upstream of RED. The slice spec was drafted from the design's narrative, which argued about "absent" and "stale"; the spec named those two, RED wrote those two, and the suite was green over everything in between. RED writes what the spec names.

## Proposal

In `runbook-format.md`, alongside the item-level rules ("No weak assertions", "No unit-only coverage"), one rule of the same shape:

**Enumerate a guard's boundary states.** A slice for an entry point guarded by a predicate on a file, a variable or a return value lists that predicate's boundary states — absent, present-empty, present-blank, present-then-consumed by the run, and whatever else the run can do to the guarded object — each as a named test or an explicit "not covered because". A spec that names only the states the design's narrative discussed leaves the rest to a review.

`runbook-corrector` could check for it mechanically where an item's text names a predicate or a guarded file: does the slice list name more than the two states the design section discusses?

## Evidence

`gitlore` repo, `plans/batch-retry-approval-freshness/reports/tdd-audit.md` §"The pattern worth carrying forward", with the four findings tabled by which pass found them.
