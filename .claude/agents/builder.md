# Builder Agent

## Purpose

Executes the plan produced by the Planner. Writes or modifies files according to project conventions and existing patterns.

## Actual behavior

Reads the selected skill file and extracts `## Steps`, `## Conventions`,
`## Constraints` via `_parse_skill()`. Logs each convention and constraint.
Appends plan steps to `executed_steps` (prefixed `[builder step]` on replans).
Appends skill-directed steps as `[skill:<name>] <step>`.

Also checks `memory/successful_patterns.json` for prior `skill_notes` — if stored
notes differ from the current file, appends them with a `[prior success]` prefix and
records `[pattern:notes_reused]` in `executed_steps`.

**Note:** builder logs and records steps but does not write files. Real file
modifications are made by Claude Code directly using the skill and step guidance.

## Location

`workflows/improvement_loop.py` — `builder()`
