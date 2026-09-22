# Release-mechanism decision recorded (D-87); D-9 rewired as reversed

Two rounds. Round 1 recorded the release-mechanism decision as D-87. Round 2,
on the lead's measurement that publication shipped, rewired D-9 and swept the
tree for postponement claims.

## Top finding — one of the lead's premises is wrong

**The marketplace entry is not missing. It exists.** Instruction (b) said to
reword `docs/marketplace.md:20` to "what is actually still missing (the entry
in `../claude-plugins/.claude-plugin/marketplace.json`)". I checked that file
read-only before writing the sentence, and it carries:

```
edify  0.2.0  {"source":"git-subdir","url":"ddaanet/edify","path":"plugin"}
```

This is my own measurement, not the lead's. `docs/marketplace.md` now says the
entry exists. Two memory files are stale on the same point, listed below. I
made no edit in `/Users/david/code/claude-plugins`.

**The reason for the reversal is unrecorded.** I checked `docs/changelog/`,
`memory/distribution-published.md`, `memory/plugin-transition-eval.md`,
`memory/MEMORY.md` and the git history either side of 2026-08-04. The parent
commit `c6fe1dbc` ("📝 record edify-cli 0.0.3 PyPI publication") is a memory
submodule bump and nothing else. The memory-side commit message says the
postponement "was reversed and 0.0.3 shipped via `just release`, verified
end-to-end through the SessionStart bootstrap resolving from PyPI" — that is
the *occasion*, not a stated rationale. Both D-9 and the new changelog entry
say the reason is not recorded, and neither invents one.

## Files changed

| Path | Lines | Change |
|---|---|---|
| `docs/references/cli-and-package.md` | 71-82 | D-9 rewired: lead kept, `*Reversed 2026-08-04:*` pointer, surviving ordering constraint |
| `docs/references/cli-and-package.md` | 122-158 | D-87 added after D-13 |
| `docs/references/cli-and-package.md` | 220-231 | Three rejected alternatives |
| `docs/decisions.md` | 23-25 | D-9 index line gains the reversal parenthetical |
| `docs/decisions.md` | 34-35 | D-87 index line |
| `docs/decisions.md` | 43-45 | Three rejected alternatives appended to the group's `*Rejected:*` line |
| `docs/design.md` | 25-32 | §1 "Do not re-litigate": publication postponement replaced by D-87 |
| `docs/design.md` | 158-163 | §5.1 gains the release/publish/marketplace ordering sentence |
| `docs/design.md` | 328-330 | §9: "Publishing to PyPI and the marketplace" non-goal deleted; the no-user-base non-goal absorbs the published-not-consumed fact |
| `docs/marketplace.md` | 19-23 | The "waits on the first PyPI publish" wait is over; entry exists |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 14-17 | "the parked entry" → "the entry that now uses it" |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 34-51 | §2 body replaced by a pointer to D-87 plus the two corrections the node does not carry |
| `docs/changelog.md` | 15-16 | New top bullet (D-87) |
| `docs/changelog.md` | 50-51 | New 2026-08-04 bullet (reversal) |
| `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md` | new, 22 | |
| `docs/changelog/2026-08-04-publication-postponement-reversed.md` | new, 22 | |

## D-87

**Conclusion line (node lead and index line, verbatim identical):**

> **D-87 — The release recipe is edify's own, because the shared plugin toolkit
> excludes hybrid repos by design.**

The argument records what `scripts/release.sh` does — including, per (d),
plainly that it publishes the wheel to PyPI, and that the publish sits between
the tag push and the GitHub release, which is where the D-9 ordering constraint
binds. It records that `claude-plugin-dev` rules edify's shape out in its own
record (repo non-goal and stated limitation, both quoted); that the excluded
shape is §5.1's two products in one tree with versions in lockstep (NFR-4); the
three structural gaps (no PyPI step and no `pyproject.toml` awareness, single
manifest rather than two version files, manifest resolved at the repo root
while edify's sits a directory down); what adoption drags in (subtree
vendoring, an imported justfile, a PreToolUse hook denying `.version` edits);
that the script lives at the repo root rather than under `plugin/`, because
that directory ships verbatim to every install and `MARKETPLACE_DIR` paths and
PyPI credentials have no business inside it; and that edify's script is a
near-verbatim port of the toolkit's GitHub and marketplace steps rather than
independent invention. Dated *Taken 2026-07-16 (user decision)*, framed
keep-now-migrate-later, with a `*Reopen-if:*`.

