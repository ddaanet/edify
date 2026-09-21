# Example Review Execution

**User:** `/review`

**Agent:** "Reviewing uncommitted changes, 5 files — the tree is dirty and
nothing is ahead of main.

*Runs git status and git diff HEAD*

Found changes in 5 files:
- plugin/agents/artisan.md (new file)
- plugin/bin/triage-feedback.sh (new file)
- CLAUDE.md (modified)
- plans/general-workflow/design.md (modified)
- .claude/agents/unification-task.md (new file)

Analyzing changes...

*Reviews each file for quality, standards, security*

Review complete.

**Overall Assessment**: Ready

**Issues found:**
- Critical: 0
- Major: 0
- Minor: 2

Full review written to: tmp/review-report-<timestamp>.md

**Minor issues:**
1. triage-feedback.sh: Consider adding a usage line to the header comment
2. artisan.md: Typo in line 87 \"specificed\" -> \"specified\"

**Recommendations:**
- All files follow project conventions
- Good documentation in script
- Comprehensive error handling

**Next steps:**
1. Fix minor typo if desired (optional)
2. Ready to commit"
