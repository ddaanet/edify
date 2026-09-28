# Classification — build-fixes

Job-level line first: `triage-feedback.sh` reads the first `Classification:`
it finds.

- **Classification:** Moderate

Implicit bundling: Majors 1–6, §4.1's share of Major 7, and 21 of the 25 minors
of `plans/build-defects/reports/deliverable-review.md`. Explicit bundling: the
queued tdd job (a)(b)(c) from `.claude/handoff-todo.md`, merged here because it
touches the same files and Major 1's resume test replaces (b)'s baseline file.
Classified per cluster.

## Resume and base — Majors 1, 2, 7 (§4.1); minors m1, m3, m16

- Classification: Moderate
- Implementation certainty: High — resume and base read committed item-report
  history (KD-1), and my human partner ruled the phase boundary is keyed on
  `phase-<P>-corrector.md`
- Requirement stability: High
- Behavioral code check: Yes — `changed-files.sh` derives the base
- Work type: Production
- Artifact destination: production (script) and agentic-prose (call sites)
- Evidence: recall entry `line-caps` — `build/SKILL.md` is at its 200-line cap,
  so the resume test needs room that §6's duplicate paragraph gives back

## Dirt handling — Major 5; (a); minors m5, m6, m13 and the recovery-copy minor

- Classification: Moderate
- Implementation certainty: High — dirt is finished or adopted by default, and
  a revert on my human partner's per-path decision is one
  `git restore --source=HEAD --staged --worktree … && rm -- …` call (probed on
  git 2.47.3)
- Requirement stability: High
- Behavioral code check: No — prose instructions only
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: recall entry `sandbox-effects` — sandbox masks show as `??`, which
  the existing annotated re-run already filters before any escalation

## Exemption tests and changed files — Major 6; minors F-3, F-4, m1, m2, m18

- Classification: Moderate
- Implementation certainty: High — the shipped script already behaves; its
  tests pin it, red by mutation, before the exempt alternation moves to a
  sourced file shared with `changed-files.sh`
- Requirement stability: High
- Behavioral code check: Yes — `changed-files.sh` and the extraction
- Work type: Production
- Artifact destination: production (`plugin/skills/build/scripts/`, `tests/`)
- Evidence: the review's own mutants (`[ M?]` XY, `.+` for `[^/]+`) survive
  the current module; `macos-gate-target` — shell edits

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

## Stale claims and decision record — minor m17; the design graph

- Classification: Simple
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose (`plugin/README.md`) and investigation
  (`docs/references/pipeline-contracts.md`, `docs/decisions.md`)
- Evidence: the README must name `changed-files.sh`; no design node records
  build-defects KD-7 or this job's decisions

## Not in this job

Major 7's generalisation (a later session, per the task frame); minors m12,
F-2, F-5 and F-6 — routed in the outline's Scope OUT.
