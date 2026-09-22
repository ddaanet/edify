# GREEN review — review-fixes (F-1, F-4, F-5)

**Verdict: fix first.** One major, one nit. The major is a false mechanism
claim in the in-situ comment GREEN added at `scripts/check_line_limits.sh:124`
— the code is correct and every behavioural contract holds, but the comment
inverts the causality it exists to record, and I proved it wrong empirically.
One-sentence fix; nothing else blocks the commit.

Everything else checks out. The F-1 code change is minimal and correct, the
unreadable-file exit-2 path still works, GREEN touched nothing under `tests/`,
F-4's sweep is genuinely at zero hits, all four F-5 paths resolve, every
site-count difference against `HEAD` is attributed, and the RED follow-up's
default-invocation tests do what their report says (one mutation repeated).

`just precommit` → `✓ Precommit OK`; full suite 355/356 passed, 1 xfail.

---

## Findings

### Major — the `pipefail` comment states the opposite of the mechanism

`scripts/check_line_limits.sh:122-131`:

```bash
    # An unreadable file leaves the tree unchecked: exit 2, since a bare
    # `set -e` abort here would surface as 1 and read as an overage. The
    # pipeline form (rather than a bare assignment) is what lets `wc -l`'s
    # own failure reach this `if` at all: `pipefail` (set above) makes the
    # pipeline's exit status the last non-zero stage's, so an unreadable
    # $file still trips this branch. `tr -d ' '` strips BSD `wc`'s
    # left-padded field width (unverified on macOS — this box is Linux —
    # but guarded the same way as the repo's other `wc -l` sites, e.g.
    # `plugin/bin/triage-feedback.sh:14`).
    if ! line_count=$(wc -l <"$file" | tr -d ' '); then
```

"The pipeline form (rather than a bare assignment) is what lets `wc -l`'s own
failure reach this `if` at all" is false. A bare assignment propagates the
failure **unconditionally and without `pipefail`** — command substitution's
exit status *is* the command's status. The pipeline form is what would *lose*
the failure; `pipefail` is what restores it. Proved:

```
$ bash -c 'set -eu; f=/nonexistent/zz; if ! n=$(wc -l <"$f" | tr -d " "); then echo CAUGHT; else echo "MISSED n=[$n]"; fi' 2>/dev/null
MISSED n=[]
$ bash -c 'set -euo pipefail; f=/nonexistent/zz; if ! n=$(wc -l <"$f" | tr -d " "); then echo CAUGHT; else echo "MISSED n=[$n]"; fi' 2>/dev/null
CAUGHT
$ bash -c 'set -eu; f=/nonexistent/zz; if ! n=$(wc -l <"$f"); then echo CAUGHT; else echo "MISSED n=[$n]"; fi' 2>/dev/null
CAUGHT
```

Row 3 is the pre-fix form with `pipefail` off: it catches the failure. So the
parenthetical's contrast runs backwards.

This matters beyond pedantry. The comment's job is the note the test review
asked GREEN to carry — "that pipeline form preserves the exit-2 contract
**only because `:32` sets `pipefail`**" (`test-review.md`, §1). As written it
tells a future editor the opposite: that reverting to the bare assignment
would *lose* error detection, when reverting would in fact make the guard
independent of `pipefail`. It also fails to say the thing that needs saying —
don't remove `pipefail` from `:32`. CLAUDE.md's No Confabulation rule applies:
an asserted mechanism that is not what the shell does.

The rest of the comment is accurate: `set -euo pipefail` is at `:32`; bash's
`pipefail` does make the status "the last (rightmost) command to exit with a
non-zero status"; `plugin/bin/triage-feedback.sh:14` does read
`| wc -l | tr -d ' '`; the macOS-unverified hedge matches the source finding's
recorded status.

**Fix.** Replace the two sentences from "The pipeline form" through "trips this
branch." with the correct direction, e.g.:

```
    # The added `tr` makes this a pipeline, so the exit-2 guard now depends
    # on `pipefail` (`:32`): without it the pipeline's status would be `tr`'s
    # zero and an unreadable $file would slip through as line_count="". Do
    # not drop `pipefail` from the `set` line.
```

