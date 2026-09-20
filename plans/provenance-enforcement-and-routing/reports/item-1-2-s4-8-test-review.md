# Item 1.2 / slices 4–8 — test review

Independent reproduction of the RED batch's proof-by-mutation, plus a
wrong-reason hunt and a fixture consolidation. Scope: `tests/test_review_range.py`
only; `plugin/bin/edify-review-range.sh` touched solely as save/mutate/restore.

**Verdict: tests proven by mutation.**

## Unmutated runs

Baseline, as handed over (11 tests):

```
tests/test_review_range.py ... 11 passed
```

Full suite at handover: `301/317 passed, 16 skipped`.

Final, after this review's changes (14 tests):

```
..............                                                           [100%]
14 passed in 2.06s
```

Full gate — `just precommit`:

```
# version consistency
Version consistent: 0.2.0
# Test Report
**Summary:** 319/320 passed, 1 xfail
✓ Precommit OK
```

`pytest -q` is run with `-p no:markdown_report`: the `pytest-markdown-report`
plugin replaces terminal reporting with a bare summary line and suppresses the
per-test `FAILED` names, which a mutation proof needs. The gate recipe keeps
the plugin; only the mutation cycles below disable it.

## Changes applied to the test file

### F-1 — Three artifact writers collapsed to one (fixture sprawl)

`_write_artifact`, `_write_artifact_with_only_derived` and
`_write_prior_without_base` were three copies of the same emitter differing
only in which bullets they wrote. `_write_artifact_with_only_derived(p, "none")`
and `_write_prior_without_base(p, "none", None)` produced byte-identical
output. Consolidated into one `_write_artifact(path, derived_from, base,
base_rationale="")` where `None` for either field omits that bullet. The
both-present output is byte-identical to the previous writer's (the three
pre-existing slice 1–3 tests pass unchanged). `_write_artifact_no_provenance_section`
is genuinely different — no `## Provenance` heading — and stays.

### F-2 — Slice 4 was missing the `Base:`-only half of its own branch

The RED parametrized `no-section` and `only-derived-from`. The script's guard is
`plugin/bin/edify-review-range.sh:93`:

```bash
if [[ -z "$base_line" ]] || [[ -z "$derived_line" ]]; then
```

Both disjuncts are deliberate, and the outline's KD-1 table names `Derived from:
absent, Base: present` as a real shape (`outline.md:66`). Added the third param
`only-base`. Proved by M-B below, which reds both halves and leaves `no-section`
green.

### F-3 — `Base:` with a trailing rationale clause was untested

The script's header states the clause may follow *either* field
(`edify-review-range.sh:10-12`), and `base_value_of` implements it by taking the
first word (`:61`). Slice 8 covers the `Derived from:` side only. The tree's real
artifacts carry it on `Base:` —
`plans/provenance-reach-and-sweep/outline.md:11`:

```
- **Base:** `926e372d…` — copied verbatim from
  the superseded outline, **not** recomputed.
