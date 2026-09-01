## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Requirements capture** → Use `/requirements` skill (extract from conversation or elicit through questions)
- **Implementation tasks** → Use `/design` skill (triages complexity, routes to appropriate workflow)
- **Workflow in progress** (check `.claude/handoff-task.md`) → Continue from current state

The `/design` skill includes complexity triage: simple tasks execute directly, moderate tasks skip design and route to planning, complex tasks get full design treatment.

**Progressive discovery:** Don't preload all workflow documentation. Details in design, runbook, and orchestrate skills.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Phased implementation plan `/orchestrate` dispatches from (previously called "plan") |
| **Phase type** | `tdd`, `general` or `inline` — determines item format, review criteria and dispatch for that phase |
| **Item** | Individual unit of work within a runbook phase |
| **Slice** | One behaviour of a tdd item: the unit of RED → review → GREEN → review dispatch |

**Note on directory naming:** The `plans/` directory is a historical convention and remains unchanged. It contains runbooks, reports, and execution artifacts.
