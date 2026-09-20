# TDD audit — Items 1.2 and 1.10

Job: `plans/provenance-enforcement-and-routing/`. Audited: Item 1.2
(`plugin/bin/edify-review-range.sh`, 8 slices) and Item 1.10
(`scripts/check_line_limits.sh`, 8 slices), from the per-slice reports under
`plans/provenance-enforcement-and-routing/reports/`, the outline's Items 1.2
and 1.10 including their list-revision paragraphs, and the commits in
`1f54633b..HEAD`.

**Overall verdict: compliant.** Every slice carries RED evidence landing on an
assertion, an independent review verdict, and either a GREEN commit that
exists and carries tests plus implementation, or — for the six slices the
recorded deviations exempt — a test-only commit with an independently
reproduced mutation proof. Every code review's fixes were committed by the
orchestrator with a diffstat matching the review report's. No assertion was
weakened between RED and GREEN; no test is skipped or xfailed inertly. Four
gaps are recorded below, all of them evidence gaps rather than defects, and
none of them invalidates a slice.

Measured at HEAD: `pytest tests/test_line_limits.py tests/test_review_range.py`
→ **26 passed** (12 + 14). `just precommit` is **red at HEAD** — see
Finding 4, which is outside these two items but concerns the gate Item 1.10
built.

## Per-slice table

`—` in the GREEN or code-review column is the recorded deviation, not an
omission; the relevant deviation audit is named in Notes.

