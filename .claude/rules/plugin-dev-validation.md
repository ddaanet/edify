---
paths:
  - ".claude/plugins/**/*"
---

# Plugin Development Validation

When planning work that creates or modifies plugin components (skills, agents, hooks, commands, plugin structure), include domain-specific validation in vet checkpoint steps.

**Domain validation skill:** `plugin/skills/plugin-dev-validation/SKILL.md`

**Artifact types:**
- Skills (`.claude/skills/**/SKILL.md`, `plugin/skills/**/SKILL.md`)
- Agents (`.claude/agents/*.md`)
- Hooks (`.claude/hooks/*.{sh,py}`, hook configuration in `settings.json`)
- Commands (`.claude/commands/**/*`)
- Plugin structure (`plugin.json`, directory layout)

**Include in corrector delegation:**

When writing runbook review checkpoint steps for plugin development work:

1. Read and apply criteria from `plugin/skills/plugin-dev-validation/SKILL.md`
2. Specify artifact type being reviewed (skills, agents, hooks, commands, plugin-structure)
3. Domain validation criteria are additive — generic quality + alignment checks still apply

**Example vet step:**

```markdown
### Step N: Checkpoint — Review [artifact description]

Delegate to corrector:
- Review all changes for quality, security, and alignment
- **Domain validation:** Read and apply criteria from
  `plugin/skills/plugin-dev-validation/SKILL.md`
  for artifact type: [skills|agents|hooks|commands|plugin-structure]
- Write report to `plans/<plan-name>/reports/vet-step-N.md`
```

**Note:** This rules file targets `.claude/plugins/**/*` only. Broader paths like `.claude/skills/**/*` and `.claude/agents/**/*` are covered by existing rules files (`skill-development.md`, `agent-development.md`). When paths overlap (e.g., creating a plugin skill), the planner receives both creation guidance and validation guidance — they are complementary.
