# Verification of `plans/skill-reviews/formalize.md` — 2026-09-21

Checked against the working tree: `plugin/skills/formalize/SKILL.md` (95 lines,
unmodified today), `src/edify/check.py`, `src/edify/check_cli.py`,
`docs/superpowers/design/invariant-guided-verify-loop.md`,
`docs/references/cli-and-package.md`.

Review tally: 3 critical, 5 major, 5 minor = 13 findings. My table carries 13.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| 1 | Critical | open-design | The wrong premise survives verbatim at SKILL.md:76-78: "`error` — surface it. A common cause is a target with no contract (CrossHair analyzed nothing); add a contract." `check.py:91-92` returns `VERIFIED` for CrossHair exit 0, and `check_cli.py:82` maps VERIFIED → exit 0, so a contract-free target still reports verified. The living design still carries the same premise: `docs/superpowers/design/invariant-guided-verify-loop.md:85` L1 "Deferred to `formalize` discipline (add a contract on `error`)". **But the reviewer's remedy is wrong:** `check_cli.py:85-87` computes `vacuity_warning = result.status is VERIFIED and per_condition_timeout is None` — it flags *any* default-budget verified run, contract-bearing or not, so it is not a no-contract signal. The fork: give the CLI a real contract-presence check (reopening L1's deferral), or have the skill detect decorator absence itself before step 3. |
| 2 | Critical | open-design | SKILL.md:59 still prints the bare `edify check <file-or-dotted-target> --json`. D-12 (`docs/references/cli-and-package.md:98-109`) still prescribes content substitution and still records an **open gate**: "one throwaway skill echoing the placeholder confirms `DATA` (not just `ROOT`) substitutes." A grep for `CLAUDE_PLUGIN_DATA` across `plugin/` returns only `bin/bootstrap-venv.sh`. Changing the invocation depends on that unresolved probe, so it is not mechanical. |
| 3 | Critical | fixed | Step 1 now forbids it explicitly (SKILL.md:46-49): "Never reach for `AskUserQuestion`. A picker hides the exchange from the transcript…" and `allowed-tools` (:10-14) is `Read, Edit, Write, Bash` — no `AskUserQuestion`. Same fix landed in `requirements/SKILL.md:185` and `review/SKILL.md:44`; `proof/SKILL.md:8` no longer declares it either. The cross-cutting decision in the README is settled by rewrite, not exception. |
| 4 | Major | open-mechanical | A grep of SKILL.md for `budget`, `vacuity`, `--timeout` returns nothing but the honest-guarantee wording at :65-67 ("no counterexample within CrossHair's search budget"). The verified branch still just "Report and stop". `check_cli.py` emits both `budget` and `vacuity_warning` in `--json`, and `--timeout` is a real option (`cli.py:126-132`). |
| 5 | Major | open-mechanical | SKILL.md:56-62 documents the three statuses and no exit codes. `check_cli.py:15-19` maps VERIFIED→0, REFUTED→1, ERROR→2, and the docstring at :82 states it. The agent's Bash tool reports 1 and 2 as command failures on a normal loop outcome. |
| 6 | Major | open-mechanical | SKILL.md:93-95 still links `docs/superpowers/specs/2026-06-08-invariant-guided-verify-loop-design.md`. Both files exist; `docs/superpowers/design/invariant-guided-verify-loop.md` is the living one. |
| 7 | Major | open-mechanical | SKILL.md:79-80 still "Do at most a small fixed number of repair iterations (e.g. 5)" — no binding limit, and the number is unlabelled. |
| 8 | Major | open-design | `plugin/skills/formalize/` still holds only `SKILL.md`; every other skill except `recall` has a `references/`. At 95 lines the body has room, so whether findings 4-5 land inline or in a new reference node is a structural call, and it is the same call as whether the budget discipline is added at all (finding 4). |
| 9 | Minor | open-mechanical | SKILL.md:51-54 gives `@require(...)` / `@ensure(...)` with no `from icontract import ...`. Working usage imports at `src/edify/check.py:7`. |
| 10 | Minor | open-mechanical | SKILL.md:21-24 still "You own *intent*… That judgment is yours"; :62 still "The result status is one of". |
| 11 | Minor | disputed | The description (:7-8) still ends "or after writing a function whose correctness matters". The shared convention reserves self-triggering for mechanical, detectable conditions — but "a function whose correctness matters" is the skill's actual purpose statement, and the three literal phrases carry the trigger surface regardless. No evidence was offered that the clause causes spurious firing; treat removal as a wording preference, not a defect. |
| 12 | Minor | fixed-in-part → open-mechanical | `Write` is still declared at SKILL.md:13 and the procedure still names only Read, Edit and Bash operations. |
| 13 | Minor | open-mechanical | SKILL.md:91-95 is still `## Backend` followed by prose and a bare "See <link>", with no statement of when to read it. |

