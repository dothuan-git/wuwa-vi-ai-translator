import re
import json
import requests

from utils import read_json, build_prompt
from default_params import DEFAULT_CONFIG

GROQ_URL = DEFAULT_CONFIG["groq_api_url"]
system_prompt = DEFAULT_CONFIG["system_prompt"]
user_prompt = DEFAULT_CONFIG["user_prompt"]

_THINK_RE_CLOSED = re.compile(r'<think>.*?</think>', re.DOTALL)
_THINK_RE_OPEN = re.compile(r'<think>.*', re.DOTALL)


def _strip_think(text: str) -> str:
    text = _THINK_RE_CLOSED.sub('', text)
    text = _THINK_RE_OPEN.sub('', text)
    return text.strip()


def _build_messages(dialogue, speaker, history):
    MAX_HISTORY = 3
    MAX_ENTRY_LEN = 500
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for orig, trans in history[-MAX_HISTORY:]:
            messages.append({"role": "user", "content": orig[:MAX_ENTRY_LEN]})
            messages.append({"role": "assistant", "content": trans[:MAX_ENTRY_LEN]})
    messages.append({"role": "user", "content": build_prompt(user_prompt, dialogue, speaker)})
    return messages


def translate_with_llama(dialogue, speaker="unknown", history=None, on_chunk=None):
    """Translate dialogue via Groq API.

    If on_chunk is provided, streams the response and calls on_chunk(partial_text)
    incrementally. Returns the final cleaned translation string.
    """
    if not dialogue.strip():
        return "Không phát hiện văn bản."

    config = read_json("config.json")
    api_key = config.get("groq_api_key", "")
    model = config.get("groq_model", DEFAULT_CONFIG["groq_model"])

    messages = _build_messages(dialogue, speaker, history)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "stream": bool(on_chunk),
    }

    try:
        if on_chunk:
            return _stream_translate(headers, payload, on_chunk)
        else:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            return _strip_think(text)
    except requests.HTTPError as e:
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text
        return f"[Translation Error] {e.response.status_code}: {detail}"
    except Exception as e:
        return f"[Translation Error] {str(e)}"


def _stream_translate(headers, payload, on_chunk):
    """Stream SSE response from Groq and call on_chunk with visible partial text."""
    accumulated = ""

    try:
        with requests.post(
            GROQ_URL, headers=headers, json=payload, stream=True, timeout=60
        ) as response:
            if not response.ok:
                try:
                    detail = response.json()
                except Exception:
                    detail = response.text
                return f"[Translation Error] {response.status_code}: {detail}"
            response.raise_for_status()
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if not delta:
                        continue
                    accumulated += delta

                    # Track <think> blocks — don't display while inside them
                    visible = _compute_visible(accumulated)
                    on_chunk(visible)
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
    except Exception as e:
        accumulated = f"[Translation Error] {str(e)}"

    return _strip_think(accumulated)


def _compute_visible(text: str) -> str:
    """Return text with closed <think> blocks removed; hide unclosed ones."""
    text = _THINK_RE_CLOSED.sub('', text)
    # If there's an unclosed <think>, hide everything from it onward
    think_start = text.find('<think>')
    if think_start != -1:
        text = text[:think_start]
    return text.strip()
