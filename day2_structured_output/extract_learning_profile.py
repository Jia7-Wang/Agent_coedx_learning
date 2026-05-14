import json
import os
from pathlib import Path

from openai import OpenAI


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


def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json") :].strip()
    elif text.startswith("```"):
        text = text[len("```") :].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def main() -> None:
    load_env_file()

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = build_client()

    user_text = (
        "我是零基础，想学Agent开发，平时每天能学2小时，希望3个月内能做出项目，"
        "也希望学习过程中穿插Git、调试、Docker这些公司项目常识。"
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一位严谨的学习规划助手。"
                    "请只返回合法 JSON，不要输出 markdown，不要输出解释。"
                ),
            },
            {
                "role": "user",
                "content": (
                    "请从下面这段学习需求中提取结构化信息，并严格返回 JSON。\n\n"
                    "字段要求：\n"
                    '- level: 字符串，只能是 "beginner"、"intermediate"、"advanced" 之一\n'
                    '- goal: 字符串，概括核心目标\n'
                    '- daily_hours: 数字\n'
                    '- target_duration_months: 数字\n'
                    '- should_include_engineering_basics: 布尔值\n'
                    "- recommended_start_topics: 字符串数组，给出 4 到 6 个主题\n\n"
                    f"学习需求：{user_text}"
                ),
            },
        ],
    )

    raw_text = response.choices[0].message.content or ""
    json_text = clean_json_text(raw_text)
    parsed = json.loads(json_text)

    print("response:", response)
    print("Model:", model)
    print("Raw response:")
    print(raw_text)
    print()
    print("Parsed JSON:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
