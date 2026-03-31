# Skill: Fix Import Error

## Purpose
Guides the Fixer on diagnosing and resolving Python import errors in this project.

## Trigger
- failure_type == "import_error"
- Test output contains ImportError or ModuleNotFoundError

## Steps
- Extract the missing module or class name from the error message
- Check alembic/env.py for a missing model import line
- Check tests/conftest.py for a missing model import line
- Check app/models/__init__.py exists and exports the target name
- Add the missing import line to each registration file that lacks it

## Conventions
- New models must be imported in both alembic/env.py and tests/conftest.py
- Import lines follow the pattern: import app.models.<name>  # noqa: F401
- A missing __init__.py is created empty or with an explicit __all__ list

## Constraints
- Only auto-apply patches to files in the allowlist: alembic/env.py and tests/conftest.py
- Do not modify model files without verifying there is no circular import risk
- Verify the proposed import line is not already present before adding it
- Do not rename modules — fix the import site instead
