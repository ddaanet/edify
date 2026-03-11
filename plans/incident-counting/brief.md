## 2026-03-11: Incident-specific learnings have recurrence-tracking value

**Origin:** /reflect on codify force-flush. Codify skill's quality criteria unconditionally reject incident-specific learnings ("describes what happened, not what to do"). User objected: "it's been very useful to be able to tell 'it's the second time this particular issue occurred'."

**Problem:** Incident-specific entries serve as occurrence counters. Dropping them loses the recurrence signal — "this happened twice" changes fix priority. The skill's criteria assume learnings only have value when generalized to principles. False dichotomy.

**Root cause classification:** Rule gap + directive conflict. Codify quality criteria too absolute; no carve-out for recurrence tracking.

**Investigation scope:**
- Examine git history to recover incidents lost since the incident-specific rejection rule was added to codify
- Ground incident counting methodology: keep full incidents? Only maintain counters and rely on git history and session logs? Segregate in specific memory files?

**Fix target:** `.claude/skills/codify/SKILL.md` Learnings Quality Criteria section — at minimum, add recurrence-tracking exception. Methodology choice may expand scope.
