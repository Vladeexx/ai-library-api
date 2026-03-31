# Workflows

This directory contains the agent orchestration loop.

## Files

| File | Purpose |
|------|---------|
| `improvement_loop.py` | Fully implemented state-driven agent loop |

## How to run

```bash
python workflows/improvement_loop.py "add books CRUD endpoint"
python workflows/improvement_loop.py "add migration for authors table"
```

Exit code 0 = run succeeded (tests passed). Exit code 1 = all attempts failed.

## Actual pipeline

```
goal
 └─► planner (4-priority skill selection)
      └─► builder (parses skill file: Steps / Conventions / Constraints)
           └─► tester (runs make test)
                ├─► [pass] skill_curator → done
                └─► [fail] fixer / import_fixer
                          └─► planner (replan v2, failure-aware)
                               └─► builder (prefixed [builder step])
                                    └─► tester
                                         └─► skill_curator → done
```

Replanning fires once per run after the first fixer pass. `decide_next_action` drives
all routing — the orchestrator contains no sequencing logic.

## Planner skill selection priority

1. Exact goal match in `memory/run_history.jsonl`
2. Plan-type match in `memory/successful_patterns.json`
3. Trigger-based match across `.claude/skills/coding/*.md`
4. Hardcoded `SKILL_MAP` fallback

## Key state fields

| Field | Meaning |
|-------|---------|
| `plan_version` | 1 = initial plan, 2+ = replanned after failure |
| `replanned` | True after post-failure replan — prevents replanning twice |
| `failure_type` | `import_error` / `test_failure` / `lint_error` / `unknown` |
| `selected_skill` | Skill name used by builder this run |
| `skills_applied` | All skills loaded and parsed (reset on replan) |
| `repair_applied` | True if import_fixer auto-patched a file |

## Inspecting a run

```bash
# Most recent run
tail -1 memory/run_history.jsonl | python3 -m json.tool

# What skills succeeded
cat memory/successful_patterns.json

# What failures were recorded
cat memory/known_failures.json
```
