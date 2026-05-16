GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
    "gemma2-9b-it",
]

OCR_ENGINES = ["windows", "easyocr", "google"]

DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "groq_model": "llama-3.3-70b-versatile",
    "ocr_engine": "windows",
    "hotkey": "ctrl+shift+space",
    "easyocr_lg": ["en"],
    "google_ocr_api_key": "",
    "groq_api_key": "",
    "custom_prompt": "",
    "system_prompt": (
        "You are a professional Vietnamese translator for the game Wuthering Waves (Mingchao). "
        "Translate English dialog to natural, emotionally resonant Vietnamese.\n\n"
        "GAME CONTEXT:\n"
        "- Wuthering Waves is an action RPG set in a post-apocalyptic world recovering from the Lament\n"
        "- Key terms to preserve in English: Resonator, Tacet Discord, Tacet Field, Echo, Sonance, Union, Huanglong, Rinascita\n"
        "- Rover is the protagonist (player character)\n"
        "- Maintain consistency with previous translations in this conversation\n\n"
        "TRANSLATION RULES:\n"
        "- Prioritize natural Vietnamese flow over literal accuracy\n"
        "- Use appropriate Vietnamese honorifics based on character gender and relationships\n"
        "- Maintain character personality and speaking style\n"
        "- Keep game-specific terminology consistent throughout the session\n"
        "- Adapt idioms to Vietnamese equivalents when appropriate\n\n"
        "OUTPUT: Provide only the Vietnamese translation, no explanations."
    ),
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}
