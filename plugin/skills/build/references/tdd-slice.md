# TDD Slice Execution

An item carrying `Slices:` lists behaviour slices and carries nothing else to
execute. It reaches here from a runbook, or from an outline or design routed to
`/build`. Read `references/dispatch-composition.md` and compose by it each of
the four dispatches that execute slice `N.M/k`, then take the after-the-slice
steps. Only such an item reaches this file.

## The four dispatches

**(a) RED** — `edify:test-driver`, RED mode named in the prompt. For k=1 it
stubs the SUT importable but inert, writes the slice's tests, runs them, and
confirms every test fails on its assertion; for k>1 it does not touch the SUT,
except for the mutation proof below, which restores it before the dispatch ends.
No commit — the tests and the report stay uncommitted in the tree for the GREEN
commit to carry; the report carries the per-test output, and the dispatch ends
there.

**Mutation proof — the fallback when the behaviour is already implemented.** A
slice whose behaviour an earlier GREEN already wrote cannot red on its own
assertion. Prove it by mutation instead: replace an exact string in the SUT —
one occurring nowhere else in the file — so the behaviour is absent, run the
slice's tests, and show **each named test** red on its own assertion. Restore by
applying that replacement with the two strings swapped, never from a copy or a
scratch directory (neither survives between tool calls reliably) and never
`git checkout`/`git stash` (both discard the dispatch's own uncommitted tests).
Prove the restore: grep for the mutation text, expect no hit, then the suite
green. One mutation per named test, not per batch; restore after each. The RED
report records it under a `Mutation proof` heading, naming the mutation against
the test it reds, and the slice goes into the list revision as proven by
mutation. `tdd-auditor` counts a mutation proof as the slice's evidence; nothing
counts a test that was neither shown red nor mutated against.

**(b) Test review** — `edify:corrector` (opus). Scope IN: this slice's test
files plus the RED report, and the SUT stub for stub completion only — an ERROR
is a stub gap, and the fix belongs to the stub, not the test. Implementation
stays out. First check is mechanical: every listed test FAILED on an assertion —
none PASSED, none ERROR. A test the RED report records under `Mutation proof`
satisfies that check by its proof instead: reproduce it with a **different**
mutation of the reviewer's own choosing, confirm the named test reds on its
assertion, restore, and verify the restore. A test that neither failed nor
carries a mutation proof fails the check. Then wrong-reason hunting per the
corrector's own criteria. Fix-all on tests, re-run to confirm still red.
UNFIXABLE → STOP. The corrector commits nothing: its report joins the tests in
the tree, and the GREEN commit carries it.

**(c) GREEN** — `edify:test-driver`, GREEN mode named in the prompt. Makes the
tests pass one at a time, full suite at the end; commits once per slice,
`<type>: <job> Item N.M/k — <title>`, carrying tests and implementation together
with the suite green. The type is the executor's choice (see
`dispatch-composition.md` §Prompt contents) — nothing keys on it. No commit ever
leaves the suite red. The commit also carries the slice's three reports so far —
RED, test review and GREEN — staged by name, never by a blanket add. So the
GREEN report names no hash, and the slice commit is the commit that adds it:

```bash
git log --diff-filter=A --format=%H \
    -- plans/<job>/reports/item-N-M-s<k>-green.md
```

**The GREEN prompt carries this slice's behaviour and nothing wider.** Where the
item's `Interfaces:` block or contract text goes in for structure, name the rest
of it out of scope in the same prompt: GREEN implements nothing the slice's
tests do not demand. A GREEN that implements the whole item leaves every later
slice unable to red, which costs each of them a mutation proof — the fallback,
not the route.

**(d) Code review** — `edify:corrector` (opus). Scope IN: the implementation
files. May run the slice's tests once against an in-place mutated SUT (mutate by
exact string replacement, run, restore by inverting it — never relocate the
tests, never restore from a copy) and report whether they redded. Applies fixes;
flags in-scope-unfixable refactorings (module split, new abstraction). UNFIXABLE
→ STOP.

## After the slice

1. **Commit the code review:** the corrector never commits, so this commit
   always happens — `<type>: <job> Item N.M/k — code-review fixes` — carrying
   (d)'s report and the fixes it applied, or the report alone where it changed
   nothing. Stage those paths by name and commit with `git commit -- <paths>`.
   It comes before the post-item verification of `SKILL.md` §4.4, the order
   `SKILL.md` §4.5's phase boundary keeps too; a review whose report stayed
   uncommitted is what leaves that gate dirty.
2. **Refactor on signal:** if (d) flagged a refactoring, dispatch
   `edify:refactor` before the next slice's RED, so later tests target the
   refactored shape. It commits its own refactoring commit on a clean tree. On
   `escalated: <reason>` → re-dispatch `edify:refactor` once with model opus
   (the Agent tool's `model` override). The prompt must state, in those words,
   that **this run is the opus escalation** — the agent cannot see its own model
   and branches on that sentence, so quoting the reason alone makes it escalate
   again — and carry the reason. A second `escalated` goes in the run summary
   and execution continues. Once the refactoring commit lands, run the post-item
   verification of `SKILL.md` §4.4. On `error` → run it too, since a failed
   refactor can leave dirt like any other step, then log and continue.
3. **List revision:** revise the remaining slices' test lists from what this
   slice revealed, or record "List revision: none" in the run summary. The
   revision is made in the file hosting the item — `runbook.md`, or the
   `outline.md` or `design.md` routed to `/build` — and its commit takes that
   file alone: stage it by name and commit with
   `git commit -- plans/<job>/<hosting file>`, subject
   `<type>: <job> Item N.M/k — list revision`, so plan-as-executed versus
   plan-as-written stays a `git diff`. Once that commit lands, run the post-item
   verification of `SKILL.md` §4.4. "List revision: none" commits nothing and
   has nothing to verify.
