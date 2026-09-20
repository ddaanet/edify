# Item 1.1 — corrector Provenance repair table

**Date:** 2026-09-20
**Commit:** `a11008a65612bb492b12a3b3145d5653b9de7aab` — `📝 Item 1.1 — corrector Provenance repair table`
**Requirements:** M-1, M-2, M-3

## Changes

### `plugin/agents/outline-corrector.md`

- **§3 Review Criteria → Clarity, line 96** (new): one criterion — an item
  carrying `Slices:` states each test's assertion in prose, the exact expected
  value/pattern/behaviour, specific enough that two executors would write the
  same test; cites `runbook-format.md` in the `runbook` skill's `references/`
  and its §"Assertion quality". Severity Major when unstated or vague, on the
  ground that such a slice cannot be dispatched RED. No repo-relative
  `plugin/…` path used, per the job's cross-cutting rule.
- **§3 Review Criteria → Provenance, lines 118-133**: the final bullet
  (`**Never fill in `Base:` yourself.** …`) replaced by KD-1's seven-row
  `Found`/`Repair` table and the three invariants stated under it. The four
  detection bullets above it (now 113-117) are unchanged.

### `plugin/agents/design-corrector.md`

- **§3.5 Check Provenance, lines 176-191**: same replacement of the final
  bullet, with the block byte-identical to outline-corrector's. The four
  detection bullets above it (172-175) are unchanged; their lack of terminal
  periods is left as found.

Nothing else was touched in either file. `corrector.md`, `docs/design.md` and
all skills are untouched.

## Shared-block diff

Extracted lines 118-133 of `outline-corrector.md` and lines 176-191 of
`design-corrector.md` and diffed them:

```
$ diff "$TMPDIR/a.txt" "$TMPDIR/b.txt" && echo "IDENTICAL"
IDENTICAL
```

The two blocks are byte-identical, table and invariants alike.

## Precommit

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

Green. The test sentinel reported the suite cached — the change is markdown
only, so no test input moved.

## Tree state

`git status --porcelain` empty after the commit.