Also worth trimming while there: eight added comment lines for a one-token code
change is out of proportion to the rest of the file's comment density.

### Nit — the F-4 rewrite drops Item 1.9's "by it" relation

`plugin/skills/design/references/write-design.md:7` and
`plugin/skills/design/references/write-outline.md:149`, identical:

```
**Recall diff:** Read `references/research-protocol.md` §A.5, re-invoke
recall on what just changed, and reconcile the artifact.
```

Imperative Read — the M-6 contract is met, and the path is unchanged as GREEN
says. But every site Item 1.9 fixed binds the Read to the action with an
explicit "by it" / "and … by its …"
(`plans/provenance-enforcement-and-routing/reports/item-1-9.md:33,38,43,48,54,60`),
e.g. `Read \`references/runbook-format.md\` and write both by it.` GREEN's form
is three coordinate imperatives, so the "do this *according to* §A.5" relation
that "per" carried is gone rather than restated. Nothing is lost operationally
and the sentence still reads as an act, not narration — hence a nit.

**Fix (optional).** `Read \`references/research-protocol.md\` §A.5 and, by it,
re-invoke recall on what just changed and reconcile the artifact.`

### Observation, not a finding — the sibling path form in those two files

`references/research-protocol.md` resolves from the **skill base**
(`plugin/skills/design/` → `plugin/skills/design/references/research-protocol.md`,
which exists), not from the citing file's own directory (which would give
`.../references/references/`). That ambiguity predates this job, is the form
Item 1.9 deliberately kept ("sibling bare form the file already uses, kept"),
and F-4 is about the "per" wording only. GREEN flagged it under "anything
unsure" and correctly left it. No action.

---

## What I verified

All commands from `/Users/david/code/edify`.

### 1. F-1 — minimal, correct, contract intact

**Code delta is one token.** `git diff` over the scoped paths shows exactly one
functional change in `scripts/check_line_limits.sh`: `wc -l <"$file"` →
`wc -l <"$file" | tr -d ' '`, plus the comment. `plugin/bin/triage-feedback.sh`
has **no diff at all** — `:77` is still the unguarded `| wc -l` feeding
`[[ … -eq 1 ]]`, left alone as the finding directed.

**Single call site confirmed.**

```
$ grep -rn 'wc -l' --include='*.sh' --include='*.bash' .
plugin/bin/triage-feedback.sh:14:files_changed=$(git diff --name-only "$baseline_commit" | wc -l | tr -d ' ')
plugin/bin/triage-feedback.sh:21:    reports_count=$(find … | wc -l | tr -d ' ')
plugin/bin/triage-feedback.sh:77:            [[ $(find … -name 'review-*.md' | wc -l) -eq 1 ]]; then
scripts/check_line_limits.sh:131:    if ! line_count=$(wc -l <"$file" | tr -d ' '); then
```

Three tree-wide sites, matching the source finding's own sweep; the fixed one
is the only whose value is formatted into output.

**Unreadable-file path still exits 2 with its diagnostic.** The suite test:

```
$ just test tests/test_line_limits_exit_codes.py tests/test_line_limits.py \
      tests/test_line_limits_wc_padding.py tests/test_line_limits_default_invocation.py
**Summary:** 23/23 passed
✓ Tests OK
```

(`test_unreadable_file_outranks_a_later_overage`,
`tests/test_line_limits_exit_codes.py:31`, is in that run.) And by hand against
a chmod-000 fixture:

```
$ ./scripts/check_line_limits.sh --allowlist "$TMPDIR/empty.allow" "$TMPDIR/ur"
./scripts/check_line_limits.sh: line 131: docs/locked.md: Permission denied
check_line_limits: cannot read docs/locked.md
EXIT=2
```

**`shell-gotchas` pass over the changed lines.** Invoked
`shell-scripting:shell-gotchas` and checked each applicable row:

- *`v=$(cmd)` under `set -e` runs with errexit off* — not a hazard here; the
  status is explicitly tested by `if !`, which is the skill's prescribed form.
