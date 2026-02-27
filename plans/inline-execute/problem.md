# Triage Feedback Loop

**Grounding:** Gap 7 in `plans/reports/design-skill-grounding.md`
**Principles:** GJP calibration (Tetlock), AAR planned-vs-actual (U.S. Army), ESI retrospective triage review
**Priority metric:** Complex↔Moderate boundary (26% of sessions are Moderate, 45% Complex — this boundary affects the most sessions)

## Problem

/design records classification predictions (complexity, axes, evidence) but no downstream mechanism compares predictions to execution outcomes. All triage corrections in project history came from explicit user intervention, not systematic measurement. 0 automatic feedback events observed across 38 sessions.

## What Exists (prediction side — complete)

The Classification Gate in /design produces a structured block:
- Classification: Simple / Moderate / Complex / Defect
- Implementation certainty: High / Moderate / Low
- Requirement stability: High / Moderate / Low
- Evidence: which criteria informed the decision

This is the recorded prediction. It lives in session transcript (JSONL), not in a persistent file.

## What's Missing (outcome side)

At execution completion, no mechanism:
1. Surfaces execution evidence (files changed, agent count, corrections applied, behavioral code written)
2. Compares classification to execution evidence
3. Detects systematic misclassification patterns
4. Feeds corrections back to triage criteria

## Constraints

- Detection is automatable; criteria updates require human judgment
- Insertion point: /orchestrate completion or /commit (not inside /design)
- Must not add ceremony to sessions that don't need it — lightweight surfacing, not mandatory review
- Classification data lives in JSONL transcripts, not plan files — extraction needed

## Open Questions

- Q1: Where does the feedback surface? Learning entry? Session note? Dedicated report?
- Q2: What execution evidence is reliably extractable? (files changed = git diff; agent count = subagents dir; corrections = review reports; behavioral code = hard to detect automatically)
- Q3: What threshold triggers a feedback event? Every session, or only when prediction and outcome diverge significantly?
- Q4: Does the classification prediction need to be persisted to a plan file during /design (currently only in JSONL transcript)?
- Q5: Batch retrospective (periodic analysis of N sessions) vs per-session inline feedback?
