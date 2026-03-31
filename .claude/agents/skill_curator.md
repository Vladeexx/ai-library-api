# Skill Curator Agent

## Purpose

Records the outcome of each improvement cycle and keeps the memory and skills directories up to date.

## Actual behavior

Sets `final_status` ("success" or "failed") and appends a structured JSON entry to
`memory/run_history.jsonl` including: goal, plan_type, skill_used, skills_applied,
skill_notes, pattern_hint, plan_version, replanned, last_failure_summary, steps_executed,
repair_applied, repair_summary.

On success with a selected skill: calls `_update_successful_pattern()` to write/update
`memory/successful_patterns.json` (key: `{plan_type}:{skill}`), incrementing
`success_count` and storing `skill_notes` and up to five `example_goals`.

On success with repair: calls `_update_repair_pattern()` to record the successful fix
under key `repair:{failure_type}:{missing_target}`.

On failure: appends a record to `memory/known_failures.json`.

## Location

`workflows/improvement_loop.py` — `skill_curator()` and `_update_*` helpers
