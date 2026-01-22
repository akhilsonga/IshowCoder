"""
Agent.py

Tiny OpenRouter client helpers.

Usage:
  from Backend.Agent import ask_openrouter
  print(ask_openrouter("Hello", api_key="..."))
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model selection
DEFAULT_MODEL = "minimax/minimax-m2"
DEFAULT_MODEL = "openai/gpt-4o-mini"
MODEL_OPTIONS: list[str] = [
    DEFAULT_MODEL,
    "google/gemini-2.5-flash-lite",
    "openai/gpt-4o-mini"
    "x-ai/grok-code-fast-1",
    "z-ai/glm-4.7",
    "openai/gpt-5.1-codex-mini",
    "moonshotai/kimi-k2",
    "google/gemini-2.5-flash",
    "google/gemini-3-flash-preview",
]



def return_model_name(model_name: str) -> str:
    return model_name





class OpenRouterError(RuntimeError):
    pass


def _write_debug_context(messages: List[Dict[str, Any]]) -> None:
    """
    Write full messages context to Backend/Debug/LLM_context.md.
    """
    try:
        debug_dir = Path(__file__).resolve().parents[1] / "Debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        out_path = debug_dir / "LLM_context.md"
        dumped = json.dumps(messages, ensure_ascii=False, indent=2)
        # Make newlines readable inside JSON strings for debug viewing.
        dumped = dumped.replace("\\n", "\n")
        content = [
            "# LLM Context",
            "",
            "```json",
            dumped,
            "```",
            "",
        ]
        out_path.write_text("\n".join(content), encoding="utf-8", errors="replace")
    except Exception:
        # Debug logging should never break model calls.
        return


def _try_load_dotenv(project_root: Optional[Path] = None) -> None:
    """
    Minimal .env loader (no external dependency).

    Loads KEY=VALUE pairs into os.environ if those keys are not already set.
    """
    root = project_root or Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists() or not env_path.is_file():
        return

    try:
        lines = env_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip('"').strip("'")
        if not key:
            continue
        os.environ.setdefault(key, val)


def _get_api_key(api_key: Optional[str]) -> str:
    # If the user placed OPENROUTER_API_KEY in project-root .env, load it.
    # (This is common in local dev, and avoids requiring manual `export`.)
    _try_load_dotenv()

    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError('Missing API key. Pass api_key=... or set env var OPENROUTER_API_KEY.')
    return key


def openrouter_chat(
    messages: List[Dict[str, Any]],
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_config: Optional[Dict[str, Any]] = None,
    timeout_s: int = 60,
) -> Dict[str, Any]:
    """
    Call OpenRouter Chat Completions and return the assistant message dict:
      {"role": "assistant", "content": "...", "reasoning_details": ...?}
    """ 
    _write_debug_context(messages)
    api_key = _get_api_key(api_key)

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    if reasoning_config:
        payload["reasoning"] = reasoning_config

    resp = requests.post(
        url=OPENROUTER_CHAT_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=timeout_s,
    )

    try:
        data = resp.json()
    except Exception as e:
        raise OpenRouterError(f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:500]}") from e

    if resp.status_code >= 400:
        raise OpenRouterError(f"OpenRouter error (HTTP {resp.status_code}): {data}")

    try:
        return data["choices"][0]["message"]
    except Exception as e:
        raise OpenRouterError(f"Unexpected response shape: {data}") from e


def openrouter_chat_stream(
    messages: List[Dict[str, Any]],
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_config: Optional[Dict[str, Any]] = None,
    timeout_s: int = 60,
) -> Iterable[str]:
    """
    Stream tokens from OpenRouter (Server-Sent Events).

    Yields content chunks (strings) as they arrive.
    """
    _write_debug_context(messages)
    api_key = _get_api_key(api_key)

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    if reasoning_config:
        payload["reasoning"] = reasoning_config

    resp = requests.post(
        url=OPENROUTER_CHAT_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        stream=True,
        timeout=timeout_s,
    )

    if resp.status_code >= 400:
        try:
            data = resp.json()
        except Exception:
            raise OpenRouterError(f"OpenRouter error (HTTP {resp.status_code}): {resp.text[:500]}")
        raise OpenRouterError(f"OpenRouter error (HTTP {resp.status_code}): {data}")

    for raw_line in resp.iter_lines(decode_unicode=True):
        if not raw_line:
            continue
        line = raw_line.strip()
        if not line.startswith("data:"):
            continue

        data_str = line[len("data:") :].strip()
        if data_str == "[DONE]":
            break

        try:
            event = json.loads(data_str)
        except Exception:
            continue

        try:
            choice0 = (event.get("choices") or [])[0] or {}
        except Exception:
            continue

        # OpenAI-style streaming: {"delta": {"content": "..."}, ...}
        delta = choice0.get("delta") or {}
        chunk = delta.get("content")
        if chunk:
            yield str(chunk)
            continue

        # Some providers may stream as message fragments.
        msg = choice0.get("message") or {}
        chunk2 = msg.get("content")
        if chunk2:
            yield str(chunk2)


def LLM(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_enabled: bool = True,
    timeout_s: int = 6000,
) -> str:
    """
    Stream a single-turn response and print it as it arrives.
    Returns the full response text.
    """
    # Set minimal reasoning with max 3000 tokens
    reasoning_config = {"max_tokens": 3000} if reasoning_enabled else None

    full: List[str] = []
    for piece in openrouter_chat_stream(
        [{"role": "user", "content": prompt}],
        api_key=api_key,
        model=model,
        reasoning_config=reasoning_config,
        timeout_s=timeout_s,
    ):
        print(piece, end="", flush=True)
        full.append(piece)
    print()  # newline after stream
    return "".join(full)


def LLM_messages(
    messages: List[Dict[str, Any]],
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_enabled: bool = True,
    timeout_s: int = 6000,
    on_first_token: Optional[callable] = None,
    line_prefix: str = "",
) -> str:
    """
    Stream a multi-turn response and print it as it arrives.
    Returns the full response text.

    Args:
        line_prefix: Optional prefix to add at the start of each line (for indentation).
    """
    reasoning_config = {"max_tokens": 3000} if reasoning_enabled else None

    full: List[str] = []
    first = True
    at_line_start = True
    for piece in openrouter_chat_stream(
        messages,
        api_key=api_key,
        model=model,
        reasoning_config=reasoning_config,
        timeout_s=timeout_s,
    ):
        if first:
            first = False
            if on_first_token is not None:
                try:
                    on_first_token()
                except Exception:
                    pass

        # Handle line prefix for indentation
        if line_prefix:
            output = ""
            for char in piece:
                if at_line_start:
                    output += line_prefix
                    at_line_start = False
                output += char
                if char == "\n":
                    at_line_start = True
            print(output, end="", flush=True)
        else:
            print(piece, end="", flush=True)
        full.append(piece)
    print()
    return "".join(full)


def ask_openrouter(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    reasoning_enabled: bool = True,
) -> str:
    """Single-turn convenience: input prompt -> output assistant text."""
    # Set minimal reasoning with max 3000 tokens
    reasoning_config = {"max_tokens": 3000} if reasoning_enabled else None

    msg = openrouter_chat(
        [{"role": "user", "content": prompt}],
        api_key=api_key,
        model=model,
        reasoning_config=reasoning_config,
    )
    return str(msg.get("content") or "")


def ask_openrouter_with_reasoning_continuation(
    prompt1: str,
    prompt2: str,
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    timeout_s: int = 60,
) -> Tuple[str, str]:
    """
    Two-turn example showing how to preserve `reasoning_details` between calls.

    Returns:
      (first_answer_text, second_answer_text)
    """
    first = openrouter_chat(
        [{"role": "user", "content": prompt1}],
        api_key=api_key,
        model=model,
        reasoning_config={"max_tokens": 3000},
        timeout_s=timeout_s,
    )

    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": prompt1},
        {
            "role": "assistant",
            "content": first.get("content"),
            "reasoning_details": first.get("reasoning_details"),  # preserve unmodified
        },
        {"role": "user", "content": prompt2},
    ]

    second = openrouter_chat(
        messages,
        api_key=api_key,
        model=model,
        reasoning_config={"max_tokens": 3000},
        timeout_s=timeout_s,
    )

    return str(first.get("content") or ""), str(second.get("content") or "")


def main() -> None:
    # Minimal demo (requires OPENROUTER_API_KEY env var or api_key=...).
    response = LLM("hello", reasoning_enabled=True)
    print("Response:")
    print(response)


if __name__ == "__main__":
    main()