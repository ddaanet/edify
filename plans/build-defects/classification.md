# Classification — build-defects

Job-level line first: `triage-feedback.sh` reads the first `Classification:`
it finds.

- **Classification:** Moderate

Implicit bundling: 21 findings migrated from the retired inline/orchestrate
skill reviews (`plans/skill-reviews/reports/verify-inline.md`,
`verify-orchestrate.md`). Explicit bundling: the D-86 mechanical-check rider
from `plans/report-digest/triage.md`. Classified per cluster.

## Changed-files reference point — orchestrate C1, M8; inline M2, m10, m12

- Classification: Moderate
- Implementation certainty: High — `finishing.md:13` already diffs against a
  recorded commit, and D-86 already resolves commits from report paths
- Requirement stability: High — each finding carries fix text
- Behavioral code check: No — prose instructions only
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: the phase-base choice is the one design call; recall entry
  `sandbox-effects` does not bear on it

## Dispatch contracts — inline M1, m15, m16 first half, m6, m11

- Classification: Moderate
- Implementation certainty: High — `corrector.md` §Edge Cases already puts
  UNFIXABLE inside the report and returns the filename
- Requirement stability: High
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: recall entry `audit-a-contract-across-its-surfaces` — rule in
  `dispatch-composition.md`, enforcer `finishing.md`, consumer the template

## Triage script — inline M3

- Classification: Moderate
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: Yes — changes the `reports_count` filter, a logic
  path; the script has no tests today
- Work type: Production
- Artifact destination: production (`plugin/bin/`)
- Evidence: triage.md — behavioural code is Moderate minimum

## Tool availability and escalation — orchestrate M1, m7, M7; inline m2

- Classification: Moderate
- Implementation certainty: High
- Requirement stability: Moderate — M7 changes a fragment's recovery policy
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: recall entry `cc-async-task-notification-quirks` — `TaskOutput`
  on a running agent can dump its raw transcript

## `build/SKILL.md` body — orchestrate M4, C2, m3, m4, m5; inline m9

- Classification: Simple
- Implementation certainty: High
- Requirement stability: High
- Behavioral code check: No
- Work type: Production
- Artifact destination: agentic-prose
- Evidence: `build/SKILL.md` is 188 lines and off the allowlist, so the
  reports' net-zero constraint no longer binds (recall entry `line-caps`)

m5 left this cluster at `/proof`: its revision (outline KD-7) exempts the
conventional dirt in `verify-step.sh`, a changed logic path in a script with no
tests, so it is Moderate and a tdd item (outline Item 1.2).

## D-86 mechanical check — rider

- Classification: Complex
- Implementation certainty: Low — a check needs the dispatch kind, since a
  review commit legitimately carries only its report
- Requirement stability: Low — no observed violation motivates it
- Behavioral code check: Yes
- Work type: Production
- Artifact destination: production
- Evidence: `plans/remaining-sweep/reports/green-report-commit.md` §Open
  names the gap and no incident; deferred out of this job (outline Q-1)
