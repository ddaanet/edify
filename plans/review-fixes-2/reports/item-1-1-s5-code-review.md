# Review: Item 1.1 slice 5 code review

**Scope**: HEAD `1e4b91cf`'s classification parse in
`plugin/bin/triage-feedback.sh`, plus an item-wide pass over the script
(`git diff bb058555 HEAD -- plugin/bin/triage-feedback.sh`) against KD-1's
m4, m5, m6, failure and m8 bullets.
**Date**: 2026-10-05T17:28:42Z
**Mode**: review + fix

## Summary

The slice removed `xargs`, `head` and `|| true` and routes grep's status
correctly. Its trim, though, mangled any label holding a colon or an
asterisk, so N-1's unrecognised-label line did not print the label
verbatim. That is fixed: the parse now strips only the prefix grep matched,
and a new parametrised case pins it, with three in-place mutations each
redding it. The item-wide pass found no further issues.

**Overall Assessment**: Ready

## Files changed

- `plugin/bin/triage-feedback.sh`
- `tests/test_triage_feedback.py` (346 → 358 lines)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The trim mangled a label holding a colon or an asterisk**
   - Location: `plugin/bin/triage-feedback.sh:150-151` (HEAD)
   - Problem: `sed -E 's/\*//g;s/.*:[[:space:]]*//;s/[[:space:]]+$//'`.
     `.*:` is greedy and cuts at the *last* colon, and `s/\*//g` deletes every
     asterisk on the line. Measured on HEAD:
     `- **Classification:** Moderate (note: see KD-3)` → `see KD-3)`, and
     `**Classification:** Moderate *really*` → `Moderate really`. N-1's
     `unrecognised classification: <label>` line therefore printed a
     fragment, against the slice's "label verbatim". Recognised labels were
     unaffected, because none holds `:` or `*`. A label such as
     `Simple: see note` read as `see note` and not as itself. Both readings
     are unrecognised, so the verdict did not change, but the reported label
     was wrong.
   - Fix: one `label_prefix_re='^-?[[:space:]]*(\*\*Classification:\*\*|Classification:)'`
     serves both grep and sed. The sed is
     `"s/${label_prefix_re}[[:space:]]*//;s/[[:space:]]+\$//"`, so it strips
     exactly the prefix grep matched, bold markers included, then trailing
     whitespace. The grep pattern is unchanged in meaning: `^-?[[:space:]]*`
     is factored out of the two alternatives. The comment is updated. The ERE
     is portable to BSD `sed -E` and bash 3.2, and shellcheck is clean.
   - **Status**: FIXED

2. **The bare `Classification:` form had no fixture**
   - Location: `tests/test_triage_feedback.py`
   - Problem: grep accepts both `**Classification:**` and plain
     `Classification:`, but every fixture in both modules used the bold form.
     A strip covering only the bold prefix would pass the suite.
   - Fix: the new `colon-label` case uses the bare form with no leading `-`
     (see Mutation proof, mutant 3).
   - **Status**: FIXED

### Minor Issues

None.

## Test added

`test_odd_names_and_labels_do_not_derail_triage[colon-label]`:
`classification.md` holds `Classification: Moderate (note: see *KD-3*)`. The
case shares the `apostrophe-label` branch's assertions:

- the line `unrecognised classification: <label>`, verbatim, is present;
- there is no `xargs` text on stderr;
- no log row is written;
- the exit is 0.

The docstring gains a `colon-label` paragraph, and the shared `label` became a
per-case lookup.

## Mutation proof

Each mutant was an exact in-place Edit of the sed expression and was
restored by the inverse Edit. Afterwards `git diff -- plugin/` shows only
the fix. Modules run: `test_triage_feedback.py` and
`test_triage_feedback_behavioral.py`, 16 tests.

1. **HEAD's greedy cut:** `s/${label_prefix_re}[[:space:]]*//;` →
   `s/\*//g;s/.*:[[:space:]]*//;`. Result: 15/16. Only `[colon-label]`
   reds, on
   `assert 'unrecognised classification: Moderate (note: see *KD-3*)' in [...]`,
   with stdout `unrecognised classification: see KD-3)`.
