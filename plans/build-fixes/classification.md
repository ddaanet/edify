# Classification — build-fixes

Job-level line first: `triage-feedback.sh` reads the first `Classification:`
it finds.

- **Classification:** Moderate

Implicit bundling: Majors 1–6 and 21 of the 25 minors of
`plans/build-defects/reports/deliverable-review.md`. Explicit bundling: the
queued tdd job (a)(b)(c) from `.claude/handoff-todo.md`, merged here because it
touches the same files and (b)'s per-job baseline is what Major 1's resume test
keys on. Classified per cluster.

## Resume and baseline — Majors 1, 2; (b); minors m1, m3, m16

- Classification: Moderate
- Implementation certainty: High — the per-job file is accepted, and my human
  partner ruled the phase boundary is the commit adding
  `phase-<P>-corrector.md`
- Requirement stability: High
- Behavioral code check: No — prose instructions only
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: recall entry `line-caps` — `build/SKILL.md` is at its 200-line cap,
  so the resume test needs room that §6's duplicate paragraph gives back

## Revert mode — Major 5; (a); minors m5, m6, m13 and the recovery-copy minor

- Classification: Moderate
- Implementation certainty: High — `git restore --source=HEAD --staged
  --worktree` reverts added, modified, deleted and renamed paths alike (probed
  on git 2.47.3)
- Requirement stability: High
- Behavioral code check: Yes — a new mode in `verify-step.sh`
- Work type: Production
- Artifact destination: production (script) and agentic-prose (call sites)
- Evidence: recall entry `sandbox-effects` — sandbox masks can appear as `??`
  between a listing and its revert, so the revert must be bound to the
  confirmed listing; `macos-gate-target` — a shell edit

## Exemption tests — Major 6; minors F-3, F-4

- Classification: Moderate
- Implementation certainty: High — the shipped script already behaves; the
  tests pin it, red by mutation
- Requirement stability: High
- Behavioral code check: No — tests only
- Work type: Production
- Artifact destination: production (`tests/`)
- Evidence: the review's own mutants (`[ M?]` XY, `.+` for `[^/]+`) survive
  the current module

## Commit discipline — Majors 3, 4; minors m14, m18

- Classification: Moderate
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: Yes — `triage-feedback.sh`'s diff form (m18)
- Work type: Production
- Artifact destination: agentic-prose and production (`plugin/bin/`)
- Evidence: KD-7's safety argument needs every commit path in
  `git commit -- <paths>` form

## Dispatch contracts — (c); minors m2, m4, m7, m8, m10, m11, m15, m19

- Classification: Simple
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: recall entry `audit-a-contract-across-its-surfaces` — naming rule
  in `dispatch-composition.md`, grouping in `finishing.md`, rows in
  `review-requirement.md`

## Stale claims — minor m17

- Classification: Simple
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose (`plugin/README.md`) and investigation
  (`docs/references/pipeline-contracts.md`)
- Evidence: the revert mode adds a `verify-step.sh` behaviour the README
  must name anyway

## Not in this job

Major 7 (a later session, per the task frame); minors m12, F-2, F-5 and F-6 —
routed in the outline's Scope OUT.
