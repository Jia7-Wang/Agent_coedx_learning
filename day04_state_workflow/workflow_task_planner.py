import json
import os
from pathlib import Path

from openai import OpenAI


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


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Copy .env.example to .env and fill in your real key."
        )

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAI(**client_kwargs)


def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    # 这是今天的“状态对象”。
    # 它不是给模型看的单纯文本，而是程序自己维护的任务中间信息。
    state = {
        "user_goal": "我想在4周内做出一个能调用工具的简单 Agent Demo，并补一点 Git 和 Docker 基础。",
        "current_step": "break_down_goal",
        "subtasks": [],
        "next_action": None,
    }

    print("Initial state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print()

    # 第一步：让模型根据 user_goal 拆解任务，并返回结构化 JSON。
    breakdown_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位严谨的任务拆解助手。"
                    "请只返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据下面的学习目标拆解 4 到 6 个子任务，并严格返回 JSON。\n\n"
                    "字段要求：\n"
                    '- subtasks: 字符串数组\n'
                    '- next_action: 字符串\n\n'
                    f"学习目标：{state['user_goal']}"
                ),
            },
        ],
    )

    raw_text = breakdown_response.choices[0].message.content or ""
    parsed = json.loads(clean_json_text(raw_text))

    print("Task breakdown:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    print()

    # 第二步：程序把模型拆出的内容写回状态对象。
    state["subtasks"] = parsed["subtasks"]
    state["next_action"] = parsed["next_action"]
    state["current_step"] = "suggest_execution_order"

    print("Updated state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print()

    # 第三步：把更新后的 state 再交给模型，让它基于当前状态给下一步执行建议。
    suggestion_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位工作流规划助手。"
                    "请根据给定 state，给出简洁清晰的下一步执行建议。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "下面是当前任务状态，请根据它给我下一步执行建议：\n\n"
                    f"{json.dumps(state, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    final_text = suggestion_response.choices[0].message.content or ""

    print("Next action suggestion:")
    print(final_text)


if __name__ == "__main__":
    main()
