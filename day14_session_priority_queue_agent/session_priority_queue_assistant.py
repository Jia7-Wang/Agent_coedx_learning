import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from openai import OpenAI


# 这些关键词用于最小版知识库检索打分。
# 问题和知识块里同时出现的关键词越多，相关性分数就越高。
KEYWORDS = [
    "Agent",
    "Git",
    "Docker",
    "项目",
    "RAG",
    "工作流",
    "工具",
    "状态",
    "工程",
    "history",
    "session",
    "持久化",
    "多会话",
    "路由",
    "优先级",
]


def load_env_file() -> None:
    # 约定把 .env 放在当前脚本同目录。
    env_path = Path(__file__).with_name(".env")
    # 如果没有 .env，就直接返回，后面继续尝试从系统环境变量读取。
    if not env_path.exists():
        return

    # 按行读取 .env 内容。
    for line in env_path.read_text(encoding="utf-8").splitlines():
        # 去掉每行首尾空白。
        line = line.strip()
        # 空行、注释行、或者不含等号的行都跳过。
        if not line or line.startswith("#") or "=" not in line:
            continue

        # 只按第一个等号切分，避免 value 里再出现等号时被切坏。
        key, value = line.split("=", 1)
        # 只在当前环境变量还没设置时才写入，避免覆盖外部显式传入的值。
        os.environ.setdefault(key.strip(), value.strip())


def build_client() -> OpenAI:
    # 读取 API Key。
    api_key = os.getenv("OPENAI_API_KEY")
    # 读取可选的 Base URL，方便你接中转 API。
    base_url = os.getenv("OPENAI_BASE_URL")

    # 没有 API Key 就直接报错，提醒先配置 .env。
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Copy .env.example to .env and fill in your real key."
        )

    # 先准备最基础的 client 参数。
    client_kwargs = {"api_key": api_key}
    # 如果配置了 base_url，就一并传给 OpenAI 客户端。
    if base_url:
        client_kwargs["base_url"] = base_url

    # 返回一个已经配置好的客户端对象。
    return OpenAI(**client_kwargs)


def now_text() -> str:
    # 生成当前时间的 ISO 字符串，并去掉微秒，输出更整洁。
    return datetime.now().replace(microsecond=0).isoformat()


def sessions_dir() -> Path:
    # 返回 sessions 目录路径，所有 session 的状态文件都放在这里。
    return Path(__file__).with_name("sessions")


def available_session_ids() -> list[str]:
    # 找出 sessions 目录下所有 json 文件，并按文件名排序。
    session_files = sorted(sessions_dir().glob("*.json"))
    # 取文件名去掉 .json 后缀，得到 session_id 列表。
    return [path.stem for path in session_files]


def session_file_path(session_id: str) -> Path:
    # 把 session_id 映射成对应状态文件路径。
    # 例如 demo-python-agent -> sessions/demo-python-agent.json
    return sessions_dir() / f"{session_id}.json"


def load_session_state(session_id: str) -> dict:
    # 根据 session_id 读出对应 json 文件，并反序列化成 Python 字典。
    return json.loads(session_file_path(session_id).read_text(encoding="utf-8"))


def save_session_state(session_id: str, state: dict) -> None:
    # 先拿到这个 session 对应的正式状态文件路径。
    state_path = session_file_path(session_id)
    # 先把 Python 字典转成完整 JSON 文本。
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    # 先把临时文件路径设为空，方便 finally 里判断是否需要清理。
    temp_path: Path | None = None

    try:
        # 在正式文件同目录下创建一个临时文件，避免直接覆盖正式文件。
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            # 不自动删除，因为后面还要用它替换正式文件。
            delete=False,
            # 临时文件放在同目录，后续 replace 更稳妥。
            dir=state_path.parent,
            # 给临时文件加上更易识别的前缀。
            prefix=f"{state_path.stem}_",
            # 临时文件后缀统一用 .tmp。
            suffix=".tmp",
        ) as temp_file:
            # 把完整 JSON 内容写入临时文件。
            temp_file.write(payload)
            # 把 Python 缓冲区的内容推给操作系统。
            temp_file.flush()
            # 尽量确保操作系统也把内容刷到磁盘。
            os.fsync(temp_file.fileno())
            # 记录临时文件路径，后面用于原子替换。
            temp_path = Path(temp_file.name)

        # 用已经写好的临时文件，一次性替换正式文件。
        # 这是这个最小版“原子写回”的核心。
        os.replace(temp_path, state_path)
    finally:
        # 如果临时文件还残留着，就删掉，避免留下垃圾 .tmp 文件。
        if temp_path and temp_path.exists():
            temp_path.unlink()