| Slice | RED evidence | Review | GREEN commit | Code review | Notes |
|---|---|---|---|---|---|
| 1.2/1 | 0/1 passed, 1 failed — `test_first_pass_emits_range` on `assert result.stdout == f"RANGE: {sha}..HEAD\n"`, stub printed `''` | RED confirmed; 1 Critical + 2 Major + 2 Minor fixed; still 0/1 after fixes | `78206a83` (exists) — SUT + test + 3 reports | `c30b7bc1` — 2 defects fixed, diffstat 82 (51/31) matches the report | The Critical was a fixture that could not discriminate a `git rev-parse HEAD` script; `_init_repo` went to two commits, proven by replay |
| 1.2/2 | 1/2 passed, 1 failed — on `assert result.returncode == 0`, stdout `NO-PRIOR: plans/prior-job/outline.md` | RED confirmed; 1 Major fixed (fixture used a wrapped shape no real artifact writes); satisfiability measured against a patched copy under `$TMPDIR` | `c63dade5` — SUT + test + 3 reports | `a63fed26` — 1 Minor fixed, diffstat 6 (4/2) matches | Review's mutations (a) and (b) survived by design; discriminator is slice 3 |
| 1.2/3 | Passed unmutated (predicted); proof by 1 RED-side mutation (unconditional `RANGE:` before the compare) → `assert 0 == 1` | **Proven by 4 independent mutations of the reviewer's own choosing** (A, B killed; C, D survive, both out of contract). Pristine sha `5b8b93c2…` matched after restore | — (deviation 1) | — (deviation 1) | Committed test-only as `45ad1184` ✅ `Item 1.2/3`; SUT absent from the diffstat |
| 1.2/4 | Passed unmutated; RED cycle 1 (`NO-PROVENANCE:` branch → `RANGE:`) → targeted FAILED, 10 others pass | **M-A, M-B — independent.** M-B (`\|\|` → `&&`) also exposed a missing third case, added as `only-base` | — | — | Test review added `only-base`; outline not revised (Finding 2) |
| 1.2/5 | Passed unmutated; RED cycle 2 (drop `git rev-parse --verify`) → `assert 0 == 1` | **M-C, M-C2 — independent.** M-C proves the git resolution step is forced, not just the 40-hex shape | — | — | |
| 1.2/6 | Passed unmutated; RED cycle 3 (drop the prior-exists guard) → `returncode 2` vs expected 1 | **M-D, M-D2 — independent.** M-D pins the path as repo-relative | — | — | |
| 1.2/7 | Passed unmutated; RED cycle 4 (drop the prior-base sha-shape check) → both params FAILED with `CONFLICT:` | **M-E1, M-E2 — independent.** M-E1 non-discriminating (3 collateral reds), reported rather than hidden; M-E2 is the clean one | — | — | Both halves (`base-absent`, `base-short`) proven separately |
| 1.2/8 | Passed unmutated; RED cycle 5 covers case 2 (`none — <rationale>`) only — **case 1 got no RED-side mutation** | **Closed by the review: M-F** (backtick capture `[^\`]+` → `[^\` ]+`) reds `test_wrapped_derived_from_with_spaced_path` alone — the word-split proof. M-G covers case 2 | — | — | Committed test-only as `f8d1e254` ✅ `Item 1.2/4-8`. Case 1's only proof is review-side; see deviation 1 |
| 1.2 tail | n/a (general, not tdd) | n/a | `62a7c6ea` — `deliverable-review/SKILL.md` + report | n/a | Verdict lines checked against the script's 10 `echo`/`printf` call sites, not its header |
| 1.10/1 | Passed **vacuously** (recorded in advance by the list revision); no RED-side proof | **Proven by the review**: SUT replaced by an unconditional `oversized-file:`/exit 1 → `assert 1 == 0`. Re-run after the review's own fixes, same result | `66e32fad` — SUT + test + 3 reports | `381c16a1` — 3 Major fixed, diffstat 23 (19/4) matches | 2 findings fixed in the test (docstring convention, weak negative assertion) |
| 1.10/2 | 1/2 passed, 1 failed — `assert 0 == 1`, script printed nothing for a 401-line `docs/notes.md` | RED confirmed; same review | `66e32fad` | `381c16a1` | Genuine red; supplies the batch's red per the list revision |
| 1.10/3 | Passed unmutated; RED mutation `cap=200` → `cap=400` → `assert 0 == 1` | **3a and 3b — independent.** 3a globally 400, 3b globally 200; together they prove *path-picked-ness*, not either cap | — (deviation 1) | — | |
| 1.10/4 | 3 failed on `assert 2 == 0` / `assert 2 == 1`, stderr `--allowlist: not implemented` | RED confirmed; 5 findings fixed, 3 new tests added | `f74d9527` — SUT + test + 3 reports | `58c99565` — 2 fixed (silent exit-1 arity; bash-4 `declare -A` → 3.2-safe scan), diffstat 47 (38/9) matches | Genuine red |
| 1.10/5 | Same batch: `assert 2 == 1` | RED confirmed | `f74d9527` | `58c99565` | |
| 1.10/6 | Passed unmutated; RED mutation drops `plans/*` from the exclusion → `assert 1 == 0` | **6, 6b, 6c — independent.** 6b pins `specs/`, 6c catches the over-wide `docs/superpowers/*` GREEN via a new living-docs test | — | — | |
| 1.10/7 | Passed unmutated; RED's first mutation attempt **failed to reproduce** the split and was reported as such; `for file in $(find …)` did | **Independent: unquoted call site** `check_cap $file` → `assert 2 == 1`, stderr `cannot read docs/my` | — | — | The negative result being reported rather than dropped is the right handling |
| 1.10/8 | 11/12 passed, 1 failed — `assert 0 == 2`, stderr `find: 'docs/locked': Permission denied`, the 401-line file silently unchecked | RED confirmed; Finding S8-1 removed a vacuous stdout assertion; Finding C's fixture fix reproduced independently (old fixture survives the basename mutant, new one kills it) | `542ff17c` — SUT + test + 3 reports | `50c35d61` — 1 Major fixed (failed `mktemp` exited 1), diffstat 23 (14/9) matches | Added mid-item after the 3–7 code review; all four dispatches present |

## Deviation audits

### 1. Slices already implemented by an earlier GREEN — **compliant, with one narrow gap**

Applies to 1.2/3, 1.2/4–8, 1.10/3, 1.10/6, 1.10/7.

**Independent mutation in the review: yes, for every one.** Every test review
states its mutations are distinct from the RED report's and names them; the
counts are 4 (1.2/3), 11 (1.2/4–8), and 6 (1.10/3, 6, 7 — including 3a/3b and
6b/6c pairs). Three reviews went further than the RED by proving a *property*
rather than a branch: 1.10/3a+3b prove path-picked-ness rather than either cap
value, 1.10/6b+6c prove the exclusion is neither too narrow nor too wide, and
1.2's M-B exposed an untested half of the guard it mutated.

