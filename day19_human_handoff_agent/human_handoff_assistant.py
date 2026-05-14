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
    "重试",
    "死信",
    "人工",
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
        # 先写临时文件，再原子替换正式文件，避免写到一半时把原 session 搞坏。
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
        "retry_count": state.get("retry_count", 0),
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


def extract_message_text(message) -> str:
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(part for part in parts if part)

    return ""


def parse_json_text(text: str) -> dict:
    cleaned = clean_json_text(text)
    if not cleaned:
        raise ValueError("Model returned empty content.")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        first_object = cleaned.find("{")
        first_array = cleaned.find("[")
        start_positions = [pos for pos in [first_object, first_array] if pos != -1]
        if not start_positions:
            raise

        start = min(start_positions)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        if end == -1 or end <= start:
            raise

        return json.loads(cleaned[start : end + 1])


def parse_json_message(message, label: str) -> dict:
    raw_text = extract_message_text(message)
    refusal_text = getattr(message, "refusal", None)

    if not raw_text:
        if refusal_text:
            raise RuntimeError(f"{label} returned refusal instead of JSON: {refusal_text}")
        raise RuntimeError(f"{label} returned empty content instead of JSON.")

    try:
        return parse_json_text(raw_text)
    except Exception as exc:
        preview = raw_text[:400]
        raise RuntimeError(
            f"{label} did not return valid JSON. Raw content preview:\n{preview}"
        ) from exc


def build_fallback_priority_queue(session_overviews: list[dict]) -> dict:
    # 当模型排序结果为空或不是合法 JSON 时，至少给出一版可运行的本地回退队列，
    # 避免整个教学 demo 因一次输出波动直接中断。
    def sort_key(item: dict) -> tuple:
        blocker = item.get("current_blocker", "")
        stage = item.get("current_stage", "")

        handoff_related = "人工" in blocker or "dead letter" in blocker.lower()
        boundary_related = "边界" in stage or "规则" in stage

        return (
            -int(handoff_related),
            -item.get("retry_count", 0),
            -int(boundary_related),
            -item.get("history_count", 0),
            item["session_id"],
        )

    sorted_overviews = sorted(session_overviews, key=sort_key)

    priority_queue = []
    for overview in sorted_overviews:
        priority_queue.append(
            {
                "session_id": overview["session_id"],
                "reason": (
                    "Fallback queue: 该 session 当前更接近 dead letter queue、人工接管"
                    " 或失败闭环主题，因此在模型排序结果不可用时被优先安排。"
                ),
            }
        )

    top_focus = (
        "Fallback focus: 先处理最接近 dead letter queue 与 human handoff 的 session，"
        "确保失败任务能够稳定转入人工接管闭环。"
    )

    return {
        "priority_queue": priority_queue,
        "top_focus": top_focus,
    }


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


def max_retry_count() -> int:
    return int(os.getenv("MAX_RETRY_COUNT", "1"))


def maybe_fail_before_update(session_id: str, retry_mode: bool) -> None:
    # 这是教学用的“故意失败开关”，方便稳定演示
    # primary fail -> retry fail -> dead letter -> human handoff 这条链路。
    fail_session_id = os.getenv("FAIL_SESSION_ID")
    fail_on_retry = os.getenv("FAIL_ON_RETRY", "false").lower() == "true"

    if fail_session_id != session_id:
        return

    if not retry_mode:
        raise RuntimeError(f"Injected primary failure for session {session_id}")

    if retry_mode and fail_on_retry:
        raise RuntimeError(f"Injected retry failure for session {session_id}")


def execute_single_session(
    client: OpenAI,
    model: str,
    queue_plan: dict,
    target: dict,
    retry_mode: bool = False,
) -> dict:
    # 这个函数只负责“推进一个 session 一次”。
    # 它不决定谁先进 retry 或 dead letter，那些分流规则在 main() 里统一处理。
    session_id = target["session_id"]
    learner_state = load_session_state(session_id)

    maybe_fail_before_update(session_id, retry_mode)

    print(f"Executing session: {session_id} (retry_mode={retry_mode})")
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

    # 每推进一次都留痕，这样后面无论复盘还是人工接手，都能看到状态是怎么一步步变化的。
    append_history_record(learner_state, update_plan)
    learner_state["today_action"] = update_plan["today_action"]
    learner_state["next_stage"] = update_plan["next_stage"]
    learner_state["current_stage"] = update_plan["next_stage"]
    # 一旦本次成功推进，就说明这条 session 暂时恢复正常，失败计数清零。
    learner_state["retry_count"] = 0

    save_session_state(session_id, learner_state)

    print("Updated learner state:")
    print(json.dumps(learner_state, ensure_ascii=False, indent=2))
    print()

    print(f"Session {session_id} persisted to file successfully with atomic write.")
    print()

    return {
        "session_id": session_id,
        "status": "success",
        "mode": "retry" if retry_mode else "primary",
        "next_stage": learner_state["current_stage"],
        "today_action": learner_state["today_action"],
    }


