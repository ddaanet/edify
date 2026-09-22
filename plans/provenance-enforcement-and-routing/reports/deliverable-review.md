# Deliverable Review: provenance-enforcement-and-routing

**Date:** 2026-09-21
**Methodology:** `docs/references/deliverable-review.md`

## Inventory

**Range.** `edify-review-range.sh plans/provenance-enforcement-and-routing/outline.md`
→ exit 0, `RANGE: 926e372d02a0366202b2bb6a684551128d1f2a66..HEAD`. The base is
the one this line has carried verbatim since `design-routing-and-provenance`,
so the range spans **three passes** of the line plus two commits that landed
**after** this job finished. Totals over `git diff --numstat <range> -- . ':!plans'
':!tmp' ':!.claude/handoff-*'`: 112 files, 7736 insertions, 2877 deletions.

Scoped to this job and what followed it (`9eb23d8a..HEAD`): 110 files,
7556 insertions, 2911 deletions. The bulk is Item 1.11's 80-column reflow, which
rewrote every markdown file in `plugin/`, `docs/` and the root — mechanical, and
it is what makes the raw line counts unrepresentative of the substantive change.

Deliverables named by the outline's Items, by type:

| Type | File | Δ lines |
|---|---|---|
| Code | `plugin/bin/edify-review-range.sh` (new) | +162 |
| Code | `scripts/check_line_limits.sh` | +180 / −16 |
| Configuration | `scripts/check_line_limits.allow` (new) | +21 |
| Configuration | `.rumdl.toml` (new) | +31 |
| Configuration | `plugin/portable.just`, `justfile`, `pyproject.toml`, `uv.lock` | +118 / −8 |
| Test | `tests/review_range_helpers.py` + 5 `test_review_range_*.py` | +492 |
| Test | `tests/line_limits_helpers.py`, `test_line_limits.py`, `test_line_limits_exit_codes.py` | +469 |
| Agentic prose | `plugin/agents/outline-corrector.md`, `design-corrector.md` | +192 / −76 |
| Agentic prose | `plugin/skills/design/{SKILL.md, references/route-to-execution.md, references/write-outline.md, references/research-protocol.md}` | substantial |
| Agentic prose | `plugin/skills/build/{SKILL.md, references/tdd-slice.md, references/phase-boundary.md, references/finishing.md, references/review-dispatch-template.md}` | substantial |
| Agentic prose | `plugin/skills/deliverable-review/SKILL.md`, `plugin/skills/runbook/SKILL.md`, `plugin/skills/review/SKILL.md`, `plugin/fragments/delegation.md` | substantial |
| Human docs | `docs/design.md` → `docs/decisions.md` + `docs/references/*.md`, `docs/changelog.md` | see F-6 |

**Design conformance summary.** Every one of the eleven findings the outline
takes as its requirements is implemented at the site it names, and both tdd
items' slice lists landed in full. KD-1 through KD-8 are each traceable to
landed text (see §Gap Analysis). The findings below are, with two exceptions,
about what the range carries *beyond* the job and about robustness of the two
scripts, not about missing requirements.

## Critical Findings

None.

## Major Findings

### F-1 — `wc -l` unguarded against BSD left-padding, in the one line KD-7 pins exactly

`scripts/check_line_limits.sh:124`:

```bash
    if ! line_count=$(wc -l <"$file"); then
```

KD-7 pins the output as `oversized-file: <path>: <n> lines > <cap>`, and
`$line_count` goes straight into it (`:129`). BSD/macOS `wc` left-pads its count
into a fixed field; GNU `wc` reading stdin does not. The repo already guards this
everywhere else it counts: `plugin/bin/triage-feedback.sh:14` and `:21` are both
written `| wc -l | tr -d ' '`. A tree-wide sweep finds three shell `wc -l` sites;
`check_line_limits.sh:124` is the only one whose value is formatted into output
rather than fed to arithmetic (`triage-feedback.sh:77` is unguarded but compared
with `-eq`, which tolerates blanks).

Impact on macOS: the gate still *decides* correctly — `[ "$line_count" -gt "$cap" ]`
tolerates leading blanks — but it prints a malformed line and reds its own suite
at the seven exact-stdout assertions in `tests/test_line_limits.py` (`:43`, `:61`,
`:128`, `:148`, `:173`, `:209`, `:321`).