- *`pipefail` + early-exit consumer (`grep -q`, `head`) → SIGPIPE 141* — `tr`
  drains its input, so no early close. Safe.
- *`x=$(producer | filter || echo FB)` under `pipefail`* — no `||` inside the
  substitution. N/A.
- *`tr -d ' '` deletes spaces only* — BSD `wc` pads with spaces, so the strip
  matches the shape claimed. No tab case exists for `wc`.
- *Quoting / filename safety* — `<"$file"` quoted; the surrounding walk already
  uses `find -print0` + `read -r -d ''` (`:166-170`). Unchanged by this fix,
  and `test_line_limits_handles_spaced_path` covers it.
- *Dishonest success paths* — none introduced; failure still reaches stderr and
  exit 2.

```
$ shellcheck -S style scripts/check_line_limits.sh
shellcheck-exit=0
```

Clean, no output. The one thing the skill's checklist asks for that the comment
gets wrong is the mechanism claim — the major finding above.

**GREEN touched nothing under `tests/`.** The `tests/` diff contains exactly
what `red.md` describes and nothing else: the three F-3 tests appended to
`tests/test_line_limits.py`, and the helper's `path_prepend` / `script` /
`allowlist="default"` / `omit_root` parameters, `_write_padded_wc_shim`, and
the two corrected docstrings. Line counts match `red.md`'s closing numbers
exactly, so no edit landed after RED closed:

```
$ wc -l tests/test_line_limits.py tests/line_limits_helpers.py \
       tests/test_line_limits_wc_padding.py tests/test_line_limits_default_invocation.py
  377 tests/test_line_limits.py          (red.md: 377)
  157 tests/line_limits_helpers.py       (red.md: 157)
   38 tests/test_line_limits_wc_padding.py  (red.md: 39 — the test review's standing nit, unchanged)
  106 tests/test_line_limits_default_invocation.py  (red.md: 106)
```

### 2. F-4 — zero hits, independently classified

```
$ rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/
EXIT=1
```

No hits, so there is nothing to classify. I did not take the empty result on
faith:

- **Pattern is live.** Fed it the pre-fix sentence verbatim —
  ``**Recall diff:** per `references/research-protocol.md` §A.5`` — and it
  matched at line 1. The sweep would have caught the old text.
- **Nothing hidden from `rg`.** `rg --files plugin/ docs/` yields 106 files;
  git (tracked + untracked, honouring `.gitignore`) yields 111. `comm` on the
  two sorted lists shows the five-file gap is `plugin/.claude-plugin/plugin.json`,
  `plugin/.claude/settings.json`, the `plugin/.claude/skills` symlink (→
  `../skills/`, already walked), `plugin/.gitignore`, and
  `plugin/skills/build/references/resuming.md` (deleted in the working tree,
  still in the index). No prose file is missed. Re-ran with
  `--hidden --no-ignore` anyway: still `EXIT=1`, zero hits.

The two rewrites are imperative Reads (`Read \`references/…\``), the paths
resolve from the skill base as they did before (see the Observation above), and
the condition is carried by the pre-existing `**Recall diff:**` label. The one
delta from Item 1.9's established form is the nit above.

### 3. F-5 — four paths resolve; every count difference attributed

**Resolution.** All four edited sites are `plugin/skills/<skill>/SKILL.md`, so
`../../fragments/delegation.md` resolves to `plugin/fragments/delegation.md`
under *either* reading — from the skill's announced base directory or from the
file's own directory, since a `SKILL.md` sits directly in the base. No
ambiguity here (unlike the `references/` sites, where only the base-directory
reading works). `plugin/fragments/delegation.md` exists, and all three cited
anchors are real headings in it:

```
$ grep -n '^#' plugin/fragments/delegation.md
39:### Quiet Execution Pattern
89:### Recall Artifacts For Sub-Agents
116:### Recall Content In Delegation Prompts
```

