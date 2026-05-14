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


def retrieve_top_chunks(question: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    scored = []

    for chunk in chunks:
        score, matched_keywords = score_chunk(question, chunk["text"])
        scored.append(
            {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": score,
                "matched_keywords": matched_keywords,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return [item for item in scored[:top_k] if item["score"] > 0]


def build_context(top_chunks: list[dict]) -> str:
    if not top_chunks:
        return "未检索到相关知识。"

    lines = []
    for chunk in top_chunks:
        lines.append(f"[Chunk {chunk['chunk_id']}]\n{chunk['text']}")

    return "\n\n".join(lines)


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    question = "如果我想学 Agent 开发，同时希望以后能接公司项目，应该优先补哪些工程基础？"

    chunks = load_knowledge_chunks()

    print("Loaded chunks with ids:")
    print(json.dumps(chunks, ensure_ascii=False, indent=2))
    print()

    top_chunks = retrieve_top_chunks(question, chunks, top_k=3)

    print("Top matched chunks with scores:")
    print(json.dumps(top_chunks, ensure_ascii=False, indent=2))
    print()

    context = build_context(top_chunks)

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位知识库问答助手。"
                    "请优先根据给定 context 回答。"
                    "尽量引用 chunk 编号，例如 [Chunk 2]。"
                    "如果 context 不足，要明确说明。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"问题：{question}\n\n"
                    f"知识库上下文：\n{context}\n\n"
                    "请基于以上上下文，用中文给出清晰回答，并尽量标注引用来源。"
                ),
            },
        ],
    )

    final_text = response.choices[0].message.content or ""

    print("Final answer with references:")
    print(final_text)


if __name__ == "__main__":
    main()
