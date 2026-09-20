# Item 1.10, slices 3-7 — test review

Verdict: **RED confirmed.**

Scope held: only `tests/test_line_limits.py` is modified. The SUT
(`scripts/check_line_limits.sh`) was touched only via mutate/restore and is
byte-clean; nothing committed.

## Mechanical run (before fixes)

`pytest tests/test_line_limits.py -v` — 5/8 passed, 3 failed. All three
failures are on the intended assertion, not an ERROR:

- `test_line_limits_reports_allowlisted_without_failing` — `assert 2 == 0`
- `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent` — `assert 2 == 0`
- `test_line_limits_fails_allowlisted_file_over_ceiling` — `assert 2 == 1`

each with `check_line_limits: --allowlist: not implemented` on stderr. The
pre-existing slice 1-2 tests and slices 3, 6, 7 passed, as the RED report
stated.

## My own mutation proofs

One mutation at a time, applied with a `python3` heredoc asserting a unique
match, restored with `git checkout -- scripts/check_line_limits.sh`;
`git diff --stat scripts/check_line_limits.sh` printed empty after every
restore (recorded as `restore diff: []` in each run). These are distinct
mutations from the RED report's, not a re-run of them.

**Slice 3a** — deleted the line
`[ "$(basename "$file")" = "SKILL.md" ] && cap=200`, so the cap is globally
400. `pytest ...::test_line_limits_fails_skill_hub_over_200` →
`assert 0 == 1` (the 201-line `SKILL.md` no longer exceeds 400).

**Slice 3b** — replaced `cap=400` + the SKILL.md line with a bare `cap=200`,
so the cap is globally 200. Same test → `assert 1 == 0` on the *second* half,
stdout `oversized-file: plugin/skills/x/notes.md: 201 lines > 200`. 3a and 3b
together prove the assertion is path-picked-ness, not either cap alone.

**Slice 6** — deleted the whole `case "$file" in ... esac` exclusion block.
`pytest ...::test_line_limits_skips_frozen_docs` → `assert 1 == 0`, stdout
`oversized-file: docs/superpowers/plans/old-plan.md: 401 lines > 400`.

**Slice 6b** (proves the exclusion case I added) — dropped only the
`docs/superpowers/specs/*` alternative. Same test → `assert 1 == 0`, stdout
`oversized-file: docs/superpowers/specs/old.md: 401 lines > 400`.

**Slice 6c** (proves the in-scope case I added) — widened the exclusion to
`docs/superpowers/*`. `test_line_limits_skips_frozen_docs` **passed** and
`test_line_limits_checks_living_superpowers_docs` failed with
`assert 0 == 1` — exactly the wrong GREEN the new test exists to catch.

**Slice 7** — unquoted the call site: `check_cap "$file" "$cap"` →
`check_cap $file "$cap"`. `pytest ...::test_line_limits_handles_spaced_path`
→ `assert 2 == 1`, stderr
`check_line_limits.sh: line 46: docs/my: No such file or directory` /
`check_line_limits: cannot read docs/my`. This is a different word-splitting
mutation from the RED report's for-over-find; it confirms the RED report's
finding that the loop's `read -r -d ''` is not the only place splitting can
enter.

## Findings and disposition

1. **Slice 3's `SKILL.md` half asserted only a substring** —
   `assert "> 200" in skill_result.stdout`. That passes on a script that
   reports the wrong path or emits extra lines. **Fixed:** tightened to
   `result.stdout.splitlines() == ["oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200"]`.
   Every other assertion in the file already used exact `splitlines()`
   equality or an explicit absence check.

2. **Slice 6 covered `plans/` only.** The script excludes `plans/` and
   `specs/`; nothing pinned `specs/`, and nothing stopped a GREEN from
   excluding `docs/superpowers/` wholesale. **Fixed:** `skips_frozen_docs`
   now loops over both frozen subdirectories in separate trees, and a new
   `test_line_limits_checks_living_superpowers_docs` asserts a 401-line
   `docs/superpowers/design/living.md` exits 1 and is reported. Mutation 6c
   above shows the pair discriminates.