**SUT restored: yes, and verified by the right instrument each time.** 1.2/3's
RED diffed against a pristine copy and its review matched `shasum 5b8b93c2…`
before and after; 1.10/8's review matched `sha256 826da029…`; the others
verified `git diff --stat <sut>` empty after every cycle, which is a byte-exact
comparison against the commit. Restores were performed after *each* mutation,
not only at the end — stated explicitly in 1.2/3's review and in both 1.10
batches.

**Behaviour left with only a RED-side proof: one.** Slice 1.2/8's *case 1*
(wrapped `Derived from:`, spaced prior path, foreign CWD) received no mutation
in the RED batch — cycle 5 targets case 2 only. The test review closed it with
M-F, so the behaviour is proven; what is missing is a proof on *both* sides for
that one case, which is the deviation's own standard. Everything else has two
independent proofs.

**Commit form: correct.** `45ad1184` and `f8d1e254` are test-only (`✅`, the
hook's rewrite of `test:`); neither diffstat contains
`plugin/bin/edify-review-range.sh`. No GREEN or code-review dispatch ran for
them, as the outline prescribes.

### 2. Batched RED/review dispatches — **compliant**

Applies to 1.2/4–8, 1.10/1–2, 1.10/3–7.

No slice rides on a sibling's proof. Each batched slice has a mutation or a red
addressed to its own named test:

- 1.2/4–8: cycles 1–5 in the RED and M-A…M-G in the review each name the
  targeted test and report the other tests staying green, which is what rules
  out a shared proof. The one non-discriminating mutation (M-E1, 3 collateral
  reds) is reported as such and paired with M-E2, which is clean.
- 1.10/1–2: slice 2 supplies the genuine red; slice 1 is proven separately by
  the review's unconditional-failure mutation. The list revision recorded this
  *before* the dispatch (`9126940f`, committed ahead of `66e32fad`).
- 1.10/3–7: slices 4 and 5 red genuinely on `--allowlist`; 3, 6 and 7 each get
  their own mutation, twice over.

One structural note rather than a fault: the batched reviews added seven tests
beyond the verbatim slice lists (1.2 F-2/F-3/F-4; 1.10 findings 2, 4, 5 and the
living-docs guard). Each pins behaviour the SUT already implemented deliberately
and each carries its own mutation proof, so none changed the SUT. The outline
was not revised to record them, so the slice list and the landed suite have
diverged — see Finding 2.

### 3. Precommit red by design, `66e32fad`..`04b627a1` — **compliant with one evidence gap**

| Commit | Full `pytest -q` in its report | shellcheck |
|---|---|---|
| `66e32fad` (1.10/1-2 GREEN) | 306/322, 16 skipped — no new failures | clean |
| `381c16a1` (1.10/1-2 CR fixes) | **absent** — only `pytest tests/test_line_limits.py` 2/2 | clean |
| `f74d9527` (1.10/3-7 GREEN) | 315 passed, 16 skipped, 0 failed | clean |
| `58c99565` (1.10/3-7 CR fixes) | 315/331, 16 skipped | clean |
| `542ff17c` (1.10/8 GREEN) | 316/332, 16 skipped | clean |
| `50c35d61` (1.10/8 CR fixes) | 316/332, 16 skipped | clean |

Five of six commits carry a full-suite run and a shellcheck run in their own
report. `381c16a1` carries shellcheck and the targeted file only. The exposure
is small — that commit touches `scripts/check_line_limits.sh` alone, which only
`tests/test_line_limits.py` exercises, and `58c99565`'s later full-suite run
covers the cumulative state — but the evidence for that commit does not exist,
and this audit does not manufacture it by reasoning. Recorded as Finding 1.

The GREEN report for `66e32fad` also documents *why* `just precommit` could not
gate the commit and confirms the repo's actual pre-commit hook (gitlore's memory
gate) is unrelated to line limits and was not bypassed — no `--no-verify`
anywhere in the window.

### 4. Slice 1.10/8, added mid-item — **compliant, all four dispatches present**

