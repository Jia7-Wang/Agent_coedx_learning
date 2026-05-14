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
    "路由",
    "优先级",
    "执行",
    "报告",
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


def session_file_path(session_id: str) -> Path:
    return sessions_dir() / f"{session_id}.json"


def load_session_state(session_id: str) -> dict:
    return json.loads(session_file_path(session_id).read_text(encoding="utf-8"))


def save_session_state(session_id: str, state: dict) -> None:
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


def build_session_overview(state: dict) -> dict:
    history = state.get("history", [])
    last_history_note = history[-1]["history_note"] if history else None

    return {
        "session_id": state["session_id"],
        "goal": state["goal"],
        "current_stage": state["current_stage"],
        "current_blocker": state["current_blocker"],
        "history_count": len(history),
        "last_history_note": last_history_note,
    }


def load_all_session_overviews() -> list[dict]:
    overviews = []
    for session_id in available_session_ids():
        state = load_session_state(session_id)
        overviews.append(build_session_overview(state))
    return overviews


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

    session_overviews = load_all_session_overviews()

    print("Available sessions:")
    print(json.dumps(session_overviews, ensure_ascii=False, indent=2))
    print()

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "在本地知识库中检索与执行报告、失败隔离、队列执行相关的文本块",
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
                    "你是一位会管理多个学习 session、生成优先级队列并输出执行报告的助理 Agent。"
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
        print("This run did not trigger retrieval, so the model will continue with current overviews only.")
        print()

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

    queue_plan = json.loads(clean_json_text(queue_response.choices[0].message.content or ""))

    print("Priority queue:")
    print(json.dumps(queue_plan, ensure_ascii=False, indent=2))
    print()

    execution_targets = queue_plan["priority_queue"][:2]

    print("Execution targets:")
    print(json.dumps(execution_targets, ensure_ascii=False, indent=2))
    print()

    execution_results = []

    for target in execution_targets:
        session_id = target["session_id"]

        try:
            learner_state = load_session_state(session_id)

            print(f"Executing session: {session_id}")
            print("Learner state before update:")
            print(json.dumps(learner_state, ensure_ascii=False, indent=2))
            print()

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
                            "你已经拿到了一个 session 优先级队列，并准备推进其中一个排在前面的 session。"
                            "请根据该 session 当前状态和队列信息，输出状态更新 JSON。\n\n"
                            "字段要求：\n"
                            '- today_action: 字符串，表示今天最该做的一件事\n'
                            '- next_stage: 字符串，表示下一阶段名称\n'
                            '- short_reason: 字符串，简要说明为什么这样更新\n'
                            '- history_note: 字符串，表示这次更新应该记入 history 的一句话摘要\n\n'
                            f"优先级队列：\n{json.dumps(queue_plan, ensure_ascii=False, indent=2)}\n\n"
                            f"当前要执行的 session：\n{json.dumps(target, ensure_ascii=False, indent=2)}\n\n"
                            f"该 session 当前状态：\n{json.dumps(learner_state, ensure_ascii=False, indent=2)}"
                        ),
                    },
                ],
            )

            update_plan = json.loads(clean_json_text(update_response.choices[0].message.content or ""))

            print("Structured update plan:")
            print(json.dumps(update_plan, ensure_ascii=False, indent=2))
            print()

            append_history_record(learner_state, update_plan)
            learner_state["today_action"] = update_plan["today_action"]
            learner_state["next_stage"] = update_plan["next_stage"]
            learner_state["current_stage"] = update_plan["next_stage"]

            save_session_state(session_id, learner_state)

            print("Updated learner state:")
            print(json.dumps(learner_state, ensure_ascii=False, indent=2))
            print()

            print(f"Session {session_id} persisted to file successfully with atomic write.")
            print()

            execution_results.append(
                {
                    "session_id": session_id,
                    "status": "success",
                    "next_stage": learner_state["current_stage"],
                    "today_action": learner_state["today_action"],
                }
            )
        except Exception as exc:
            print(f"Session {session_id} failed: {exc}")
            print()

            execution_results.append(
                {
                    "session_id": session_id,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    report_prompt = {
        "priority_queue": queue_plan["priority_queue"],
        "execution_targets": execution_targets,
        "execution_results": execution_results,
    }

    report_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会总结 session 队列执行结果的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据本轮队列执行结果，输出一个 execution report JSON。\n\n"
                    "字段要求：\n"
                    '- total_targets: 整数，本轮执行目标数\n'
                    '- succeeded: 整数，成功数\n'
                    '- failed: 整数，失败数\n'
                    '- summary: 字符串，概括本轮执行结果\n'
                    '- next_round_suggestion: 字符串，表示下一轮应如何调整\n\n'
                    f"执行上下文：\n{json.dumps(report_prompt, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    execution_report = json.loads(clean_json_text(report_response.choices[0].message.content or ""))

    print("Execution report:")
    print(json.dumps(execution_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