**Verification status:** the padding claim is **not executed on macOS** — this box
is Linux (bash 5.2.37), where `wc -l < f` printed unpadded. It rests on the two
in-repo `tr -d ' '` guards and on the script's own three explicit macOS
accommodations (`:106` no `declare -A`, `:141` no `mapfile -d ''`, `:154` BSD
`mktemp` needs a template) — a script that codes for bash 3.2 on macOS at three
sites and then consumes `wc` raw at a fourth. *(Layer 1, Major 1.)*

### F-2 — Eight line-limits tests silently read the production allowlist

`tests/line_limits_helpers.py:29-47` omits `--allowlist` when `allowlist is None`,
so the script falls back to `scripts/check_line_limits.sh:64`,
`$SCRIPT_DIR/check_line_limits.allow` — the repository's real, hand-maintained
sidecar. Affected: `test_line_limits_passes_clean_tree`,
`…_fails_markdown_over_400`, `…_fails_skill_hub_over_200`, `…_skips_frozen_docs`,
`…_checks_living_superpowers_docs`, `…_fails_when_find_cannot_walk`,
`…_handles_spaced_path`, and both tests in `tests/test_line_limits_exit_codes.py`.

This is demonstrated, not inferred. Under a basename-matching mutant of
`check_line_limits.sh:111`, `test_line_limits_fails_skill_hub_over_200` went red —
and that test passes no `--allowlist`. It could only have changed behaviour by
matching the production entry `plugin/skills/build/SKILL.md<TAB>218`
(`scripts/check_line_limits.allow:19`), which gave the fixture's 201-line
`plugin/skills/x/SKILL.md` a ceiling of 218 and turned exit 1 into exit 0.

The allowlist is hand-maintained and grows. An entry named `docs/notes.md`,
`docs/my notes.md`, `docs/over.md`, `plugin/locked.md`,
`docs/superpowers/design/living.md` or `plugin/skills/x/SKILL.md` — each a live
fixture path — converts the matching test into a permanent green with nothing to
signal it. KD-7's "overridable by argument so a test can supply its own" exists
precisely to prevent this; the helper defaults the wrong way. Fix is one line:
default to an empty allowlist file under `tmp_path`. *(Layer 1, Major 3.)*

### F-3 — KD-7's "the Python loop adopts the same line" has no test

KD-7 (`outline.md:172`) specifies that the pre-existing Python branch adopt the
`oversized-file:` line. `scripts/check_line_limits.sh:162-169` implements it, and
this job changed that branch's output from `❌ $file: $line_count lines (exceeds
$MAX_LINES line limit)` to the new form. No test touches it: every fixture tree in
`tests/line_limits_helpers.py` and both test modules writes only `.md`.

Probed correct today — a 401-line `src/pkg/big.py` and `tests/big.py` both report
`oversized-file: … 401 lines > 400`, exit 1, and an allowlist entry suppresses the
failure. Correct but unpinned: the Python branch is where the pre-existing
`src/`+`tests/` contract lives, so a regression there silently un-gates it.
*(Layer 1, Major 2.)*

### F-4 — The trailing sweep commit reintroduced M-6, the defect form this job eliminated

Item 1.9's exit condition is `rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/`
with every hit classified, and its report records four searches at zero hits. At
HEAD the same search returns **two**:

- `plugin/skills/design/references/write-outline.md:149` —
  `**Recall diff:** per \`references/research-protocol.md\` §A.5 — re-invoke recall`
- `plugin/skills/design/references/write-design.md:7` — the same sentence

Both are must-open pointers by Item 1.9's own classification (the reader has to
open §A.5 to know what "reconcile the artifact" means). Both were written by
`5594a753` ("sweep the non-design remaining items"), which is inside the review
range and after this job's last item. Before that commit the sentence spelled the
procedure out inline and matched no pattern; the sweep replaced it with a "per"
citation.

### F-5 — Four new repo-relative `plugin/…` paths in skill and agent bodies, against the job's cross-cutting rule

