# Fixer Agent

## Purpose

Invoked when the Tester reports failures. Diagnoses the root cause and applies a targeted fix.

## Planned responsibilities

- Read failing test output and locate the source of the error
- Check `memory/known_failures.json` for previously seen patterns
- Apply the minimal fix required — avoid touching unrelated code
- Hand back to the Tester for re-validation

## Status

Scaffold only — not yet implemented.
