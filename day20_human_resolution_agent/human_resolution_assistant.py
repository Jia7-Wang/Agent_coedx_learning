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
    "handoff",
    "requeue",
    "close",
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
        # 继续使用原子写入，避免中途崩溃时把 session 文件写坏。
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


def parse_json_text(text: str):
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


def parse_json_message(message, label: str):
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


def build_fallback_priority_queue(session_overviews: list[dict]) -> dict:
    def sort_key(item: dict) -> tuple:
        blocker = item.get("current_blocker", "")
        stage = item.get("current_stage", "")

        human_related = "人工" in blocker or "人工" in stage or "dead letter" in blocker.lower()
        return (
            -int(human_related),
            -item.get("retry_count", 0),
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
                    "Fallback queue: 该 session 当前更接近人工接管与失败闭环主题，"
                    "因此在模型排序结果不可用时被优先安排。"
                ),
            }
        )

    return {
        "priority_queue": priority_queue,
        "top_focus": "Fallback focus: 先处理最接近人工处理回写和重新入队决策的 session。",
    }


def max_retry_count() -> int:
    return int(os.getenv("MAX_RETRY_COUNT", "1"))


def human_decision_preference() -> str:
    return os.getenv("HUMAN_DECISION_PREFERENCE", "balanced")


def maybe_fail_before_update(session_id: str, retry_mode: bool) -> None:
    # 这里继续保留 Day18/19 的教学用失败注入，方便触发 dead letter。
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
    # 单个 session 的自动推进逻辑保持和前几天一致。
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
                    "你已经拿到了一份 session 优先级队列，准备推进其中一个排在前面的 session。"
                    "请根据该 session 当前状态和队列信息，输出状态更新 JSON。\n\n"
                    "字段要求：\n"
                    '- today_action: 字符串，表示今天最该做的一件事\n'
                    '- next_stage: 字符串，表示下一阶段名称\n'
                    '- short_reason: 字符串，简要说明为什么这样更新\n'
                    '- history_note: 字符串，表示这次更新应该写进 history 的一句话摘要\n\n'
                    f"优先级队列：\n{json.dumps(queue_plan, ensure_ascii=False, indent=2)}\n\n"
                    f"当前要执行的 session：\n{json.dumps(target, ensure_ascii=False, indent=2)}\n\n"
                    f"该 session 当前状态：\n{json.dumps(learner_state, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    update_plan = parse_json_message(
        update_response.choices[0].message,
        label=f"Session update response for {session_id}",
    )

    print("Structured update plan:")
    print(json.dumps(update_plan, ensure_ascii=False, indent=2))
    print()

    append_history_record(learner_state, update_plan)
    learner_state["today_action"] = update_plan["today_action"]
    learner_state["next_stage"] = update_plan["next_stage"]
    learner_state["current_stage"] = update_plan["next_stage"]
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
    state = load_session_state(session_id)
    state["retry_count"] = state.get("retry_count", 0) + 1
    save_session_state(session_id, state)
    return state["retry_count"]


def build_fallback_handoff_checklist(dead_letter_queue: list[dict]) -> dict:
    checklist = []
    for item in dead_letter_queue:
        checklist.append(
            {
                "session_id": item["session_id"],
                "failure_reason": item["error"],
                "human_owner_hint": "工程或工作流负责人",
                "first_manual_check": "先检查失败日志、重试阈值和该任务最近一次状态更新。",
                "recommended_next_step": "确认是真实故障还是演示性注入，再决定重新入队还是人工关闭。",
            }
        )

    return {
        "checklist": checklist,
        "handoff_summary": "Fallback handoff: 已把 dead letter queue 转成最小人工接管清单。",
    }


