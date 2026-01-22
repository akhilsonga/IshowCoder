import json
import os
import sys


def token_estimate(text: str) -> int:
    return max(0, int((len(text) + 3) / 4))


def load_system_prompt() -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_dir, "Agent", "system_prompt_1.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return ""


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python check_chat_tokens.py /path/to/chat.json")
        return 1

    chat_path = sys.argv[1]
    try:
        with open(chat_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading chat: {exc}")
        return 1

    director_chain = []
    if isinstance(data, dict):
        director_chain = data.get("director_chain", [])
        if not director_chain and isinstance(data.get("messages"), list):
            director_chain = data.get("messages", [])
    elif isinstance(data, list):
        director_chain = data

    system_prompt = load_system_prompt()
    context_tokens = token_estimate(system_prompt) if system_prompt else 0
    output_tokens = 0

    for msg in director_chain:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content", "")
        if content:
            context_tokens += token_estimate(content)
        if role == "assistant":
            output_tokens += token_estimate(content)

    print(f"Context tokens: {context_tokens}")
    print(f"Output tokens: {output_tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

