import os
from pathlib import Path


def load_env_file() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_env_file()

    owner_name = os.getenv("OWNER_NAME", "Agent learner")
    project_stage = os.getenv("PROJECT_STAGE", "day21-git-basics")

    tasks = [
        "Run git status first",
        "Edit one line in this file",
        "Run git diff",
        "Stage only this file",
        "Commit with a clear message",
    ]

    print("Day 21 Git Basics Lab")
    print(f"Owner: {owner_name}")
    print(f"Stage: {project_stage}")
    print("Tasks:")
    print("-" * 20)

    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")


if __name__ == "__main__":
    main()
