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


def ask_for_json(client: OpenAI, model: str, system_text: str, user_text: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ],
    )

    raw_text = response.choices[0].message.content or ""
    return json.loads(clean_json_text(raw_text))


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    # 这是多步循环工作流里的共享状态对象。
    state = {
        "user_goal": "我想在4周内做出一个能调用工具的简单 Agent Demo，并补一点 Git 和 Docker 基础。",
        "current_step": "break_down_goal",
        "subtasks": [],
        "execution_order": [],
        "week1_plan": [],
        "next_action": None,
    }

    print("Initial state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print()

    # 第 1 步：拆解目标
    if state["current_step"] == "break_down_goal":
        result = ask_for_json(
            client=client,
            model=model,
            system_text=(
                "你是一位严谨的任务拆解助手。"
                "请只返回合法 JSON，不要输出 markdown，不要输出解释。"
            ),
            user_text=(
                "请根据下面的学习目标拆解 4 到 6 个子任务，并严格返回 JSON。\n\n"
                "字段要求：\n"
                '- subtasks: 字符串数组\n'
                '- next_action: 字符串\n\n'
                f"学习目标：{state['user_goal']}"
            ),
        )

        print("Step 1 result - task breakdown:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

        state["subtasks"] = result["subtasks"]
        state["next_action"] = result["next_action"]
        state["current_step"] = "suggest_execution_order"

        print("State after step 1:")
        print(json.dumps(state, ensure_ascii=False, indent=2))
        print()

    # 第 2 步：根据 subtasks 排执行顺序
    if state["current_step"] == "suggest_execution_order":
        result = ask_for_json(
            client=client,
            model=model,
            system_text=(
                "你是一位工作流规划助手。"
                "请只返回合法 JSON，不要输出 markdown，不要输出解释。"
            ),
            user_text=(
                "下面是当前任务状态，请根据它给出推荐执行顺序，并严格返回 JSON。\n\n"
                "字段要求：\n"
                '- execution_order: 字符串数组\n'
                '- next_action: 字符串\n\n'
                f"{json.dumps(state, ensure_ascii=False, indent=2)}"
            ),
        )

        print("Step 2 result - execution order:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

        state["execution_order"] = result["execution_order"]
        state["next_action"] = result["next_action"]
        state["current_step"] = "plan_week1"

        print("State after step 2:")
        print(json.dumps(state, ensure_ascii=False, indent=2))
        print()

    # 第 3 步：根据 execution_order 生成第一周计划
    if state["current_step"] == "plan_week1":
        result = ask_for_json(
            client=client,
            model=model,
            system_text=(
                "你是一位学习计划助手。"
                "请只返回合法 JSON，不要输出 markdown，不要输出解释。"
            ),
            user_text=(
                "下面是当前任务状态，请根据它生成第一周计划，并严格返回 JSON。\n\n"
                "字段要求：\n"
                '- week1_plan: 字符串数组\n'
                '- next_action: 字符串\n\n'
                f"{json.dumps(state, ensure_ascii=False, indent=2)}"
            ),
        )

        print("Step 3 result - week 1 plan:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()

        state["week1_plan"] = result["week1_plan"]
        state["next_action"] = result["next_action"]
        state["current_step"] = "done"

        print("Final state:")
        print(json.dumps(state, ensure_ascii=False, indent=2))
        print()

    print("Workflow summary:")
    print(f"Current step: {state['current_step']}")
    print(f"Next action: {state['next_action']}")


if __name__ == "__main__":
    main()