def build_fallback_human_resolution(handoff_checklist: dict, preference: str) -> dict:
    decisions = []

    for item in handoff_checklist.get("checklist", []):
        session_id = item["session_id"]

        if preference == "close_first":
            decision = "close"
        elif preference == "requeue_first":
            decision = "requeue"
        else:
            decision = "requeue" if "engineering" in session_id else "close"

        if decision == "requeue":
            decisions.append(
                {
                    "session_id": session_id,
                    "decision": "requeue",
                    "resolution_reason": "人工已确认该任务仍值得继续推进，适合修复后重新进入主队列。",
                    "next_stage": "人工处理后重新入队",
                    "next_blocker": "我已经拿到人工处理结论，但还需要验证修复后的任务是否能稳定重新回到自动执行主线。",
                    "today_action": "把人工修复结论回写到 session，并将该任务标记为下一轮可重新入队验证。",
                    "history_note": "人工接管后确认该任务可以修复并重新入队，开始把人工处理结论回写到 session。",
                    "human_note": "已人工确认这不是永久关闭项，建议回到主队列继续验证。",
                }
            )
        else:
            decisions.append(
                {
                    "session_id": session_id,
                    "decision": "close",
                    "resolution_reason": "人工已确认该任务当前不适合继续自动推进，应先结案或暂停。",
                    "next_stage": "人工确认关闭或暂停",
                    "next_blocker": "我已经有人工结论，但还需要在系统里清晰标记这条任务为何被关闭或暂停。",
                    "today_action": "把人工结论写回 session，并标记该任务本轮不再重新入队。",
                    "history_note": "人工接管后确认该任务暂不继续自动推进，开始把关闭结论回写到 session。",
                    "human_note": "已人工确认本轮不再自动恢复，等待后续专项处理。",
                }
            )

    return {
        "decisions": decisions,
        "resolution_summary": "Fallback resolution: 已为每个 handoff 项生成最小人工处理决定。",
    }


def apply_human_resolution(session_id: str, decision: dict) -> dict:
    learner_state = load_session_state(session_id)

    update_plan = {
        "today_action": decision["today_action"],
        "next_stage": decision["next_stage"],
        "short_reason": decision["resolution_reason"],
        "history_note": decision["history_note"],
    }

    append_history_record(learner_state, update_plan)
    learner_state["today_action"] = decision["today_action"]
    learner_state["next_stage"] = decision["next_stage"]
    learner_state["current_stage"] = decision["next_stage"]
    learner_state["current_blocker"] = decision["next_blocker"]
    learner_state["retry_count"] = 0
    learner_state["human_resolution"] = {
        "resolved_at": now_text(),
        "decision": decision["decision"],
        "resolution_reason": decision["resolution_reason"],
        "human_note": decision["human_note"],
    }

    if decision["decision"] == "requeue":
        learner_state["status"] = "ready_for_requeue"
    else:
        learner_state["status"] = "closed_by_human"

    save_session_state(session_id, learner_state)

    return {
        "session_id": session_id,
        "decision": decision["decision"],
        "status": learner_state["status"],
        "next_stage": learner_state["current_stage"],
        "today_action": learner_state["today_action"],
    }


