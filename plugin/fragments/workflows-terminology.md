## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Requirements capture** → Use `/requirements` skill (extract from conversation or elicit through questions)
- **Implementation tasks** → Use `/design` skill (triages complexity, routes to appropriate workflow)
- **Workflow in progress** (check `.claude/handoff-task.md`) → Continue from current state

The `/design` skill includes complexity triage: simple tasks execute directly, moderate tasks skip design and route to planning, complex tasks get full design treatment.

**Progressive discovery:** Don't preload all workflow documentation. Details in the design, runbook and build skills.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Phased implementation plan `/build` dispatches from (previously called "plan") |
| **Phase type** | `tdd` or `general` — determines item format and review criteria, and for `tdd` the dispatch structure. It does not decide whether an item is delegated; `/build` decides that per item at dispatch time |
| **Item** | Individual unit of work within a runbook phase |
| **Slice** | One behaviour of a tdd item: the unit of RED → review → GREEN → review dispatch |
| **Orchestrator** | The role the executing skill plays while it walks the work — dispatching, monitoring, synthesizing. A role, not a skill name: `/build` fills it today, and agent and fragment prose that says "the orchestrator" means whoever is executing |

**Note on directory naming:** The `plans/` directory is a historical convention and remains unchanged. It contains runbooks, reports, and execution artifacts.
