# build-defects — leg 2 (slice 1.2/2, Items 2.1–2.4; 2.5 blocked)

**Status: stopped at Item 2.5, blocked by the auto-mode classifier.** Slice
1.2/2, both of my human partner's decisions and Items 2.1–2.4 are committed.
Item 2.5's exact old→new text is in `item-2-5.md`, committed with this report.
Items 2.6–2.9 are not started.

**How the leg went, in order:**
1. First stop. In auto mode, every `Edit` under `plugin/` (`SKILL.md`,
   `phase-boundary.md`) got "gave no verdict". The patched-copy fallback was
   then *denied* as "[Auto-Mode Bypass]". The parent withdrew that route and
   deleted `tmp/patched/`.
2. My human partner took the session out of auto mode. This leg then applied
   Item 2.1 itself.
3. The first artisan still ran in auto mode, which it had inherited at spawn,
   and was refused on 2.2.
4. A fresh artisan, spawned under accept-edits, committed 2.2–2.4.
5. The session then returned to auto mode, and the artisan's `Edit` of
   `dispatch-composition.md` (2.5) got "no verdict". The parent had
   authorized this leg to make item edits itself if the artisan was refused.
   This leg's own `Edit` of the same file got the same "no verdict", so it
   stopped rather than work around it.

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

## Item 2.1 — `SKILL.md`: done — `28ba697c`

This leg applied it with `Edit`, verbatim from the artisan's `item-2-1.md`,
after auto mode was lifted. `just format` reflowed it. The report's Status
line now records that. `SKILL.md` is 200 lines. Review: the text was authored
by a delegated artisan (§4.2), and this leg only transcribed it, so no per-item
corrector ran. §5's review gate covers it. Post-item verification: CLEAN.

What the report records, one bullet per finding:
- orch M1/m7: frontmatter drops `TaskOutput`, `TaskStop`.
- orch C2: §1 says `<job>` is the invocation's path.
- orch m5: the §2 DIRTY bullet names the KD-7 exemptions and the mask re-run.
- inline m9: §3.2 is now a sentence.
- orch m3: §4.1 is "scoped to this item's changes".
- orch M4: §4.2 has the corrector-item commit, made with
  `git commit -- <paths>`.
- orch M4: §4.4 lists that case.

**Carry-forward, done in Item 2.3.** `SKILL.md` §2 said "Section 4 and
`references/phase-boundary.md` call the same one". It now reads "Section 4
and `references/finishing.md` §1 call the same one". An `rg` check found
`verify-step.sh` run at `SKILL.md` §2 and §4.4 and at `finishing.md` §1, and
no longer in `phase-boundary.md`.

## Items 2.2–2.4 — done (one fresh opus artisan dispatch)

- `5e2039fb` Item 2.2, `phase-boundary.md`, applied from the first
  artisan's prepared text:
  - the `verify-step.sh` run is dropped (m4);
  - the KD-1 phase base: `tmp/build-baseline` for phase 1, and for phase P>1
    the `git log --diff-filter=A` resolution of `phase-<P-1>-corrector.md`
    (C1);
  - the dispatch is scoped to the phase's items (m3);
  - the halt covers the full §Execution Context set, Constraints included
    (M8);
  - the boundary commit takes `git commit -- <paths>`.
- `653d9c45` Item 2.3, `finishing.md`, plus the one `SKILL.md` sentence
  above:
  - group scope;
  - UNFIXABLE validation;
  - the report-only re-dispatch;
  - `verify-step.sh` must exit 0 before §2;
  - `WARNING: No corrector report` handling.
- `24879259` Item 2.4, `review-dispatch-template.md`:
  - an explicit changed-files list;
  - a `**Constraints:**` block;
  - an agent-definition criteria line;
  - report path and return defer to `dispatch-composition.md`;
  - the routing paragraph replaced by a pointer to `finishing.md` §1.

The artisan's judgement calls, recorded in the item reports:
- **2.3.** KD-2 does not say what the single report-only re-dispatch's
  findings become. Settled: they are appended to the same `review-<group>.md`
  and applied, with no further pass. The re-dispatch's name was left unsaid.
  A non-zero verify exit routes to `escalation.md` §Post-item remediation.
- **2.4.** Its pointers to `dispatch-composition.md` land fully only once
  Item 2.5 adds `review-<group>` and the report-only exception. Until then
  they are partly dangling.
- **2.4, noticed and not changed.** The §Example dispatches a skill group
  through the fix-capable template, while `review-requirement.md` routes skill
  definitions to the report-only `plugin-dev:skill-reviewer`. The example is
  correct only under the plugin-dev-absent fallback.

Post-item verification after `24879259`: see Final `verify-step.sh` output.

## Item 2.5 — blocked; Items 2.6–2.9 not started

`item-2-5.md`, committed with this report, holds the exact old→new text for
all five edits:
- §Naming `review-<group>`;
- §Prompt contents item 4, `git commit -- <paths>`;
- item 5, the report-only reviewer as the second exception, with UNFIXABLE
  inside the report;
- `test-driver.md` GREEN step 6;
- `refactor.md` Step 6.

Nothing was applied: the artisan's three `Edit`s and this leg's one `Edit` on
`dispatch-composition.md` all got "no verdict". The agent definitions were
not tried. Its note: `references/tdd-slice.md`'s orchestrator commits (OUT)
lack the pathspec form.

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

The run after `24879259` (Item 2.4), the last item commit, is below. For
reference, the earlier run after `e8179177` is kept after it. The sandbox was
disabled for both.

After `24879259`: this run follows in the commit after this report's first
commit. Only reports changed between the two, so the run is on the same
plugin tree.

After `e8179177`:

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

- **Where the next leg starts.** Item 2.5, applied from `item-2-5.md` once
  edits under `plugin/` can land. That means the session out of auto mode,
  and any executor spawned *after* the mode change, since an agent keeps the
  mode it was spawned under. Re-check each old string first. Then update the
  report's Status line and commit it with the three targets. Then Items
  2.6–2.9 in order, then §5 Finish. §5 has not run.
- **Before §5.** Item 2.4's pointers to `dispatch-composition.md` land fully
  only after 2.5. The 2.3 judgement on the re-dispatch's findings is the
  artisan's reading of KD-2; §5's review gate should check it.
- **Commit form.** Every commit uses `git commit -- <paths>` (KD-7). That
  includes the orchestrator's own, until Item 2.5 writes it into the pipeline
  text.
- **Tree state at stop.** Clean except for the untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md`. That file
  belongs to another session, is KD-7-exempt, and must never be staged.
  Gitignored scratch left in place: `tmp/mutants/` (the rebind harness and
  mutants). The parent deleted `tmp/patched/`.
- **Baseline.** `tmp/build-baseline` holds `f44ddbbf…`, unchanged. §5 Finish
  uses it; it has not run.
