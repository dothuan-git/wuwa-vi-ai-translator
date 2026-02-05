
import re
import requests

from utils import read_json, build_prompt
from default_params import DEFAULT_CONFIG


# ============================= GLOBAL PARAMS =============================
# Groq API settings
GROQ_URL     = DEFAULT_CONFIG["groq_api_url"]

# Retrieve prompts from config
system_prompt = DEFAULT_CONFIG["system_prompt"]
user_prompt   = DEFAULT_CONFIG["user_prompt"]
# =========================================================================


# Translation with LLaMA via Groq
def translate_with_llama(dialogue, speaker="unknown", history=None):
    config = read_json("config.json")
    GROQ_API_KEY = config["groq_api_key"]
    model = config.get("groq_model", DEFAULT_CONFIG["groq_model"])

    if not dialogue.strip():
        return "Không phát hiện văn bản."

    refined_prompt = build_prompt(user_prompt, dialogue, speaker)

    # Build multi-turn messages with conversation history (truncated to avoid 413)
    MAX_HISTORY = 3
    MAX_ENTRY_LEN = 500
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for orig, trans in history[-MAX_HISTORY:]:
            messages.append({"role": "user", "content": orig[:MAX_ENTRY_LEN]})
            messages.append({"role": "assistant", "content": trans[:MAX_ENTRY_LEN]})
    messages.append({"role": "user", "content": refined_prompt})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        text_response = response.json()["choices"][0]["message"]["content"].strip()
        # Strip Qwen3 chain-of-thought: closed <think>...</think> and unclosed <think>...
        text_response = re.sub(r'<think>.*?</think>', '', text_response, flags=re.DOTALL)
        text_response = re.sub(r'<think>.*', '', text_response, flags=re.DOTALL)
        text_response = text_response.strip()
        return text_response
    except Exception as e:
        return f"[LLaMA Error] {str(e)}"