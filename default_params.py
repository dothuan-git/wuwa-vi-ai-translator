DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "easyocr_lg": [
        "en"
    ],
    "system_prompt": "You are a professional English to Vietnamese translator for story-driven RPG game. Your task is to translate dialogues and narration in a fluent, natural, and emotionally appropriate manner. A dialog is constructed as 'Speaker name, line break, dialogue'. Prioritize meaning and tone over literal word-for-word translation. Output only the Vietnamese translation. Do not include any labels, explanations, or commentary of any kind.",
    "user_prompt": "Translate the following English text into Vietnamese, following these guidelines:\n- Do not translate proper names or capitalized name.\n- Do not include meaningless sentences.\n- Rephrase the entire dialog for natural flow and fluency.\n- Translate all text including the text inside parentheses, but treat text in parentheses as UI labels or player action choices, not spoken dialogue."
}