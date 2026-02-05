
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
    GROQ_API_KEY = read_json("config.json")["groq_api_key"]

    if not dialogue.strip():
        return "Không phát hiện văn bản."

    refined_prompt = build_prompt(user_prompt, dialogue, speaker)

    # Build multi-turn messages with conversation history
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for orig, trans in history:
            messages.append({"role": "user", "content": orig})
            messages.append({"role": "assistant", "content": trans})
    messages.append({"role": "user", "content": refined_prompt})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen/qwen-3-32b",
        "messages": messages,
        "temperature": 0.3
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        text_response = response.json()["choices"][0]["message"]["content"].strip()
        return text_response
    except Exception as e:
        return f"[LLaMA Error] {str(e)}"