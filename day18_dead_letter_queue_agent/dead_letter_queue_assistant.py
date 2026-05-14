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
    # 从环境变量读取“最大允许自动重试次数”。
    # 如果没配置，就默认最多允许 1 次重试。
    return int(os.getenv("MAX_RETRY_COUNT", "1"))


def maybe_fail_before_update(session_id: str, retry_mode: bool) -> None:
    # 读取要故意失败的 session_id，用于教学演示失败链路。
    fail_session_id = os.getenv("FAIL_SESSION_ID")
    # 是否连 retry 阶段也一起故意失败。
    fail_on_retry = os.getenv("FAIL_ON_RETRY", "false").lower() == "true"

    # 如果当前 session 不是被指定的失败对象，就什么都不做。
    if fail_session_id != session_id:
        return

    # 主执行阶段命中时，直接抛错，模拟 primary failure。
    if not retry_mode:
        raise RuntimeError(f"Injected primary failure for session {session_id}")

    # retry 阶段如果也要求失败，就再次抛错，模拟 retry failure。
    if retry_mode and fail_on_retry:
        raise RuntimeError(f"Injected retry failure for session {session_id}")


def execute_single_session(
    client: OpenAI,
    model: str,
    queue_plan: dict,
    target: dict,
    retry_mode: bool = False,
) -> dict:
    # 当前要执行的 session_id。
    session_id = target["session_id"]
    # 读取这个 session 当前完整状态。
    learner_state = load_session_state(session_id)

    # 正式执行前先判断是否要注入失败，用于演示 primary/retry 分支。
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

    append_history_record(learner_state, update_plan)
    learner_state["today_action"] = update_plan["today_action"]
    learner_state["next_stage"] = update_plan["next_stage"]
    learner_state["current_stage"] = update_plan["next_stage"]
    # 一旦本次执行成功，就把 retry_count 清零。
    # 这表示当前任务已经恢复正常，不再处于“连续失败”状态。
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
    # 读取失败 session 的当前状态。
    state = load_session_state(session_id)
    # 连续失败次数 +1。
    state["retry_count"] = state.get("retry_count", 0) + 1
    # 立刻写回文件，确保后面的分流判断使用的是最新 retry_count。
    save_session_state(session_id, state)
    # 返回更新后的 retry_count，方便主流程直接判断。
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
                "description": "在本地知识库中检索与 dead letter queue、最大重试次数、失败恢复相关的文本块",
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
                    "你是一位会管理多个学习 session、生成优先级队列、执行任务并管理 dead letter queue 的助理 Agent。"
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

    primary_results = []
    retry_queue = []
    dead_letter_queue = []

    for target in execution_targets:
        session_id = target["session_id"]
        try:
            # 先走主执行阶段。
            result = execute_single_session(client, model, queue_plan, target, retry_mode=False)
            primary_results.append(result)
        except Exception as exc:
            # 主执行失败后，先把这个 session 的 retry_count +1。
            retry_count = increment_retry_count(session_id)

            failure_result = {
                "session_id": session_id,
                "status": "failed",
                "mode": "primary",
                "retry_count": retry_count,
                "error": str(exc),
            }
            primary_results.append(failure_result)

            # 如果失败次数已经超过最大允许重试次数，
            # 说明它不该再继续自动恢复，直接进入 dead letter queue。
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
                # 否则先放进 retry_queue，等待后面再尝试一次恢复。
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
            # 对 retry_queue 里的失败项再执行一次，这就是 retry 阶段。
            result = execute_single_session(client, model, queue_plan, target, retry_mode=True)
            retry_results.append(result)
        except Exception as exc:
            # retry 仍然失败，就再次增加 retry_count。
            retry_count = increment_retry_count(session_id)
            failure_result = {
                "session_id": session_id,
                "status": "failed",
                "mode": "retry",
                "retry_count": retry_count,
                "error": str(exc),
            }
            retry_results.append(failure_result)

            # 如果这次 retry 后失败次数已经超过阈值，
            # 就把它送入 dead letter queue，停止自动恢复。
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

    # 把本轮执行过程里的关键中间结果收集起来，交给模型做最后总结。
    # 这里不是让模型“回忆”刚才发生了什么，而是把结构化上下文显式传给它。
    report_prompt = {
        "priority_queue": queue_plan["priority_queue"],
        "execution_targets": execution_targets,
        "primary_results": primary_results,
        "retry_queue": retry_queue,
        "retry_results": retry_results,
        "dead_letter_queue": dead_letter_queue,
        # 把本轮使用的最大重试次数也放进去，方便模型解释为什么会进入 dead letter queue。
        "max_retry_count": max_retry_count(),
    }

    # 最后一轮模型调用：不再做执行，而是做“执行结果汇总”。
    report_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位会总结主执行、retry 和 dead letter queue 结果的助理 Agent。"
                    "请严格返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请根据本轮主执行、retry 与 dead letter 结果，输出一个 execution report JSON。\n\n"
                    "字段要求：\n"
                    '- total_targets: 整数，本轮主执行目标数\n'
                    '- primary_failed: 整数，主执行失败数\n'
                    '- retry_attempted: 整数，进入 retry 的数量\n'
                    '- dead_lettered: 整数，进入 dead letter queue 的数量\n'
                    '- summary: 字符串，概括本轮执行结果\n'
                    '- next_round_suggestion: 字符串，表示下一轮应如何调整\n\n'
                    f"执行上下文：\n{json.dumps(report_prompt, ensure_ascii=False, indent=2)}"
                ),
            },
        ],
    )

    # 解析模型返回的 execution report JSON。
    execution_report = json.loads(clean_json_text(report_response.choices[0].message.content or ""))

    # 打印最终执行报告，作为本轮运行的总复盘结果。
    print("Execution report:")
    print(json.dumps(execution_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