3. **No allowlist fixture carried a `#` comment or a blank line**, so a GREEN
   that treated every line as an entry would pass. **Fixed:** `_write_allowlist`
   now always prepends `# path\tceiling\tnote` and a blank line, so all six
   allowlist tests exercise the skip. Docstring updated to say why.

4. **Nothing forced exact allowlist path matching.** **Fixed:** new
   `test_line_limits_matches_allowlist_paths_exactly` — three 401-line files,
   only `docs/notes.md` allowlisted; `docs/my-notes.md` (caught by an
   unanchored `case "$file" in *$entry*`) and `docs/sub/notes.md` (caught by a
   basename comparison) must still fail. Asserts exit 1 and all three lines
   present. Both decoy names stay inside the markdown scope and match
   `find -name "*.md"`, so they are actually scanned — a `.bak` decoy would
   not have been.

5. **The TAB separator's own motivation was untested.** The format is
   TAB-separated *because* a path may contain a space (slice 7), yet no
   allowlist fixture used one. **Fixed:** new
   `test_line_limits_allowlists_a_spaced_path` — `docs/my notes.md` at 401,
   allowlisted at ceiling 401: exit 0 with the path intact in the reported
   line. A GREEN splitting an entry on whitespace gets path `docs/my` and
   ceiling `notes.md` and cannot pass this.

### Wrong-reason checks that passed as written

- Slice 4's ceiling equals the file's count (401/401) and it asserts the
  `oversized-file:` line is **still** printed — a silently-skipping GREEN
  fails it. Correct as the "lists the old" half of KD-7.
- Slice 4/5 together pin the boundary exactly: 401 vs ceiling 401 passes,
  451 vs ceiling 450 fails. `>=` and `>` are distinguished.
- Slice 5's message names the path-picked cap (`> 400`), not the ceiling.
  Asserted exactly.
- Slice 7's spaced path is asserted via full-line equality, so it appears
  intact and exactly once.
- Slice 3 uses two separate fixture trees, correctly — a shared tree would
  exit 1 from the `SKILL.md` regardless of the sibling's cap.

### Left, with reason

- **`./`-prefixed allowlist entry** — left per the dispatch.
- **Missing or unreadable allowlist file.** No test pins whether that is exit
  2 (a failure to run, consistent with the script's existing `cd`/`wc`
  handling) or a silent empty allowlist. Out of the slices' scope; flagging
  it so GREEN picks deliberately rather than by accident.
- **Ceiling ratchets down only.** KD-7 says the ceiling only ratchets down,
  but that is a property of how entries are *authored*, not something the
  script can enforce at check time, and no slice asks for it. Not tested.
- **A file both frozen-excluded and allowlisted.** Unreachable combination in
  practice; not worth a fixture.

## Final state

`pytest tests/test_line_limits.py`: 6/11 passed, 5 failed. All five failures
are assertion failures — `assert 2 == 0` ×3, `assert 2 == 1` ×2 — with
`check_line_limits: --allowlist: not implemented` on stderr. No ERRORs.

Red (all five are the `--allowlist` surface, unimplemented by design):

- `test_line_limits_reports_allowlisted_without_failing` (slice 4)
- `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent` (slice 4)
- `test_line_limits_fails_allowlisted_file_over_ceiling` (slice 5)
- `test_line_limits_allowlists_a_spaced_path` (added, finding 5)
- `test_line_limits_matches_allowlist_paths_exactly` (added, finding 4)

Green against current code, as expected for slices 3, 6, 7 plus the added
in-scope guard: `passes_clean_tree`, `fails_markdown_over_400`,
`fails_skill_hub_over_200`, `skips_frozen_docs`,
`checks_living_superpowers_docs`, `handles_spaced_path`.

Full suite (`pytest -q`, before finding 5's test was added): 310 passed, 4
failed, 16 skipped — the 4 failures all in `tests/test_line_limits.py` and all
the intended allowlist reds. No failure anywhere else in the suite.

Lint bar, all clean on `tests/test_line_limits.py`:

- `ruff check` — all checks passed
- `ruff format --check` — already formatted
- `mypy` — no output
- `docformatter --diff` — no diff
- `wc -l` — 278 lines (cap 400)

Paths in the tests are built with `Path` `/` joins throughout; no test splits
any value on whitespace.
