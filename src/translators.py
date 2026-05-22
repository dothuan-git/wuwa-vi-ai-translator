import logging
import re
import json
import requests

from utils import (
    read_json,
    build_prompt,
    UNKNOWN_SPEAKER,
)
from default_params import DEFAULT_CONFIG, build_system_prompt

logger = logging.getLogger(__name__)

user_prompt = DEFAULT_CONFIG["user_prompt"]

_THINK_RE_CLOSED = re.compile(r'<think>.*?</think>', re.DOTALL)
_THINK_RE_OPEN = re.compile(r'<think>.*', re.DOTALL)


def _strip_think(text: str) -> str:
    text = _THINK_RE_CLOSED.sub('', text)
    text = _THINK_RE_OPEN.sub('', text)
    return text.strip()


def _clip(text, limit):
    """Truncate without splitting a word, so history examples stay clean."""
    if len(text) <= limit:
        return text
    head = text[:limit]
    return head.rsplit(' ', 1)[0] if ' ' in head else head


def _speaker_of(item):
    """Speaker label of a history item; tolerate legacy (orig, trans) pairs."""
    return item[0] if len(item) == 3 else UNKNOWN_SPEAKER


def _build_history_block(history, max_items=3, max_chars=300):
    """One-line-per-turn Vietnamese summary of recent translations, for voice and
    vocabulary continuity. Returns "" when there's no usable history."""
    if not history:
        return ""
    lines = []
    for item in history[-max_items:]:
        if len(item) == 3:
            h_speaker, _h_orig, h_trans = item
        else:
            _h_orig, h_trans = item
            h_speaker = UNKNOWN_SPEAKER
        if not h_trans or not h_trans.strip():
            continue
        label = h_speaker if h_speaker and h_speaker != UNKNOWN_SPEAKER else "Narration"
        lines.append(f"{label}: {_clip(h_trans, max_chars)}")
    if not lines:
        return ""
    return "Recent translated lines (for voice and vocabulary continuity):\n" + "\n".join(lines)


def _build_messages(dialogue, speaker, history, pronouns=None):
    history = history or []

    # System prompt's PRONOUNS section is specialized to the live turn's speaker.
    sys_msg = build_system_prompt(speaker)
    messages = [{"role": "system", "content": sys_msg}]

    live_user = build_prompt(user_prompt, dialogue, speaker, pronouns)
    history_block = _build_history_block(history)
    if history_block:
        live_user = history_block + "\n\n" + live_user

    messages.append({"role": "user", "content": live_user})
    return messages


def _log_prompt(provider, model, messages):
    """Dump the full message stack about to be sent, one block per role."""
    sep = "=" * 70
    lines = [f"\n{sep}\nPROMPT  provider={provider}  model={model}\n{sep}"]
    for m in messages:
        lines.append(f"[{m['role']}]\n{m['content']}")
    lines.append(sep)
    logger.info("\n".join(lines))


def translate_with_llama(dialogue, speaker="unknown", history=None, on_chunk=None, pronouns=None):
    """Translate dialogue via the configured AI provider.

    pronouns: dict with keys rover_self, rover_to_other, and optionally
    other_self, other_to_listener. None for narration (no pronoun tags injected).

    If on_chunk is provided, streams the response and calls on_chunk(partial_text)
    incrementally. Returns the final cleaned translation string.
    """
    if not dialogue.strip():
        return "Không phát hiện văn bản."

    config = read_json("config.json")
    provider = config.get("provider", DEFAULT_CONFIG["provider"])
    url = config.get(f"{provider}_api_url", DEFAULT_CONFIG[f"{provider}_api_url"])
    api_key = config.get(f"{provider}_api_key", "")
    model = config.get(f"{provider}_model", DEFAULT_CONFIG[f"{provider}_model"])

    messages = _build_messages(dialogue, speaker, history, pronouns)
    _log_prompt(provider, model, messages)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "stream": bool(on_chunk),
    }
    _m = model.lower()
    if "qwen" in _m or _m.startswith("gemini-2.5"):
        payload["reasoning_effort"] = "none"

    try:
        if on_chunk:
            return _stream_translate(url, headers, payload, on_chunk)
        else:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
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


def _stream_translate(url, headers, payload, on_chunk):
    """Stream SSE response from the provider and call on_chunk with visible partial text."""
    accumulated = ""

    try:
        with requests.post(
            url, headers=headers, json=payload, stream=True, timeout=60
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
    think_start = text.find('<think>')
    if think_start != -1:
        text = text[:think_start]
    return text.strip()
