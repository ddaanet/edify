## Brief: outlines cite `path:line`, and the numbers rot before the outline is executed

2026-09-18

Arrived from the `claude-plugin-dev` repo, after a deliverable review of an
executed plan found that most of the plan's own source citations had gone stale.

### The gap

Nothing in `/design` states a citation convention, so outlines pick up
`path:line` by imitation and use it heavily — it is the default way an outline
points at the code it is about. `/runbook` is the only place that names an
alternative, at `plugin/skills/runbook/SKILL.md:103`:

> **Code-fix items enumerate affected call sites** (file:function or
> file:line).

That offers the two as equivalent. They are not: one is stable under edits and
the other is invalidated by the very edits the plan prescribes.

### The evidence

A deliverable review of `plans/2026-09-15-first-release-version` reported one
stale citation as a Minor. A whole-tree sweep for `<script>.sh:<line>` during
triage found four such citations and grew the stale count from one to three:

- `toolkit/release.sh:254` cites `:780-785` for "release_preflight never runs on
  resume". The mode dispatch moved to `:837-843`; `:780-785` is now the
  marketplace commit-gate rollback — a real code block, so the citation reads as
  valid and points at the wrong mechanism.
- `tests/version-guard-test.sh:340` cites `release.sh:446-455` for a bump
  argument being refused on an unreleased plugin. That range is now the
  version-drift refusal; the claim lives at `:472-481`.
- `tests/version-guard-test.sh:341` cites `release.sh:456-460` for a bare
  `just release` publishing `$current`. That range is now a `die` plus a resume
  hint; the claim has since split across `:470-486` and `:618-626`.

The failure mode worth naming is the first one: a rotted line number rarely
dangles. It lands on *different real code*, so a reader who follows it gets a
confident wrong answer rather than an error.

The fix pass that found these also prescribes two edits inside
`toolkit/release.sh` that shift its line numbers again. Repairing the three
numbers would have bought citations that rot within the same pass — which is
what moved us to change the convention instead of the numbers.

### Proposed change

Have `/design`'s outline-writing guidance state the convention, and tighten
`/runbook`'s existing bullet from "file:function or file:line" to the stable
form only.

The stable form is not just a function name — a function can be long enough that
the name loses the precision the number carried. What survives editing is
**unambiguous line context**: the enclosing symbol plus a short quoted fragment
of the line itself, e.g.

> `release.sh`, in `release_preflight`, the `origin_release_tags` empty-list
> branch

or, where a symbol does not scope it tightly enough, a quoted distinctive
substring the reader can search for. Both survive insertions above them, and
both fail loudly rather than silently when the code they name is gone.

### The exception, so it is not over-applied

A citation *into a frozen dated artifact* — an executed outline, a runbook, a
changelog entry, a review report — should keep its line numbers. Those files are
write-time records and are never revised, so the number is permanently correct
and is the most precise pointer available. The convention targets citations into
live source and into living design docs only.

### Additional context

No change is proposed to the `claude-plugin-dev` repo beyond its own fix pass,
and nothing here asks `/design` to verify citations — only to stop emitting the
form that cannot survive its own plan's execution. If a verification step is
wanted later, the natural owner is the outline corrector, not the author.
