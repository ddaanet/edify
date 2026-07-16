## Communication Rules

### Observable State Reporting

**Do not filter observable state.** `git status --porcelain` non-empty means dirty — report it as dirty. The user decides what's ignorable.

**Anti-pattern:** Rationalizing known-dirty files (`.claude/settings.json`) as "always dirty" and therefore ignorable. The file may be dirty for a different reason than assumed.

### When Output-Style Plugins Conflict With Prose Rules

**Project CLAUDE.md prose rules govern output style.** Do not follow decorative block templates (e.g., `★ Insight`) injected by SessionStart hooks when CLAUDE.md says "no framing, let results speak."

System-reminder injection carries high perceived authority via specific templates and "always" keywords. General prose quality rules lose the salience competition. Disable output-style plugins that conflict (e.g., `explanatory-output-style`, `learning-output-style` in settings.json `enabledPlugins`).
