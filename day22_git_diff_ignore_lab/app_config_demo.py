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

    app_name = os.getenv("APP_NAME", "day22-git-diff-ignore-lab")
    owner_name = os.getenv("OWNER_NAME", "Agent learner")
    log_level = os.getenv("LOG_LEVEL", "info")

    print("Day 22 Git Diff And Ignore Lab")
    print(f"App: {app_name}")
    print(f"Owner: {owner_name}")
    print(f"Log level: {log_level}")
    print("Focus:")
    print("1. Check unstaged changes with git diff")
    print("2. Check staged changes with git diff --staged")
    print("3. Verify .env is ignored")
    print("4. Verify .env is not tracked by git")


if __name__ == "__main__":
    main()
