# agents/

Project knowledge that isn't code: design decisions, accumulated learnings, and
direction. Agent *behavioral* rules live in the project-root `CLAUDE.md`,
inlined directly (not generated from fragments).

- **decisions/** — architecture decision records, one file per topic (`cli`,
  `markdown-tooling`, `data-processing`, `testing`, `project-config`,
  `deliverable-review`, `plugin-packaging`). The permanent record of why
  something was chosen over the alternatives.
- **learnings.md** — institutional knowledge accumulated across sessions.
  Append-only, soft-capped at 80 lines; older entries graduate into
  `decisions/`.
- **ROADMAP.md** — direction and planned work.
- **guides/** — longer-form reference (`IMPLEMENTATION_STATUS.md`).
