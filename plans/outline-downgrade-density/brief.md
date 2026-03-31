# Brief: Add Content Density to Outline Downgrade Criteria

## Context

The post-outline complexity re-check in `/design` (`write-outline.md`) has four downgrade criteria that assess coordination complexity:
- Changes additive, no implementation loops
- No open questions remain
- Scope boundaries explicit
- No cross-file coordination requiring sequencing

These criteria miss content density. An 8-decision outline with risks section and 2 components passed all four criteria (low coordination complexity) but the corrector found 1 major + 3 minor issues (high content density benefited from review).

Session evidence: agent applied downgrade criteria mechanically, skipped corrector (A.6), user challenged, agent gave contradictory answer ("criteria technically hold but spirit doesn't match"), user directed corrector run, corrector found real value.

## Proposed Change

Add a content density criterion to the downgrade check in `write-outline.md` §Post-Outline Complexity Re-check:

- **Content density check:** Outline has ≤3 decisions AND no risks section. Outlines with higher decision count or explicit risks warrant corrector review regardless of coordination complexity.

The threshold (≤3) needs validation — it's based on reasoning about where corrector review adds value, not empirical data. Mark as ungrounded heuristic subject to adjustment.

## Affected Files

- `plugin/skills/design/references/write-outline.md` §Post-Outline Complexity Re-check

## Evidence

- Outline had 8 decisions (D1-D8), risks section, 2 components → all 4 criteria held → corrector skipped → corrector found real issues when run
- Corrector findings: missing component identifiers (major), missing citations (minor × 2), missing blocker context (minor)
- Current criteria: `write-outline.md` lines 116-119
