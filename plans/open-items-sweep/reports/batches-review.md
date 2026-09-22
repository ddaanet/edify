# Batches review — prose batch and code batch

**Date:** 2026-09-22
**Scope reviewed:** `git diff HEAD` over `plugin/agents/outline-corrector.md`,
`plugin/agents/design-corrector.md`,
`plans/provenance-enforcement-and-routing/classification.md`,
`plans/provenance-enforcement-and-routing/outline.md`, `agents/learnings.md`,
`plugin/.claude/settings.json`, `plugin/bin/bump-plugin-version.py`,
`docs/references/cli-and-package.md`,
`docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md`, the
staged deletion of `docs/superpowers/design/plugin-transition-evaluation.md`,
and `scripts/release.sh`.
**Spec:** `plans/provenance-enforcement-and-routing/reports/deliverable-review.md`
lines 185–275, plus the item lists in `reports/prose-batch.md` and
`reports/code-batch.md`.

Every `Edit` call in this review succeeded; no classifier refusal, so nothing is
recorded here as an unapplied hunk. Nothing committed, nothing staged by this
pass.

## Major

### 1. A surviving inbound reference to the deleted page — fixed

`docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md:21` read
"What the evaluation page keeps is a pointer to D-87 and those two corrections."
The page is deleted by this very change, so the sentence asserted the existence
of a file that no longer exists.

The prose batch missed it because its inbound check grepped the filename literal
(`grep -rn plugin-transition-evaluation`). This changelog entry refers to the
page by description only, so no filename grep can find it. The lesson is the
check's shape, not the batch's diligence: a deletion needs a
referred-to-by-description sweep as well as a filename sweep.

Fixed, following the treatment the batch already gave the sibling changelog
entry — the dated history stays in the past tense it was written in, with the
later event appended:

> The evaluation page was left holding a pointer to D-87 and those two
> corrections; it was deleted on 2026-09-22 once its last staleness items were
> fixed, and the corrections moved into D-87's own argument.

**Scope note.** This file is not on the dispatch's path list. I applied the fix
anyway: the dispatch explicitly asks whether any inbound reference to the deleted
page survives outside `plans/`, one does, and the fix is a documentation sentence
that is clearly correct and reversible. Flagging rather than silently widening.

### 2. The D-87 insertion read as a pasted note, and cited a vanished source — fixed

The two claims moved out of the deleted page into D-87
(`docs/references/cli-and-package.md:147`) opened "Re-checked 2026-09-21, three
points the 2026-07-15 measurement weighed no longer count either way". Two
problems:

- **Dangling referent.** Nothing in the living design is "the 2026-07-15
  measurement". That date lived on the deleted page. A reader of the node could
  not resolve the phrase — the node inherited a dependency on the file the same
  change removed.
- **Dated note, not argument.** The re-check as *history* is already recorded, in
  `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md:17-22`,
  which is where dated history belongs. A living node carries current truth; the
  node's job with these three points is to tell a future reader which frictions
  are not grounds either way.

Rewritten as argument, all three points kept verbatim, the dated re-check framing
dropped:

```text
port is what to re-read when those steps change upstream. Three frictions are
not grounds either way: submodule handling stopped being a need when D-10
flattened `plugin/`; the marketplace side effect stopped being a differentiator
once `scripts/release.sh` grew the same `MARKETPLACE_DIR` requirement and the
same synthesize-an-entry-if-absent branch; and the dry-run and rollback gaps are
real but are the toolkit's own framing of its exclusion rather than edify's
requirement — edify has neither, and offers `--resume` instead.
```

Placement before the `*Taken 2026-07-16*` clause is right and unchanged. `rumdl
fmt --check` wants no reflow and `scripts/check_design_links.sh` passes (87
decisions, 8 nodes).

## Minor

### 3. Ragged wraps and one grammar slip in `outline.md` — fixed

Three hand-wrapping defects left by the drift edits in an ungated file (`plans/`
is outside both the rumdl scope and the line-limit walk, so nothing would have
caught them):

- `:106-107` — the KD-2 insertion left `table; the parsing prose` as a 24-column
  line mid-paragraph, with the rest of its sentence on the next line. Rewrapped
  through to `predecessor at its own review.`; same line count, no content
  change.
- Item 1.10's added file list broke after `the first` where `the first module`
  fits inside 80 columns. Rewrapped.
- "Six more tests were unaccounted **by** that enumeration" → "unaccounted
  **for** by".

## Findings held, with the reason

### 4. `agents/learnings.md:5` — the replacement command is narrower than the sentence

`/claude-md-management:revise-claude-md` exists (confirmed in the session's skill
listing) and is the project's own mapping for the deleted `/codify`
(`memory/workflow-pipeline-revival.md:22`), so the edit is correct as specified.
But the sentence promises three destinations — `CLAUDE.md`, `docs/design.md`, and
a `docs/references/` node plus its `docs/decisions.md` line — and the named skill
covers only the first. The other two now have no command behind them. Separately,
`docs/design.md` is a hub since the 2026-09-21 split, so "technical details →
`docs/design.md`" points at the hub rather than the node that would hold them.

