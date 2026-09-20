# Item 1.5 — route by need for the runbook layer

Target: `plugin/skills/design/references/route-to-execution.md` (60 → 67 lines).
Requirements: M-3, m-3. Specification: outline KD-3, KD-4, KD-5.

## Requirement-to-line checklist

| Requirement | Where it lands |
|---|---|
| KD-3 route table, verbatim three branches | `:31-35` |
| KD-3 "first branch is a hard gate" sentence deleted | absent (was `:33`) |
| KD-3 prose-path branch and **Prose path rationale** paragraph deleted | absent (was `:27`, `:35-39`) |
| KD-3 commutativity definition relocated under the first discriminator | `:44-48` |
| KD-3 `test↔implementation` example dropped | absent; only `build↔verify` at `:47-48` |
| KD-3 "Implementation loops" discriminator deleted | absent (was `:46`) |
| KD-3 second discriminator, marked ungrounded with no threshold | `:49-51` |
| KD-3 first precondition binds every branch | `:15` |
| KD-3 second precondition binds `/build` branches only, evaluated after the route (M-3) | `:15-17` |
| KD-3 Simple / Moderate-agentic-prose sentence kept | `:17-19` |
| KD-3 what `/runbook` adds, stated | `:39-42` |
| KD-4 second precondition gains "slices written", in `runbook-format.md`'s item shape | `:24-27` |
| KD-5 scope sentence covers all four callers | `:3-6` |
| KD-5 precondition-failed branch gains the Phase 0 Moderate non-prose return point | `:58-61`, "Do not route." kept at `:61` |
| m-3 mislabelled final `ELSE` gone | `:34` is a bare `ELSE` |
| Cross-cutting rule: no repo-relative `plugin/…` path | `grep -n 'plugin/'` — no match |
| Closing per-sub-problem paragraph untouched | `:63-67` |
| Under 400 lines | 67 |

Paths written are skill-relative from `design/`:
`../runbook/references/runbook-format.md` (`:27`),
`../build/references/phase-boundary.md` (`:40`).

## Not applied

Nothing in KD-3, KD-4 or KD-5 scoped to this file was left unapplied.

Two wording choices worth recording. The scope sentence names the callers by
role (both sufficiency gates, C.5, the Phase 0 Moderate non-prose route)
rather than by file and line, as instructed. And the two preconditions stayed
one bullet each: KD-4's "slices written" clause joined the edit-targets
bullet rather than becoming a third precondition, since both bind the same
branches and KD-4 words it as a gain on the second.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

The single commit carrying both the edit and this report, subject
`📝 Item 1.5 — route by need for the runbook layer`. A commit cannot
name its own hash; read it with `git log --oneline -1` on the commit whose
subject is above.
