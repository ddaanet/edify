# Brief: Inline Resume Policy

Add resume-between-cycles directive to /inline skill's delegation protocol. Currently each cycle dispatches a fresh agent. Should resume same agent within a phase until ~150k tokens (context limit), then fresh agent. Pattern already exists in /orchestrate via delegation.md's delegate-resume section.

## Change

Edit `plugin/skills/inline/SKILL.md` delegation protocol section. Add: "Resume same agent between cycles within a phase. Fresh agent when context nears 150k tokens."

## Source

delegation.md already codifies: "Resume if: Agent has context... Skip resume if: Agent exchanged >15 messages (context likely near-full — 200K token limit)." The 150k threshold is a tighter bound than 200k — leaves headroom for the cycle prompt itself.
