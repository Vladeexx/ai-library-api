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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MEMORY_DIR = Path(__file__).parent.parent / "memory"
RUN_HISTORY = MEMORY_DIR / "run_history.jsonl"
KNOWN_FAILURES_FILE = MEMORY_DIR / "known_failures.json"
SUCCESSFUL_PATTERNS_FILE = MEMORY_DIR / "successful_patterns.json"
TEST_COMMAND = "make test"


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log(agent: str, message: str) -> None:
    print(f"[{agent}] {message}")


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def orchestrator(goal: str) -> dict:
    log("orchestrator", f"received goal: {goal!r}")
    plan = planner(goal)
    build_result = builder(plan)
    passed, steps_executed = tester(build_result)
    if not passed:
        steps_executed = fixer(steps_executed)
    status = skill_curator(
        goal=goal,
        passed=passed,
        steps_executed=steps_executed,
        plan_type=plan["plan_type"],
        builder_status=build_result["builder_status"],
        skill_used=build_result["skill_used"],
    )
    log("orchestrator", f"run complete — status: {status}")
    return {"status": status, "steps_executed": steps_executed}


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


def planner(goal: str) -> dict:
    history = _load_run_history()
    prior_runs = [e for e in history if e.get("goal") == goal]
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

    keywords = goal.lower()

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

    relevant_patterns = _find_relevant_patterns(goal, plan_type)
    plan = {
        "goal": goal,
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
    return plan


SKILL_MAP = {
    "crud_endpoint": "add_crud_endpoint",
    "migration": "add_alembic_migration",
    "generic": None,
}

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills" / "coding"


def builder(plan: dict) -> dict:
    log("builder", "starting execution")

    if plan.get("preferred_skill"):
        skill = plan["preferred_skill"]
        log("builder", f"reusing preferred skill from memory: {skill}")
    else:
        skill = SKILL_MAP.get(plan["plan_type"])
        if skill:
            log("builder", f"using default skill: {skill}")
        else:
            log("builder", "no specific skill for this plan type")

    if skill:
        skill_file = SKILLS_DIR / f"{skill}.md"
        if skill_file.exists():
            skill_file.read_text()
            log("builder", f"loaded skill definition for {skill}")
        else:
            log("builder", "skill definition file not found")

    steps = plan["steps"]
    total = len(steps)
    executed_steps = []
    for i, step in enumerate(steps, start=1):
        log("builder", f"step {i}/{total}: {step}")
        executed_steps.append(step)
    return {
        "plan": plan,
        "executed_steps": executed_steps,
        "builder_status": "completed",
        "skill_used": skill,
    }


def tester(build_result: dict) -> tuple[bool, list[str]]:
    steps = build_result["executed_steps"]
    log("tester", f"running real test suite: {TEST_COMMAND!r}")

    result = subprocess.run(
        TEST_COMMAND,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())

    passed = result.returncode == 0
    if passed:
        log("tester", "tests passed")
    else:
        log("tester", f"tests FAILED (exit code {result.returncode})")

    return passed, steps


def fixer(steps_executed: list[str]) -> list[str]:
    log("fixer", "tests failed — a fix would be attempted here in a future phase")
    return steps_executed + ["fix attempted"]


def skill_curator(
    goal: str,
    passed: bool,
    steps_executed: list[str],
    plan_type: str,
    builder_status: str,
    skill_used: Optional[str],
) -> str:
    status = "success" if passed else "failed"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "plan_type": plan_type,
        "builder_status": builder_status,
        "skill_used": skill_used,
        "status": status,
        "steps_executed": steps_executed,
        "test_command": TEST_COMMAND,
        "test_passed": passed,
    }
    with RUN_HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    log("skill_curator", f"run recorded to memory/run_history.jsonl (status: {status})")
    return status


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflows/improvement_loop.py \"<goal>\"")
        sys.exit(1)

    goal = sys.argv[1]
    orchestrator(goal)