The outline's §Requirements cross-cutting rule (my human partner, at `/proof`):
"every path this job writes into a skill body resolves from an installed plugin…
A repo-relative `plugin/…` path is a defect", with the references already in the
tree scoped out. Counting backticked `plugin/{skills,agents,fragments,bin,hooks}/`
paths inside `plugin/skills`, `plugin/agents` and `plugin/fragments`: **30 sites in
13 files at `9eb23d8a`, 33 sites in 16 files at HEAD.** The rule's purpose is that
`CLAUDE_PLUGIN_ROOT` is unset in an agent's Bash, so these do not resolve from an
installed plugin.

Three went away in the range — `finishing.md:10` and `review/SKILL.md` ×2, of
which Item 1.9 claims one (`:207` → `../../fragments/review-requirement.md`) and
records leaving `:211` to the deferred job; `:211` is gone too, removed later.
Four new ones arrived, all in files that carried none at `9eb23d8a`, all from
`5594a753`:

- `plugin/skills/recall/SKILL.md:20` and `:45` — `` `plugin/fragments/delegation.md` ``
- `plugin/skills/ground/SKILL.md:70` — `` `plugin/fragments/delegation.md` ``
- `plugin/skills/deliverable-review/SKILL.md:104` — `` `plugin/fragments/delegation.md` ``
- `plugin/agents/tdd-auditor.md:209` — `` `plugin/skills/build/references/finishing.md` ``

`tdd-auditor.md` is an agent definition, which gets no announced base directory,
so that one has no skill-relative form available and belongs with
`fragments/delegation.md:33` in the deferred repo-relative job. The three skill
bodies do: from base `plugin/skills/<skill>/`, the fragment is
`../../fragments/delegation.md`, the form Item 1.9 established at
`build/references/finishing.md:10`.

### F-6 — Two later jobs' work sits inside the range and is indistinguishable from this job's

`10513694` (the `docs/design.md` split into hub, `docs/decisions.md` and eight
`docs/references/` nodes) and `5594a753` (the `remaining-sweep` job — `ruff format
--check` in the gates, `scripts/check_design_links.sh`, D-84/D-85/D-86, 95 skill
review findings, `src/edify/*.py` reformatting, `tests/conftest.py`) both landed
after this job's final commit and both are in `base..HEAD`. Each has its own plan
directory (`plans/design-doc-split`, `plans/remaining-sweep`), so each is
explained — but not by *this* job's outline, and nothing in the range tells a
reviewer where this job's deliverable ends.

