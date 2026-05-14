import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI


# 工具参数里允许出现的学习等级。
VALID_LEVELS = {"beginner", "intermediate", "advanced"}


def log_event(event: str, **data: object) -> None:
    # 统一日志出口。
    # 这里把日志打印成 JSON，方便后续程序读取、筛选和分析。
    payload = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "data": data,
    }
    print(json.dumps(payload, ensure_ascii=False))


def load_env_file() -> None:
    # 从当前脚本所在目录读取 .env 文件。
    # 这样运行脚本时，不需要你手动 export 环境变量。
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    # 按行读取 .env 文件内容。
    for line in env_path.read_text(encoding="utf-8").splitlines():
        # 去掉每行两端空白字符。
        line = line.strip()

        # 跳过空行、注释行和不符合 key=value 的行。
        if not line or line.startswith("#") or "=" not in line:
            continue

        # 只在第一个 = 处分割，避免 value 中再出现 = 时出错。
        key, value = line.split("=", 1)

        # 如果环境变量还没设置，就把 .env 中的值写进去。
        os.environ.setdefault(key.strip(), value.strip())


def build_client() -> OpenAI:
    # 从环境变量读取 API Key 和中转地址。
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    # 没有 API Key 就直接报错，不继续运行。
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Copy .env.example to .env and fill in your real key."
        )

    # 先准备最基础的 client 参数。
    client_kwargs = {"api_key": api_key}

    # 如果配置了中转地址，就把它一起传给 SDK。
    if base_url:
        client_kwargs["base_url"] = base_url

    # 返回 OpenAI 客户端实例。
    return OpenAI(**client_kwargs)


def get_learning_plan_by_level(level: str) -> dict:
    # 本地工具 1：
    # 根据学习者等级，返回对应学习建议。
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

    # 这里直接按 key 取值。
    # 如果 level 不合法，前面的参数校验会先拦住，不会跑到这里。
    return plans[level]


def get_engineering_basics_topics() -> dict:
    # 本地工具 2：
    # 返回适合初学者同步补充的工程基础主题。
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


def validate_tool_args(tool_name: str, tool_args: dict) -> None:
    # 这个函数负责校验“模型给出的工具参数”是否合法。
    # 真实项目里不能默认模型传的参数一定正确。

    if tool_name == "get_learning_plan_by_level":
        # 取出 level 参数。
        level = tool_args.get("level")

        # 要求 level 必须是字符串。
        if not isinstance(level, str):
            raise ValueError("Argument 'level' must be a string.")

        # 要求 level 必须在允许值范围里。
        if level not in VALID_LEVELS:
            raise ValueError(
                f"Argument 'level' must be one of {sorted(VALID_LEVELS)}."
            )

        return

    if tool_name == "get_engineering_basics_topics":
        # 这个工具不需要参数。
        # 如果模型传了奇怪的参数，也要拦住。
        if tool_args not in ({}, None):
            raise ValueError("This tool does not require arguments.")

        return

    # 如果工具名本身就不认识，直接报错。
    raise ValueError(f"Unknown tool name: {tool_name}")


def run_tool(tool_name: str, tool_args: dict) -> dict:
    # 先做参数校验，确保工具在安全输入下运行。
    validate_tool_args(tool_name, tool_args)

    # 根据工具名路由到对应的 Python 函数。
    if tool_name == "get_learning_plan_by_level":
        return get_learning_plan_by_level(tool_args["level"])

    if tool_name == "get_engineering_basics_topics":
        return get_engineering_basics_topics()

    # 理论上不会走到这里，因为 validate_tool_args 已经挡过一次。
    raise RuntimeError(f"Unexpected tool name: {tool_name}")


def safe_parse_arguments(raw_args: str) -> dict:
    # 负责把模型返回的工具参数字符串解析成 Python 字典。
    try:
        # 如果 raw_args 为空，就按空对象处理。
        parsed = json.loads(raw_args or "{}")
    except json.JSONDecodeError as exc:
        # 如果 JSON 格式不合法，转成更清晰的业务错误。
        raise ValueError(f"Tool arguments are not valid JSON: {raw_args}") from exc

    # 我们要求参数解析后必须是一个 JSON 对象，也就是 Python dict。
    if not isinstance(parsed, dict):
        raise ValueError("Tool arguments must parse to a JSON object.")

    return parsed