def increment_retry_count(session_id: str) -> int:
    # retry_count 持久化在 session 文件里，而不是只放内存里，
    # 这样多次运行脚本后，系统仍然记得这个任务已经失败过几次。
    state = load_session_state(session_id)
    state["retry_count"] = state.get("retry_count", 0) + 1
    save_session_state(session_id, state)
    return state["retry_count"]


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
                "description": "在本地知识库中检索与 human handoff、人工接管、dead letter queue 相关的文本块",
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
                    "你是一位会管理多个学习 session、生成优先级队列、执行任务并生成人工接管清单的助理 Agent。"
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

    try:
        queue_plan = parse_json_message(
            queue_response.choices[0].message,
            label="Priority queue response",
        )
    except Exception as exc:
        print(f"Priority queue model output could not be parsed: {exc}")
        print("Falling back to a local deterministic queue.")
        print()
        queue_plan = build_fallback_priority_queue(session_overviews)

    print("Priority queue:")
    print(json.dumps(queue_plan, ensure_ascii=False, indent=2))
    print()

    execution_targets = queue_plan["priority_queue"][:2]

    print("Execution targets:")
    print(json.dumps(execution_targets, ensure_ascii=False, indent=2))
    print()

    primary_results = []
    retry_queue = []
    dead_letter_queue = []

    # 第一轮先按正常节奏执行。失败项先不直接放弃，而是看是否还值得进 retry queue。
    for target in execution_targets:
        session_id = target["session_id"]
        try:
            result = execute_single_session(client, model, queue_plan, target, retry_mode=False)
            primary_results.append(result)
        except Exception as exc:
            retry_count = increment_retry_count(session_id)

            failure_result = {
                "session_id": session_id,
                "status": "failed",
                "mode": "primary",
                "retry_count": retry_count,
                "error": str(exc),
            }
            primary_results.append(failure_result)

            # 如果失败次数已经超过上限，就别再自动试了，直接转 dead letter queue 等人工介入。
            if retry_count > max_retry_count():
                dead_letter_queue.append(
                    {
                        "session_id": session_id,
                        "reason": "Exceeded max retry count during primary execution",
                        "retry_count": retry_count,
                        "error": str(exc),
                    }
                )
            else:
                retry_queue.append(target)

    print("Primary execution results:")
    print(json.dumps(primary_results, ensure_ascii=False, indent=2))
    print()

    print("Retry queue:")
    print(json.dumps(retry_queue, ensure_ascii=False, indent=2))
    print()

    retry_results = []

    # 第二轮只处理刚才失败、但还允许自动恢复的任务。
    for target in retry_queue:
        session_id = target["session_id"]
        try:
            result = execute_single_session(client, model, queue_plan, target, retry_mode=True)
            retry_results.append(result)
        except Exception as exc:
            retry_count = increment_retry_count(session_id)
            failure_result = {
                "session_id": session_id,
                "status": "failed",
                "mode": "retry",
                "retry_count": retry_count,
                "error": str(exc),
            }
            retry_results.append(failure_result)

            # 重试后仍然超过阈值，说明自动化闭环先到这里为止，需要交给人。
            if retry_count > max_retry_count():
                dead_letter_queue.append(
                    {
                        "session_id": session_id,
                        "reason": "Exceeded max retry count during retry execution",
                        "retry_count": retry_count,
                        "error": str(exc),
                    }
                )

    print("Retry execution results:")
    print(json.dumps(retry_results, ensure_ascii=False, indent=2))
    print()

    print("Dead letter queue:")
    print(json.dumps(dead_letter_queue, ensure_ascii=False, indent=2))
    print()

    # 到了 dead letter queue 这一步，目标已经不是“继续自动修”，
    # 而是把上下文整理成一份人能立即接手的清单。
    handoff_prompt = {
        "dead_letter_queue": dead_letter_queue,
        "priority_queue": queue_plan["priority_queue"],
        "primary_results": primary_results,
        "retry_results": retry_results,
    }

    handoff_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会把 dead letter queue 转换成人工接管清单的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据 dead letter queue 和执行上下文，输出一个 human handoff checklist JSON。\n\n"
                    "字段要求：\n"
                    '- checklist: 数组，每个元素包含 session_id、failure_reason、human_owner_hint、first_manual_check、recommended_next_step\n'
                    '- handoff_summary: 字符串，概括这轮需要人工接手的情况\n\n'
                    f"handoff 上下文：\n{json.dumps(handoff_prompt, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    handoff_checklist = parse_json_message(
        handoff_response.choices[0].message,
        label="Human handoff response",
    )

    print("Human handoff checklist:")
    print(json.dumps(handoff_checklist, ensure_ascii=False, indent=2))
    print()

    # 最后的 execution report 不只总结成功/失败，
    # 还要把 dead letter 和 human handoff 一并纳入完整闭环。
    report_prompt = {
        "priority_queue": queue_plan["priority_queue"],
        "execution_targets": execution_targets,
        "primary_results": primary_results,
        "retry_queue": retry_queue,
        "retry_results": retry_results,
        "dead_letter_queue": dead_letter_queue,
        "handoff_checklist": handoff_checklist,
        "max_retry_count": max_retry_count(),
    }

    report_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会总结主执行、retry、dead letter queue 和 human handoff 结果的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据本轮执行、重试、死信和人工接管结果，输出一个 execution report JSON。\n\n"
                    "字段要求：\n"
                    '- total_targets: 整数，本轮主执行目标数\n'
                    '- primary_failed: 整数，主执行失败数\n'
                    '- dead_lettered: 整数，进入 dead letter queue 的数量\n'
                    '- handoff_items: 整数，进入人工接管清单的数量\n'
                    '- summary: 字符串，概括本轮执行结果\n'
                    '- next_round_suggestion: 字符串，表示下一轮应如何调整\n\n'
                    f"执行上下文：\n{json.dumps(report_prompt, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    execution_report = parse_json_message(
        report_response.choices[0].message,
        label="Execution report response",
    )

    print("Execution report:")
    print(json.dumps(execution_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
