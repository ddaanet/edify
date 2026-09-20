# Item 1.7 — `/build` fires TDD execution on an item carrying `Slices:`

Requirements: M-3, M-6. Key decision: KD-4.

Files changed: `plugin/skills/build/SKILL.md`,
`plugin/skills/build/references/tdd-slice.md`.

## `plugin/skills/build/SKILL.md`

Line count: **222 before, 221 after** (net −1, against the ~200 hub
guideline).

### §4 intro, lines 103-108 → 103-108

Before:

```
Walk the work in order: a runbook's phases and items, or the design's changes.
Per item, decide **at dispatch time** whether to do it in session or delegate.
The decision is the batching rule — an agent offsets context churn in this
session, so one agent owning a run of mechanical edits is right where one
agent per edit is not. A runbook item's type plays no part in it: type
determines item format, and for `tdd` the dispatch structure, nothing else.
```

After:

```
Walk the work in order: a runbook's phases and items, or an outline's or
design's items. Per item, decide **at dispatch time** whether to do it in
session or delegate — the batching rule: an agent offsets context churn in
this session, so one agent owning a run of mechanical edits is right where one
agent per edit is not. No type plays a part: §4.3 fires on the item carrying
`Slices:`, whether a runbook, an outline or a design holds it.
```

Two changes in one paragraph:

- "or the design's changes" → "or an outline's or design's items", since an
  outline routed to `/build` is now one of the artifacts walked, and both
  carry *items* rather than "changes".
- The type sentence no longer keys the dispatch structure on a type at all.
  Type is dropped as a selector rather than restated, because in a runbook
  `tdd` is a *phase* attribute and an outline has no phases to carry it. The
  selector named is the item-level `Slices:` marker, with the artifact
  explicitly not mattering — which carries KD-4's "whichever artifact holds
  it" once, so §4.3 need not repeat it.
- "The decision is the batching rule —" folded into the preceding sentence to
  hold the paragraph at six lines.

### §4.3, lines 129-131 → 129-130

Before:

```
**When the item's type is `tdd`:** it lists behaviour slices. Read
`references/tdd-slice.md` and execute each slice by it — four dispatches and
the after-the-slice steps.
```

After:

```
**When the item carries `Slices:`** it carries nothing else to execute: Read
`references/tdd-slice.md` and execute each slice by it.
```

The trigger moves from the type to the marker. "it carries nothing else to
execute" replaces "it lists behaviour slices": the fact the hub needs at this
point is that no general work hides in such an item, not a restatement of
what `Slices:` holds. The "four dispatches and the after-the-slice steps"
tail was dropped — `tdd-slice.md`, which the very next clause Reads, is where
both are defined, and dropping it is what buys the line that keeps the hub
net-negative. The Read of `references/tdd-slice.md` is kept, skill-relative.

The `### 4.3 TDD items` heading is unchanged: "TDD" there names the kind of
work, not an item type, and KD-4 does not falsify it.

### §References, line 214

Before:

```
- **`references/tdd-slice.md`** — §4.3, a `tdd` item's slices
```

After:

```
- **`references/tdd-slice.md`** — §4.3, an item carrying `Slices:`
```

Aligned with §4.3's trigger.

## `plugin/skills/build/references/tdd-slice.md`

Line count: 54 before, 56 after (no cap applies — a `references/` node's
guideline is 400).

### Lines 3-5 → 3-7

Before:

```
A tdd item lists behaviour slices. Execute slice `N.M/k` as four dispatches,
each composed per `dispatch-composition.md`, then take the after-the-slice
steps. Only a tdd item reaches this file.
```

After:

```
An item carrying `Slices:` lists behaviour slices and carries nothing else to
execute. It reaches here from a runbook, or from an outline or design routed
to `/build`. Read `dispatch-composition.md` and compose by it each of the four
dispatches that execute slice `N.M/k`, then take the after-the-slice steps.
Only such an item reaches this file.
```

Three changes:

- "A tdd item" → "An item carrying `Slices:`", and "Only a tdd item reaches
  this file" → "Only such an item reaches this file" — the type-keyed
  entry condition, which KD-4 falsifies, becomes the marker-keyed one. The
  originating artifact is now stated explicitly here, because this file is
  reached directly and carries no other statement of where its work comes
  from.
- "each composed per `dispatch-composition.md`" → "Read
  `dispatch-composition.md` and compose by it" (M-6). The pointer was a
  citation the reader could satisfy by assuming they knew the content; it is
  now an act taken while the file is open. Cited as the bare sibling name,
  matching how this file cites `dispatch-composition.md` at line 28 and
  `SKILL.md` at line 43.

### Other "tdd item" / "type" uses in the file — checked, none changed

- Line 1, `# TDD Slice Execution` — names the kind of work.
- Lines 27-28, "`<type>: Item N.M/k — <title>` … The type is the executor's
  choice" — the *commit* type, unrelated to item type.
- Line 41, "`<type>: Item N.M/k — code-review fixes`" — likewise the commit
  type.

## Constraints

- No repo-relative `plugin/…` path appears in any text written here. The four
  paths written are `references/tdd-slice.md` (×2, skill-relative from the
  hub), `dispatch-composition.md` (sibling) and `/build` (a skill name, not a
  path). Pre-existing repo-relative paths elsewhere in both files were left
  untouched.
- `verify-step.sh` call sites, §2, §5 and `finishing.md` untouched.

## Precommit

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit`, full output:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

`docs: Item 1.7 — /build fires TDD execution on an item carrying Slices`
