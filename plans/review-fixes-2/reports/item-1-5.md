# Item 1.5: script hygiene

## m1
`changed-files.sh`: dropped line 2 `exec 2>&1`. The script's `ERROR:` and
`NO-BASE:` lines stay on stdout; git diagnostics now go to stderr. The header
sentence became "keeps git's skipped-rename warning, which goes to stderr, out
of the paths on stdout." `verify-step.sh` keeps its own `exec 2>&1` (outside
the item's scope, which named only `changed-files.sh`).

## KD to D mappings
- changed-files.sh `KD-1` (base from earliest item-report commit) -> D-88
- changed-files.sh `KD-6` (changed-files list, exempt paths) -> D-90
- changed-files.sh `KD-2` (`--phase` base) -> D-89
- changed-files.sh `KD-8` (path, never the commit subject) -> D-94
- verify-step.sh `KD-6` (exempt alternation in exempt-paths.sh) -> D-91
- verify-step.sh `KD-7` (safe to exempt: commits stage by name) -> D-91
- exempt-paths.sh `KD-6` (sourced exempt alternation) -> D-91

No KD lacked a matching D-ID.

## Tests
None adjusted: no test asserted git diagnostics on stdout. No m1 assertion
added.

## triage-feedback.sh check
It captures `changed-files.sh` stdout with `$(...)` and parses line 1 as
`BASE:` and the rest as paths; on non-zero exit it prints the captured stdout
(carrying `ERROR:`/`NO-BASE:`) and exits 2. Git diagnostics on stderr no
longer enter the captured list (previously a warning could be counted as a
path); they pass through to triage's own stderr. The consumption holds.

## Verification
`just precommit` green (402/403 passed, 1 xfail; oversized-file lines for
three agents are pre-existing). `grep -n 'KD-'` on the scripts is empty;
`grep -n 'exec 2>&1'` on changed-files.sh is empty.