Note on 12: recorded as `open-mechanical`; the "fixed-in-part" label in the
status column is an artefact of `AskUserQuestion` leaving the `allowed-tools`
list, which did not touch `Write`.

## Cross-file links

- Finding 3 is the same defect as requirements C2, review C1 and proof M7 — all
  four are now fixed by the same rewrite pattern (inline numbered prose plus an
  explicit prohibition).
- Finding 1's living-design half (L1) is the same class as
  deliverable-review C3: a skill and the design node it cites disagreeing, with
  the design node the more authoritative side.

## Exact edits for `open-mechanical`

`plugin/skills/formalize/SKILL.md` is not on the line-limit allowlist (95 lines,
cap 200), so these may add lines.

### Finding 4 + 5 — step 3, :56-62

- old:
  ```
  3. **Check.** Run:

     ```
     edify check <file-or-dotted-target> --json
     ```

     The result status is one of `verified`, `refuted`, or `error`.
  ```
- new:
  ```
  3. **Check.** Run:

     ```
     edify check <file-or-dotted-target> --json
     ```

     Status is `verified`, `refuted` or `error`, and the exit code encodes it —
     0, 1, 2 respectively. A nonzero exit here is a result, not a command
     failure: this is the case the project's error-handling rule carves out, so
     read the JSON rather than suppressing the exit.

     `--json` also returns `budget` (the per-condition timeout used, `null` at
     the default) and `vacuity_warning` (true for any `verified` reached at the
     default budget). Re-run a `verified` result with an explicit
     `--timeout <seconds>` before reporting it, and state the budget the verdict
     was reached at.
  ```
  (Finding 4's verified-branch change also touches :65-67 — add "State the
  per-condition budget the verdict was reached at" to that bullet. Whether the
  re-run is *required* rather than recommended is the open-design half in
  finding 8.)

### Finding 6 — :93-95

- old: `oracle; this skill is the intent-holder. See`
  `` `docs/superpowers/specs/2026-06-08-invariant-guided-verify-loop-design.md`. ``
- new: `oracle; this skill is the intent-holder. Read`
  `` `docs/superpowers/design/invariant-guided-verify-loop.md` `` for the
  `four-state output contract, the seed-function rule and CrossHair's verbose`
  `reporting — it is the living document and supersedes the 2026-06-08 frozen`
  `spec where they diverge.`
  (This also closes finding 13, which asks for a statement of what the link
  holds.)

### Finding 7 — :79-80

- old: `5. **Loop with a cap.** Do at most a small fixed number of repair iterations`
  `   (e.g. 5). If you hit the cap, STOP and report the honest state: the last`
- new: `5. **Loop with a cap.** At most 5 repair iterations — an arbitrary number,`
  `   not calibrated. At the cap, STOP and report the honest state: the last`

### Finding 9 — :51-54

- insert the import above the decorator forms:
  `   `from icontract import require, ensure`, then`
  `   `@require(lambda <args>: <precondition>)` and`

### Finding 10 — :20-24 and :62

- :21-24 old: `verifier (`edify check`, backed by CrossHair) owns deduction. You own *intent*:`
  `what the function should guarantee. Verification proves code meets a contract;`
  `it does NOT prove the contract is the right one. That judgment is yours, and`
  `when intent is genuinely ambiguous you ASK rather than guess.`
- new: `verifier (`edify check`, backed by CrossHair) owns deduction; the skill owns`
  `*intent* — what the function should guarantee. Verification proves code meets a`
  `contract; it does NOT prove the contract is the right one. That judgment stays`
  `here, and genuinely ambiguous intent gets asked about rather than guessed.`
- :62 is replaced wholesale by the finding-4/5 edit above.

### Finding 12 — :13

- delete the `  - Write` line from `allowed-tools`.