```

Added `test_base_with_trailing_rationale_emits_range`. Proved by M-H.

### F-4 — The final `NO-PROVENANCE:` fallthrough was untested

`edify-review-range.sh:159` — `Derived from:` present, not `none`, carrying no
`superseding` clause: the "names only the motivating report" shape, which the
outline lists at `:70`. No slice reached it. Added
`test_derived_from_naming_only_a_report_reported`. Proved by M-I.

**Disposition note for the orchestrator:** F-2, F-3 and F-4 add three cases
beyond the verbatim slice list. Each pins behaviour the script already
implements deliberately and each is proved by its own mutation, so none of them
changes the SUT. If the batch must match the slice list exactly, F-3 and F-4 are
the droppable ones (F-2 is the second half of slice 4's own guard).

### Checked and found sound, no change

- **Assertion strength.** Every test asserts an exact `result.stdout == "…\n"`
  and an exact `returncode`. No substring matching, no `in`.
- **Whitespace safety.** Every path is built with `Path` `/` operators, never
  string concatenation; the script is invoked through a `subprocess.run` argv
  list, never a shell. Nothing in the file splits on whitespace. The one string
  concatenation is `env["PATH"] = f"{BIN_DIR}{os.pathsep}…"`, which is the
  required form and joins on `os.pathsep`, not a space.
- **Slice 8's spaced path.** `plans/my job/outline.md` — the space is in a
  *directory* component, not the filename. M-F proves the prior is actually
  read through that path.
- **Slice 8's foreign CWD.** `_run_review_range` runs from `tmp_path/elsewhere`
  with the artifact as an absolute path, for every test. Correct, though as the
  RED's own docstring says this asserts nothing slice 8 does not already get
  from the shared helper.
- **The `none — <rationale>` idiom.** Verified as U+2014 (`e2 80 94`) by
  hexdump, matching the outline's `:236` wording.
- **Slice 7 covers both halves.** `base-absent` and `base-short`, and M-E1/M-E2
  isolate one each.

## Mutation cycles

Each mutation applied alone to `plugin/bin/edify-review-range.sh`, the file
restored with `git checkout --` immediately after the run, and
`git diff --stat plugin/bin/edify-review-range.sh` confirmed empty before the
next. Eleven cycles; all restores verified empty.

| # | Slice | Mutation | Targeted FAILED |
|---|---|---|---|
| M-A | 4 / no-section | `echo "NO-PROVENANCE:"` → `echo "NO PROVENANCE:"` in the `-z "$provenance"` branch only (`:86`) | `test_missing_provenance_reported[no-section]` — 1 failed, 11 passed |
| M-B | 4 / only-derived-from, only-base | `:93` `\|\|` → `&&` (require *both* fields missing) | `…[only-derived-from]` and `…[only-base]` — 2 failed, 10 passed |
| M-C | 5 | `:112-115` replaced by `resolved_base="$base"` (trust the base, skip git resolution) | `test_unresolvable_base_reported` — 1 failed, 11 passed |
| M-C2 | 5 | `:113` `echo "UNRESOLVED: $base"` → `echo "UNRESOLVED:"` | `test_unresolvable_base_reported` — 1 failed, 11 passed |
| M-D | 6 | `:136` `NO-PRIOR: $prior_path` → `NO-PRIOR: $prior` (absolute, not repo-relative) | `test_missing_prior_artifact_reported` — 1 failed, 11 passed |
| M-D2 | 6 | `:135-138` prior-exists guard deleted | `test_missing_prior_artifact_reported` — 1 failed, 11 passed |
| M-E1 | 7 / base-short | `:144` `{40}` → `{6}` | `test_prior_without_base_reported[base-short]` (+3 collateral, see below) |
| M-E2 | 7 / base-absent | `:144` guarded with `[[ -n "$prior_base" ]] &&` | `test_prior_without_base_reported[base-absent]` — 1 failed, 11 passed |
| M-F | 8 / spaced path | `:128` quoted capture `[^`]+` → `[^` ]+` (a space ends the path) | `test_wrapped_derived_from_with_spaced_path` — 1 failed, 11 passed |
| M-G | 8 / none-rationale | `:117` `"${derived_from%% *}"` → `"$derived_from"` | `test_first_pass_none_with_rationale_emits_range` — 1 failed, 11 passed |
| M-H | F-3 | `:61` `base=${base%% *}` → `base=${base}` | `test_base_with_trailing_rationale_emits_range` — 1 failed, 13 passed |
| M-I | F-4 | `:159` `echo "NO-PROVENANCE:"` → `echo "NO-SUPERSEDING:"` | `test_derived_from_naming_only_a_report_reported` — 1 failed, 13 passed |

Selected failure text, quoted:

- **M-B**, `only-derived-from`: `assert 'UNRESOLVED: \n' == 'NO-PROVENANCE:\n'`;
  `only-base`: `assert 'UNRESOLVED: 0000…0000\n' == 'NO-PROVENANCE:\n'`.
- **M-C**: `AssertionError: RANGE: 0000…0001..HEAD` / `assert 0 == 1`. Proves the
  test forces the `git rev-parse --verify` step to exist, not merely the
  40-hex shape check — the fake base is well-formed hex and passes `:105`.
- **M-D**: `assert 'NO-PRIOR: /tmp/…/repo/plans/missing-job/outline.md\n' ==
  'NO-PRIOR: plans/missing-job/outline.md\n'`. Pins the path as repo-relative.
- **M-F**: `AssertionError: NO-PRIOR: \`plans/my` / `assert 1 == 0`. This is the
  requested word-split proof: with a space ending the capture the path truncates
  at the directory boundary, the prior is not found, and the test reds. The
  other eleven tests stay green, so the space is what the test is pinning.
