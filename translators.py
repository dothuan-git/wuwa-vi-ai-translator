
import requests
import json

from utils import *


# ============================= GLOBAL PARAMS =============================
with open("config.json", "r", encoding='utf-8') as f:
    config = json.load(f)

# Groq API settings
GROQ_API_KEY = config["groq_api_key"]
GROQ_URL     = config["groq_api_url"]

# Retrieve prompts from config
system_prompt = config["system_prompt"]
user_prompt   = config["user_prompt"]
custom_prompt = config["custom_prompt"]
# =========================================================================


# Translation with LLaMA 3 via Groq
def translate_with_llama3(dialogue, speaker):
    if not dialogue.strip():
        return "Không phát hiện văn bản."
    
    # Build the refined prompt with pronouns
    refined_prompt = build_prompt_with_pronouns(user_prompt, custom_prompt, dialogue, speaker)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": refined_prompt}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        text_response = response.json()["choices"][0]["message"]["content"].strip()
        return text_response
    except Exception as e:
        return f"[LLaMA Error] {str(e)}"