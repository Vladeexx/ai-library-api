# Planner Agent

## Purpose

Receives a goal from the Orchestrator and produces a structured, step-by-step implementation plan before any code is written.

## Actual behavior

Selects a skill and emits a step list using a four-priority chain:

1. Exact goal match in `memory/run_history.jsonl` → preferred_skill
2. Plan-type match in `memory/successful_patterns.json` → preferred_skill + pattern_hint
3. Trigger-based match across `.claude/skills/coding/*.md` → trigger_skill + pattern_hint
4. Hardcoded `SKILL_MAP` fallback (applied in builder, not here)

When `plan_version > 1` (post-failure replan): resets `skills_applied`/`skill_notes`,
builds `last_failure_summary`, re-runs trigger matching with `failure_type` as context,
emits a shorter targeted step list, sets `replanned = True`, resets `build_complete`.

## Location

`workflows/improvement_loop.py` — `planner()`
