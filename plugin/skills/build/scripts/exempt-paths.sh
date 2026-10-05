# shellcheck shell=bash
# Sourced by verify-step.sh and changed-files.sh (D-91): the exempt
# alternation lives in one place these two scripts both read, so it never
# drifts between them. This file is not executable as a command — only
# sourced — and defines one variable: a bare ERE alternation, unanchored and
# unquoted. Each caller wraps it in its own anchors and whatever
# porcelain- or diff-specific context it needs.
#
# Three paths are dirty or changed by convention, never the run's own work:
# `memory` (the gitlore submodule, normally reported ` M`),
# `.claude/handoff-*.md` (`/handoff` and `/precompact` leave it modified or
# staged) and `inbox/*.md` (briefs dropped or updated uncommitted on
# purpose).
# shellcheck disable=SC2034 # read by every script that sources this file
EXEMPT_PATHS_ALTERNATION='memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md'
