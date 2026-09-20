# Item 1.4 — scope "as shown" to the Provenance labels

Requirement: m-1 (`plans/provenance-reach-and-sweep/reports/deliverable-review.md`
§Minor Findings, item 1).

Target: `plugin/skills/design/references/research-protocol.md`, the sentence
that closed §A.5's example outline (line 41 before the edit).

## Before

```
Write the Provenance heading and its two fields as shown; adapt the rest.
```

Read literally, "as shown" covers the example block's values, and the block
carries `Derived from: none` — the first-pass case. A second-pass author
following the sentence copies `none`.

## After

```
Only the `## Provenance` heading and the two field labels are as shown; both
values come from `references/design-content-rules.md` §Provenance Section, which
the Content list above routes through. The example's `none` and its `Base:` are
one first-pass case, not values to copy. Adapt the rest.
```

"As shown" now covers the heading and the labels only. The values are attributed
to the rule the file already routes through in its **Content** list
(`- Provenance -- Read references/design-content-rules.md §Provenance Section
and write the section it specifies`), which is where the first-pass /
second-pass split for both fields is stated.

The reference is written `references/design-content-rules.md`, matching the
existing citation in the same file; no repo-relative `plugin/…` path introduced.
The example block and every other line are untouched — one sentence replaced by
three short ones.

## Validation

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

`docs: Item 1.4 — scope "as shown" to the Provenance labels` — the single commit
carrying both the edited file and this report. Its hash cannot be written here
(the report is part of the commit it would name); it is in the reply that
delivered this report, and in `git log --format='%H %s' -1 --grep='Item 1.4'`.
