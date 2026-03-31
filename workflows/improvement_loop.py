"""
improvement_loop.py
-------------------
Minimal runnable agent improvement loop.

Orchestrates the pipeline:
    orchestrator → planner → builder → tester → (fixer) → skill_curator

Usage:
    python workflows/improvement_loop.py "add books CRUD endpoint"
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

@dataclass
class RunState:
    goal: str
    attempt_number: int = 1
    plan: dict = field(default_factory=dict)
    selected_skill: Optional[str] = None
    # Skills that were loaded and consumed by builder during this run.
    skills_applied: list[str] = field(default_factory=list)
    # Conventions and constraints extracted from the loaded skill file.
    skill_notes: str = ""
    build_complete: bool = False
    executed_steps: list[str] = field(default_factory=list)
    test_passed: bool = False
    test_output: str = ""
    # One entry is appended per failed tester run. decide_next_action depends
    # on len(errors) == number of completed tester runs to route correctly.
    errors: list[str] = field(default_factory=list)
    fixer_notes: str = ""
    failure_type: str = ""
    suggested_fix: dict = field(default_factory=dict)
    repair_applied: bool = False
    repair_summary: str = ""
    final_status: Optional[str] = None


REPO_ROOT = Path(__file__).parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
RUN_HISTORY = MEMORY_DIR / "run_history.jsonl"
KNOWN_FAILURES_FILE = MEMORY_DIR / "known_failures.json"
SUCCESSFUL_PATTERNS_FILE = MEMORY_DIR / "successful_patterns.json"
TEST_COMMAND = "make test"
MAX_ATTEMPTS = 3


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log(agent: str, message: str) -> None:
    print(f"[{agent}] {message}")


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


def _load_json_file(path: Path) -> dict:
    """Load a JSON file, returning an empty dict on any error."""
    try:
        text = path.read_text().strip()
        if not text:
            return {}
        return json.loads(text)
    except (OSError, json.JSONDecodeError):
        return {}


# Keywords associated with each plan type, used for memory pattern matching.
_PLAN_KEYWORDS = {
    "crud_endpoint": {"crud", "endpoint", "router", "schema", "route"},
    "migration": {"migration", "migrate", "model", "alembic", "column", "table"},
    "generic": set(),
}


def _find_relevant_patterns(goal: str, plan_type: str) -> list[str]:
    """
    Return pattern names from memory files that are relevant to the goal.

    Relevance is determined by simple keyword overlap: a pattern name is
    included if any word from it appears in the goal, or if the pattern
    name contains a keyword associated with the current plan type.
    """
    goal_words = set(goal.lower().split())
    type_keywords = _PLAN_KEYWORDS.get(plan_type, set())

    relevant: list[str] = []
    for source_file in (SUCCESSFUL_PATTERNS_FILE, KNOWN_FAILURES_FILE):
        data = _load_json_file(source_file)
        for key in data:
            key_words = set(key.lower().replace("_", " ").replace("-", " ").split())
            if key_words & goal_words or key_words & type_keywords:
                relevant.append(key)

    return relevant


def _load_run_history() -> list[dict]:
    if not RUN_HISTORY.exists():
        return []
    entries = []
    for line in RUN_HISTORY.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def planner(state: RunState) -> RunState:
    history = _load_run_history()
    prior_runs = [e for e in history if e.get("goal") == state.goal]
    last_failed = False
    preferred_skill = None
    if prior_runs:
        last_status = prior_runs[-1].get("status", "unknown")
        log("planner", "previous run detected for goal")
        log("planner", f"last status: {last_status}")
        last_failed = last_status == "failed"
        successful = [
            e for e in prior_runs
            if e.get("status") == "success" and e.get("skill_used")
        ]
        if successful:
            preferred_skill = successful[-1]["skill_used"]
            log("planner", f"previous successful skill detected: {preferred_skill}")

    keywords = state.goal.lower()

    if any(k in keywords for k in ("crud", "endpoint")):
        plan_type = "crud_endpoint"
        steps = [
            "analyse codebase",
            "inspect routers",
            "inspect schemas",
            "inspect models",
            "implement endpoint change",
            "add or update tests",
            "run tests",
        ]
    elif "migration" in keywords:
        plan_type = "migration"
        steps = [
            "analyse codebase",
            "inspect models",
            "prepare migration change",
            "run migrations",
            "run tests",
        ]
    else:
        plan_type = "generic"
        steps = [
            "analyse codebase",
            "identify files to create or modify",
            "implement change",
            "run tests",
        ]

    if last_failed:
        steps.insert(1, "review previous failure")
        log("planner", "adapting plan based on previous failure")

    relevant_patterns = _find_relevant_patterns(state.goal, plan_type)
    state.plan = {
        "plan_type": plan_type,
        "preferred_skill": preferred_skill,
        "steps": steps,
        "relevant_patterns": relevant_patterns,
    }
    log(
        "planner",
        f"selected plan_type={plan_type!r} with {len(steps)} steps"
        f" and {len(relevant_patterns)} relevant patterns",
    )
    return state


SKILL_MAP = {
    "crud_endpoint": "add_crud_endpoint",
    "migration": "add_alembic_migration",
    "generic": None,
}

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills" / "coding"


def _parse_skill(skill_path: Path) -> dict[str, list[str]]:
    """
    Parse a markdown skill file into a dict of section_name -> [bullet items].

    Only ``## `` headings become section keys (lowercased, spaces → underscores).
    Lines starting with ``- `` inside a section are collected as items.
    Prose lines and sub-headings are ignored so the parser stays simple.

    Example — given a skill with::

        ## Steps
        - Inspect existing routers
        - Create the endpoint file

    Returns ``{"steps": ["Inspect existing routers", "Create the endpoint file"], ...}``.
    """
    result: dict[str, list[str]] = {}
    current_section: Optional[str] = None

    for line in skill_path.read_text().splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip().lower().replace(" ", "_")
            result.setdefault(current_section, [])
        elif current_section and line.strip().startswith("- "):
            result[current_section].append(line.strip()[2:].strip())

    return result


def builder(state: RunState) -> RunState:
    log("builder", "starting execution")

    preferred_skill = state.plan.get("preferred_skill")
    if preferred_skill:
        skill = preferred_skill
        log("builder", f"reusing preferred skill from memory: {skill}")
    else:
        skill = SKILL_MAP.get(state.plan.get("plan_type", "generic"))
        if skill:
            log("builder", f"using default skill: {skill}")
        else:
            log("builder", "no specific skill for this plan type")

    skill_steps: list[str] = []

    if skill:
        skill_file = SKILLS_DIR / f"{skill}.md"
        if skill_file.exists():
            parsed = _parse_skill(skill_file)

            conventions = parsed.get("conventions", [])
            constraints = parsed.get("constraints", [])
            skill_steps = parsed.get("steps", [])

            # Build a human-readable summary of what the skill contributed.
            notes_parts: list[str] = []
            if conventions:
                notes_parts.append("conventions: " + "; ".join(conventions))
            if constraints:
                notes_parts.append("constraints: " + "; ".join(constraints))
            state.skill_notes = " | ".join(notes_parts)

            state.skills_applied.append(skill)

            log("builder", f"loaded skill {skill!r}: "
                f"{len(skill_steps)} steps, "
                f"{len(conventions)} conventions, "
                f"{len(constraints)} constraints")

            for convention in conventions:
                log("builder", f"  applying convention: {convention}")
            for constraint in constraints:
                log("builder", f"  applying constraint: {constraint}")
        else:
            log("builder", f"skill file not found for {skill!r}")

    state.selected_skill = skill
    steps = state.plan.get("steps", [])
    total = len(steps)
    for i, step in enumerate(steps, start=1):
        log("builder", f"step {i}/{total}: {step}")
        state.executed_steps.append(step)

    # Append skill-specific steps after the plan steps so run history records
    # which concrete actions the skill directed. Prefixed with [skill:<name>]
    # to make the source clear.
    if skill_steps:
        log("builder", f"executing {len(skill_steps)} skill-directed steps from {skill!r}")
        for skill_step in skill_steps:
            log("builder", f"  [skill:{skill}] {skill_step}")
            state.executed_steps.append(f"[skill:{skill}] {skill_step}")

    state.build_complete = True
    return state


def tester(state: RunState) -> RunState:
    log("tester", f"running real test suite: {TEST_COMMAND!r}")

    result = subprocess.run(
        TEST_COMMAND,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    state.test_output = "\n".join(filter(None, [result.stdout.rstrip(), result.stderr.rstrip()]))
    if state.test_output:
        print(state.test_output)

    state.test_passed = result.returncode == 0
    if state.test_passed:
        log("tester", "tests passed")
        state.failure_type = ""
    else:
        log("tester", f"tests FAILED (exit code {result.returncode})")
        state.errors.append(f"tests failed with exit code {result.returncode}")
        state.failure_type = _classify_failure(state.test_output)
        log("tester", f"classified failure as: {state.failure_type}")

    return state


def _classify_failure(test_output: str) -> str:
    """Classify the most recent tester output into a structured failure type."""
    if any(t in test_output for t in ("ImportError", "ModuleNotFoundError")):
        return "import_error"
    if any(t in test_output for t in ("AssertionError", "FAILED", "ERROR")):
        return "test_failure"
    if any(t in test_output for t in ("E501", "E302", "flake8", "ruff")):
        return "lint_error"
    return "unknown"


def fixer(state: RunState) -> RunState:
    log("fixer", "tests failed — a fix would be attempted here in a future phase")
    last_error = state.errors[-1] if state.errors else "unknown error"
    state.fixer_notes = f"attempt {state.attempt_number} failed: {last_error}"
    log("fixer", f"noted: {state.fixer_notes}")
    state.executed_steps.append("fix attempted")
    state.attempt_number += 1
    return state


def _inspect_files(relative_paths: list[str], target: Optional[str]) -> list[str]:
    """
    For each path in relative_paths, check whether the file exists and whether
    target appears in its contents. Returns one short finding string per file.
    """
    findings = []
    for rel_path in relative_paths:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            findings.append(f"{rel_path}: file not found")
            continue
        if not target:
            findings.append(f"{rel_path}: file exists")
            continue
        try:
            content = full_path.read_text()
        except OSError:
            findings.append(f"{rel_path}: could not read")
            continue
        if target in content:
            findings.append(f"{rel_path}: '{target}' found")
        else:
            findings.append(f"{rel_path}: '{target}' not found")
    return findings


def _build_patch_proposal(
    missing_target: Optional[str],
    is_internal: bool,
    findings: list[str],
) -> Optional[dict]:
    """
    Parse inspection_findings and return one concrete patch proposal, or None
    if no specific proposal can be made.

    Finding strings have the format  "<rel_path>: <message>"  where message is
    one of:  "'X' found" | "'X' not found" | "file not found" | "file exists"
    """
    if not missing_target:
        return None

    # Build a lookup so we can query findings by file path.
    finding_map: dict[str, str] = {}
    for f in findings:
        if ": " in f:
            path, msg = f.split(": ", 1)
            finding_map[path] = msg

    if is_internal:
        # Derive the import line the registration files should contain.
        # Convention: modules live at app.models.<name_lower> (e.g. app.models.author).
        if "." in missing_target:
            import_line = f"import {missing_target}  # noqa: F401"
        else:
            import_line = f"import app.models.{missing_target.lower()}  # noqa: F401"

        # Priority: check registration files in order; propose the first one missing the target.
        for reg_file in ("alembic/env.py", "tests/conftest.py"):
            msg = finding_map.get(reg_file, "")
            if msg == "file not found":
                continue  # unusual — skip; don't propose adding to a missing file
            if "not found" in msg:  # "'X' not found" — file exists but target absent
                return {
                    "target_file": reg_file,
                    "action": "add_import",
                    "proposed_change": import_line,
                    "reason": (
                        f"'{missing_target}' is not imported in {reg_file}; "
                        "required for model registration"
                    ),
                    "confidence": "high",
                }

        # If the model __init__ is entirely absent, the model file itself may not exist.
        if finding_map.get("app/models/__init__.py") == "file not found":
            return {
                "target_file": f"app/models/{missing_target.lower()}.py",
                "action": "verify_model_file",
                "proposed_change": (
                    f"verify that app/models/{missing_target.lower()}.py exists "
                    f"and defines '{missing_target}'"
                ),
                "reason": (
                    "app/models/__init__.py not found; "
                    "the model file itself may not have been created yet"
                ),
                "confidence": "medium",
            }

        return None  # target already present in all checked files — no proposal needed

    else:
        # External package case — inspect requirements.txt finding.
        msg = finding_map.get("requirements.txt", "")
        if msg == "file not found":
            return {
                "target_file": "requirements.txt",
                "action": "create_and_add_dependency",
                "proposed_change": (
                    f"create requirements.txt and add '{missing_target}'"
                ),
                "reason": "requirements.txt does not exist",
                "confidence": "low",
            }
        if "not found" in msg:
            return {
                "target_file": "requirements.txt",
                "action": "add_dependency",
                "proposed_change": f"add '{missing_target}' to requirements.txt",
                "reason": f"'{missing_target}' is not listed in requirements.txt",
                "confidence": "high",
            }
        if "found" in msg and "not found" not in msg:
            return {
                "target_file": None,
                "action": "check_install",
                "proposed_change": (
                    "run 'pip install -r requirements.txt' "
                    "or rebuild the Docker container"
                ),
                "reason": (
                    f"'{missing_target}' is listed in requirements.txt "
                    "but may not be installed in the current environment"
                ),
                "confidence": "medium",
            }

        return None


# Files that _apply_patch_proposal is permitted to modify automatically.
# Deliberately narrow: only well-understood registration files.
_PATCH_ALLOWLIST = {"alembic/env.py", "tests/conftest.py"}


def _apply_patch_proposal(proposal: dict, state: "RunState") -> "RunState":
    """
    Apply a high-confidence add_import patch proposal to a single file.

    Safety gates (all must pass; any failure sets repair_summary and returns):
    - action must be "add_import"
    - target_file must be in _PATCH_ALLOWLIST
    - confidence must be "high"
    - proposed_change must be a non-empty single line starting with "import " or "from "
    - target file must already exist (never creates files)
    - proposed_change must not already be present in the file (idempotency)
    """
    action = proposal.get("action")
    target_file = proposal.get("target_file")
    confidence = proposal.get("confidence")
    proposed_change = (proposal.get("proposed_change") or "").strip()

    # Gate 1: action and allowlist
    if action != "add_import":
        state.repair_summary = f"repair skipped: action '{action}' is not auto-applicable"
        return state
    if target_file not in _PATCH_ALLOWLIST:
        state.repair_summary = f"repair skipped: '{target_file}' is not in the safe allowlist"
        return state

    # Gate 2: confidence
    if confidence != "high":
        state.repair_summary = f"repair skipped: confidence '{confidence}' is below threshold"
        return state

    # Gate 3: proposed_change is a valid single import line
    if not proposed_change:
        state.repair_summary = "repair skipped: proposed_change is empty"
        return state
    if "\n" in proposed_change:
        state.repair_summary = "repair skipped: proposed_change spans multiple lines"
        return state
    if not (proposed_change.startswith("import ") or proposed_change.startswith("from ")):
        state.repair_summary = (
            "repair skipped: proposed_change does not start with 'import ' or 'from '"
        )
        return state

    # Gate 4: file must exist
    full_path = REPO_ROOT / target_file
    if not full_path.exists():
        state.repair_summary = f"repair skipped: target file '{target_file}' does not exist"
        return state

    # Gate 5: idempotency — do not append if the line is already present
    try:
        existing = full_path.read_text()
    except OSError:
        state.repair_summary = f"repair skipped: could not read '{target_file}'"
        return state

    if proposed_change in existing:
        state.repair_summary = (
            f"repair skipped: '{proposed_change}' already present in {target_file}"
        )
        return state

    # All gates passed — append the import line.
    try:
        with full_path.open("a") as fh:
            # Ensure we start on a new line even if the file does not end with one.
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(proposed_change + "\n")
    except OSError as exc:
        state.repair_summary = f"repair failed: could not write to '{target_file}': {exc}"
        return state

    state.repair_applied = True
    state.repair_summary = f"appended '{proposed_change}' to {target_file}"
    return state


# Files known to require manual import registration in this codebase.
# Derived from memory/repo_conventions.md and .claude/skills/coding/fix_import_error.md.
_IMPORT_ERROR_FILES = [
    "alembic/env.py",
    "tests/conftest.py",
    "app/models/__init__.py",
]


def import_fixer(state: RunState) -> RunState:
    log("import_fixer", "import error detected — analysing failure history")
    # failure_type is intentionally not modified here: tester already classified
    # this run as "import_error" and that classification should be preserved
    # for skill_curator and run history.

    known = _load_json_file(KNOWN_FAILURES_FILE)
    prior_import_errors = [
        e for e in (known if isinstance(known, list) else [])
        if e.get("failure_type") == "import_error" and e.get("goal") == state.goal
    ]

    if prior_import_errors:
        last = prior_import_errors[-1]
        last_error = last.get("last_error", "unknown")
        diagnosis = (
            f"repeated import error detected ({len(prior_import_errors)} prior occurrence(s)); "
            f"possible missing module import or incorrect package path; "
            f"last recorded error: {last_error}"
        )
        confidence = "high"
    else:
        diagnosis = (
            "first observed import error for this goal; "
            "possible missing module import or incorrect package path"
        )
        confidence = "medium"

    # Extract missing import target from the actual tester output.
    # Matches two pytest error patterns:
    #   "cannot import name 'Author'"          → group 1 (a name import — always internal)
    #   "No module named 'app.models.author'"  → group 2 (a module import — check prefix)
    match = re.search(
        r"cannot import name ['\"](\w+)['\"]|No module named ['\"]([.\w]+)['\"]",
        state.test_output,
    )
    if match:
        missing_target = match.group(1) or match.group(2)
        # group(1) → "cannot import name" pattern: the named thing lives inside a module
        # that already exists. In this codebase that almost always means a model or schema
        # that isn't exported yet → treat as internal.
        # group(2) → "No module named" pattern: internal only if the path starts with "app."
        is_internal = bool(match.group(1)) or (match.group(2) or "").startswith("app.")
    else:
        missing_target = None
        is_internal = True  # no match: conservative fallback to internal advice

    if is_internal:
        state.suggested_fix = {
            "likely_cause": "missing or incorrect module import",
            "missing_target": missing_target,
            "likely_files_to_inspect": _IMPORT_ERROR_FILES,
            "suggested_fix": (
                "ensure new models are imported in alembic/env.py and tests/conftest.py; "
                "check for missing __init__.py in new package directories"
            ),
            "confidence": confidence,
        }
    else:
        state.suggested_fix = {
            "likely_cause": "missing external package or unresolvable module",
            "missing_target": missing_target,
            "likely_files_to_inspect": ["requirements.txt"],
            "suggested_fix": (
                f"check that '{missing_target}' is listed in requirements.txt and installed"
            ),
            "confidence": confidence,
        }

    findings = _inspect_files(state.suggested_fix["likely_files_to_inspect"], missing_target)
    state.suggested_fix["inspection_findings"] = findings
    for finding in findings:
        log("import_fixer", f"inspected: {finding}")

    patch_proposal = _build_patch_proposal(missing_target, is_internal, findings)
    state.suggested_fix["patch_proposal"] = patch_proposal
    if patch_proposal:
        log("import_fixer", f"patch proposal: {patch_proposal['action']} → {patch_proposal.get('target_file', 'n/a')}")
        state = _apply_patch_proposal(patch_proposal, state)
        log("import_fixer", f"repair: {state.repair_summary}")

    state.fixer_notes = f"attempt {state.attempt_number}: {diagnosis}"
    log("import_fixer", state.fixer_notes)
    log("import_fixer", f"suggested_fix produced (confidence: {confidence}, target: {missing_target or 'unknown'})")
    state.executed_steps.append("import_fixer analyzed previous import failures")
    state.attempt_number += 1
    return state


def skill_curator(state: RunState) -> RunState:
    state.final_status = "success" if state.test_passed else "failed"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": state.goal,
        "plan_type": state.plan.get("plan_type"),
        "builder_status": "completed",
        "skill_used": state.selected_skill,
        "skills_applied": state.skills_applied or None,
        "skill_notes": state.skill_notes or None,
        "status": state.final_status,
        "steps_executed": state.executed_steps,
        "test_command": TEST_COMMAND,
        "test_passed": state.test_passed,
        "fixer_notes": state.fixer_notes or None,
        "failure_type": state.failure_type or None,
        "suggested_fix": state.suggested_fix or None,
        "repair_applied": state.repair_applied or None,
        "repair_summary": state.repair_summary or None,
    }
    with RUN_HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    log("skill_curator", f"run recorded to memory/run_history.jsonl (status: {state.final_status})")

    if state.final_status == "failed":
        failure = {
            "failure_type": state.failure_type or "unknown",
            "goal": state.goal,
            "plan_type": state.plan.get("plan_type"),
            "skill_used": state.selected_skill,
            "last_error": state.errors[-1] if state.errors else None,
            "suggested_fix": state.suggested_fix or None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        existing = _load_json_file(KNOWN_FAILURES_FILE)
        failures = existing if isinstance(existing, list) else []
        failures.append(failure)
        KNOWN_FAILURES_FILE.write_text(json.dumps(failures, indent=2))
        log("skill_curator", "failure recorded to memory/known_failures.json")

    return state


# ---------------------------------------------------------------------------
# Agent registry
#
# Maps agent names to their handler functions.  The orchestrator uses this
# table instead of calling functions directly, which is the groundwork for
# later decision-based orchestration where the next agent is chosen at
# runtime rather than being hardcoded in the control flow.
# ---------------------------------------------------------------------------

AGENT_REGISTRY: dict[str, Callable[[RunState], RunState]] = {
    "planner": planner,
    "builder": builder,
    "tester": tester,
    "fixer": fixer,
    "import_fixer": import_fixer,
    "skill_curator": skill_curator,
}


# ---------------------------------------------------------------------------
# Decision function
#
# Separates "what should happen next?" from "execute it". The orchestrator
# calls this on every iteration and dispatches whatever name is returned.
#
# This is the foundation for future adaptive behavior: fixer or skill_curator
# can write a diagnosis or structured result back into RunState, and this
# function can then route differently on the next iteration — without touching
# the orchestrator or any other agent.
# ---------------------------------------------------------------------------

def decide_next_action(state: RunState) -> str:
    if not state.plan:
        return "planner"
    if not state.build_complete:
        return "builder"
    if state.final_status is not None:
        return "done"
    if state.test_passed:
        return "skill_curator"
    # Invariant: len(state.errors) == number of completed tester runs.
    # If errors < attempt_number, tester has not yet run this attempt.
    if len(state.errors) < state.attempt_number:
        return "tester"
    # Tester ran and failed this attempt.
    # Route to a specialised fixer if retries remain, otherwise close out.
    if state.attempt_number < MAX_ATTEMPTS:
        if state.failure_type == "import_error":
            return "import_fixer"
        return "fixer"
    return "skill_curator"


def orchestrator(goal: str) -> RunState:
    """
    Pure dispatch loop. Contains no sequencing logic of its own.

    On each iteration decide_next_action reads RunState and returns the name
    of the next agent to run. The orchestrator dispatches it through
    AGENT_REGISTRY and repeats. This loop is what makes future adaptive
    behavior possible: once fixer writes a real diagnosis into RunState,
    decide_next_action can route differently on the next pass — and
    skill_curator can record richer outcomes — without changing anything here.
    """
    log("orchestrator", f"received goal: {goal!r}")
    state = RunState(goal=goal)

    while True:
        action = decide_next_action(state)
        if action == "done":
            break
        if action == "tester":
            log("orchestrator", f"test attempt {state.attempt_number}/{MAX_ATTEMPTS}")
        if action == "skill_curator" and not state.test_passed:
            log("orchestrator", f"all {MAX_ATTEMPTS} attempts exhausted — recording as failed")
        state = AGENT_REGISTRY[action](state)

    log("orchestrator", f"run complete — status: {state.final_status}")
    return state


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflows/improvement_loop.py \"<goal>\"")
        sys.exit(1)

    goal = sys.argv[1]
    final_state = orchestrator(goal)
    sys.exit(0 if final_state.final_status == "success" else 1)
