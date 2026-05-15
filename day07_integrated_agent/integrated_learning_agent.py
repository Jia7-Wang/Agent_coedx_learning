import json
import os
from pathlib import Path

from openai import OpenAI


KEYWORDS = ["Agent", "Git", "Docker", "项目", "RAG", "工作流", "工具", "状态", "工程"]


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


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    user_goal = (
        "我是零基础，想在 6 周内做出一个简单 Agent 项目，"
        "同时希望补 Git、日志调试和 Docker 基础。请给我一个下一步行动方案。"
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "在本地知识库中检索与学习目标相关的文本块",
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
                    "你是一位学习助理 Agent。"
                    "如果用户的目标需要知识库支持，请先调用工具检索，再给行动建议。"
                ),
            },
            {
                "role": "user",
                "content": user_goal,
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

    if not message.tool_calls:
        print("This run did not trigger knowledge retrieval.")
        print("We can add a fallback version later if needed.")
        return

    tool_messages = []
    tool_results = []

    for tool_call in message.tool_calls:
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

    print("Knowledge tool result:")
    print(json.dumps(tool_results, ensure_ascii=False, indent=2))
    print()

    second_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位学习助理 Agent。"
                    "请基于检索结果，给出一个清晰的下一步行动方案。"
                    "要求包含：学习重点、建议顺序、一个最小项目建议。"
                    "尽量引用 chunk 编号。"
                ),
            },
            {
                "role": "user",
                "content": user_goal,
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

    print("Final action plan:")
    print(final_text)


if __name__ == "__main__":
    main()
