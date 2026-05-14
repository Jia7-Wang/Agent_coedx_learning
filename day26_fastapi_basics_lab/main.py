"""Minimal FastAPI app for Day 26.

This lab focuses on the smallest useful service shape:
- one root route
- one /health route
"""

from __future__ import annotations


def _missing_dependency_message(package_name: str) -> str:
    return (
        f"Missing dependency: {package_name}. "
        "Install the Day 26 dependencies with "
        "`pip install -r .\\day26_fastapi_basics_lab\\requirements.txt`."
    )


try:
    from fastapi import FastAPI
except ModuleNotFoundError as exc:  # pragma: no cover - friendly local setup path
    raise SystemExit(_missing_dependency_message("fastapi")) from exc


app = FastAPI(
    title="Day 26 FastAPI Basics Lab",
    description="A minimal FastAPI service with root and health endpoints.",
    version="1.0.0",
)


@app.get("/")
def read_root() -> dict[str, object]:
    return {
        "message": "Day 26 FastAPI basics lab is running.",
        "focus": "Learn routing, request/response flow, and a minimal API service.",
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "day26-fastapi-basics-lab",
    }


if __name__ == "__main__":
    try:
        import uvicorn
    except ModuleNotFoundError as exc:  # pragma: no cover - friendly local setup path
        raise SystemExit(_missing_dependency_message("uvicorn")) from exc

    uvicorn.run(
        "day26_fastapi_basics_lab.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