This is the inheritance rule (D-80) behaving as designed — the base is copied
verbatim so no work escapes review — meeting a review run late. The two prior
passes in the range (`provenance-reach-and-sweep`,
`design-routing-and-provenance`) are the same situation on the other side. D-80
anticipates the near side ("commits landing between artifact generation and the
work fall inside the range and surface as unspecified deliverables — bounded and
visible") but not the far side: nothing bounds commits landing *after* the work,
and `..HEAD` grows without limit until the review runs. Recorded as a finding
against the mechanism rather than the job.

## Minor Findings

**Robustness, `plugin/bin/edify-review-range.sh`** *(Layer 1, Minor 4–7)*

- `:40` strips only `[ \t]+$`, so a `\r` survives into `base`. A CRLF artifact
  prints `UNRESOLVED: <40 hex chars that `git rev-parse` resolves fine>` — the
  operator is told the base is unresolvable and shown a base that is not. Never a
  false green (`:107` rejects before any `RANGE:`). The sibling script in this same
  job grew two dedicated CRLF tests and an explicit diagnostic
  (`check_line_limits.sh:82-85`, `tests/test_line_limits.py:247`, `:281`) on the
  argument that a misleading message masks a genuine encoding problem; the argument
  was not carried across.
- `:151` compares `$resolved_base` (git-canonical lowercase) against `$prior_base`
  (raw artifact text, validated only by the syntactic regex at `:146`). Probed: a
  prior writing the sha uppercase yields `CONFLICT: base 2083da05… != 2083DA05…`
  for two artifacts naming the same commit, and a prior whose 40-hex `Base:` names
  no commit yields `CONFLICT: … != 000000…`, presenting a nonexistent commit as an
  inherited base. KD-2 makes `CONFLICT:` the hard stop meaning "one of two
  artifacts is wrong"; neither case is that. One
  `git -C "$root" rev-parse --verify --quiet "${prior_base}^{commit}"` before `:151`
  fixes both.
- `:64` strips backticks from the `Base:` value; `:119` tests the raw value against
  `none`. `` - **Derived from:** `none` `` → `NO-PROVENANCE:`. The prescribed shape
  at `design-content-rules.md:139` backticks every path, so backticking `none` for
  symmetry is a plausible slip, and the verdict says the section is missing rather
  than that the value is malformed.
- `:88`, `:96` and `:161` all print bare `NO-PROVENANCE:` for three distinct causes
  (no heading; heading without `Base:`/`Derived from:`; report-only `Derived from:`)
  while every other verdict carries its subject. The skill's action is the same in
  all three, so this is a note on KD-2's table as designed, not a deviation.

**Robustness, `scripts/check_line_limits.sh`** *(Layer 1, Minor 8–9)*

- `:56-59`: the `*)` arm assigns `ROOT="$1"` unconditionally, so a second positional
  silently discards the first. Probed: `check_line_limits.sh "$L/a" "$L/b"` with a
  401-line file under `$L/a` exits **0** with no output. Usage at `:4` is `[ROOT]`,
  singular; the `-*)` arm two lines above does diagnose and exit 2.
- `wc -l` counts newlines. A 401-line file with no terminating newline exits 0
  against cap 400. Low realism for markdown (`rumdl fmt` terminates files) — worth a
  comment stating the residual bound rather than code.

**Contract alignment**

- Both correctors describe the `Derived from:` criterion as naming "the review
  report that motivated the outline and the artifact it supersedes"
  (`outline-corrector.md:130-132`, `design-corrector.md:199-201`) without naming the
  literal `superseding` keyword that `edify-review-range.sh:130-133` requires to
  locate the prior artifact. An artifact written "…, replacing `plans/x/outline.md`"
  passes both correctors and yields `NO-PROVENANCE:` from the script. The prescribed
  template (`design-content-rules.md:139`) does use `superseding`, so the authority
  is unambiguous — but the correctors, which are the enforcement point, never state
  the token they are enforcing.
- `classification.md:38` records the M-4 artifact destination as
  `plugin/skills/*/scripts/`; KD-2 settled it as `plugin/bin/` and that is where it
  landed. Planning-artifact drift, no deliverable impact.
- `classification.md:63` attributes the outline-corrector criterion to "outline Item
  1.7"; the outline assigns it to Item 1.1, which is where it landed. Likewise
  `outline.md:209` lists Item 1.1's requirements as "M-1, M-2, M-3" where M-3 is a
  Part B routing finding.

**Test-suite bookkeeping** *(Layer 1, Minor 10–11)*

- Item 1.2 (`outline.md:212`) and KD-2 (`:104`) both name
  `tests/test_review_range.py`. That file does not exist: the suite landed as five
  modules plus a helper (492 lines total). A split was needed; five was a choice,
  and none of the five states why it exists. The sibling split does —
  `tests/test_line_limits_exit_codes.py:7`, "Split from `tests/test_line_limits.py`
  to keep that module under its line cap".
- `outline.md:322-328` ("Final list revision (TDD audit)") enumerates seven tests
  added beyond the slice lists. Six more are unaccounted:
  `test_one_hop_only_ignores_grandprior_mismatch`,
  `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent`,
  `test_line_limits_rejects_crlf_on_full_entry_line`,
  `…_rejects_crlf_on_two_field_entry_line`, and both functions in
  `test_line_limits_exit_codes.py`. All six do real work —
  `test_one_hop_only…` is the only thing pinning KD-2's "One hop only" clause — so
  the defect is the stale enumeration, not the tests. `tests/line_limits_helpers.py`
  and `tests/test_line_limits_exit_codes.py` are likewise absent from Item 1.10's
  file list.

**Duplication**

- `justfile:79-83` duplicates `plugin/portable.just:117-121` verbatim — the
  four-line rumdl rationale comment plus its `report` line — so the root copy can
  add `run-design-links`. The override is justified in situ (`justfile:64-70`); the
  verbatim comment block is what will drift.
- KD-1's 17-line repair table now exists twice, at `outline-corrector.md:140-155`
  and `design-corrector.md:209-224`. Verified byte-identical after indent
  normalisation, as KD-1 requires. Both files are over the 400-line cap (450 and
  460) and on the allowlist. Dedup is deferred to pilfer defect 21 by §Scope.

## Gap Analysis

| Requirement | Status | Evidence |
|---|---|---|
| M-1 — repair writes `TODO` scoped to `Base:` | covered | `outline-corrector.md:140-155`, `design-corrector.md:209-224`; six of seven rows TODO only one field |
| M-2 — allow the verbatim copy, ban derived bases | covered | same table row 3; three invariants at `outline-corrector.md:152-155` |
| M-3 — "edit targets named" binds `/build` branches only | covered | `route-to-execution.md:13-27`; D-82/D-35 in `docs/references/execution-routing.md:56-95` |
| M-4 — the review checks the inheritance rule | covered | `plugin/bin/edify-review-range.sh`; `deliverable-review/SKILL.md:39-53`; exercised live by this review |
| M-5 — node defers to a gate branch that now exists | covered | `write-outline.md:264-267` |
| M-6 — stale "per X" pointers made imperative Reads | covered, then regressed | `reports/item-1-9.md` records 9 sites fixed at 0 residual hits; 2 new hits at HEAD (**F-4**) |
| m-1 — `research-protocol.md` "as shown" scoped | covered | `research-protocol.md:57` — "Only the `## Provenance` heading and the two field labels are as shown" |
| m-2 — `design/SKILL.md` singular "B gate" | covered | `design/SKILL.md:22-27` and `:272-275` carry the four-caller list; no "B gate" remains |
| m-3 — final `ELSE` mislabelled | covered | `route-to-execution.md:31-35` |
| m-4 — changelog entry narrower than 2026-09-17's | covered | `docs/changelog.md:147` — "This narrows the 2026-09-17 routing-node entry below" |
| m-5 — formatter and guard in the gate | covered | `.rumdl.toml`, `portable.just:111-123`, `justfile:73-86`, `check_line_limits.sh`, `check_line_limits.allow` |
| KD-1 — repair table, three invariants, duplicated identically | covered | verified byte-identical |
| KD-2 — script, six verdicts, stop on conflict, one hop | covered | Layer 1 conformance table; all six verdicts have tests |
| KD-3 — route asks whether work needs the runbook layer | covered | `route-to-execution.md:29-50`; D-82 |
| KD-4 — an outline carries a TDD change as a `tdd` item | covered | `build/SKILL.md:107`, `:128`; `tdd-slice.md:3-7`; `route-to-execution.md:25-27`; D-83 |
| KD-5 — Phase 0 Moderate non-prose reads the node | covered | `design/SKILL.md:3-7` description, `:22-27`, `:234`, `:268-275`; D-35 four callers; `route-to-execution.md:58-60` return point |
| KD-6 — not-routable sub-problem reopens its own entry | covered | `write-outline.md:264-267` |
| KD-7 — guard fails on new overage, lists the old | covered | gate run on the real tree: 7 `oversized-file:` lines, exit 0; ceilings match measured counts |
| KD-7 — "the Python loop adopts the same line" | covered, untested | **F-3** |
| KD-8 — rumdl MD013 normalize, non-fixing precommit check | covered | `.rumdl.toml`; `portable.just:117-121` records the probe result the outline left **unverified**, with the reasoning inline |
| Cross-cutting — every path this job writes is skill-relative | covered for this job's items, regressed in range | Item 1.9 removed 3; 4 new sites arrived (**F-5**) |
| §Scope OUT — sweep mechanism, 34 repo-relative refs, corrector dedup, allowlisted-file splits | held | none attempted; `docs/design.md`'s split landed as its own job (**F-6**) |

Unspecified deliverables in range, all explained by their own plan directories:
`scripts/check_design_links.sh` + `tests/test_design_links.py` +
`tests/design_links_helpers.py` (+734), the `docs/design.md` → hub/index/eight-node
split, `ruff format` reflow of `src/edify/*.py` and `tests/conftest.py`, and the
`plugin/fragments/token-economy.md` retirement. See **F-6**.

## Summary

**Critical 0 · Major 6 · Minor 15**

All eleven findings the outline takes as requirements are implemented at the sites
it names; both tdd items' slice lists landed complete; every KD-2 verdict and every
KD-7 branch has a test. Two of the six Major findings (F-1, F-2) are robustness and
test-integrity defects in the shipped scripts; one (F-3) is an untested branch the
outline specified; two (F-4, F-5) are regressions of this job's own requirements
introduced by a later commit inside the review range; one (F-6) is the review-range
mechanism itself.

Checks run that found nothing: whitespace safety in both scripts (`find -print0`
into a spool, `while IFS= read -r -d ''` at all three consumption sites, allowlist
parsed with `IFS=$'\t' read -r`, spaced ROOT and spaced allowlist path both probed);
exit-code discipline (every failure-to-run path exits 2, each with an in-situ reason);
the three `|| true`s are all `grep -m1` no-match with the absent case handled on the
next line — the sanctioned exception; no `2>/dev/null` in either script; bash 3.2 /
BSD portability everywhere except `wc`; idempotency (both scripts pure readers, spool
trapped); test specificity proven by two mutations with confined reds, both restored;
every test runs the script as a subprocess and asserts on exit code and streams only;
`shellcheck -S style` clean on both; all eight `plugin/fragments/` files open with a
`## ` heading naming their rule; the two correctors' Provenance blocks byte-identical;
`./scripts/check_design_links.sh` → exit 0, 86 decisions indexed and matching across
8 nodes; the line-limit gate on the real tree → exit 0 with its 7 allowlisted reports;
frontmatter tool lists cover what each edited skill and agent body instructs.

Tree state: I edited only this report and read everything else. The working tree is
**not** clean — `CLAUDE.md`, `docs/changelog.md`, `docs/references/agent-instructions.md`,
`plugin/skills/proof/SKILL.md`, `plugin/skills/proof/references/item-review.md` modified,
and `.claude/autodrive.exited`, `.claude/launch.json`, `.claude/loop.md`,
`.claude/output-styles`, `.claude/routines`, `.claude/workflows`, `docs/changelog/`,
`plans/changelog-split/`, `plans/proof-verdict-prompt/` untracked. None of it is this
review's; concurrent agents in this session are writing it. My human partner decides
what is ignorable.

## Needs my human partner's call

1. **F-4 and F-5 are regressions by a later job, not defects in this one.** They
   belong to `plans/remaining-sweep` by authorship and to this job by requirement.
   Whether they are fixed here, filed against `remaining-sweep`, or folded into the
   already-scoped repo-relative-references job is a routing decision I should not
   take. The `tdd-auditor.md:209` site in F-5 genuinely has no skill-relative form
   and belongs with the deferred job regardless.
2. **F-6 asks whether `..HEAD` should be bounded.** D-80 reasons carefully about
   commits landing between artifact generation and the work, and not at all about
   commits landing after it. Options I can see: leave it (the review reads wide and
   reports what it finds, which is what happened here); have the script take an
   optional end ref; or have `/build`'s completion record the terminal commit in the
   plan directory so the review can bound itself. Each is a change to D-80's
   contract, so it is a design question rather than a fix.
3. **F-1's macOS claim is unverified on macOS.** If this repo is only ever gated on
   Linux, F-1 drops to Minor. If macOS is a target, the one-line `tr -d ' '` is
   cheap enough that verifying first may not be worth the round trip.
4. **The two correctors are 450 and 460 lines** and this job grew both, adding a
   17-line block that is identical in each. Pilfer defect 21 already owns the dedup;
   the allowlist ceilings are now pinned at the post-growth counts, so the next edit
   to either file turns the gate red. That is KD-7 working as designed, and it means
   the dedup is now on the critical path for any further corrector work.

## Sub-reports

- `plans/provenance-enforcement-and-routing/reports/deliverable-review-code-tests.md`
  — Layer 1, code and tests partition (opus). Findings F-1, F-2, F-3 and the
  robustness and bookkeeping Minors are merged from it; its probe log and
  conformance table carry the evidence in full.
