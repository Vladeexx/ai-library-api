# Tester Agent

## Purpose

Validates the Builder's output by running the test suite and checking for regressions or missing coverage.

## Actual behavior

Runs `make test` via subprocess, captures stdout+stderr, sets `test_passed` and
appends to `errors`. Calls `_classify_failure(test_output)` which returns one of:
`import_error` / `test_failure` / `lint_error` / `unknown`.

`decide_next_action` routes to `import_fixer` for `import_error`, `fixer` for all
other failures. After a post-failure replan and rebuild, tester re-runs and the
result goes to `skill_curator`.

## Location

`workflows/improvement_loop.py` — `tester()` and `_classify_failure()`
