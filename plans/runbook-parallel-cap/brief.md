# Brief: Runbook Parallel Cap

## Problem

/runbook Tier 3 Execution Model currently has no convention for parallel agent count. The planner either hardcodes a number or leaves it unspecified. User preference varies by machine resources and willingness to manage concurrent agents.

## Scope

Add to /runbook skill: ask user for max concurrent agents during Execution Model generation (default 3, matching pr-review-toolkit convention). Specify sliding window dispatch in the Execution Model template — next agent launches when any slot frees, not fixed waves.

## Evidence

Edify-rename SP-1 /proof: user specified max 4 agents. The number is a user preference, not a design decision — should be asked, not assumed.