def build_tools() -> list[dict]:
    # 这个函数负责把“可用工具声明”整理出来。
    # 注意：这里不是执行工具，而是在告诉模型“你可以用哪些工具”。
    return [
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


def main() -> None:
    # 第一步：加载 .env 配置。
    load_env_file()

    # 第二步：读取模型名。
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # 第三步：创建模型客户端。
    client = build_client()

    # 第四步：准备工具清单。
    tools = build_tools()

    # 这是给模型的用户需求。
    user_request = (
        "我是零基础，想学习 Agent 开发，并且希望学习过程中穿插公司项目常识，"
        "比如 Git、调试和 Docker。请给我一个适合的下一步建议。"
    )

    # 记录一次请求开始日志。
    log_event("request.start", model=model)

    # 第一次模型请求：
    # 让模型先看问题和工具清单，决定要不要调工具。
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

    # 取出第一轮模型消息。
    message = first_response.choices[0].message

    # 记录第一轮响应结果。
    log_event(
        "response.first",
        finish_reason=first_response.choices[0].finish_reason,
        tool_calls_count=len(message.tool_calls or []),
    )

    # 如果模型没有发起工具调用，就记录并结束。
    if not message.tool_calls:
        log_event("response.no_tool_calls")
        print("模型本轮没有触发工具调用。")
        return

    # 这个列表用来保存之后要回传给模型的 tool 消息。
    tool_messages = []

    # 这个列表用来记录本轮工具执行中出现的错误。
    tool_errors = []

    # 遍历模型请求的每一个工具调用。
    for tool_call in message.tool_calls:
        # 取出工具名。
        tool_name = tool_call.function.name

        # 取出工具原始参数字符串；如果为空就按空对象处理。
        raw_args = tool_call.function.arguments or "{}"

        # 先记录“模型请求了哪个工具、给了什么原始参数”。
        log_event("tool.requested", tool_name=tool_name, raw_args=raw_args)

        try:
            # 先把参数字符串解析成 Python 字典。
            tool_args = safe_parse_arguments(raw_args)

            # 再真正执行工具。
            tool_result = run_tool(tool_name, tool_args)

            # 记录工具成功日志。
            log_event(
                "tool.success",
                tool_name=tool_name,
                tool_args=tool_args,
                tool_result=tool_result,
            )

            # 如果工具成功，把结果包装成统一格式回传给模型。
            tool_content = json.dumps(
                {
                    "ok": True,
                    "result": tool_result,
                },
                ensure_ascii=False,
            )
        except Exception as exc:
            # 如果工具失败，不让程序直接崩掉，而是记录错误并继续。
            error_text = str(exc)

            # 把错误记到总错误列表里。
            tool_errors.append({"tool_name": tool_name, "error": error_text})

            # 记录工具失败日志。
            log_event("tool.error", tool_name=tool_name, error=error_text)

            # 把失败信息也作为 tool 消息返回模型。
            # 这样模型可以知道某个工具失败了，并尽量基于其他成功结果继续回答。
            tool_content = json.dumps(
                {
                    "ok": False,
                    "error": error_text,
                },
                ensure_ascii=False,
            )

        # 把每个工具的执行结果包装成 role=tool 的消息，后面统一发回模型。
        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_content,
            }
        )

    # 第二次模型请求：
    # 把“模型刚才发起的工具调用”以及“工具执行结果”一起发回模型，
    # 让模型基于工具结果生成最终面向用户的答案。
    second_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位 Agent 学习规划助手。"
                    "请结合工具结果给出清晰建议。"
                    "如果某个工具失败了，要如实说明，并尽量基于成功结果继续回答。"
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

    # 取出最终文本答案。
    final_text = second_response.choices[0].message.content or ""

    # 记录最终响应日志。
    # 这里保留工具错误列表和最终答案预览，方便排查。
    log_event(
        "response.final",
        tool_errors=tool_errors,
        final_text_preview=final_text[:120],
    )

    # 打印最终回答给用户看。
    print()
    print("Final answer:")
    print(final_text)


# Python 脚本直接运行时，从这里进入主流程。
if __name__ == "__main__":
    main()