def build_fallback_execution_report(
    execution_targets: list[dict],
    primary_results: list[dict],
    dead_letter_queue: list[dict],
    handoff_checklist: dict,
    applied_resolution_results: list[dict],
) -> dict:
    primary_failed = sum(1 for item in primary_results if item["status"] == "failed")
    requeued = sum(1 for item in applied_resolution_results if item["decision"] == "requeue")
    closed = sum(1 for item in applied_resolution_results if item["decision"] == "close")

    return {
        "total_targets": len(execution_targets),
        "primary_failed": primary_failed,
        "dead_lettered": len(dead_letter_queue),
        "handoff_items": len(handoff_checklist.get("checklist", [])),
        "human_resolved": len(applied_resolution_results),
        "requeued": requeued,
        "closed": closed,
        "summary": (
            f"本轮主执行处理了 {len(execution_targets)} 个目标，其中 {primary_failed} 个主执行失败；"
            f"{len(dead_letter_queue)} 个任务进入 dead letter queue，"
            f"随后有 {len(applied_resolution_results)} 个任务得到人工处理结论。"
        ),
        "next_round_suggestion": (
            "下一轮应优先检查 ready_for_requeue 的任务是否需要重新回到主队列，"
            "并把 closed_by_human 的任务从自动节奏中移出。"
        ),
    }


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
                "description": "在本地知识库中检索与人工接管、处理回写、重新入队相关的文本块",
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
                    "你是一位会管理多个学习 session、生成优先级队列、执行任务并处理人工接管后续决策的助理 Agent。"
                    "如果需要知识库支持，请先调用工具检索。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "下面是当前所有学习 session 的概览。"
                    "请先获取必要知识，再输出一个当前优先级队列。\n\n"
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
                    '- top_focus: 字符串，表示当前最优先队列项对应关注什么\n\n'
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

    if dead_letter_queue:
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

        try:
            handoff_checklist = parse_json_message(
                handoff_response.choices[0].message,
                label="Human handoff response",
            )
        except Exception as exc:
            print(f"Human handoff output could not be parsed: {exc}")
            print("Falling back to a local handoff checklist.")
            print()
            handoff_checklist = build_fallback_handoff_checklist(dead_letter_queue)
    else:
        handoff_checklist = {
            "checklist": [],
            "handoff_summary": "本轮没有任务进入 dead letter queue，因此不需要人工接管清单。",
        }

    print("Human handoff checklist:")
    print(json.dumps(handoff_checklist, ensure_ascii=False, indent=2))
    print()

    if handoff_checklist["checklist"]:
        resolution_prompt = {
            "handoff_checklist": handoff_checklist,
            "preference": human_decision_preference(),
            "queue_plan": queue_plan,
            "dead_letter_queue": dead_letter_queue,
        }

        resolution_response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位模拟人工处理者的助理 Agent。"
                        "你会根据 human handoff checklist 决定任务是重新入队还是关闭。"
                        "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "请根据人工接管清单，输出人工处理决定 JSON。\n\n"
                        "字段要求：\n"
                        '- decisions: 数组，每个元素包含 session_id、decision、resolution_reason、next_stage、next_blocker、today_action、history_note、human_note\n'
                        '- resolution_summary: 字符串，概括本轮人工处理结论\n\n'
                        "其中 decision 只能是 requeue 或 close。\n\n"
                        f"人工处理上下文：\n{json.dumps(resolution_prompt, ensure_ascii=False, indent=2)}"
                    ),
                },
            ],
        )

        try:
            human_resolution = parse_json_message(
                resolution_response.choices[0].message,
                label="Human resolution response",
            )
        except Exception as exc:
            print(f"Human resolution output could not be parsed: {exc}")
            print("Falling back to local human decisions.")
            print()
            human_resolution = build_fallback_human_resolution(
                handoff_checklist,
                preference=human_decision_preference(),
            )
    else:
        human_resolution = {
            "decisions": [],
            "resolution_summary": "本轮没有 handoff 项，因此没有额外人工处理决定。",
        }

    print("Human resolution decisions:")
    print(json.dumps(human_resolution, ensure_ascii=False, indent=2))
    print()

    applied_resolution_results = []
    requeue_candidates = []
    closed_items = []

    for decision in human_resolution["decisions"]:
        applied = apply_human_resolution(decision["session_id"], decision)
        applied_resolution_results.append(applied)

        if applied["decision"] == "requeue":
            requeue_candidates.append(applied)
        else:
            closed_items.append(applied)

    print("Applied human resolutions:")
    print(json.dumps(applied_resolution_results, ensure_ascii=False, indent=2))
    print()

    print("Requeue candidates:")
    print(json.dumps(requeue_candidates, ensure_ascii=False, indent=2))
    print()

    print("Closed items:")
    print(json.dumps(closed_items, ensure_ascii=False, indent=2))
    print()

    report_prompt = {
        "priority_queue": queue_plan["priority_queue"],
        "execution_targets": execution_targets,
        "primary_results": primary_results,
        "retry_queue": retry_queue,
        "retry_results": retry_results,
        "dead_letter_queue": dead_letter_queue,
        "handoff_checklist": handoff_checklist,
        "human_resolution": human_resolution,
        "applied_resolution_results": applied_resolution_results,
        "max_retry_count": max_retry_count(),
    }

    report_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会总结主执行、retry、dead letter、human handoff 和人工处理回写结果的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据本轮执行、重试、死信、人工接管与人工处理回写结果，输出一个 execution report JSON。\n\n"
                    "字段要求：\n"
                    '- total_targets: 整数，本轮主执行目标数\n'
                    '- primary_failed: 整数，主执行失败数\n'
                    '- dead_lettered: 整数，进入 dead letter queue 的数量\n'
                    '- handoff_items: 整数，进入人工接管清单的数量\n'
                    '- human_resolved: 整数，已得到人工处理决定的数量\n'
                    '- requeued: 整数，被人工决定重新入队的数量\n'
                    '- closed: 整数，被人工决定关闭或暂停的数量\n'
                    '- summary: 字符串，概括本轮执行与人工处理结果\n'
                    '- next_round_suggestion: 字符串，表示下一轮应该如何调整\n\n'
                    f"执行上下文：\n{json.dumps(report_prompt, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    try:
        execution_report = parse_json_message(
            report_response.choices[0].message,
            label="Execution report response",
        )
    except Exception as exc:
        print(f"Execution report output could not be parsed: {exc}")
        print("Falling back to a local execution report.")
        print()
        execution_report = build_fallback_execution_report(
            execution_targets=execution_targets,
            primary_results=primary_results,
            dead_letter_queue=dead_letter_queue,
            handoff_checklist=handoff_checklist,
            applied_resolution_results=applied_resolution_results,
        )

    print("Execution report:")
    print(json.dumps(execution_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