The form matches what the source finding prescribed verbatim
(`deliverable-review.md:160-162`: "from base `plugin/skills/<skill>/`, the
fragment is `../../fragments/delegation.md`") and matches the pre-existing
same-depth precedent `plugin/skills/review/SKILL.md:158` at `HEAD`.

**Counts.** Backticked `` `plugin/(skills|agents|fragments|bin|hooks)/…` ``
inside `plugin/skills`, `plugin/agents`, `plugin/fragments`:

| | sites | files |
|---|---|---|
| `HEAD` | **33** | **16** |
| working tree | **27** | **14** |

The `HEAD` figure reproduces the source finding's own measurement exactly
(`deliverable-review.md:141-142`: "33 sites in 16 files at HEAD"). GREEN's
"before: 31 in 16" is the *working tree* at its start, which equals 27 + its
own 4 removals — self-consistent.

Per-file delta `HEAD` → working tree, every difference accounted for:

| File | HEAD | WT | Attribution |
|---|---|---|---|
| `skills/recall/SKILL.md` | 2 | 0 | **this job**, F-5 edits 2 and 3 |
| `skills/ground/SKILL.md` | 1 | 0 | **this job**, F-5 edit 1 |
| `skills/deliverable-review/SKILL.md` | 2 | 1 | **this job**, F-5 edit 4 |
| `skills/design/SKILL.md` | 4 | — | other agent: text extracted verbatim into… |
| `skills/design/references/triage.md` | — | 4 | …this new untracked file (net 0; `` `plugin/bin/` ``, `` `plugin/skills/` ``, `` `plugin/fragments/` ``, `` `plugin/agents/` `` on the same two lines, moved `:134-135` → `:63-64`) |
| `skills/build/SKILL.md` | 3 | 1 | other agent: `escalation-acceptance.md` moved out to the new `references/escalation.md` (and *rewritten* there to `../../fragments/…`), and the `delegation.md` bullet removed with the references list at `:48-55` |
| all others | | | unchanged |

33 − 2 − 1 − 1 − 4 + 4 − 2 = 27. ✓

`plugin/agents/tdd-auditor.md` still carries its one repo-relative path —
correctly left to the deferred job, as F-5 itself directs.

### 4. RED follow-up spot-check — default-invocation tests

**Relocated copy with its executable bit:** two of the three do, and the third
deliberately does not.

- `_copy_script` (`tests/test_line_limits_default_invocation.py:28`) uses
  `shutil.copy2` (preserves mode) **and** an explicit `script_copy.chmod(0o755)`.
  `_run_check_line_limits` invokes `[str(script_path)]` with no shell, so the
  bit and the shebang are load-bearing exactly as in production's
  `./scripts/check_line_limits.sh` (`git ls-files -s` → `100755`).
- `test_line_limits_root_defaults_to_cwd_when_omitted` (`:89`) runs the
  **canonical** `SCRIPT` with `omit_root=True`, not a copy — correct, since it
  pins `ROOT="."` in isolation from the sidecar question and says so in its
  docstring. The task's premise that all three relocate is not quite right; the
  design is.

Neither relocated test can read the production allowlist: `allowlist="default"`
resolves the sidecar next to the *copy*, under `tmp_path/bin/`, and the script
`cd`s into `ROOT` (`tmp_path/root`) so `bin/` is never walked.

**Mutation repeated — RED's Mutation 1.** `scripts/check_line_limits.sh:64`,
`ALLOWLIST="$SCRIPT_DIR/check_line_limits.allow"` →
`ALLOWLIST="$PWD/check_line_limits.allow"`:

```
$ just test tests/test_line_limits_default_invocation.py tests/test_line_limits.py \
      tests/test_line_limits_exit_codes.py tests/test_line_limits_wc_padding.py
**Summary:** 22/23 passed, 1 failed

### tests/test_line_limits_default_invocation.py::test_line_limits_default_sidecar_applies_its_ceiling FAILED
tests/test_line_limits_default_invocation.py:60:
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: oversized-file: docs/notes.md: 401 lines > 400
E   assert 1 == 0
```

Exactly one red, and it is the test named for that mutation — reproducing
`red.md`'s Mutation 1 result precisely (the overage line is still printed; only
the ceiling fails to apply, because `$PWD/check_line_limits.allow` does not
exist at that cwd and the sidecar silently resolves empty). The other two
default-invocation tests are correctly blind to it: the no-sidecar test asserts
exit 1 either way, and the `ROOT` test never reaches the sidecar branch.

