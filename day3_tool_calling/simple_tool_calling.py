import json
import os
from pathlib import Path

from openai import OpenAI


def load_env_file() -> None:
    # 读取当前目录下的 .env 文件，把配置写入环境变量。
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
    # 从环境变量中读取 API 配置，并创建 SDK client。
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
    # 这是今天演示用的“本地工具”。
    # 它不是模型自己执行的，而是由 Python 程序执行。
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


def main() -> None:
    # 先加载配置，再创建模型客户端。
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    # 这段 tools 不是在“执行工具”，而是在“把可用工具声明给模型”。
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
        }
    ]

    # 第一次请求：
    # 目标不是拿最终答案，而是看看模型会不会决定调用工具。
    first_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一位 Agent 学习规划助手，必要时请调用工具后再回答。",
            },
            {
                "role": "user",
                "content": (
                    "我是零基础，想学习 Agent 开发。"
                    "请先判断我的等级，并给我一个适合我的下一步学习建议。"
                ),
            },
        ],
        tools=tools,
        tool_choice="auto",
    )

    # 取出模型第一轮返回的消息对象。
    message = first_response.choices[0].message

    print("Model:", model)
    print("First response finish reason:", first_response.choices[0].finish_reason)
    print("Assistant content before tool call:", message.content)
    print("Tool calls:", message.tool_calls)

    # 如果模型没有触发工具调用，就先提示并退出。
    if not message.tool_calls:
        print()
        print("This model or proxy did not trigger a tool call in this run.")
        print("If this keeps happening, we can switch to a compatibility teaching version.")
        return

    # 读取模型请求调用的工具名和参数。
    tool_call = message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    print()
    print("Tool selected by model:", tool_name)
    print("Tool arguments:")
    print(json.dumps(tool_args, ensure_ascii=False, indent=2))

    # 这里做一个最小校验，确保模型调用的是我们预期的工具。
    if tool_name != "get_learning_plan_by_level":
        raise RuntimeError(f"Unexpected tool name: {tool_name}")

    # 真正执行工具的是 Python 代码，不是模型。
    tool_result = get_learning_plan_by_level(tool_args["level"])

    print()
    print("Tool result:")
    print(json.dumps(tool_result, ensure_ascii=False, indent=2))

    # 第二次请求：
    # 把“模型刚才发起的工具调用”和“工具执行结果”一起发回模型，
    # 让模型基于工具结果生成最终答案。
    second_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一位 Agent 学习规划助手，必要时请调用工具后再回答。",
            },
            {
                "role": "user",
                "content": (
                    "我是零基础，想学习 Agent 开发。"
                    "请先判断我的等级，并给我一个适合我的下一步学习建议。"
                ),
            },
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": message.tool_calls,
            },
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            },
        ],
    )

    # 这一次拿到的才是最终给用户看的自然语言答案。
    final_text = second_response.choices[0].message.content or ""

    print()
    print("Final answer after tool result:")
    print(final_text)


if __name__ == "__main__":
    main()
