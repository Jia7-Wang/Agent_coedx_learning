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
    "多会话",
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


def sessions_dir() -> Path:
    return Path(__file__).with_name("sessions")


def available_session_ids() -> list[str]:
    session_files = sorted(sessions_dir().glob("*.json"))
    return [path.stem for path in session_files]


def choose_session_id() -> str:
    # 如果 .env 里显式指定了 LEARNER_SESSION_ID，就优先使用它。
    # 这样我们可以手动切换当前要操作哪个 session。
    env_session_id = os.getenv("LEARNER_SESSION_ID")
    if env_session_id:
        return env_session_id

    # 如果没有显式指定，就读取当前 sessions 目录下所有可用的 session。
    session_ids = available_session_ids()
    if not session_ids:
        raise RuntimeError("No session files found in sessions directory.")

    # 默认先取第一个 session，避免初学阶段引入额外交互输入。
    # 这样脚本开箱即用，不需要你每次手动输入 session_id。
    return session_ids[0]


def session_file_path(session_id: str) -> Path:
    # 把 session_id 映射成对应的状态文件路径。
    # 例如 demo-python-agent -> sessions/demo-python-agent.json
    return sessions_dir() / f"{session_id}.json"


def build_default_state(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "goal": "我想学习如何让一个 Agent 同时管理多个会话。",
        "current_stage": "多 session 管理入门",
        "completed_topics": [
            "模型调用",
            "结构化输出",
            "单工具调用",
            "状态与工作流基础",
            "持久化 session",
        ],
        "current_blocker": "我还不清楚不同 session 应该怎样分开存储和恢复。",
        "today_action": "理解 session_id、状态文件、会话隔离三者的关系",
        "next_stage": "多 session 管理入门",
        "history": [],
    }


def load_or_create_state(session_id: str) -> tuple[dict, str]:
    # 先根据 session_id 算出这个会话对应的状态文件位置。
    state_path = session_file_path(session_id)
    if state_path.exists():
        # 如果文件已存在，说明这个 session 以前跑过，直接恢复旧状态。
        state = json.loads(state_path.read_text(encoding="utf-8"))
        return state, "loaded_from_file"

    # 如果文件不存在，说明这是一个新的 session。
    # 先构造默认状态，再立即保存一次，确保后面这个 session 也能被恢复。
    state = build_default_state(session_id)
    save_state(session_id, state)
    return state, "created_default_state"


def save_state(session_id: str, state: dict) -> None:
    state_path = session_file_path(session_id)
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=state_path.parent,
            prefix=f"{state_path.stem}_",
            suffix=".tmp",
        ) as temp_file:
            temp_file.write(payload)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        os.replace(temp_path, state_path)
    finally:
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

    session_id = choose_session_id()
    learner_state, state_source = load_or_create_state(session_id)

    print("Session id:", session_id)
    print("Available sessions:", available_session_ids())
    print("State source:", state_source)
    print("State file:", session_file_path(session_id))
    print()

    print("Learner state before update:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "在本地知识库中检索与多 session 管理、状态隔离、会话恢复相关的文本块",
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
                    "你是一位会管理多 session 学习状态的助理 Agent。"
                    "如果需要知识库支持，请先调用工具检索。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "下面是某个 session 的当前学习状态。"
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
                    "你是一位会推进多 session 学习状态的助理 Agent。"
                    "请基于当前状态、历史轨迹和检索结果，严格返回合法 JSON。"
                    "不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据当前 session 的学习状态、已有 history 和可能的检索结果，输出一个状态更新方案。\n\n"
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

    save_state(session_id, learner_state)

    print("Updated learner state:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    print("Session persisted to file successfully with atomic write.")


if __name__ == "__main__":
    main()
