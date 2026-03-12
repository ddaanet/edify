**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Review Agent Quality

## Problem

Corrector and review agents (corrector, design-corrector, outline-corrector, runbook-corrector) produce false positives and miss real issues. Quality improvement requires evidence collection before designing fixes.

- **Corrector audit:** Systematic collection of false positive evidence from corrector agent runs. Currently evidence is anecdotal — scattered across session learnings and conversation history. Need structured evidence corpus to identify patterns (which rules produce false positives, which file types trigger spurious findings).

- **Diagnostic opus review:** Post-vet root cause analysis of review failures. When a review agent misses a real issue that surfaces later, trace back to identify why (wrong review scope, missing context, incorrect rule application). Requires opus for nuanced RCA.

## Investigation Approach

1. Collect false positive evidence from recent corrector runs (git log for corrector report files)
2. Categorize by root cause (rule too broad, context insufficient, pattern mismatch)
3. Collect missed-issue evidence from post-merge bugs
4. Design targeted fixes for top categories

## Success Criteria

- Evidence corpus with 10+ categorized false positive instances
- Top 3 false positive categories identified with fix proposals
- At least 2 missed-issue RCAs completed
