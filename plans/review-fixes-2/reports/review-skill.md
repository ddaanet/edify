# Review gate: review-skill (review-fixes-2)

**Reviewer**: `plugin-dev:skill-reviewer` (report-only, §Report-only variant),
dispatch name `review-skill`. One reply carried all four parts and ended
`END OF REPORT`. The findings below are the reviewer's, written to file by the
orchestrating session, which applied the fixes (§Fixes Applied).
**Baseline**: `888eda7a312e962a28ba59c2695eecd5f34c6e14`
**Files**: `plugin/skills/build/SKILL.md`; `references/` `dispatch-composition.md`,
`escalation.md`, `finishing.md`, `review-dispatch-template.md`, `tdd-slice.md`;
`plugin/fragments/` `delegation.md`, `escalation-acceptance.md`,
`review-requirement.md`.

## Summary (reviewer)

All nine files carry their items' edits (KD-3, KD-4, KD-5, KD-6, KD-7, KD-8,
KD-9; m9, m10, m12, m14, m15, m16, m18). No file cites an outline `KD-N`.
SKILL.md 199 lines; every reference under 300; no crammed lines. The prose
matches the scripts' outputs and exits. No critical, 3 major, 8 minor, no
UNFIXABLE. Rating: Needs Improvement — the majors are cross-file mismatches
within one contract.

## Major

1. **finishing.md §2, last sentence: N-1's line is dropped where the output is
   read.** "On match or no-classification with no warning → proceed silently"
   covers a run printing `unrecognised classification: <label>`, so neither the
   bad label nor the missing row reaches my human partner. (The code review's
   Minor 5, rated higher.) Change: surface that line inline, stating that the
   label is none of the four classes and no row was logged.
   - **Status**: FIXED
2. **finishing.md §3 step 1 and dispatch-composition.md `final-review` bullet:
   the m16 skip on an empty list sends a corrector over nothing.** §1 step 1
   takes the `review-skip.md` branch on an empty list; §3.1 then dispatches
   `final-review` for "a run whose review was skipped", with an empty Changed
   files list, which `review-requirement.md` §Execution Context forbids
   ("Must not be empty"). Change: "skipped over a non-empty list", "an empty
   list has nothing to review here either", mirrored in the bullet.
   - **Status**: FIXED
