import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from openai import OpenAI


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
]


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


def now_text() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def state_file_path() -> Path:
    return Path(__file__).with_name("state.json")


def build_default_state() -> dict:
    return {
        "session_id": "day11-persistent-session",
        "goal": "我想在 6 周内做出一个简单 Agent 项目，并且以后能接公司项目。",
        "current_stage": "状态历史记录与可复盘工作流",
        "completed_topics": [
            "模型调用",
            "结构化输出",
            "单工具调用",
            "多工具路由",
            "状态与工作流基础",
            "最小 RAG",
            "知识库 Agent",
            "带状态助理 Agent",
            "状态更新助理 Agent",
            "Session History Agent",
        ],
        "current_blocker": "我知道 history 很重要，但还不清楚怎样让这些状态跨多次运行保留下来。",
        "today_action": "把 state 和 history 从内存对象改成可保存到文件的持久化状态",
        "next_stage": "持久化状态与会话恢复",
        "history": [
            {
                "step_index": 1,
                "updated_at": "2026-05-10T20:30:00",
                "from_stage": "Day 6 到 Day 7 学习中",
                "to_stage": "知识库 Agent 与整合型 Agent",
                "today_action": "跑通知识库检索和工具调用的最小闭环",
                "short_reason": "先把检索和工具调用串起来，后面做带状态助理会更顺。",
                "history_note": "完成了 Day 6 和 Day 7 的核心串联。",
            },
            {
                "step_index": 2,
                "updated_at": "2026-05-11T21:00:00",
                "from_stage": "知识库 Agent 与整合型 Agent",
                "to_stage": "状态自动推进与工作流落地",
                "today_action": "让 Agent 在输出建议后自动写回 state",
                "short_reason": "你已经会读 state，下一步就该学会写 state。",
                "history_note": "状态从只读输入变成了可更新的数据对象。",
            },
            {
                "step_index": 3,
                "updated_at": "2026-05-13T08:08:59",
                "from_stage": "状态自动推进与工作流落地",
                "to_stage": "状态历史记录与可复盘工作流",
                "today_action": "在现有自动更新 state 的最小工作流里新增 history 追加逻辑：每次执行后记录 from_stage、to_stage、today_action、short_reason 和 history_note。",
                "short_reason": "你当前的阻塞点正是缺少更新轨迹；先把 history/session trace 固化下来，才能支持复盘、调试和后续更复杂的工作流推进。",
                "history_note": "在自动写回 state 的基础上，进一步加入了每次状态变更的 history 记录机制。",
            },
        ],
    }


def load_or_create_state() -> tuple[dict, str]:
    state_path = state_file_path()
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        return state, "loaded_from_file"

    state = build_default_state()
    save_state(state)
    return state, "created_default_state"


def save_state(state: dict) -> None:
    # 正式状态文件路径，也就是最终要落盘的 state.json。
    state_path = state_file_path()
    # 先把 Python 字典转成完整 JSON 字符串，后面统一写入临时文件。
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    # 先把临时文件路径设为 None，方便 finally 里判断是否需要清理。
    temp_path: Path | None = None

    try:
        # 在正式文件同目录创建一个临时文件，避免直接覆盖 state.json。
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            # 这里不能自动删除，因为后面还要用它替换正式文件。
            delete=False,
            # 临时文件和正式文件放同一个目录，替换时更稳妥。
            dir=state_path.parent,
            prefix=f"{state_path.stem}_",
            suffix=".tmp",
        ) as temp_file:
            # 先把完整 JSON 内容写入临时文件。
            temp_file.write(payload)
            # 把 Python 缓冲区里的内容立刻推给操作系统。
            temp_file.flush()
            # 尽量确保操作系统也把内容真正刷到磁盘，降低中途断开的风险。
            os.fsync(temp_file.fileno())
            # 记录临时文件路径，后面要用它替换正式文件。
            temp_path = Path(temp_file.name)

        # 临时文件写完后，再一次性替换正式文件，这就是原子写回的核心。
        os.replace(temp_path, state_path)
    finally:
        # 如果临时文件还残留着，就清理掉，避免目录里留下垃圾 .tmp 文件。
        if temp_path and temp_path.exists():
            temp_path.unlink()