Inverted the same Edit. Restoration confirmed by identical `git diff`
fingerprint before and after, plus a residue grep:

```
$ git diff -- scripts/check_line_limits.sh | sha256sum     # before mutation
8b94403ddce1dd28e1ab9ccc2e9e1631c7a37778558e813a3ba1091441f2b474  -
$ git diff -- scripts/check_line_limits.sh | sha256sum     # after inversion
8b94403ddce1dd28e1ab9ccc2e9e1631c7a37778558e813a3ba1091441f2b474  -
$ grep -n 'PWD/check_line_limits' scripts/check_line_limits.sh
residue-grep-exit=1
```

I did not repeat Mutations 2 and 3; one was asked for. Their reported shapes
are consistent with the code I read (`:74`'s `-f` guard, `:35`'s `ROOT="."`),
and `red.md`'s honest note that Mutation 2 is caught by the *stdout* assertion
rather than the return code — bash's redirection-failure exit is 1 by
coincidence — is the kind of finding that argues the report was not
back-filled.

### 5. Gate

```
$ just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

**PASS.** The three `oversized-file:` lines are allowlisted entries, reported
per KD-7's design and not gating; none is a file this job touched.

`precommit` reported `Tests cached`, so to make that leg real evidence rather
than a sentinel hit I ran the suite explicitly:

```
$ just test
# Test Report

**Summary:** 355/356 passed, 1 xfail
✓ Tests OK
```

Matching `green.md`'s figures.

---

## Commands run

1. `git diff --stat` / `git diff` over the scoped paths; `git status --porcelain`
   over `scripts/ plugin/bin/ plugin/skills/ tests/`
2. `sed -n` over `scripts/check_line_limits.sh` (`:25-40`, `:60-80`, `:115-140`,
   `:160-175`); `grep -rn 'wc -l' --include='*.sh'`
3. `Skill(shell-scripting:shell-gotchas)`; `shellcheck -S style scripts/check_line_limits.sh`
4. Three `bash -c` probes of `pipefail` vs bare-assignment status propagation
5. Hand probe: chmod-000 fixture through `./scripts/check_line_limits.sh` → `EXIT=2`
6. `rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/` → 0 hits; pattern-liveness
   check on the pre-fix sentence; `comm` of `rg --files` against `git ls-files`
   (tracked + untracked); re-run with `--hidden --no-ignore` → 0 hits
7. `git ls-tree -r HEAD` + `git show HEAD:<f>` piped through
   `grep -Eo '`plugin/(skills|agents|fragments|bin|hooks)/[^`]*`'` → 33 in 16;
   same `grep -rEo` over the working tree → 27 in 14; per-file `uniq -c` diff and
   attribution via `git diff -- plugin/skills/build/SKILL.md` and
   `git show HEAD:plugin/skills/design/SKILL.md`
8. `grep -rn '\.\./\.\./fragments/' plugin/`; `grep -n '^#' plugin/fragments/delegation.md`;
   `ls plugin/skills/design/references/`
9. `just test` over the four line-limit modules → 23/23
10. Edit `:64` → `$PWD`; same `just test` → 22/23, one named red; Edit inverted;
    diff-hash and residue grep clean
11. `just precommit` → `✓ Precommit OK`; `just test` → 355/356, 1 xfail

## Tree state

I edited only this report, plus the one mutation at
`scripts/check_line_limits.sh:64` which is inverted and proved identical by
`git diff` fingerprint. The scoped tree is unchanged from how GREEN left it.
Unrelated dirt from concurrent agents (`plugin/skills/build/`, `design/`,
`proof/`, `requirements/`, `scripts/check_line_limits.allow`) is not mine and
is not touched.
