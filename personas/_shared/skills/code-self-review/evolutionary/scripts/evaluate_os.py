import argparse
import json
import os
from pathlib import Path


def evaluate_os(os_path: Path) -> dict:
    skill_dir = os_path.parent
    workflows_dir = skill_dir / "workflows"
    resources_dir = skill_dir / "resources"

    required_workflows = [
        "unit-tests.md",
        "integration-tests.md",
        "lint.md",
        "typecheck.md",
        "build.md",
        "manual-checklist.md",
    ]

    findings = {
        "os_exists": os_path.exists(),
        "workflows_dir_exists": workflows_dir.exists(),
        "resources_dir_exists": resources_dir.exists(),
        "missing_workflows": [],
        "l1_sections": 0,
    }

    if workflows_dir.exists():
        for name in required_workflows:
            if not (workflows_dir / name).exists():
                findings["missing_workflows"].append(name)

    if os_path.exists():
        content = os_path.read_text(encoding="utf-8")
        findings["l1_sections"] = content.count("<L1>")

    recommendations = []
    if findings["missing_workflows"]:
        recommendations.append("Add missing workflow files.")
    if findings["l1_sections"] < 2:
        recommendations.append("Ensure core routing and evolution checks are in L1.")

    return {
        "summary": {
            "status": "pass" if not findings["missing_workflows"] else "warn",
            "l1_sections": findings["l1_sections"],
        },
        "findings": findings,
        "recommendations": recommendations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--os-path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    os_path = Path(args.os_path)
    report = evaluate_os(os_path)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
