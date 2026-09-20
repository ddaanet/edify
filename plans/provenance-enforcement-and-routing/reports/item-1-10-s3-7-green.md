# Item 1.10, slices 3-7 — GREEN

## Approach

Slices 3, 6, 7 already passed against the code from Item 1.10/1-2 — no
change needed there. The remaining work was slices 4 and 5: implementing
`--allowlist`.

- **Default path:** `check_line_limits.allow` beside the script, resolved
  from the script's own location via `SCRIPT_DIR="$(cd "$(dirname
  "${BASH_SOURCE[0]}")" && pwd)"` — never from `ROOT` or `CWD`. `--allowlist
  FILE` overrides it.
- **Parse timing:** the allowlist is read *before* `cd "$ROOT"`, since a
  relative `--allowlist` argument is relative to the original CWD, not
  `ROOT`. The default path is already absolute via `SCRIPT_DIR`.
- **Missing file:** a missing default allowlist is silently an empty
  allowlist; a missing file named explicitly by `--allowlist` is exit 2.
- **Format parsing:** `while IFS=$'\t' read -r entry_path ceiling _note`,
  skipping blank lines (`[ -z "$entry_path" ]`) and comment lines
  (`case "$entry_path" in \#*) continue ;; esac`) before validating
  `ceiling` as an integer (`[[ "$ceiling" =~ ^[0-9]+$ ]]`, else exit 2
  naming the allowlist file and line number).
- **Lookup structure:** a bash associative array (`declare -A
  ALLOWLIST_CEILING`) keyed by the exact root-relative path — bash 4+ is
  assumed (this repo's `/usr/bin/env bash` and Linux CI both satisfy that);
  a linear scan would be the fallback for bash 3.2, not implemented since
  no slice asks for it.
- **`check_cap` behaviour:** unchanged for a file at or under its cap
  (nothing printed, regardless of allowlist). Over cap: always print
  `oversized-file: <path>: <n> lines > <cap>` (the cap, never the
  ceiling); if unlisted or `line_count > ceiling`, set `EXIT_CODE=1`; if
  listed and `line_count <= ceiling`, print only, no failure.

## Test results

`pytest tests/test_line_limits.py -v`: 11/11 passed.

`pytest -q` (full suite): 315 passed, 16 skipped, 0 failed.

`shellcheck scripts/check_line_limits.sh`: no output (clean).

## `just precommit` on the real tree

Exits 1, as expected — Item 1.11 populates the real allowlist from
post-reflow counts; none was created here. `oversized-file:` lines:

```
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
```

Seven overages, matching the count named in the dispatch. No
`scripts/check_line_limits.allow` file exists in the tree after this run.

## Commit

Staged `scripts/check_line_limits.sh`, `tests/test_line_limits.py`, and the
three reports (`item-1-10-s3-7-red.md`, `item-1-10-s3-7-test-review.md`,
this file). Committed once, hook running (no `--no-verify`). Tree left
clean afterward.
