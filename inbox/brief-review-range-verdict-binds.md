## Brief: deliverable-review's exit-0 range is binding, whatever other documents say

2026-10-07

From sandbox-lies. A memory fact there recorded this rule, and it is being
retired in favour of the skill stating it. Nothing is tracked in sandbox-lies
after this note. Sections are named, not line-numbered.

### The gap

`plugin/skills/deliverable-review/SKILL.md`, the step "Establish the review
range", has a verdict table whose exit-0 row reads `RANGE: <base>..HEAD` →
"proceed with it". The table does not say that this verdict outranks a
narrower scope stated elsewhere. In one run, the reviewing agent printed and
read `RANGE: 52e6dd8..HEAD` (exit 0) and then reviewed `d61e60a..HEAD`
instead. Two documents had scoped the review more narrowly:

- the task file: "the review covers this build's commits";
- the outline's Provenance: an earlier review "ran over `e873bf4..HEAD`" and
  "a reviewer of this job should do the same".

My human partner rejected that review as failing to follow the skill's
directive. Its report was set aside and the review re-run over the printed
range. In the re-run, the review again met both scoping sentences, reviewed the
printed range, and named the disagreement in the report's Inventory. My human
partner accepted that as the correct behaviour.

### Decisions (from my human partner)

- Exit 0 decides the range. Only the exit-1 rows open a question.
- A scope sentence in a task file, an outline or design (Provenance or
  otherwise), a delegate status file or an earlier report is input, not an
  override.
- When a document disagrees with the printed range, review the printed range
  anyway and name the disagreement in the report's Inventory. Never resolve it
  by choosing another base, and do not stop to ask.

### Suggested change (wording is edify's call)

- On the exit-0 row, or as one sentence under the table: the printed range is
  reviewed whole; a narrower scope stated in any other document is recorded in
  Inventory, not applied.
- The report template's Inventory (`references/example-report.md`, and the
  report-structure section of `SKILL.md`) gets a slot for a "Scope
  disagreements" line, so the place to record a disagreement already exists
  when one is met.
- Consider whether the outline or design template's Provenance section should
  stop prescribing a base to later reviewers, since the script derives the
  base. A Provenance base that differs from the script's result is the same
  conflict the exit-1 `CONFLICT` row already handles for inherited bases.

### Constraints

- Keep the table's existing CONFLICT wording ("do not substitute a range").
  The new sentence extends that prohibition to exit 0; it does not replace it.
- Per the `craft:directive-writing` style, state it as the act to perform
  (review the printed range, record the disagreement), not as a narrative of
  this incident.

### Additional context

- The skill body is the one instruction certain to be in front of the agent
  when it reads the verdict line. A memory fact in a consumer repo reaches the
  agent only if recall fires, and the fact this brief replaces is being
  removed.