2. **Prefix strip plus a blanket `*` delete:**
   `s/${label_prefix_re}[[:space:]]*//;` →
   `s/${label_prefix_re}[[:space:]]*//;s/\*//g;`. Result: 15/16. Only
   `[colon-label]` reds, with stdout
   `unrecognised classification: Moderate (note: see KD-3)`.
3. **Bold-prefix-only strip:** `s/${label_prefix_re}[[:space:]]*//;` →
   `s/^-?[[:space:]]*\*\*Classification:\*\*[[:space:]]*//;`. Result:
   15/16. Only `[colon-label]` reds, with stdout
   `unrecognised classification: Classification: Moderate (note: see *KD-3*)`.

Post-restore: 16/16.

## Item-wide pass (KD-1)

- **m4:** both git calls (`triage-feedback.sh:58-59`, `:109-110`) put
  `--` before their pathspecs, and the `:(literal)` / `:(glob)` magic is
  intact. There is no other git call. `grep -E "$label_prefix_re"`: the
  pattern starts with `^`, so it cannot read as an option.
- **m5:** no here-string (the only `here-string` text is in a comment). The
  behavioural grep takes `PIPESTATUS[1]`: 0 is yes, 1 is no, anything else
  is `ERROR: grep failed` with exit 2. The classification grep takes `$?`
  with the same three arms.
- **m6:** no `xargs`, no `|| true`, no `2>/dev/null`. The `|| status=$?`
  and `|| grep_status=$?` forms capture a status rather than discard it.
  Trimming is by `sed`, and the first line is taken by parameter expansion.
- **Failures:** every failure path (`changed-files.sh` non-zero, two
  `git diff` sites, two grep sites, `sed`) prints `ERROR:` on stdout and
  exits 2, before the log append. A `changed-files.sh` failure prints that
  script's output first. The usage error keeps exit 1 and `Usage:` on
  stderr.
- **m8:** no `KD-` in any comment. The citations are D-88 (base), D-90
  (list, Reports) and D-91 (exemptions), matching the outline's mapping.
- Not raised, because they predate Item 1.1 (outside
  `git diff bb058555 HEAD`): the `review_artifact` block's
  `$(find … | wc -l)` and the log append's `mkdir`/`date`/`>>` lines.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:140-151`: a shared `label_prefix_re`. sed
  strips only that prefix, then trailing whitespace. The comment is updated.
- `tests/test_triage_feedback.py:299-351`: the `colon-label` parametrised
  case, its docstring paragraph, and the per-case `label` lookup.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m4 | Satisfied | `--` at both git calls; `[head-file]` |
| m5 | Satisfied (form) | grep 1 = no, ≥ 2 = `ERROR:` exit 2, at both grep sites; no here-string |
| m6 | Satisfied | no `xargs`/`|| true`; `[apostrophe-label]`, `[colon-label]`, `[no-label-line]` |
| N-1 | Satisfied | label printed verbatim (`[colon-label]`, mutants 1-3); no row |
| Failures | Satisfied | all failure paths `ERROR:` + exit 2 before the append |
| m8 | Satisfied | D-numbers only |

## Verification

- `tests/test_triage_feedback.py` + `tests/test_triage_feedback_behavioral.py`:
  16/16 passed.
- `shellcheck plugin/bin/triage-feedback.sh`: clean.
- `just precommit`: the full suite passed (394/395, plus 1 pre-existing
  xfail), followed by `Precommit OK`. Its existing `oversized-file`
  warnings for `corrector.md`, `outline-corrector.md` and
  `design-corrector.md` are unrelated to this change.
- Tree: only `plugin/bin/triage-feedback.sh` and
  `tests/test_triage_feedback.py` are modified by this review; the
  pre-existing staged and untracked files are untouched.

No REFACTOR-NEEDED.
