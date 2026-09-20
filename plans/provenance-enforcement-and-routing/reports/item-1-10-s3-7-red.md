# Item 1.10, slices 3-7 — RED

## Allowlist file format

Pinned in `_write_allowlist`'s docstring (`tests/test_line_limits.py:50-64`):
one entry per line, `<path><TAB><ceiling><TAB><note>` — TAB because a path
may contain spaces (slice 7) and a note may contain anything; `#` comments
and blank lines are ignored by the script. `path` is root-relative,
`ceiling` is the entry's line-count ceiling (only ratchets down), `note`
names the retiring job or `"no job yet"`.

## Slices added

3. `test_line_limits_fails_skill_hub_over_200` — two fixture trees: a
   201-line `SKILL.md` alone (exit 1, `> 200` in output), and a 201-line
   `notes.md` alone beside where a `SKILL.md` would sit (exit 0, no
   `oversized-file:` line) — one tree per assertion, since a shared tree
   would exit 1 regardless of the sibling's own cap.
4. `test_line_limits_reports_allowlisted_without_failing` — a 401-line
   `docs/notes.md` allowlisted at ceiling 401: exit 0, `oversized-file:`
   line still printed. Plus
   `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent` — same
   allowlist entry (ceiling 401) but the file now 350 lines: exit 0, no
   `oversized-file:` line (no stale-entry failure).
5. `test_line_limits_fails_allowlisted_file_over_ceiling` — ceiling 450,
   file 451 lines: exit 1, message names the path-picked cap 400
   (`> 400`), not the ceiling.
6. `test_line_limits_skips_frozen_docs` — 401-line file under
   `docs/superpowers/plans/`: exit 0, no `oversized-file:` line.
7. `test_line_limits_handles_spaced_path` — 401-line `docs/my notes.md`:
   exit 1, reported path intact (`oversized-file: docs/my notes.md: 401
   lines > 400`).

## Unmutated run

`pytest tests/test_line_limits.py -v`: 5/8 passed, 3 failed.

Passed (implemented by slices 1-2's GREEN, no code change needed):
- `test_line_limits_fails_skill_hub_over_200`
- `test_line_limits_skips_frozen_docs`
- `test_line_limits_handles_spaced_path`
(plus the two pre-existing slice 1-2 tests)

Failed on the intended assertion — `--allowlist` currently exits 2 with
`check_line_limits: --allowlist: not implemented` on stderr, so each fails
its exit-code assertion, not a crash:
- `test_line_limits_reports_allowlisted_without_failing`:
  `assert 2 == 0` (returncode), stderr shows the not-implemented message.
- `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent`:
  same `assert 2 == 0`.
- `test_line_limits_fails_allowlisted_file_over_ceiling`:
  `assert 2 == 1`, same stderr.

## Mutation proofs for slices 3, 6, 7

One mutation at a time; each restored via `git checkout -- scripts/check_line_limits.sh`
before the next, `git diff --stat scripts/check_line_limits.sh` confirmed empty
after every restore.

**Slice 3** — cap bug: line 73 `[ "$(basename "$file")" = "SKILL.md" ] &&
cap=200` mutated to `cap=400`. Targeted run:
`pytest tests/test_line_limits.py::test_line_limits_fails_skill_hub_over_200`
→ `assert 0 == 1` (script now exits 0 since the 201-line `SKILL.md` no
longer exceeds cap 400). Restored; diff empty.

**Slice 6** — exclusion bug: line 70
`docs/superpowers/plans/* | docs/superpowers/specs/*) continue ;;` mutated
to drop the `plans/*` alternative, leaving only
`docs/superpowers/specs/*) continue ;;`. Targeted run:
`pytest tests/test_line_limits.py::test_line_limits_skips_frozen_docs` →
`assert 1 == 0`, stdout shows
`oversized-file: docs/superpowers/plans/old-plan.md: 401 lines > 400`
(the file is now reported since the exclusion no longer matches). Restored;
diff empty.

**Slice 7** — whitespace-splitting bug: first attempt (swap
`while IFS= read -r -d '' file` for `while read -r file` fed from
`find ... ` without `-print0`) did **not** break the test — `read` without
`-d ''` still reads a whole line into one variable, so a filename with an
internal space stays intact as long as it has no embedded newline. The
mutation that actually reproduces word-splitting is
`for file in $(find "$dir" -type f -name "*.md")` (command substitution
underneath a `for`, unquoted) replacing the `while read -d ''` loop.
Targeted run:
`pytest tests/test_line_limits.py::test_line_limits_handles_spaced_path` →
`assert 2 == 1`, stderr:
`check_line_limits.sh: line 46: docs/my: No such file or directory` /
`check_line_limits: cannot read docs/my` — the path split at the space and
`check_cap` tried to read the first word alone. Restored; diff empty.
(shellcheck SC2044 fired on this intermediate mutated state, as expected
for a for-over-find loop; not a defect in the restored file.)

## Full-suite check and lint

`pytest -q` (full suite, unmutated tree): 306/325 passed, 16 skipped, 3
failed — the 3 intended slice 4/5 failures above; no other regressions.

`ruff check tests/test_line_limits.py`: all checks passed.
`mypy tests/test_line_limits.py`: no errors.
`docformatter --diff tests/test_line_limits.py`: no diff.
`wc -l tests/test_line_limits.py`: 204 lines (cap 400).

`git diff --stat scripts/check_line_limits.sh`: empty — the SUT was only
ever touched via mutate/restore, never left modified.

Scope respected: only `tests/test_line_limits.py` changed; nothing
committed.
