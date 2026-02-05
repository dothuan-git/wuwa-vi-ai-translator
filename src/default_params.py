GROQ_MODELS = [
    "moonshotai/kimi-k2-instruct-0905",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "openai/gpt-oss-120b",
]

DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "groq_model": "moonshotai/kimi-k2-instruct-0905",
    "easyocr_lg": [
        "en"
    ],
    "system_prompt": "You are a professional Vietnamese translator for the game Wuthering Waves (Mingchao). Translate English dialog to natural, emotionally resonant Vietnamese.\n\nGAME CONTEXT:\n- Wuthering Waves is an action RPG set in a post-apocalyptic world recovering from the Lament\n- Key terms to preserve in English: Resonator, Tacet Discord, Tacet Field, Echo, Sonance, Union, Huanglong, Rinascita\n- Rover is the protagonist (player character)\n- Maintain consistency with previous translations in this conversation\n\nTRANSLATION RULES:\n- Prioritize natural Vietnamese flow over literal accuracy\n- Use appropriate Vietnamese honorifics based on character gender and relationships\n- Maintain character personality and speaking style\n- Keep game-specific terminology consistent throughout the session\n- Adapt idioms to Vietnamese equivalents when appropriate\n\nOUTPUT: Provide only the Vietnamese translation, no explanations.",
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}