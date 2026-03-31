# Memory

This directory stores persistent context for the agent improvement loop.

## Files

| File | Purpose |
|------|---------|
| `run_history.jsonl` | Append-only log of each improvement cycle (one JSON object per line) |
| `known_failures.json` | Map of recurring failure patterns to their known fixes |
| `successful_patterns.json` | Map of approaches that have worked reliably in this codebase |
| `repo_conventions.md` | Human-readable summary of project conventions the Builder must follow |

## Written by

All files are written automatically by `skill_curator` in `workflows/improvement_loop.py`.
`run_history.jsonl` is append-only. `successful_patterns.json` and `known_failures.json`
are updated in-place after each run. Do not edit these files manually between runs.
