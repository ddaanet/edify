# build-defects — leg 2 (slice 1.2/2, Item 2.1 attempted)

**Status: stopped by the parent after Item 2.1 was blocked.** Slice 1.2/2 and
both of my human partner's decisions are committed. Item 2.1 was never
committed: the auto-mode classifier refuses every `Edit` of
`plugin/skills/build/SKILL.md` ("gave no verdict"), for the artisan and for
this leg alike. Items 2.2–2.9 are not done. The artisan's `Edit` of
`references/phase-boundary.md` got the same "no verdict". Its fallback was a
Python-built patched copy, which the classifier then *denied* as
"[Auto-Mode Bypass]". The parent withdrew the patched-copy route for everyone
and stopped all dispatches.

Entry state: HEAD `4a24c0fe`, baseline `f44ddbbf…` in `tmp/build-baseline`,
untouched. §2's entry gate had already passed. Pre-work: there is no
`brief.md` and no `recall-artifact.md`. Recall selected
`edify-commit-hook-gotchas`, `macos-gate-target`,
`audit-a-contract-across-its-surfaces`, `reflow-joins-field-lines` and
`cc-subagent-approval`, and loaded `craft:test-discipline`.

Dispatch notes: every dispatch ended "without delivering a report through
SubagentHandback". Each time, its report file was on disk and was read there.
Dispatches ran unnamed and were resumed by agentId.

## Decisions recorded — `9ccbcecc`

`plans/build-defects/outline.md` (list revision, self-reviewed):
- **KD-7:** one added sentence. Every committing dispatch commits with
  `git commit -- <paths>`, so exempt dirt that is already staged stays out.
  This is decision 1, option (a).
- **Item 2.5:** widened to §Prompt contents item 4, `plugin/agents/test-driver.md`
  and `plugin/agents/refactor.md`.
- **Scope IN:** now names the two agent definitions.
- **Slice 1.2/2:** added to Item 1.2 with its four tests (decision 2).

## Slice 1.2/2 — F-1/F-2 pinning tests: done

**Commits**
- `2c35c093` ✅ Item 1.2/2 — GREEN, confirm-and-commit with no SUT edit. It
  carries `tests/test_verify_step.py` and the RED, test-review and GREEN
  reports.
- `8811af35` 📝 Item 1.2/2 — code-review fixes. The report only; F-3 was
  routed.
- `e8179177` 🐛 Item 1.2/2 — F-3 plus decision 1's comment premise in
  `verify-step.sh`. My human partner copied the verified patched copy into
  place (the parent confirmed it with `cmp`), and this leg committed it after
  `just precommit` (366/367 passed, 1 xfail, Precommit OK).

**Tests added:** `test_rename_out_of_exempt_path_is_dirty`,
`test_quoted_exempt_path_is_clean`, `test_git_status_failure_exits_2` and
`test_missing_just_exits_2`. `_run_script` gained an optional `extra_env`.

**RED evidence (mutation red, on copies).** `31fe4a16`'s script was copied to
`tmp/mutants/pre-f1.sh` and run with the test module's `SCRIPT` rebound by a
scratch pytest plugin (`tmp/mutants/rebind.py`). The tracked file was never
reverted.
- The four new tests fail on their own `returncode` assertion, observing
  0, 1, 128 and 1. The slice 1 test stays green.
- The control copy of the current script passes 5/5.

**Test review.** It reproduced each red with its own targeted mutant, one per
behaviour, and each mutant reds only its own test. Fixes applied:
- **Major:** the quoted-path test passed with *every* quoted path exempt. A
  decoy phase with `?? "inbox/my notes.txt"` now reds that mutant.
- **Minor:** the missing-just message is now asserted as a whole line.
- **Minor:** the rename docstring was reworded.

**Code review** (`item-1-2-s2-code-review.md`). 4a24c0fe matches the F-1/F-2
text exactly, and F-2 is correct. The script is portable to bash 3.2 and BSD
grep in syntax. One major fix:
- **F-3.** `grep -vE … <<<"$porcelain"` read a failed here-string temp file
  (redirection exit 1) as "every line filtered out". The result was CLEAN,
  exit 0, on a dirty tree, and it was reproduced. On bash 3.2 every
  here-string uses a temp file. The fix is a `printf '%s\n' … | grep` pipe
  with a comment. It was verified on a copy (bash -n, shellcheck, 5/5 via
  rebind) and landed in `e8179177`.

