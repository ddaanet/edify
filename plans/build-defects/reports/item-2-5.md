# Item 2.5 — `plugin/skills/build/references/dispatch-composition.md`, `plugin/agents/test-driver.md`, `plugin/agents/refactor.md`

Status: **blocked, Edit refused, twice across two legs.** In leg 2 the first
three Edits on `dispatch-composition.md` each came back with "The server-side
auto mode classifier gave no verdict (it skipped this action)". This session
had switched back to auto mode after Item 2.4 committed.

Leg 3 re-checked all five old strings below against the current files: each
still matches verbatim (`dispatch-composition.md` lines 91–92, 46–49 and
34–38; `test-driver.md` 101–102; `refactor.md` 177–183). Its first Edit, the
§Naming one below on `plugin/skills/build/references/dispatch-composition.md`,
got the same "gave no verdict" under auto mode, so leg 3 stopped.

Nothing was applied: all three targets are unchanged and nothing is committed
for this item. No retry and no sed, Bash or Write fallback was attempted, and
the agent definitions were not tried.

Requirements: inline M1, m15; orch m5.

The exact edits prepared, old → new, one per bullet:

## §Naming — `review-<group>` (inline M1, KD-2)

- old:

  ```
  re-dispatch reuses the name), `phase-P-corrector` for checkpoints,
  `final-review` for
  ```

- new:

  ```
  re-dispatch reuses the name), `phase-P-corrector` for checkpoints,
  `review-<group>` for a review-gate dispatch, `<group>` being the artifact group
  `finishing.md` §1 routed, `final-review` for
  ```

## §Prompt contents item 5 — second exception, UNFIXABLE in the report (inline m15, KD-2)

- old:

  ```
     path. Return contract: the report path on success, or `blocked: <reason>` —
     except `edify:refactor`, whose own protocol returns `success` /
     `escalated: <reason>` / `error: <reason>` and still writes its report at the
     assigned path.
  ```

- new:

  ```
     path. Return contract: the report path on success, or `blocked: <reason>`.
     UNFIXABLE is never a return: a reviewer marks an issue it cannot fix
     `UNFIXABLE` inside its report. Two exceptions to the contract:
     `edify:refactor`, whose own protocol returns `success` /
     `escalated: <reason>` / `error: <reason>` and still writes its report at the
     assigned path; and a report-only reviewer (`plugin-dev:skill-reviewer`),
     which returns its findings as text in parts and writes nothing — the
     dispatching session writes them to the assigned path
     (`review-dispatch-template.md` §Report-only variant).
  ```

  Pointer checked: `review-dispatch-template.md` §Report-only variant holds the
  parts-and-end-marker return and says the calling session writes the report.

## §Prompt contents item 4 — pathspec commit (orch m5, KD-7)

- old:

  ```
     match. A committing dispatch stages the paths it names — its own report among
     them — and never `git add -A`. Overrides: a RED dispatch commits nothing and
     stops after the red run; a review dispatch commits nothing either — the
     orchestrator commits the corrector's report, with the fixes it applied where
     there are any.
  ```

- new:

  ```
     match. A committing dispatch stages the paths it names — its own report among
     them — and never `git add -A`, then commits with `git commit -- <paths>`,
     naming the paths it staged. Overrides: a RED dispatch commits nothing and
     stops after the red run; a review dispatch commits nothing either — the
     orchestrator commits the corrector's report, with the fixes it applied where
     there are any, in the same form.
  ```

## `plugin/agents/test-driver.md` GREEN step 6 (KD-7)

- old:

  ```
     theirs uncommitted for this commit to carry. Never `git add -A` or
     `git add .`, which sweep in whatever else the tree holds. The commit leaves
  ```

- new:

  ```
     theirs uncommitted for this commit to carry. Never `git add -A` or
     `git add .`, which sweep in whatever else the tree holds. Commit with
     `git commit -m "<subject>" -- <the same paths>`, so nothing staged before
     this dispatch rides along. The commit leaves
  ```

## `plugin/agents/refactor.md` Step 6 (KD-7)

- old:

  ````
  assigns), then stage the files you changed together with it and commit the
  refactoring as its own commit:

  ```bash
  git add <the files you changed> plans/<job>/reports/item-N-M-s<k>-refactor.md
  git commit -m "refactor: Item N.M/k — <what changed>"
  ```
  ````

- new:

  ````
  assigns), then stage the files you changed together with it and commit the
  refactoring as its own commit, naming the same paths:

  ```bash
  git add <the files you changed> plans/<job>/reports/item-N-M-s<k>-refactor.md
  git commit -m "refactor: Item N.M/k — <what changed>" \
      -- <the files you changed> plans/<job>/reports/item-N-M-s<k>-refactor.md
  ```
  ````

## Noted, not edited

- `plugin/skills/build/references/tdd-slice.md` is OUT: its orchestrator
  commits (§(d) "Commit the code review", and the RED/test-review hand-off to
  the GREEN commit) do not name the `git commit -- <paths>` form. Once item 4
  above lands, `dispatch-composition.md` states it for every committing
  dispatch and for the orchestrator's review commit, but `tdd-slice.md`'s own
  wording still lacks it.
- `plugin/agents/artisan.md` has no `git add` / `git commit` text (checked by
  `rg`), so it takes the form from the dispatch prompt's item 4 alone.