Origin recorded: the 3–7 code review's Finding 3 (`find` failing inside process
substitution leaves the gate green, measured at exit 0 with a 401-line file
unreported) was left unfixed and referred to the orchestrator, which is the
correct disposition for a defect no slice covers. The orchestrator added the
slice to the outline in `92daa041` — committed *after* `58c99565` and *before*
`542ff17c`, i.e. before the work.

- **RED** (`item-1-10-s8-red.md`): genuine, 11/12 with `assert 0 == 2` and
  `find: 'docs/locked': Permission denied` on stderr. Also carried Finding C's
  fixture correction, with the basename mutant killing the new fixture.
- **Test review**: RED confirmed independently; sha256 match on restore; found
  the stdout assertion vacuous (nothing is printable under *any* implementation
  in that fixture) and removed it, rewriting the docstring to say what is
  deliberately unasserted.
- **GREEN** (`542ff17c`): `walk()` helper spooling `find -print0` to a `mktemp`
  file with an EXIT trap, 12/12 and 316/332 full suite, shellcheck clean.
- **Code review** (`50c35d61`): mutation restoring the process-substitution form
  reds the new test and nothing else; found and fixed a failed `mktemp` exiting
  1 (the overage code) — the same class the 1-2 and 3-7 reviews each caught on a
  different line.

## Test integrity

**No assertion weakened between RED and GREEN.** Diffed the two test files
across every slice commit. Removed lines in `tests/test_review_range.py` are
confined to fixture writers — `c63dade5` removed two docstring/format lines,
`f8d1e254` removed the three-writer sprawl consolidated into one
`_write_artifact`. No assertion line was removed or relaxed in Item 1.2.

One test was materially rewritten in Item 1.10: `542ff17c` changed
`test_line_limits_matches_allowlist_paths_exactly`, dropping the
`docs/my-notes.md` decoy and its asserted line and raising the allowlisted
ceiling 401 → 500. On its face this removes an assertion; it is a
**strengthening**, and it is proven rather than argued. The 3–7 code review's
Finding C measured that the old fixture *survived* a basename-matching mutant
(ceiling 401 equal to every decoy's line count made the two implementations
observationally identical, and the confound `docs/my-notes.md` fixed exit 1
regardless of allowlist behaviour). The slice-8 RED and its review both
reproduced this: old fixture PASSES under the mutant, new fixture FAILS
(`assert 0 == 1`). The docstring's false substring claim went with it.

**No inert skip and no xfail.** The only `pytest.skip` in either file is
`tests/test_line_limits.py:288`, guarding the chmod-0o000 fixture when running
as root, with the reason stated. The `skip` matches elsewhere are the word in
prose and in `test_line_limits_skips_frozen_docs`'s name. The `1 xfail` visible
in several `just precommit` transcripts is a pre-existing
`pytest-markdown-report` case, unrelated to either item.

**Assertion strength.** Every test in both files asserts an exact
`result.stdout == "…\n"` or `result.stdout.splitlines() == [...]` plus an exact
`returncode`; the two substring assertions that existed were tightened during
review (1.10/3's `"> 200" in stdout` → full-line equality; 1.10/1's
`startswith` scan → `"oversized-file:" not in stdout`). Every sha and line count
asserted comes from the fixture's own `git rev-parse` or `_write_lines`, never
a literal.

**After-the-slice steps.** All five list revisions are committed, each ahead of
the work it governs: `52a11878`, `c7b3af94`, `7bf52397` (Item 1.2),
`9126940f`, `92daa041` (Item 1.10). No refactor dispatch was flagged by any
review — the only occurrence of the word is
`item-1-2-s2-code-review.md:205`, an "In-scope-unfixable refactorings: None"
heading. Confirmed.

## Findings

### Finding 1 — `381c16a1` has no full-suite evidence

The only commit in the precommit-red window whose report does not record a full
`pytest -q`. Low exposure, zero evidence. If the window recurs, the substitute
gate should be stated once as a checklist the dispatch requires back
(full suite, shellcheck, targeted file) rather than left to each agent's report
shape — four of the six volunteered it, one did not.

### Finding 2 — the outline's slice lists no longer describe the landed suite