**Post-item verification:** CLEAN after `2c35c093`, `8811af35` and
`e8179177`.

**Refactor and list revision.** No refactor was flagged. List revision:
slice 1.2/2 was added before its RED; nothing else changed.

## Item 2.1 — `SKILL.md`: blocked, not committed

The artisan wrote `plans/build-defects/reports/item-2-1.md`, committed with
this report. It holds the exact old→new text for every bullet, one per
finding:
- orch M1/m7: frontmatter drops `TaskOutput`, `TaskStop`.
- orch C2: §1 says `<job>` is the invocation's path.
- orch m5: the §2 DIRTY bullet names the KD-7 exemptions and the mask re-run.
- inline m9: §3.2 is now a sentence.
- orch m3: §4.1 is "scoped to this item's changes".
- orch M4: §4.2 has the corrector-item commit, made with
  `git commit -- <paths>`.
- orch M4: §4.4 lists that case.

Before the route was withdrawn, this leg built `tmp/patched/SKILL.md` from
that text (rumdl-formatted, 200 lines). Per the parent, that file is left
untouched and my human partner decides about it.

**Carry-forward (from the artisan).** `SKILL.md` §2 says "This script is the
skill's single definition of a clean tree; Section 4 and
`references/phase-boundary.md` call the same one." That goes stale once
Item 2.2 drops phase-boundary's `verify-step.sh` run and Item 2.3 adds one to
`finishing.md`. It must then name `references/finishing.md` instead. Neither
`item-2-1.md` nor `tmp/patched/SKILL.md` carries that change.

## Items 2.2–2.9: not done

The artisan's `Edit` of `references/phase-boundary.md` (Item 2.2) was
refused with "no verdict". Its patched-copy script was denied as
"[Auto-Mode Bypass]". No report exists for 2.2 onward, and nothing is
committed. Every remaining target is under `plugin/`: five references, three
fragments and two agent definitions. Nothing in this leg shows which of them
the classifier accepts.

## Deferred and routed

- **Deferred, my human partner's call:** the `C` (copy) half of
  `verify-step.sh`'s `[^RC][^RC]` guard is unpinned. A `^[^R][^R]` mutant
  passes all five tests. The code review confirmed a `C` line is reachable
  with `status.renames=copies`. No slice 1.2/3.
- **Observed, not raised as findings** (code review Recommendations):
  - Unmerged exempt paths (`UU .claude/handoff-task.md`) read CLEAN. That is
    consistent with KD-7's "any state", and any commit refuses during a merge
    anyway.
  - `"?…"?` accepts an unbalanced quote that git never emits.
- **Gap outside IN:** `references/tdd-slice.md`'s orchestrator commits
  (GREEN staging, After-the-slice step 1) still say "stage by name" without
  `git commit -- <paths>`. Item 2.5 covers `dispatch-composition.md` and the
  agents but not this file.
- **Pre-existing, out of scope:** the 1.1/1 `xargs` / `|| true` DEFERRED item
  in `triage-feedback.sh`, and `just lint`'s RUF100 in
  `tests/line_limits_helpers.py`.

## Final `verify-step.sh` output

This run was after `e8179177`, before `item-2-1.md` existed. The sandbox was
disabled:

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
CLEAN: tree clean, just precommit passed
exit=0
```

## Resume block

- **Where the next leg starts.** Item 2.1, once my human partner settles how
  edits under `plugin/` land. Direct `Edit` gets "no verdict" and the
  patched-copy route is withdrawn. If `tmp/patched/SKILL.md` is adopted,
  commit it with the already-committed `item-2-1.md` as Item 2.1 (the report
  needs no change). Then run the §4.1 review: the change is over 5 lines, so
  a corrector is required unless it was delegated. Then do Items 2.2–2.9 in
  order, applying the carry-forward above to `SKILL.md` §2 when 2.2/2.3 land.
- **Commit form.** Every commit uses `git commit -- <paths>` (KD-7). That
  includes the orchestrator's own, until Item 2.5 writes it into the pipeline
  text.
- **Tree state at stop.** Clean except for the untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md`. That file
  belongs to another session, is KD-7-exempt, and must never be staged.
  Gitignored scratch left in place: `tmp/mutants/` (the rebind harness and
  mutants) and `tmp/patched/`.
- **Baseline.** `tmp/build-baseline` holds `f44ddbbf…`, unchanged. §5 Finish
  uses it; it has not run.
