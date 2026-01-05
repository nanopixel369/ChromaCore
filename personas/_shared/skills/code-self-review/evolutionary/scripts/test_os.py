import argparse
from pathlib import Path


def assert_file(path: Path, label: str) -> list[str]:
    return [] if path.exists() else [f"Missing {label}: {path}"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[2]
    errors = []

    os_path = skill_dir / "SKILL.md"
    workflows_dir = skill_dir / "workflows"
    resources_dir = skill_dir / "resources"

    errors += assert_file(os_path, "OS skill")
    errors += assert_file(workflows_dir, "workflows directory")
    errors += assert_file(resources_dir, "resources directory")

    required_workflows = [
        "unit-tests.md",
        "integration-tests.md",
        "lint.md",
        "typecheck.md",
        "build.md",
        "manual-checklist.md",
    ]

    for name in required_workflows:
        path = workflows_dir / name
        errors += assert_file(path, f"workflow {name}")
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "<L1>" not in content:
                errors.append(f"Workflow missing L1 section: {name}")
            if "Closeout" not in content:
                errors.append(f"Workflow missing Closeout section: {name}")

    if errors:
        raise SystemExit("\n".join(errors))

    if args.verbose:
        print("All checks passed.")


if __name__ == "__main__":
    main()