Seven tests were added by test reviews beyond the verbatim slice lists, and one
slice's asserted contract changed. Specifically: Item 1.10 slice 8 in the
outline still reads "asserts exit 2 **and no `oversized-file:` line**", but the
test review removed that assertion as vacuous and the landed test does not make
it. A reader auditing the outline against the suite will find a claim the code
does not support. The list-revision mechanism exists and was used five times;
these changes did not go through it.

### Finding 3 — two contracts confirmed by probe but pinned by no test

Both are recorded in the reports and both are real:

- **Exit-2 over exit-1 precedence** when a walk failure and an overage coexist.
  Probed in the 1.10/8 code review (`exit=2` with the overage line already
  printed); no slice covers it. Flagged by the test review and again by the code
  review, with the fixture named (over-cap file in `plugin/`, unreadable dir
  under `docs/`, assert exit 2). It needs a test owner.
- **`Derived from:` naming only the motivating report, with no `superseding`**.
  Currently answered `NO-PROVENANCE:`, which is plainly false about such an
  artifact. KD-1's sixth row treats the shape as real; KD-2's table has no
  verdict for it. Flagged in the 1.2/1 review, still open at 1.2/2, and the
  1.2/4–8 review then added `test_derived_from_naming_only_a_report_reported`
  pinning the *current* answer. That test now locks in behaviour the reviews
  twice called wrong. It needs a KD-2 amendment, and the test moves with it.

### Finding 4 — `just precommit` is red at HEAD

Not an Item 1.2/1.10 compliance failure; reported because it concerns the gate
Item 1.10 built and because observable state is not filtered. Measured at HEAD:

```
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 285 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/design.md: 1237 lines > 400
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✗ Precommit failed   (exit 1)
```

The four review-gate commits after `04b627a1` grew `docs/design.md` past its
1221 ceiling and pushed `plugin/skills/design/SKILL.md` and
`plugin/skills/proof/SKILL.md` over cap with no allowlist entry. The gate is
behaving exactly as Item 1.10 specified — the ratchet caught growth — but the
window the outline says closes at `04b627a1` did not close. Tests themselves
are green (`Tests cached (inputs unchanged)`; the two TDD suites re-run clean at
26 passed).

## Process recommendations

Grounded in what these sixteen slices show; no thresholds are asserted that the
reports do not support.

1. **Keep the "already implemented by an earlier GREEN" deviation.** It worked.
   In six slices it produced *stronger* evidence than an ordinary red would
   have: a red against unimplemented behaviour proves only that the code was
   absent, whereas these reviews proved which line of the SUT the test is
   holding. 1.10/3a+3b and 1.10/6b+6c are the clearest cases — a single red
   could not have established either property.
2. **Require the RED and the review to mutate independently, per named test,
   not per batch.** The one gap this audit found (1.2/8 case 1) is exactly the
   shape a per-batch reading lets through: five cycles for five slices, one of
   which had two cases. Naming the test rather than the slice in the dispatch's
   proof requirement closes it.
3. **Route a review's added tests back through the list-revision mechanism.**
   The mechanism is already in place and already used; it was simply not applied
   to test-review additions. The 1.2/4–8 review anticipated this and asked the
   orchestrator for a disposition on F-3 and F-4, which is the right instinct —
   the missing step is the outline edit that records the answer.
4. **Give a reviewer's unfixed finding an explicit ruling, recorded.** Both
   items did this well: 1.10/3–7's Finding 3 became slice 8 with the outline
   revised first, and Finding S8-1's ruling ("exit 2 is the contract; a partial
   report is permitted but must not be relied on") is quoted in the report that
   acted on it. Finding 3 above lists the two that are still awaiting one.
5. **The same defect class recurred on three separate lines** — a
   failure-to-run path exiting 1, the interface's overage code (`--allowlist`
   discarded and `shift 2`, then `--allowlist` arity again, then a failed
   `mktemp`). Each was caught by the next code review rather than by the GREEN
   that introduced it. For a script whose exit codes are its interface, an
   explicit "every failure-to-run path exits 2" probe in the GREEN dispatch
   would have caught all three at the point of writing.