def build_session_overview(state: dict) -> dict:
    # 尝试取出 history，没有就给空列表。
    history = state.get("history", [])
    # 如果有 history，就取最后一条的 history_note 作为最近进展摘要。
    last_history_note = history[-1]["history_note"] if history else None

    # 这里只返回“概览信息”，而不是完整 state。
    # 这样更适合做全局排序和路由。
    return {
        "session_id": state["session_id"],
        "goal": state["goal"],
        "current_stage": state["current_stage"],
        "current_blocker": state["current_blocker"],
        "history_count": len(history),
        "last_history_note": last_history_note,
    }


def load_all_session_overviews() -> list[dict]:
    # 准备收集所有 session 的概览。
    overviews = []
    # 遍历当前所有可用的 session_id。
    for session_id in available_session_ids():
        # 读取这个 session 的完整状态。
        state = load_session_state(session_id)
        # 把完整状态压缩成概览信息后加入列表。
        overviews.append(build_session_overview(state))
    # 返回所有 session 的 overview 列表。
    return overviews


def load_knowledge_chunks() -> list[dict]:
    # 本地知识库文件和脚本放在同目录。
    kb_path = Path(__file__).with_name("knowledge_base.txt")
    # 读取知识库全文。
    text = kb_path.read_text(encoding="utf-8")
    # 按空行做最简单分块。
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    # 给每个块补上 chunk_id，方便调试和引用。
    return [{"chunk_id": idx + 1, "text": chunk} for idx, chunk in enumerate(chunks)]


def score_chunk(question: str, chunk_text: str) -> tuple[int, list[str]]:
    # 记录命中了哪些关键词。
    matched_keywords = []
    # 初始化相关性分数。
    score = 0

    # 遍历预设关键词，做最小版关键词重叠打分。
    for word in KEYWORDS:
        # 只有问题和知识块里同时出现这个词，才算命中。
        if word in question and word in chunk_text:
            score += 1
            matched_keywords.append(word)

    # 返回分数和命中的关键词列表。
    return score, matched_keywords


def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    # 先读取所有知识块。
    chunks = load_knowledge_chunks()
    # 用来存放每个块的打分结果。
    scored = []

    # 逐个知识块计算相关性。
    for chunk in chunks:
        score, matched_keywords = score_chunk(query, chunk["text"])
        scored.append(
            {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": score,
                "matched_keywords": matched_keywords,
            }
        )

    # 按分数从高到低排序。
    scored.sort(key=lambda item: item["score"], reverse=True)
    # 只保留前 top_k 个且分数大于 0 的块。
    top_chunks = [item for item in scored[:top_k] if item["score"] > 0]

    # 返回一个结构化检索结果对象。
    return {
        "query": query,
        "top_chunks": top_chunks,
    }


def clean_json_text(text: str) -> str:
    # 去掉首尾空白。
    text = text.strip()
    # 如果模型把 JSON 包在 ```json 代码块里，就去掉头。
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    # 如果只是普通 ``` 代码块，也去掉头。
    elif text.startswith("```"):
        text = text[len("```") :].strip()

    # 如果结尾还有 ```，也去掉。
    if text.endswith("```"):
        text = text[:-3].strip()

    # 返回清洗后的纯 JSON 文本。
    return text


def append_history_record(learner_state: dict, update_plan: dict) -> None:
    # 根据这次更新方案，构造一条新的 history 记录。
    history_record = {
        "step_index": len(learner_state["history"]) + 1,
        "updated_at": now_text(),
        "from_stage": learner_state["current_stage"],
        "to_stage": update_plan["next_stage"],
        "today_action": update_plan["today_action"],
        "short_reason": update_plan["short_reason"],
        "history_note": update_plan["history_note"],
    }
    # 追加进当前 session 的 history 列表。
    learner_state["history"].append(history_record)


