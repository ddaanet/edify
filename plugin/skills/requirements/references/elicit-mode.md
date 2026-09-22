# Elicit Mode Procedure

Read when mode detection lands on elicit — a fresh conversation or minimal
context, with no prior feature discussion to extract from. Extract mode never
reads this file.

## 1. Semi-Structured Elicitation

Ask inline, in numbered prose, one turn per round — same form as §Gap-Fill
Questions in `references/formats-and-exit.md`, and for the same reason. Cover
the critical sections (Functional Requirements, Scope Boundaries), adding
Constraints/Dependencies where the job suggests them. Each question states a
proposed answer inferred from the job name and the conversation; the user
corrects what is wrong and silence carries the rest. Then 1-2 adaptive
follow-ups based on what came back.

Elicit mode has less to infer from than Extract mode, so its proposals will be
weaker — say so, rather than presenting a guess with the confidence of a
derivation.

The question budget is the one stated in Extract mode's §4 Gap Detection: 4-6
questions total for elicit, section questions and adaptive follow-ups together.

## 2-6. Shared Steps

After elicitation, follow Extract mode steps 2, 2.5 and 3-6 (Codebase Discovery,
Post-Explore Recall, Structure, Gap Detection, Write and Validate, Finalise).
