# Fixer Agent

## Purpose

Invoked when the Tester reports failures. Diagnoses the root cause and applies a targeted fix.

## Actual behavior

Two implementations exist:

**`fixer`** (generic): placeholder — logs that a fix would be attempted, increments
`attempt_number`. Used for `test_failure`, `lint_error`, `unknown`.

**`import_fixer`** (specialist, fully implemented): extracts missing import target
from test output via regex, inspects `alembic/env.py` / `tests/conftest.py` /
`app/models/__init__.py`, builds a structured `suggested_fix` with patch proposal,
and auto-applies safe `add_import` patches to allowlisted files if confidence is
high. Checks `successful_patterns.json` for prior successful repairs.

Both increment `attempt_number` so `decide_next_action` routes to planner for a
post-failure replan on the next iteration (if `replanned` is still False).

## Location

`workflows/improvement_loop.py` — `fixer()`, `import_fixer()`, `_apply_patch_proposal()`