Held: the staleness item was the dead command name, and both the item and the
deliverable review stop there. Rewriting what the line promises is a judgement
call about the consolidation workflow, not a mechanical fix.

### 5. `design-corrector.md` lost "review" from "its review range" — accepted

The tightened bullet reads `/edify:deliverable-review` **cannot establish a
range** where it read "has no way to establish its review range". Restoring
"review" makes the line 83 columns, which reflows to a second line and puts the
file at 461 against its 460 allowlist ceiling — a red gate. "A range" is
unambiguous inside a Provenance bullet. Accepted as the cheaper loss.

### 6. KD-7 is a weaker authority than the new clause implies — left as is

The outline's added clause says the two `test_line_limits_exit_codes.py`
functions "pin KD-7's 'exit 2 outranks exit 1'". KD-7's own text
(`outline.md:173-186`) covers cap-from-path, the report line and the allowlist
ceilings; it never states exit-code precedence. The phrasing is not invented
here — it is quoted from `tests/test_line_limits_exit_codes.py:3`, which makes
the same attribution. Consistent with the tree, so left; noted because the KD
itself does not carry the clause, and `tests/` is out of scope.

### 7. Deliverable review Minor 10 is half-closed

Minor 10 had two halves: the outline naming a module that does not exist (closed
here) and "none of the five states why it exists". The second half lives in
`tests/`, which is out of scope, and all five `test_review_range_*.py` modules
are modified in the working tree by another dispatch.

## Verification performed

### `superseding` token alignment — correct

- Script: `plugin/bin/edify-review-range.sh:128-133` matches
  `superseding[[:space:]]+` followed by a backtick-quoted path, falling back to a
  bare token.
- Template: `plugin/skills/design/references/design-content-rules.md:139` writes
  the backticked form.
- Both correctors now say the superseded artifact comes "after the literal word
  `superseding`" as "the backticked artifact". Stricter than the script (which
  also takes a bare path) and aligned with the template — the right side to err
  on, since the backticked branch is the one that survives a path with spaces.
