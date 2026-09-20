# TDD Slice Execution

An item carrying `Slices:` lists behaviour slices and carries nothing else to
execute. It reaches here from a runbook, or from an outline or design routed
to `/build`. Read `dispatch-composition.md` and compose by it each of the four
dispatches that execute slice `N.M/k`, then take the after-the-slice steps.
Only such an item reaches this file.

## The four dispatches

**(a) RED** — `edify:test-driver`, RED mode named in the prompt. For k=1 it
stubs the SUT importable but inert, writes the slice's tests, runs them, and
confirms every test fails on its assertion; for k>1 it does not touch the SUT.
No commit — the tests stay uncommitted in the tree; the report carries the
per-test output, and the dispatch ends there.

**(b) Test review** — `edify:corrector` (opus). Scope IN: this slice's test
files plus the RED report, and the SUT stub for stub completion only — an
ERROR is a stub gap, and the fix belongs to the stub, not the test.
Implementation stays out. First check is mechanical: every listed test FAILED
on an assertion — none PASSED, none ERROR. Then wrong-reason hunting per the
corrector's own criteria. Fix-all on tests, re-run to confirm still red.
UNFIXABLE → STOP.

**(c) GREEN** — `edify:test-driver`, GREEN mode named in the prompt. Makes the
tests pass one at a time, full suite at the end; commits once per slice,
`<type>: Item N.M/k — <title>`, carrying tests and implementation together
with the suite green. The type is the executor's choice (see
`dispatch-composition.md` §Prompt contents) — nothing keys on it. No commit
ever leaves the suite red. The GREEN report names the slice commit's hash.

**(d) Code review** — `edify:corrector` (opus). Scope IN: the implementation
files. May run the slice's tests once against an in-place mutated SUT (save,
mutate, run, restore — never relocate the tests) and report whether they
redded. Applies fixes; flags in-scope-unfixable refactorings (module split,
new abstraction). UNFIXABLE → STOP.

## After the slice

1. **Commit the review fixes:** the corrector never commits. If (d) changed
   anything, commit it — `<type>: Item N.M/k — code-review fixes` — before the
   post-item verification of `SKILL.md` §4.4, the same step §5 takes at a
   phase boundary. Nothing to commit → go straight to verification.
2. **Refactor on signal:** if (d) flagged a refactoring, dispatch
   `edify:refactor` before the next slice's RED, so later tests target the
   refactored shape. It commits its own refactoring commit on a clean tree. On
   `escalated: <reason>` → re-dispatch `edify:refactor` once with model opus
   (the Agent tool's `model` override). The prompt must state, in those words,
   that **this run is the opus escalation** — the agent cannot see its own
   model and branches on that sentence, so quoting the reason alone makes it
   escalate again — and carry the reason. A second `escalated` goes in the run
   summary and execution continues. On `error` → log and continue.
3. **List revision:** revise the remaining slices' test lists in `runbook.md`
   from what this slice revealed, or record "List revision: none" in the run
   summary. Commit the `runbook.md` edits after the slice — plan-as-executed
   versus plan-as-written stays a `git diff`.