**Rejected alternatives named** — three, in the node's
`## Rejected alternatives` section and on the group's `*Rejected:*` line:

- **Extending `claude-plugin-dev` to cover hybrid repos** — reverses that
  project's documented non-goal; by its own reasoning the conditionals would
  obscure its main path or break edify outright.
- **Un-hybridising edify so the toolkit fits** — the single-manifest model would
  apply if the plugin were published as its own thing again, which is what D-10
  undid.
- **Adopting the toolkit on the grounds that its exclusion predates the merge**
  — the exclusion stands in that project's current record, so adopting anyway is
  edify deciding another project's scope for it. It is D-87's reopen gate, not a
  route around it.

These are the eval's options 1, 3 and 4; option 2 is the decision.

## D-9 rewired

Superseding shape copied from D-31 in `pipeline-contracts.md`: the original lead
stays intact, a `*Reversed 2026-08-04:*` pointer states current truth, and the
part of the decision that survived is kept rather than dropped with the rest.

- **Node** (`cli-and-package.md:71`) — lead unchanged; the reversal, the PyPI
  0.0.3 ship, the marketplace `git-subdir` entry, "Edify is installable", the
  unrecorded-reason statement, and the surviving ordering constraint (the
  bootstrap installs `edify-cli==<plugin version>`, so the package can never lag
  the plugin) with a pointer to where `scripts/release.sh` encodes it.
- **Index** (`decisions.md:23`) — `- **D-9** — Publication is postponed
  indefinitely (2026-07-17, user decision) (reversed 2026-08-04: `edify-cli`
  0.0.3 shipped and the marketplace entry exists).` The node lead is a strict
  prefix of the index conclusion, which is what `check_design_links.sh`'s
  `conclusion-mismatch` rule requires of a superseded decision.

