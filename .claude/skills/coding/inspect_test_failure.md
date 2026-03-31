# Skill: Inspect Test Failure

## Purpose
Guides the Fixer on diagnosing a failing pytest test in this project.

## Trigger
- failure_type == "test_failure"

## Steps
- Read the full test output to identify which test(s) failed and the assertion message
- Locate the failing test function in tests/
- Locate the implementation code being tested in app/
- Identify the mismatch between expected and actual values
- Apply the smallest targeted fix to the implementation (not the test)
- Re-run tests to confirm the fix

## Conventions
- Test output includes the file path, line number, and failing assertion
- Prefer fixing the implementation over changing the test assertion
- Only change the test assertion if the test expectation itself was wrong

## Constraints
- Do not change test assertions to paper over a broken implementation
- Do not add new tests to fix a failing test — fix the root cause instead
- Do not modify files unrelated to the failing test