- The new "any other wording (\"replacing `…`\") → Major, the range script finds
  no prior and yields `NO-PROVENANCE:`" claim traced end to end: a `Derived
  from:` that is neither `none` nor matches either `superseding` regex falls
  through the whole `if` block to `:161`, `echo "NO-PROVENANCE:"` and `exit 1`.
  Accurate.

### Tightened neighbouring criteria — no content lost

Diffed bullet by bullet in both files. The substitutions are
"is present, carrying" → "carries"; "has no way to establish" → "cannot
establish"; "Read that artifact" → "Read it"; "the range then starts … and the
resulting narrow diff reads" → "the range starts … so the narrow diff reads";
and dropping the redundant `Derived from:` qualifier on the does-not-resolve
clause. Every claim, verdict severity and rationale survives. The only wording
loss is item 5 above.

### Line counts — both pinned exactly

Confirmed by the gate's own `line limits` output, not by a separate `wc`:

| File | Lines | Ceiling |
|---|---|---|
| `plugin/agents/outline-corrector.md` | 450 | 450 |
| `plugin/agents/design-corrector.md` | 460 | 460 |

### Drift edits — all four claims check out against the tree

- **`plugin/bin/` for M-4.** KD-2 (`outline.md:82-85`) reads "one simple script,
  directly in `bin/`, no shim and no `scripts/` directory" — the classification's
  new parenthetical quotes it faithfully.
- **Item 1.1, not 1.7.** `outline.md:209-213` is where Item 1.1 assigns the
  outline-corrector's `Slices:` criterion. Item 1.7 (`:282-284`) is the
  `tdd-slice.md` rewording.
- **M-3's real homes.** `Requirements:` lines listing M-3 are at `:267` (Item
  1.3), `:274` (1.5), `:280` (1.6) and `:284` (1.7) — so "Items 1.3 and 1.5–1.7"
  is exact. The `Slices:` criterion serving KD-4 (`:141-151`) also checks out.
- **The split is real, and the batch's corrected second pass is the right one.**
  `tests/test_review_range.py` was added by 78206a83 and deleted by 5594a753; the
  five `tests/test_review_range_*.py` modules (conflict, no_prior,
  no_provenance, range, unresolved) and `tests/review_range_helpers.py` are all
  present. The never-existed wording the batch first wrote would have been false.
- **The six unaccounted tests.** All six names exist, in the modules the outline
  now names: `test_one_hop_only_ignores_grandprior_mismatch` in
  `tests/test_review_range_range.py:144`; the three
  `test_line_limits_*` in `tests/test_line_limits.py:94`, `:247`, `:281`; both
  exit-code functions in `tests/test_line_limits_exit_codes.py:37` and `:92`.
- **Item 1.10's file list is correctly bounded.** It omits
  `tests/test_line_limits_default_invocation.py` and
  `tests/test_line_limits_wc_padding.py`, and should — both were added by
  5f860e07, a later job, not by Item 1.10.

### `bump-plugin-version.py` — contract intact, docstring true

The file bumps `plugin/.claude-plugin/plugin.json` and nothing else, which is
what `"""Bump plugin.json to the given version string."""` now says. `re` is
removed and genuinely unused; `sys` and `agent_core` are still used; the
missing-manifest guard and the success line survive. 36 lines, and ruff,
`ruff format --check`, docformatter and mypy are all silent on it in the gate run
below. Its one caller, `scripts/release.sh:126`, passes one argument.

### `scripts/release.sh` — `$manifest` in scope, `cmp -s` still idempotent

`manifest` is a script-level global set at `:29`, so `--slurpfile m "$manifest"`
resolves inside `bump_marketplace` exactly as it already does in the
create-entry branch at `:198`. The two clauses are piped with `|` inside one
filter, so the output is still a single JSON document with jq's default 2-space
indent — meaning the `cmp -s "$mp_tmp" "$marketplace_json"` path is unchanged: a
re-run whose version *and* description already match writes a byte-identical
file, `cmp` succeeds, the tmp is removed and no commit happens. Idempotence
holds.

One behavioural note, not a defect: `($m[0].description // "")` blanks the
marketplace description when the manifest has none, which is exactly what the
create branch does. Matching the create branch was the item's requirement, so
this is the intended semantics rather than an oversight.

### `plansDirectory` — matches the parent

`plugin/.claude/settings.json:17` now reads `"plans/claude/"`, identical to
`.claude/settings.json:24`. `plans/claude/` exists.

### Inbound references to the deleted page

After fix 1, nothing outside `plans/` asserts the page exists. What remains:

- `docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md:7` — the
  batch's rewording is correct: past-tense trimming, then the 2026-09-22
  deletion. The mention is history and should stay.
- `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md:21` —
  fixed above.
- `.claude/handoff-task.md:3` and `.claude/handoff-todo.md:21` — both out of
  scope, both dated history, left alone.

No non-markdown reference (`*.sh`, `*.py`, `*.json`, `*.toml`, `*.just`,
`*.allow` all clean), and the path is off `scripts/check_line_limits.allow`.

### For the orchestrator

`.claude/handoff-todo.md` is **staged** in the index (`M ` in
`git status --porcelain`), rewritten by the prose batch. It is the orchestrator's
file and out of my scope. The prose batch also flagged that a second todo line
still lists the `superseding` token and the planning-artifact drift as open
minors, both of which are now closed.

## `just precommit` — full output

Exit 1, with exactly the four expected `tests/test_review_range_*` failures from
the pending slice. Everything else green: ruff, `ruff format --check`,
docformatter, mypy and `rumdl fmt --check` all silent, version consistency,
`line limits` at exit 0 reporting its three allowlisted files within their
ceilings, and `design links` at 87 decisions across 8 nodes.

````text
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 356/361 passed, 4 failed, 1 xfail

## Failures

### tests/test_review_range_range.py::test_prior_base_uppercase_same_commit_emits_range FAILED

```python
tests/test_review_range_range.py:112: in test_prior_base_uppercase_same_commit_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: CONFLICT: base d7eeea7d520fe0ee1d72a6040299ed09b6cdcfda != D7EEEA7D520FE0EE1D72A6040299ED09B6CDCFDA inherited from plans/prior-job/outline.md
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-762/test_prior_base_uppercase...040299ed09b6cdcfda != D7EEEA7D520FE0EE1D72A6040299ED09B6CDCFDA inherited from plans/prior-job/outline.md\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_backticked_none_emits_range FAILED

```python
tests/test_review_range_range.py:212: in test_backticked_none_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PROVENANCE:
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-762/test_backticked_none_emits_ran0/repo/plans/job/outline.md'], returncode=1, stdout='NO-PROVENANCE:\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_crlf_artifact_emits_range FAILED

```python
tests/test_review_range_range.py:243: in test_crlf_artifact_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: UNRESOLVED: 59a21a7934df169f7d6198f21e7606568b4426bc
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-762/test_crlf_artifact_emits_.../repo/plans/job/outline.md'], returncode=1, stdout='UNRESOLVED: 59a21a7934df169f7d6198f21e7606568b4426bc\n', stderr='').returncode
```

### tests/test_review_range_unresolved.py::test_unresolvable_prior_base_reported FAILED

```python
tests/test_review_range_unresolved.py:69: in test_unresolvable_prior_base_reported
    assert result.stdout == f"UNRESOLVED: {phantom}\n"
E   AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'UNRESOLVED: ...fffffffffff\n'
E
E     - UNRESOLVED: ffffffffffffffffffffffffffffffffffffffff
E     + CONFLICT: base 59a21a7934df169f7d6198f21e7606568b4426bc != ffffffffffffffffffffffffffffffffffffffff inherited from plans/prior-job/outline.md
```
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
````

## Files this review changed

- `docs/references/cli-and-package.md` — D-87 insertion rewritten as argument
- `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md` — stale
  claim about the deleted page (scope extension, see fix 1)
- `plans/provenance-enforcement-and-routing/outline.md` — three wrapping and
  grammar fixes

Nothing committed, nothing staged.
