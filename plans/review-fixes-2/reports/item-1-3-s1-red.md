# Item 1.3 slice 1 RED — NUL-delimited read pin

Test added: `tests/test_changed_files.py::test_paths_with_space_and_non_ascii_bytes_are_listed_whole`
(file now 271 lines). No helper changes. `changed-files.sh` unchanged (byte-identical after both restores; `git status` shows only the test file modified).

## Per-test output

Against the script as it stands: passes (module 6/6), as expected — the behaviour exists (Item 1.2), so RED is by mutation.

## Mutation proof

Both mutants replace this exact string (occurs once in `plugin/skills/build/scripts/changed-files.sh`):

`git diff --name-only --no-renames -z "$base_sha" HEAD -- | while IFS= read -r -d '' path; do`

### Mutant 1 — word-split `for` loop

Replacement:
`for path in $(git diff --name-only --no-renames "$base_sha" HEAD --); do`

Test reds on its assertion (`done || {` still parses after a `for`):

```
E   AssertionError: BASE: 636818520c427da00d71df6cca24e257752f572e
E     "caf\303\251.txt"
E     "inbox/\303\251.md"
E     my
E     file.txt
E     At index 1 diff: '"caf\\303\\251.txt"' != 'café.txt'
E     Left contains 2 more items, first extra item: 'my'
```

Both failure shapes appear: `my file.txt` split into `my` / `file.txt`, and `café.txt` C-quoted (git's `core.quotePath`, since `-z` is gone), which also lets `inbox/é.md` evade the exempt match.

Restore: inverse replacement. Proof: `grep -c 'for path in \$(git diff'` gives 0; module 6/6 passed.

### Mutant 2 — newline `read` with `-z` dropped from the diff

Replacement:
`git diff --name-only --no-renames "$base_sha" HEAD -- | while IFS= read -r path; do`

Test reds on its assertion:

```
E   AssertionError: BASE: 88503d8ccd90e0983c2525ebb66878eb71dfd1d5
E     "caf\303\251.txt"
E     "inbox/\303\251.md"
E     my file.txt
E     At index 1 diff: '"caf\\303\\251.txt"' != 'café.txt'
E     Left contains one more item: 'my file.txt'
```

Here `my file.txt` stays whole (newline read does not split on a space); the red comes from the C-quoted `"caf\303\251.txt"` and the leaked, quoted `"inbox/\303\251.md"`. Confirms the brief's expectation.

Restore: inverse replacement. Proof: `grep -c 'HEAD -- | while IFS= read -r path'` gives 0; module 6/6 passed.

## Fixtures tried and rejected

None. `my file.txt` alone would not red mutant 2 (the space survives a newline read), and `café.txt` alone would not red mutant 1's split; both are needed, as is `inbox/é.md` to show the quoted name escaping the exempt filter.
