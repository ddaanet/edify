# 2026-09-21 — what the TDD audit changed: slice-scoped GREEN, mutation proof, report commits

The TDD audit of `plans/provenance-enforcement-and-routing/` found the
over-implementing GREEN: each dispatch was handed the whole item contract "for
structure" and implemented all of it, so six later slices — 1.2/3, 1.2/4–8,
1.10/3, /6, /7 — had no behaviour left to red against, and nothing forbade it.
The contract legitimately goes into the prompt, and once it is there an agent
told to make one test pass has no reason to stop at the test. So the prompt now
names the rest of it out of scope in all three places it has to act —
`dispatch-composition.md` §Prompt contents (where the prompt is composed),
`tdd-slice.md` §(c) (where the dispatch is described) and `test-driver.md` GREEN
mode (where the agent reads it); the first two alone would have been rules the
agent never sees.

The recovery those six slices actually used is now the recorded fallback, D-84's
second half: a mutation proof, per named test and never per batch. The audit
rates it *stronger* evidence than an ordinary red, which is why it is kept
rather than counted as a failure — and not a reason to plan for it. It also
reconciles three statements that each read as absolute: a passing RED test has
named itself vacuous, the test review's first check is that every listed test
FAILED, and a slice whose behaviour exists cannot fail.

The same audit's other hole, D-86: GREEN committed the slice and then wrote its
report, leaving it untracked for `verify-step.sh` to call every GREEN dispatch
dirty — as were the RED, test-review and code-review reports whenever their
review changed no file. A report now rides the commit whose work it reports and
names no hash; the commit is the one that adds it, `git log --diff-filter=A`.
