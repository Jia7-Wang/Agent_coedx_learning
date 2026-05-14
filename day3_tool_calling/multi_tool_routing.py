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


def get_learning_plan_by_level(level: str) -> dict:
    plans = {
        "beginner": {
            "focus": "Python, API basics, structured output, tool calling",
            "next_action": "从单 Agent 和小工具开始练习",
        },
        "intermediate": {
            "focus": "RAG, workflow, state management, evaluation",
            "next_action": "开始做有状态的业务 Agent",
        },
        "advanced": {
            "focus": "multi-agent orchestration, guardrails, production deployment",
            "next_action": "优化架构并建立评测与监控体系",
        },
    }
    return plans.get(
        level,
        {
            "focus": "clarify user level first",
            "next_action": "请先确认学习者等级",
        },
    )


def get_engineering_basics_topics() -> dict:
    return {
        "topics": [
            "Git 基础与分支协作",
            "日志与调试",
            "项目目录结构",
            "API 联调基础",
            "Docker 基础",
        ],
        "reason": "这些内容能帮助学习者更快进入真实公司项目。",
    }


def run_tool(tool_name: str, tool_args: dict) -> dict:
    if tool_name == "get_learning_plan_by_level":
        return get_learning_plan_by_level(tool_args["level"])

    if tool_name == "get_engineering_basics_topics":
        return get_engineering_basics_topics()

    raise RuntimeError(f"Unexpected tool name: {tool_name}")


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    user_request = (
        "我是零基础，想学习 Agent 开发，并且希望学习过程中穿插公司项目常识，"
        "比如 Git、调试和 Docker。请给我一个适合的下一步建议。"
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_learning_plan_by_level",
                "description": "根据学习者等级返回对应的 Agent 学习建议",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "description": "学习者当前等级",
                        }
                    },
                    "required": ["level"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_engineering_basics_topics",
                "description": "返回适合 Agent 学习者同步补充的工程协作基础主题",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]

    first_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位 Agent 学习规划助手。"
                    "如果用户既需要学习路线，又提到了公司项目常识，"
                    "请按需要选择最合适的工具。"
                ),
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        tools=tools,
        tool_choice="auto",
    )

    message = first_response.choices[0].message

    print("Model:", model)
    print("First response finish reason:", first_response.choices[0].finish_reason)
    print("Assistant content before tool call:", message.content)
    print("Tool calls:", message.tool_calls)

    if not message.tool_calls:
        print()
        print("This model or proxy did not trigger a tool call in this run.")
        print("If needed, we can add a compatibility fallback version.")
        return

    tool_messages = []

    print()
    print("Selected tools:")

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        raw_args = tool_call.function.arguments or "{}"
        tool_args = json.loads(raw_args)
        tool_result = run_tool(tool_name, tool_args)

        print("-", tool_name)
        print("  arguments:", json.dumps(tool_args, ensure_ascii=False))
        print("  result:", json.dumps(tool_result, ensure_ascii=False))

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            }
        )

    second_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位 Agent 学习规划助手。"
                    "如果用户既需要学习路线，又提到了公司项目常识，"
                    "请按需要选择最合适的工具。"
                ),
            },
            {
                "role": "user",
                "content": user_request,
            },
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": message.tool_calls,
            },
            *tool_messages,
        ],
    )

    final_text = second_response.choices[0].message.content or ""

    print()
    print("Final answer after tool routing:")
    print(final_text)


if __name__ == "__main__":
    main()
