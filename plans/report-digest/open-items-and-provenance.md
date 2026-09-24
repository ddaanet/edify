# Open items digest — open-items-sweep and provenance deliverable review

**Date:** 2026-09-23
**Inputs:** every file in `plans/open-items-sweep/reports/` (eight reports,
two patches) and
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md`
(cited as DR). Frame: `.claude/handoff-todo.md` §Remaining, bullets numbered
R1–R13 in order (R1 read-the-reports, R2 repo-relative `plugin/…` job, R3
claude-plugins README, R4 skill-reviews findings, R5 sweep exit condition, R6
pilfer defect 21, R7 brief-triage jobs, R8 `just test` on macOS, R9 FR-12
remainder, R10 pilfer-superpowers, R11 README dprint, R12 untracked
`.claude/` paths, R13 MEMORY.md budget).

Status checked against the tree at `0b4c46f8`.

**Patches.** Both are applied:
`git apply --reverse --check` exits 0 for
`edify-review-range.patch` (landed in `20ed4fb5`) and
`run-project-checks.patch` (landed in `10b509e2`).

## STILL-OPEN, in frame

### provenance-enforcement-and-routing

- **F-5 remainder: repo-relative `plugin/…` paths in shipped bodies.** Paths
  that do not resolve from an installed plugin, including
  `plugin/agents/tdd-auditor.md:209` (agent definition, no skill-relative
  form). Sources: DR F-5, DR "Needs my human partner's call" 1. Evidence:
  `tdd-auditor.md:209` still cites `plugin/skills/build/references/finishing.md`;
  a backticked `plugin/{skills,agents,fragments,bin,hooks}/` grep over
  `plugin/skills plugin/agents plugin/fragments` returns 27 sites in 14 files,
  matching R2's count. Frame: **R2**. (The three skill-body sites F-5 added
  are resolved — see below.)
- **Sweep exit condition misses the defect form outside the edited files.**
  F-4 was a later commit reintroducing M-6 past Item 1.9's zero-hit sweep; the
  batch review's Major 1 was an inbound reference to a deleted page, naming it
  by description, that the filename grep missed. Sources: DR F-4 and §Gap
  Analysis "§Scope OUT — sweep mechanism", `batches-review.md` Major 1
  ("a deletion needs a referred-to-by-description sweep"). Evidence: R5 names
  both reproductions and records the job as "not yet started". Frame: **R5**.
- **Corrector family over cap, ceilings pinned, KD-1 table duplicated.**
  `corrector.md` 682, `design-corrector.md` 460, `outline-corrector.md` 450,
  each allowlisted at exactly its count, so any growth reds the gate; KD-1's
  17-line repair table sits in both design and outline correctors. Sources:
  DR Minor "Duplication" (KD-1), DR "Needs my human partner's call" 4, DR §Gap
  Analysis "§Scope OUT — corrector dedup, allowlisted-file splits",
  `preflight.md` I2. Evidence: `wc -l` gives 682/460/450;
  `scripts/check_line_limits.allow` lists the same three ceilings against
  "pilfer defect 21". Frame: **R6**.
- **F-1 BSD `wc` padding: verification on macOS.** The code fix landed
  (`scripts/check_line_limits.sh:143` pipes `wc -l` through `tr -d ' '`, added
  in `5f860e07`) with a shim test; the padding claim itself is still unexecuted
  on macOS. Sources: DR F-1 "Verification status", DR "Needs my human
  partner's call" 3. Evidence: comments `scripts/check_line_limits.sh:134`
  ("unverified on macOS") and `tests/line_limits_helpers.py:144`. Frame:
  **R8**.

### open-items-sweep

- **README pairs `edify markdown` with dprint and calls `docs/design.md` the
  design record.** Source: `preflight.md` W2. Evidence: `README.md:30` and
  `:68` still name dprint, `:60-61` still reads "Design is recorded in
  `docs/design.md`", and `.dprint.json` still exists. Frame: **R11**.
- **Five untracked `.claude/` sandbox device paths not ignored.**
  `launch.json`, `loop.md`, `output-styles`, `routines`, `workflows` break a
  bulk `git add`. Sources: `preflight.md` W1; also reported in
  `red-scripts-review.md` §Working tree and `green-scripts.md` §Working tree.
  Evidence: `git status --porcelain` lists all five as `??`;
  `git check-ignore -v` on them exits 1. Frame: **R12**.

## STILL-OPEN, missing from frame

### provenance-enforcement-and-routing

- **F-6 — the review range `..HEAD` is unbounded after the work.** Commits
  landing after a job's last commit fall inside its review range; D-80 does
  not address them. DR lists three options (leave it, optional end ref,
  `/build` records the terminal commit) and calls it a D-80 contract question.
  Sources: DR F-6, DR "Needs my human partner's call" 2. Evidence:
  `plugin/bin/edify-review-range.sh:131` and `:176` still print
  `RANGE: %s..HEAD`; the D-80 conclusion (`docs/decisions.md:77-78`) is
  unchanged. The frame's "F-6" mentions (R7) are brief-triage IDs, a different
  namespace (`plans/remaining-sweep/reports/brief-triage.md:74`: resume the
  reviewer after an escalation).
- **Three causes share a bare `NO-PROVENANCE:`.** No heading; heading without
  `Base:`/`Derived from:`; a `Derived from:` that is neither `none` nor a
  `superseding` artifact. DR records it as a note on KD-2's table as designed,
  not a deviation. Source: DR Minor "Robustness, `edify-review-range.sh`"
  (fourth bullet). Evidence: `edify-review-range.sh:94`, `:102`, `:185` each
  `echo "NO-PROVENANCE:"` with no subject.

### open-items-sweep

- **`UNRESOLVED: <sha>` does not say which artifact's base failed.** Since the
  patch, the same line covers this artifact's own `Base:` and a prior's.
  RED review: "worth a KD-2 note if the verdict line is ever revisited";
  GREEN review: header table documents it, "left as designed". Sources:
  `red-scripts-review.md` Minor 1 (residual), `green-scripts-review.md` §No
  proposed hunks. Evidence: `edify-review-range.sh:121` and `:168` both print
  `UNRESOLVED: <sha>`; header `:27` carries the clause.
- **`\r` in awk's bracket expression unverified on non-Linux awk.** Probed on
  mawk 1.3.4 only; no shim test locks the CRLF fix against a stricter awk.
  Source: `green-scripts-review.md` §No proposed hunks, fourth item. Evidence:
  no test under `tests/` substitutes or shims `awk`. R8's macOS `just test`
  run would exercise `test_crlf_artifact_emits_range`, but R8 names only the
  two `wc` comments.
- **`none,` with a comma-attached rationale yields `NO-PROVENANCE:`.** Bare
  or backticked; pre-existing, "not this patch's business"; the tree's idiom
  `none — <rationale>` works. Source: `green-scripts-review.md` §No proposed
  hunks, third item. Evidence: `edify-review-range.sh:129` takes
  `${derived_from%% *}`, so the comma stays on the first word.
- **`second_root` with `omit_root=True` becomes the first positional.**
  A test combining them would exercise the wrong root and pass for the wrong
  reason; no caller does today. Scoped out by the RED review, left by the
  GREEN review. Sources: `red-scripts-review.md` §Checked and clean ("one
  latent trap"), `green-scripts-review.md` §One latent trap. Evidence:
  `tests/line_limits_helpers.py:97-100` appends `second_root` regardless of
  `omit_root`.
- **KD-7 does not state "exit 2 outranks exit 1", yet two sites attribute it
  to KD-7.** Source: `batches-review.md` #6 (left as is). Evidence: the KD-7
  paragraph (`plans/provenance-enforcement-and-routing/outline.md:173-184`)
  has no exit-precedence clause; `tests/test_line_limits_exit_codes.py:3` and
  `outline.md:349-350` both attribute it to KD-7.
- **Two pre-existing over-80-column lines rumdl cannot reflow in the
  correctors.** Reported, not addressed. Source: `prose-batch.md` Item 1.
  Evidence: `outline-corrector.md:61` is 118 columns and
  `design-corrector.md:105` is 104 columns (awk length check). The gate's
  `rumdl fmt --check` does not flag them.

## RESOLVED-SINCE

### provenance-enforcement-and-routing

- **F-2 — line-limits tests read the production allowlist.** Evidence:
  `tests/line_limits_helpers.py:90-94` writes an empty allowlist when none is
  given, with `allowlist="default"` as the explicit opt-in (`:57-61`);
  `git log -S'_empty_allowlist_for_test'` → `5f860e07` "deliverable review
  fixes…". Source: DR F-2.
- **F-3 — KD-7's Python branch untested.** Evidence:
  `tests/test_line_limits.py:335`, `:348`, `:368` write 401-line `.py`
  fixtures under `src/` and `tests/`, one with an allowlist entry; added in
  `5f860e07`. Source: DR F-3, DR §Gap Analysis "KD-7 — Python loop".
- **F-4 — two "per `references/research-protocol.md`" pointers.** Evidence:
  `write-outline.md:149` and `write-design.md:7` now read "Read
  `references/research-protocol.md` §A.5"; Item 1.9's `rg` pattern over
  `plugin/ docs/` returns zero hits; changed in `5f860e07`. Sources: DR F-4,
  DR "Needs my human partner's call" 1, DR §Gap Analysis M-6. (The mechanism
  behind it is R5, above.)
- **F-5 — three skill-body `plugin/fragments/delegation.md` sites.**
  Evidence: none of `recall/SKILL.md`, `ground/SKILL.md`,
  `deliverable-review/SKILL.md` contains the path; `git log -S` shows it
  removed in `5f860e07`. Source: DR F-5. (Remainder is R2, above.)
- **Review-range robustness minors: CRLF artifact, uppercase or phantom prior
  `Base:`, backticked `none`.** Evidence: `edify-review-range.patch` reverse-
  applies cleanly; `20ed4fb5` "edify-review-range.sh and check_line_limits.sh
  minors from the deliverable review"; `edify-review-range.sh:130` strips
  backticks, `:168` prints `UNRESOLVED: $prior_base`. Sources: DR Minor
  "Robustness, `edify-review-range.sh`" bullets 1–3; `red-scripts.md` tests
  1–4; `red-scripts-review.md` Major 1–2; `green-scripts.md` §The patch and
  §Blocker; `green-scripts-review.md` "What is left" 1.
- **Second positional `ROOT` silently discards the first.** Evidence:
  `20ed4fb5` touches `scripts/check_line_limits.sh` (+15) and
  `tests/test_line_limits_exit_codes.py`. Sources: DR Minor "Robustness,
  `check_line_limits.sh`" bullet 1; `red-scripts.md` test 5;
  `green-scripts.md` §test 5.
- **`wc -l` no-trailing-newline residual needs a comment.** Evidence:
  `scripts/check_line_limits.sh:138` "Residual, unguarded…" (`git log -S` →
  `20ed4fb5`), carrying the corrected reasoning (`ruff format` terminates
  Python; rumdl does not terminate markdown). Sources: DR Minor "Robustness,
  `check_line_limits.sh`" bullet 2; `green-scripts-review.md` Major 1.
- **Correctors enforce `Derived from:` without naming `superseding`.**
  Evidence: `superseding` now appears in both `outline-corrector.md` and
  `design-corrector.md`; `10b509e2` "Correctors name the superseding token at
  pinned line counts". Sources: DR Minor "Contract alignment" bullet 1;
  `prose-batch.md` Item 1.
- **Planning-artifact drift (M-4 destination, Item 1.1 attribution, Item
  1.1's M-3).** Evidence: `classification.md:38` reads `plugin/bin/`, `:64`
  reads "outline Item 1.1"; `outline.md:211-213` lists M-1, M-2 and assigns
  M-3 to Items 1.3 and 1.5–1.7; `10b509e2`. Sources: DR Minor "Contract
  alignment" bullets 2–3; `prose-batch.md` Item 2.
- **Minor 10 — outline names the deleted `tests/test_review_range.py`; the
  five modules do not say why they exist.** Evidence: `outline.md:104-105`
  and `:216-217` carry the "since split into five" clause (`10b509e2`); each
  module docstring now reads "One of five modules split from…"
  (`tests/test_review_range_range.py:3-4`, `20ed4fb5`). Sources: DR Minor
  "Test-suite bookkeeping" bullet 1; `prose-batch.md` Item 2;
  `batches-review.md` #7 (half-closed at the time); `green-scripts.md`
  §Test-file bookkeeping.
- **Minor 11 — six tests missing from the final list revision; two files
  missing from Item 1.10's list.** Evidence: `outline.md:331` and `:348-350`
  enumerate them (`10b509e2`). The prose batch flagged its own rewording of
  that paragraph for the orchestrator; it was committed as written. Sources:
  DR Minor "Test-suite bookkeeping" bullet 2; `prose-batch.md` Item 2.
- **Root `justfile` duplicates portable `precommit` and its rumdl comment.**
  Evidence: `run-project-checks.patch` reverse-applies cleanly;
  `plugin/portable.just:90` defines the no-op hook and `:126` calls it;
  `justfile:205` overrides it to `run-design-links`; `justfile` defines no
  `precommit` recipe; `10b509e2`. Sources: DR Minor "Duplication" bullet 1;
  `code-batch.md` Item 1 (blocked at the time); `run-project-checks.patch`.

### open-items-sweep

- **`agents/learnings.md:5` promised three destinations with one command
  behind them, and pointed at the hub.** Evidence: `agents/learnings.md:5`
  now routes decisions through `craft:design-doc-writing` into the
  `docs/references/` node, its `docs/decisions.md` line and the hub "where a
  conclusion changes"; `git log -S'craft:design-doc-writing'` → `0b4c46f8`.
  Source: `batches-review.md` #4.
- **Uncommitted batch work awaiting a commit decision.** Covers the eight
  unstaged test/script files, the staged page deletion, and the prose batch's
  edit to the orchestrator's `.claude/handoff-todo.md` (including the stale
  todo line still listing the `superseding` and drift minors). Evidence:
  `20ed4fb5` and `10b509e2` carry the work; `git status --porcelain` shows
  only the five R12 paths; the current §Remaining lists neither minor.
  Sources: `green-scripts-review.md` "What is left" 2; `prose-batch.md` Item 6;
  `batches-review.md` §For the orchestrator.
- **Preflight B1 — tracked `.claude/handoff-todo.md` diff blocked the
  release.** Evidence: `e7e106f6` "Release 0.3.0"; tag `v0.3.0` exists.
  Source: `preflight.md` B1.
- **Preflight I3 — patch versus minor bump.** Evidence:
  `plugin/.claude-plugin/plugin.json` is 0.3.0, tag `v0.3.0`. Source:
  `preflight.md` I3.
- **Preflight W3 — the release cannot run from a sandboxed call.** Moot for
  the release it warned about: `v0.3.0` landed (`e7e106f6`), and the
  marketplace entry reads version 0.3.0. Source: `preflight.md` W3.

## UNCLEAR

None.

## Frame observation

R3's second sentence says the marketplace `description` "clears itself at
the next `just release`". That release has run: the `edify` entry in
`/Users/david/code/claude-plugins/.claude-plugin/marketplace.json` now carries
version 0.3.0 and a description identical to
`plugin/.claude-plugin/plugin.json`'s. The reports themselves recorded this as
done (`code-batch.md` Item 2 applied the sync; `preflight.md` I4 said no action
needed), so it is not counted above.

## Counts

| Classification | Entries |
|---|---|
| STILL-OPEN, in frame | 6 |
| STILL-OPEN, missing from frame | 8 |
| RESOLVED-SINCE | 17 |
| UNCLEAR | 0 |