Nothing was erased: the postponement is still legible as the position that was
held, and the incorrect parts of its body ("The marketplace manifest has no
`edify` entry, so edify is uninstallable meanwhile") are gone rather than left
standing as false current truth.

## Sweep for postponement claims — (c)

`rg -U -i "postpon|parked|not yet publish|uninstallable|no .edify. entry|waits
on|before the first publish|not on pypi|is not published"` over `docs/`,
`plugin/`, `CLAUDE.md`, `README*`, `scripts/`, `src/`, `tests/`, `justfile`.

**Fixed:**

1. `docs/references/cli-and-package.md:71-76` — D-9 body (above).
2. `docs/decisions.md:23` — D-9 index line (above).
3. `docs/design.md:26` — §1 "Do not re-litigate" listed "the publication
   postponement (D-9)". It *was* re-litigated and reversed, so it is no longer a
   settled-question entry. Replaced with D-87, which genuinely is one.
4. `docs/design.md` §9 Non-goals — "**Publishing to PyPI and the marketplace** —
   parked indefinitely by user decision (D-9), not blocked." Deleted; publishing
   is not a non-goal, it is what happens. The neighbouring cross-version
   non-goal absorbed the durable half: published, but nothing outside this repo
   consumes either artifact, so compatibility still justifies nothing.
5. `docs/design.md` §5.1 — now states the release ordering (PyPI before the
   marketplace bump) rather than leaving publication unmentioned.
6. `docs/marketplace.md:19-21` — the "waits on the first `edify-cli` PyPI
   publish" wait is over; rewritten to say the entry exists, with its
   `git-subdir` shape and the fact that `scripts/release.sh` bumps it last.
7. `docs/superpowers/design/plugin-transition-evaluation.md:15` — "the parked
   entry" → "the entry that now uses it".

**Deliberately left alone:**

- `docs/changelog/2026-07-17-bootstrap-reversed-from-stdlib-venv-to-uv.md:10-12`
  — "Publication was postponed indefinitely by user decision the same day (D-9)
  … so edify is uninstallable meanwhile." This is a write-time record of
  2026-07-17 and was true then. `craft:design-doc-writing` splits write-time
  record from current truth, and changelog entries are the former; rewriting one
  destroys the audit trail the changelog exists to be. The new 2026-08-04 entry
  is what a reader reaches next.
- `src/`, `tests/`, `plugin/`, `CLAUDE.md`, `README*`, `justfile`, `scripts/` —
  no hits at all except `scripts/release.sh:82`, which is a die-message about a
  plugin having no marketplace entry (generic script logic, not a claim about
  edify).

## Changelog entries

Both design-significant.

- `docs/changelog/2026-08-04-publication-postponement-reversed.md` — leads with
  the reversal, states in bold that the reason is not recorded anywhere in the
  repo, keeps the surviving ordering constraint, and closes on
  published ≠ consumed.
- `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md` — the
  decision getting a home, the exclusion that makes it structural, and the two
  frictions that re-checking dropped.

## Claims verified, corrected, dropped

Verified against `/Users/david/code/edify` and, read-only, against
`/Users/david/code/claude-plugin-dev` and `/Users/david/code/claude-plugins`.
No edit was made in either other repo.

- **Both `claude-plugin-dev` exclusion quotations survive; neither citation
  does.** The eval cited `CLAUDE.md:91-94` and `DESIGN.md:320-325`. `DESIGN.md`
  no longer exists — the limitation is in `docs/design.md` under
  "## Limitations" — and the CLAUDE.md non-goal moved down the file. I wrote
  both quotations without file:line, since both have already moved once.
- **No PyPI step in the toolkit** — confirmed:
  `grep -i "dry.run\|uv build\|uv publish\|pypi"` over `toolkit/release.just`,
  `toolkit/release.sh` and `toolkit/install.sh` returns nothing.
- **Manifest hardcoded root-relative** — confirmed, citation stale. The toolkit
  now has both `release.just` and `release.sh`; the hardcoded
  `manifest=".claude-plugin/plugin.json"` is at `release.sh:25`, not the eval's
  `release.just:28`. Fact written, line number dropped.
- **Subtree vendoring** — confirmed (`git subtree add --prefix=...`) at
  `install.sh:95`, not the eval's `install.sh:63`. Line number dropped.
- **`version-guard.sh` denies Write/Edit of `.version`** — confirmed from its
  header. It governs *agent* edits; `scripts/release.sh` bumps through a
  Bash-run Python script, so this is a side effect of adoption, not a blocker.
  Written as the former.
- **Two versions in lockstep** — confirmed:
  `plugin/bin/check-version-consistency.py` compares `plugin.json` against the
  `[project]` version in `pyproject.toml`; `scripts/release.sh` calls it twice
  (preflight, and after the bump) and syncs via `uv version`.
- **Script at the repo root, not under `plugin/`** — the reason (that `plugin/`
  ships verbatim to every install, so `MARKETPLACE_DIR` paths and PyPI
  credentials have no business inside it) comes from
  `memory/ddaanet/edify-release-flow.md` and is consistent with the tree.
  Added to D-87 in round 2.
- **Submodule-handling gap — DROPPED.** Stopped being a need when D-10
  flattened `plugin/`.
- **Marketplace side effect — DROPPED as a differentiator.** The eval argued
  adopting the toolkit would start publishing edify to the marketplace against
  D-9. Edify's own `scripts/release.sh` now carries the same `MARKETPLACE_DIR`
  requirement (`common_preflight` dies if unset) and the same
  synthesize-an-entry-if-absent branch (`bump_marketplace`'s
  `marketplace_entry_exists=0` path). The recipes no longer differ here. This is
  also what removed the argument's only D-9 dependency in round 1 — which is why
  round 2's D-9 rewrite required no change to D-87's reasoning, only the
  additions (d) invited.
- **Dry-run and rollback gaps — reported, not claimed as edify's needs.** They
  are the toolkit's own framing of its exclusion. Edify has neither and offers
  `--resume`; the toolkit has `resume-release` too. Kept in the eval page, out
  of D-87.
- **The eval's gap table — DROPPED.** A feature matrix of another repo's current
  state is a measurement of mutable state in the design-doc sense and rots on
  every upstream commit. The durable facts are in D-87's prose.
- **`bump-plugin-version.py`'s dead `sessionstart-health.sh` block** — still
  present behind `if health_sh.exists():`, so the eval's staleness item 1 is
  live and was kept.

Not asserted anywhere because it is unresolvable without auditing another repo's
internals, which D-87 does not need: whether the toolkit's `release.just` still
*requires* `MARKETPLACE_DIR` (its header says it skips non-fatally when unset,
while `release.sh` dies on it).

## Evidence supplied by the lead, not re-run by me

Per (d). PyPI `edify-cli` has releases 0.0.3, 0.1.0, 0.1.1, 0.2.0 (latest
0.2.0); GitHub `ddaanet/edify` has releases v0.0.3 (2026-08-04), v0.1.0
(2026-08-14), v0.1.1 (2026-08-27), v0.2.0 (2026-09-02), none with assets.
Checked 2026-09-21 by the lead; I did not re-run it.

What I did measure myself: local tags `v0.0.2`, `v0.0.3`, `v0.1.0`, `v0.1.1`,
`v0.2.0`; `plugin.json` and `pyproject.toml` both at `0.2.0`; the `edify` entry
in `/Users/david/code/claude-plugins/.claude-plugin/marketplace.json` at 0.2.0
with a `git-subdir` source. The design text I wrote names no version number, so
none of this is load-bearing in the docs — D-9's node cites only 0.0.3 and the
date, which are the write-time facts of the reversal.

## Stale memory sentences (not edited, per the original instruction)

`memory/plugin-transition-eval.md`:

- Line 3 (`description:`) — "the **blocked** release-mechanism decision". It is
  recorded as D-87; nothing is blocked.
- Lines 39-45 — the whole "**`just release` is currently BROKEN and the merge
  fixes it**" paragraph. The merge landed (D-10); `scripts/release.sh` works.
  A 2026-07-15 present-tense claim that is now false.
- Lines 47-52 — "**Release-mechanism decision RESOLVED 2026-07-16**". Two
  defects: the `CLAUDE.md:91-94` / `DESIGN.md:320-325` citations are both stale,
  and "no submodule" is no longer one of edify's needs. Should route to D-87.
- Lines 35-37 — "the PyPI publish **shipped 2026-08-04** (0.0.3), **the
  marketplace entry is still missing**". First half correct, second half wrong:
  the entry exists.

`memory/distribution-published.md`:

- Body, first paragraph — "`edify-cli` is on PyPI and the plugin is in the
  `claude-plugins` marketplace" is **correct** and contradicts the
  still-missing claim in `plugin-transition-eval.md`. The two memory files
  disagree with each other; `distribution-published.md` is the right one.

`memory/MEMORY.md`:

- Line 74 — the `distribution-published.md` index line says "Marketplace entry
  still missing." Wrong; the body it indexes says the opposite.
- Line 75 — the `plugin-transition-eval.md` index line ends
  "release-mechanism decision blocked on user." No longer blocked (D-87).

`memory/ddaanet/edify-release-flow.md` — checked and found **accurate**
throughout; it is where D-87's repo-root-not-`plugin/` reason came from.

## Questions and defaults taken

1. **Rewrite the 2026-07-17 changelog entry?** Default taken: no. It is a
   write-time record; the new 2026-08-04 entry supersedes it for a reader.
   Reverse if the changelog is meant to read as current truth.
2. **Delete the publishing non-goal outright, or mark it lifted?** Default
   taken: delete. §9 is a list of things the project is not doing; a lifted
   non-goal is not one. The reversal's record lives in D-9 and the changelog.
3. **Replace D-9 in the "Do not re-litigate" list, or just remove it?** Default
   taken: replace with D-87, which is a real settled question and was otherwise
   unmentioned in the hub's §1.
4. **Hub `docs/design.md` edits** — not asked for in round 1; three made across
   both rounds (§1, §5.1, §9). Each is independently reversible.
5. **D-number** — D-87, the next free one (highest was D-86; no D-87 or D-88
   anywhere under `docs/`).

## Line counts (post-`just format`)

| File | Lines | Cap |
|---|---|---|
| `docs/references/cli-and-package.md` | 237 | 400 |
| `docs/decisions.md` | 187 | 400 |
| `docs/design.md` | 349 | 400 |
| `docs/marketplace.md` | 40 | 400 |
| `docs/changelog.md` | 60 | 400 |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 66 | 400 |
| `docs/changelog/2026-08-04-publication-postponement-reversed.md` | 22 | 400 |
| `docs/changelog/2026-09-21-release-mechanism-recorded-as-a-decision.md` | 22 | 400 |

No ceiling raised; `scripts/check_line_limits.allow` untouched.

## Does the eval doc still justify a page?

Yes, marginally — 66 lines. It keeps the trimmed preamble, the shrunk §2
(pointer to D-87 plus the two corrections that are deliberately *not* in the
node, so they exist nowhere else), and three live staleness items: the dead
`sessionstart-health.sh` block in `bump-plugin-version.py`, the `plansDirectory`
disagreement between `plugin/.claude/settings.json` and the parent
`.claude/settings.json`, and `agents/learnings.md:5` routing through the deleted
`/codify`. Those three are tasks, not design; once fixed, the page has nothing
left. Not deleted.

## `just format` (final run)

```
**Reformatted files:**
  - docs/changelog/2026-08-04-publication-postponement-reversed.md
  - docs/design.md
  - docs/marketplace.md
  - docs/references/cli-and-package.md
  - docs/superpowers/design/plugin-transition-evaluation.md
```

## `just precommit` — full output, PASS

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 351/352 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Exit 0. The suite grew from 348/349 to 351/352 between my first and last runs —
three tests another agent added in this shared tree, not anything of mine; I
touched no test file. The final `just format` reformatted nothing. The three `oversized-file` lines are pre-existing and none of mine: all
three are listed in `scripts/check_line_limits.allow` with ceilings equal to
their current counts (682/460/450, "pilfer defect 21 — corrector-family
dedup"), which by that file's documented contract reports them without failing
the run. `design-links` counts 87 decisions (up from 86) with conclusions
matching — both the new D-87 pair and the reworded D-9 pair satisfy the prefix
rule.

## D-9 rewiring

The lead re-sent this task on the grounds that "D-9 still reads 'postponed' in
the tree". It does — **by design, and by the lead's own instruction (a)**: the
superseding rule in `craft:design-doc-writing` keeps the original lead intact
as the position that was held, and puts current truth in a one-line pointer
directly beneath it. Every item (a)–(d) and (f) had already landed in the
previous round. Verified in the tree before touching anything:

- `docs/references/cli-and-package.md:71-82` — lead unchanged, then
  `*Reversed 2026-08-04:*` with the 0.0.3 PyPI ship, the `git-subdir`
  marketplace entry, "Edify is installable", the unrecorded-reason statement,
  and the surviving ordering constraint.
- `docs/decisions.md:23-25` — `- **D-9** — Publication is postponed
  indefinitely (2026-07-17, user decision) (reversed 2026-08-04: `edify-cli`
  0.0.3 shipped and the marketplace entry exists).` Node lead is a strict
  prefix of the index conclusion, which is what the gate requires; confirmed by
  `check_design_links.sh` reporting conclusions match.
- `docs/design.md` §9 — the "Publishing to PyPI and the marketplace" non-goal is
  gone; the cross-version non-goal carries the durable half.
- `docs/marketplace.md:19-23` — states the entry exists, with its shape.
- `docs/changelog/2026-08-04-publication-postponement-reversed.md` — the second
  entry, which is the "(f) … or a second entry if cleaner" option.

**The lead's own sweep regex, re-run verbatim** —
`rg -U -i 'postpon|parked|uninstallable|not yet (added|published)|waits on'`
over `docs/`, `plugin/`, `CLAUDE.md`, `README*` — returns ten hits, all
accounted for and none a live false claim:

| Hit | Disposition |
|---|---|
| `docs/references/cli-and-package.md:71` | D-9's superseded lead — kept deliberately |
| `docs/references/cli-and-package.md:75` | "why the postponement was lifted" — describes the reversal |
| `docs/decisions.md:23` | D-9 index line — superseded lead plus the reversal parenthetical |
| `docs/changelog.md:50` | the bullet pointing at the reversal entry |
| `docs/changelog/2026-08-04-publication-postponement-reversed.md:1,4,9` | the reversal entry itself |
| `docs/changelog/2026-07-17-bootstrap-reversed-from-stdlib-venv-to-uv.md:10-12` | write-time record of 2026-07-17, left alone |

Nothing in `plugin/`, `CLAUDE.md` or `README*` matches at all.

**(e) declined.** D-87 may state that the recipe has published four versions; I
did not add it. A count of shipped releases is a measurement of mutable state
in `craft:design-doc-writing`'s sense — it is wrong the next time
`just release` runs, and refreshing it just schedules the same correction. D-87
already says the recipe publishes the wheel to PyPI, which is the durable fact.
The version list stays in the changelog entry, where a write-time record is
what the document is for.

**New finding from the lead, for another repo — not acted on.** The `edify`
entry's `description` in `/Users/david/code/claude-plugins` still says
"framework-agnostic", which no longer describes this plugin. That file is
another repo; I made no edit there and hold no task for it. Worth a note in
that repo by whoever owns it, or a rewrite of `description` in
`plugin/.claude-plugin/plugin.json` here so the next
`scripts/release.sh` run propagates a correct one — but the script only
synthesizes `description` when creating an absent entry, so an existing entry's
description is never refreshed by a release. That is a real gap in the recipe,
independent of the wording.

### Checks — `just precommit` deliberately not run, per the lead

`just format` — exit 0, reformatted nothing.

`just lint` — **exit 1**, on a test that is not mine:

```
# Test Report

**Summary:** 351/353 passed, 1 failed, 1 xfail

## Failures

### tests/test_line_limits_wc_padding.py::test_line_limits_reports_unpadded_count_under_bsd_style_wc FAILED

```python
tests/test_line_limits_wc_padding.py:36: in test_line_limits_reports_unpadded_count_under_bsd_style_wc
    assert result.stdout.splitlines() == [
E   AssertionError: oversized-file: docs/notes.md:      401 lines > 400
E
E   assert ['oversized-f... lines > 400'] == ['oversized-f... lines > 400']
E
E     At index 0 diff: 'oversized-file: docs/notes.md:      401 lines > 400' != 'oversized-file: docs/notes.md: 401 lines > 400'
E     Use -v to get more diff
```
✗ Lint failed
```

This is the deliberately-red test the lead warned about — a RED-phase
assertion about `check_line_limits.sh` not stripping BSD `wc`'s padding. It
belongs to the agent working in `tests/`; I touched no test file and no shell
script. `just lint` runs the suite, so it cannot go green while that slice is
red.

`just red-lint` (the same checks without the suite) — **exit 0**, `Red Lint OK`.
That is the signal that isolates my work from the red slice.

`./scripts/check_design_links.sh` — **exit 0**:

```
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
```