def main() -> None:
    # 先加载 .env，让脚本能读取 API 配置。
    load_env_file()

    # 从环境变量读取模型名，没有就用默认值。
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    # 创建 OpenAI 客户端。
    client = build_client()

    # 先读取所有 session 的概览，作为“全局排序输入”。
    session_overviews = load_all_session_overviews()

    # 打印当前所有 session 概览，方便观察排序输入。
    print("Available sessions:")
    print(json.dumps(session_overviews, ensure_ascii=False, indent=2))
    print()

    # 定义可供模型调用的本地工具。
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "在本地知识库中检索与 session 优先级、路由、排序相关的文本块",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "用于检索知识库的问题或关键词",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    # 第一轮：先把所有 session 概览交给模型。
    # 这轮的目标不是直接更新，而是看模型是否需要先检索知识库。
    first_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会管理多个学习 session 并生成优先级队列的助理 Agent。"
                    "如果需要知识库支持，请先调用工具检索。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "下面是当前所有学习 session 的概览。"
                    "请先获取必要知识，再输出一个当前优先级队列：\n\n"
                    f"{json.dumps(session_overviews, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
        tools=tools,
        tool_choice="auto",
    )

    # 取出第一轮返回的消息对象。
    message = first_response.choices[0].message

    # 打印第一轮的模型信息和是否触发工具调用。
    print("Model:", model)
    print("First response finish reason:", first_response.choices[0].finish_reason)
    print("Tool calls:", message.tool_calls)
    print()

    # 收集后续要传回给模型的 tool 消息。
    tool_messages = []
    # 收集工具真正执行后的结果，方便打印调试。
    tool_results = []

    # 遍历模型请求的所有工具调用。
    for tool_call in message.tool_calls or []:
        # 取出工具名。
        tool_name = tool_call.function.name
        # 解析模型传入的 JSON 参数。
        tool_args = json.loads(tool_call.function.arguments)

        # 当前脚本只允许调用 search_knowledge_base。
        if tool_name != "search_knowledge_base":
            raise RuntimeError(f"Unexpected tool name: {tool_name}")

        # 真正执行本地知识库检索函数。
        tool_result = search_knowledge_base(tool_args["query"])
        # 保存结果，方便打印。
        tool_results.append(tool_result)
        # 构造符合 chat completions 协议的 tool 消息，第二轮要传回模型。
        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            }
        )

    # 如果确实检索到了工具结果，就打印出来。
    if tool_results:
        print("Knowledge tool result:")
        print(json.dumps(tool_results, ensure_ascii=False, indent=2))
        print()
    else:
        # 如果这次没触发检索，也给出明确提示。
        print("Knowledge tool result: []")
        print("This run did not trigger retrieval, so the model will continue with current overviews only.")
        print()

    # 第二轮：让模型基于 session 概览 + 工具结果，输出完整优先级队列。
    queue_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会在多个学习 session 之间输出优先级队列的助理 Agent。"
                    "请基于 session 概览和检索结果，严格返回合法 JSON。"
                    "不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请从这些 session 概览中输出一个优先级队列 JSON。\n\n"
                    "字段要求：\n"
                    '- priority_queue: 数组，按优先级从高到低排列，每个元素包含 session_id 和 reason\n'
                    '- top_focus: 字符串，表示当前最优先队列项应关注什么\n\n'
                    f"session 概览：\n{json.dumps(session_overviews, ensure_ascii=False, indent=2)}"
                ),
            },
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": message.tool_calls,
            },
            *tool_messages,
        ],
    )

    # 取出第二轮文本，并解析成结构化 queue_plan。
    queue_plan = json.loads(clean_json_text(queue_response.choices[0].message.content or ""))

    # 打印完整优先级队列。
    print("Priority queue:")
    print(json.dumps(queue_plan, ensure_ascii=False, indent=2))
    print()

    # 取出队列第一名的 session_id。
    top_session_id = queue_plan["priority_queue"][0]["session_id"]
    # 加载这个最高优先级 session 的完整状态。
    learner_state = load_session_state(top_session_id)

    # 打印最高优先级 session 的原始状态。
    print("Top priority learner state before update:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    # 第三轮：只针对队列第一名 session，生成具体状态更新方案。
    update_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会推进单个学习 session 状态的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "你已经拿到了一个 session 优先级队列，并准备推进当前最高优先级的 session。"
                    "请根据该 session 当前状态和队列结论，输出状态更新 JSON。\n\n"
                    "字段要求：\n"
                    '- today_action: 字符串，表示今天最该做的一件事\n'
                    '- next_stage: 字符串，表示下一阶段名称\n'
                    '- short_reason: 字符串，简要说明为什么这样更新\n'
                    '- history_note: 字符串，表示这次更新应该记入 history 的一句话摘要\n\n'
                    f"优先级队列：\n{json.dumps(queue_plan, ensure_ascii=False, indent=2)}\n\n"
                    f"当前最高优先级 session 状态：\n{json.dumps(learner_state, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    # 解析第三轮返回的结构化更新方案。
    update_plan = json.loads(clean_json_text(update_response.choices[0].message.content or ""))

    # 打印本次对 top 1 session 的更新计划。
    print("Structured update plan:")
    print(json.dumps(update_plan, ensure_ascii=False, indent=2))
    print()

    # 先把本次更新追加到 history。
    append_history_record(learner_state, update_plan)
    # 再把几个关键状态字段更新成最新值。
    learner_state["today_action"] = update_plan["today_action"]
    learner_state["next_stage"] = update_plan["next_stage"]
    learner_state["current_stage"] = update_plan["next_stage"]

    # 把更新后的 top 1 session 原子写回到它自己的状态文件。
    save_session_state(top_session_id, learner_state)

    # 打印更新后的完整状态。
    print("Updated learner state:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    # 最后给出成功提示，说明已完成原子写回。
    print("Top priority session persisted to file successfully with atomic write.")


if __name__ == "__main__":
    # 直接运行脚本时，从 main() 入口开始。
    main()