- **M-H**: `assert 1 == 0`, stdout `UNRESOLVED: 8c388d5f… — copied verbatim from
  the superseded outline, **not** recomputed.`
- **M-I**: `assert 'NO-SUPERSEDING:\n' == 'NO-PROVENANCE:\n'`.

### M-E1 was not discriminating

`{40}` → `{6}` also rejects a legitimate 40-hex prior base, so it reds four
tests rather than one: `test_second_pass_matching_base_emits_range`,
`test_second_pass_recomputed_base_is_conflict`,
`test_wrapped_derived_from_with_spaced_path` and the targeted
`test_prior_without_base_reported[base-short]`. The targeted test still failed on
its own assertion, with the expected wrong verdict —
`assert 'CONFLICT: base 64e6f1e5… != abc123 inherited from
plans/prior-job/outline.md\n' == 'NO-PRIOR: plans/prior-job/outline.md\n'` — so
the proof holds; the collateral is noted rather than hidden. M-E2 is the
discriminating one, and the collateral has a use of its own: it shows
`test_wrapped_derived_from_with_spaced_path` genuinely *reads the prior's
`Base:`*, not merely that the spaced path resolves to an existing file.

### Equivalent mutants (recorded, not counted as proof)

Deleting the `-z "$provenance"` guard at `:85-88` outright does **not** red
anything: with no section, `base_line` and `derived_line` are both empty and
`:93` produces the same `NO-PROVENANCE:` / exit 1. That guard is behaviourally
redundant. This is a property of the script, not a gap in the test — the test
pins observable behaviour and the behaviour is unchanged — so M-A mutates the
branch's payload instead, which is what discriminates it. Worth noting for a
later simplification pass on the script; **not** a finding against these tests
and not something to fix here (scope is test-only).

## Lint and formatting

```
ruff check tests/test_review_range.py   → All checks passed!
mypy tests/test_review_range.py         → exit 0, no output
docformatter -c tests/test_review_range.py → exit 0
just precommit                          → ✓ Precommit OK
```

One correction to the RED report's lint section: `docformatter -c` did **not**
pass on the file as handed over once this review's docstrings were added, and
`[tool.docformatter] in-place = true` in `pyproject.toml` means `-c` and
`--diff` rewrite the file rather than only reporting. `just format` reflowed one
docstring; the result is committed in the working tree and re-verified green.

Unrelated pre-existing observation, **not** acted on (out of scope): bare
`ruff format --check` reports the file as needing reformatting *at `HEAD` too*,
i.e. before any change in this batch, and `ruff format -q --diff` reports
pending diffs across `src/edify/`. `just precommit` is green, so the gate does
not run `ruff format --check`. Flagging only; nothing here depends on it.

## Line count

`tests/test_review_range.py` — **396 lines**, under the 400-line cap, and
`just line-limits` (inside `just precommit`) passes.

This is 4 lines of headroom. Per the shared convention, a file parked at its cap
has stopped emitting the signal: the next test added to this file will cross it.
The natural split, when that happens, is by verdict — the three `RANGE:` /
`CONFLICT:` tests that exercise the happy path and the compare, versus the nine
tests that exercise the five refusal verdicts — but splitting now would cost a
shared-fixture import for no present gain. Flagged as a judgement call for the
orchestrator, not applied.

## Final state

- `git diff plugin/bin/edify-review-range.sh` — **empty**. The SUT is
  byte-for-byte as committed after all eleven cycles; re-verified after the last
  one and again after `just format`.
- `git status --porcelain`: `M tests/test_review_range.py` plus the untracked
  `plans/provenance-enforcement-and-routing/reports/item-1-2-s4-8-red.md` (and
  this report). Nothing committed, per instruction.