def load_knowledge_chunks() -> list[dict]:
    kb_path = Path(__file__).with_name("knowledge_base.txt")
    text = kb_path.read_text(encoding="utf-8")
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return [{"chunk_id": idx + 1, "text": chunk} for idx, chunk in enumerate(chunks)]


def score_chunk(question: str, chunk_text: str) -> tuple[int, list[str]]:
    matched_keywords = []
    score = 0

    for word in KEYWORDS:
        if word in question and word in chunk_text:
            score += 1
            matched_keywords.append(word)

    return score, matched_keywords


def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    chunks = load_knowledge_chunks()
    scored = []

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

    scored.sort(key=lambda item: item["score"], reverse=True)
    top_chunks = [item for item in scored[:top_k] if item["score"] > 0]

    return {
        "query": query,
        "top_chunks": top_chunks,
    }


def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def append_history_record(learner_state: dict, update_plan: dict) -> None:
    history_record = {
        "step_index": len(learner_state["history"]) + 1,
        "updated_at": now_text(),
        "from_stage": learner_state["current_stage"],
        "to_stage": update_plan["next_stage"],
        "today_action": update_plan["today_action"],
        "short_reason": update_plan["short_reason"],
        "history_note": update_plan["history_note"],
    }
    learner_state["history"].append(history_record)


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    learner_state, state_source = load_or_create_state()

    print("State source:", state_source)
    print("State file:", state_file_path())
    print()

    print("Learner state before update:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "在本地知识库中检索与当前学习状态、状态持久化、会话恢复相关的文本块",
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

    first_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会管理持久化学习状态的助理 Agent。"
                    "如果需要知识库支持，请先调用工具检索。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "下面是我从文件恢复出来的当前学习状态。"
                    "请先获取必要知识，再给出下一步的结构化状态更新建议：\n\n"
                    f"{json.dumps(learner_state, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
        tools=tools,
        tool_choice="auto",
    )

    message = first_response.choices[0].message

    print("Model:", model)
    print("First response finish reason:", first_response.choices[0].finish_reason)
    print("Tool calls:", message.tool_calls)
    print()

    tool_messages = []
    tool_results = []

    for tool_call in message.tool_calls or []:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        if tool_name != "search_knowledge_base":
            raise RuntimeError(f"Unexpected tool name: {tool_name}")

        tool_result = search_knowledge_base(tool_args["query"])
        tool_results.append(tool_result)
        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            }
        )

    if tool_results:
        print("Knowledge tool result:")
        print(json.dumps(tool_results, ensure_ascii=False, indent=2))
        print()
    else:
        print("Knowledge tool result: []")
        print("This run did not trigger retrieval, so the model will continue with current state only.")
        print()

    second_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会推进学习状态并维护持久化 session 的助理 Agent。"
                    "请基于当前状态、历史轨迹和检索结果，严格返回合法 JSON。"
                    "不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据当前学习状态、已有 history 和可能的检索结果，输出一个状态更新方案。\n\n"
                    "字段要求：\n"
                    '- today_action: 字符串，表示今天最该做的一件事\n'
                    '- next_stage: 字符串，表示下一阶段名称\n'
                    '- short_reason: 字符串，简要说明为什么这样更新\n'
                    '- history_note: 字符串，表示这次更新应该记入 history 的一句话摘要\n\n'
                    f"当前状态：\n{json.dumps(learner_state, ensure_ascii=False, indent=2)}"
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

    raw_text = second_response.choices[0].message.content or ""
    update_plan = json.loads(clean_json_text(raw_text))

    print("Structured update plan:")
    print(json.dumps(update_plan, ensure_ascii=False, indent=2))
    print()

    append_history_record(learner_state, update_plan)
    learner_state["today_action"] = update_plan["today_action"]
    learner_state["next_stage"] = update_plan["next_stage"]
    learner_state["current_stage"] = update_plan["next_stage"]

    save_state(learner_state)

    print("Updated learner state:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    print("State persisted to file successfully with atomic write.")


if __name__ == "__main__":
    main()