3. **finishing.md §3 step 2 and dispatch-composition.md §Prompt contents item
   2: the tdd-audit inputs contradict the auditor as KD-7 changed it.** Both
   restrict the auditor to the slice reports ("and nothing else"; git "only" to
   resolve and diff report commits), while `tdd-auditor.md` now reads the
   hosting file's history to account for list-revision commits — check 2 would
   flag each one as unaccounted. SKILL.md §1 option 2 also gives no order
   between `design.md` and `outline.md` for the auditor's own derivation.
   Change: inputs include the hosting file, named in the prompt; git also reads
   its list-revision commits.
   - **Status**: FIXED (the `tdd-auditor.md` fallback derivation is
     review-agent's file)

## Minor

1. **finishing.md §1 landed check and §3.1: no `--no-show-signature`.**
   `changed-files.sh` passes it on both its `git log` calls so a user's
   `log.showSignature` cannot print ahead of the hash. Add it to the three.
   - **Status**: FIXED
2. **escalation-acceptance.md §Verification sequence step 3: only a first
   `DIRTY:` has a branch.** First-run `CLEAN:` is implied; `PRECOMMIT:` and
   exit 2 have none. Change: prefix the step with the first-run branches.
   - **Status**: FIXED
3. **review-dispatch-template.md §Template return placeholder vs §Example.**
   The placeholder points at `dispatch-composition.md` item 5, which lacks the
   subcategory code and three-gate summary m18 put into §Example. Change:
   extend the placeholder to "plus the UNFIXABLE marking as §Example words it".
   - **Status**: FIXED
4. **escalation.md §Resuming step 2 assumes an item remains.** `finishing.md`
   §1 now names a run killed inside finishing as a resume case, where no item
   remains. Change: with no item remaining, dirt is judged against
   `finishing.md`'s first unlanded stage, and precommit first runs at that
   stage's verification.
   - **Status**: FIXED
5. **escalation.md §Resuming step 2, "as §2 says"** reads as step 2 itself
   inside this file. Change: "as `/build` §2 says".
   - **Status**: FIXED
6. **SKILL.md §4.4 vs tdd-slice.md step 2.** §4.4 runs once a commit lands;
   tdd-slice.md also runs it when a refactor returns `error`, where none does.
   Change "its refactor" to "its refactor, `error` included" only if the hub
   stays at most 199 lines after `just format`; otherwise leave tdd-slice.md
   as the governing text.
   - **Status**: NOT APPLIED — the hub is at 199 lines and the phrase lands on
     an already-full line, so it would reflow past the cap. Per the reviewer's
     own condition, `tdd-slice.md` step 2 stays the governing text.
7. **escalation.md §Post-item remediation step 2 and dispatch-composition.md
   §Naming: the fresh remediation dispatch has no name.** Reusing the step's
   name would overwrite its committed report. Suggested `<step name>-fix`.
   The reviewer notes the gap predates this job for general items.
   - **Status**: DEFERRED — a new naming convention outside the outline's
     items; recorded for my human partner.
8. **escalation.md §Resuming step 1: a list revision is not inventoried.**
   After a kill following the code-review commit, nothing shows a revision was
   still owed. The reviewer notes the gap predates this job.
   - **Status**: DEFERRED — a change to the resume inventory outside the
     outline's items; recorded for my human partner.

## On the code review's Major 1 (reviewer's view, not a fix)

- (a) a KD-4-style landed check on §2 over
  `plans/reports/triage-feedback-log.md`. Limit: the log is shared between
  jobs, so another job's Finish on the same branch after `<L>` would wrongly
  skip §2 — the interleaving D-90's Limitation already admits. A
  no-classification run commits no log change, so §2 re-runs harmlessly.
- (b) with (a) in place, excluding `tdd-audit.md` only matters for re-runs; a
  D-90 consistency fix, not a requirement.
- (c) reintroduces a copy of D-90's filters, which KD-1 rejects.

## Scope completeness (reviewer)

Items 2.1–2.4 and 2.6–2.10 done; Majors 1–3 are cross-file mismatches, not
missing edits. (Item 2.5 is review-agent's.)

## Fixes Applied

- `plugin/skills/build/references/finishing.md` — §1 landed-check commands and
  §3.1's query take `--no-show-signature` (Minor 1); §2 surfaces the
  `unrecognised classification:` line (Major 1); §3.1 skips an empty list
  (Major 2); §3.2's inputs include the hosting file, named in the prompt, and
  its list-revision commits (Major 3).
- `plugin/skills/build/references/dispatch-composition.md` — item 2's
  `tdd-audit` exception adds the hosting file and its history (Major 3); the
  `final-review` bullet says "skipped over a non-empty list" (Major 2).
- `plugin/fragments/escalation-acceptance.md` — step 3's first-run branches
  (Minor 2).
- `plugin/skills/build/references/review-dispatch-template.md` — §Template's
  return placeholder (Minor 3).
- `plugin/skills/build/references/escalation.md` — §Resuming step 2's
  "`/build` §2" (Minor 5) and the no-item-remaining bound (Minor 4).

## Second pass

`review-skill` resumed once by `SendMessage`, naming the fixes applied. It
confirmed Majors 1–3 and Minors 1, 2, 3 and 5 fixed correctly, and raised
three issues in the fixes, none UNFIXABLE:

1. **escalation.md §Resuming step 2, the new sentence: "that stage's
   verification" does not exist when the first unlanded stage is
   `finishing.md` §2**, which runs no verify-step. Change: precommit first
   runs at the next verify-step `finishing.md` runs — after §1's report
   commit, or after §3.3's closing commit.
   - **Status**: FIXED
2. **`plugin/agents/tdd-auditor.md` §Inputs still says "The dispatch does not
   name it"** (the hosting file), contradicting the fixed `finishing.md` §3.2
   and `dispatch-composition.md` item 2.
   - **Status**: OUT-OF-SCOPE for this group — routed to `review-agent`.
3. **Nit: finishing.md §3.1's inline query runs to ~100 columns** after
   `--no-show-signature`; suggested a fenced block, "leave it if `just format`
   and the line checker already accept it".
   - **Status**: NOT APPLIED — `just format` and the line checker accept it.

The second pass's fix goes unreviewed by design (`finishing.md` §1).
