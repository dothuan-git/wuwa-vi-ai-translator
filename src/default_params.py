PROVIDERS = ["groq"]

GROQ_MODELS = [
    "qwen/qwen3-32b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

MODELS_BY_PROVIDER = {
    "groq": GROQ_MODELS,
}

OCR_ENGINES = ["windows", "easyocr", "google"]

DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "provider": "groq",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "groq_model": "qwen/qwen3-32b",
    "groq_api_key": "",
    "ocr_engine": "windows",
    "hotkey": "ctrl+shift+space",
    "easyocr_lg": ["en"],
    "google_ocr_api_key": "",
    "custom_prompt": "",
    "system_prompt": (
        "You are a professional Vietnamese translator for the game Wuthering Waves (Mingchao). "
        "Translate English dialog to natural, emotionally resonant Vietnamese.\n\n"
        "GAME CONTEXT:\n"
        "- Wuthering Waves is an action RPG set in a post-apocalyptic world recovering from the Lament\n"
        "- Keep these terms in English (do not translate): Resonator, Tacet Discord, Tacet Field, "
        "Echo, Sonance, Sonance Casket, Forte, Concerto, Resonance, Union, Sentinel, Threnodian, "
        "the Lament, Reverberation, Coordinated Attack\n"
        "- Keep proper nouns in English: Huanglong, Jinzhou, Rinascita, Black Shores, "
        "Mt. Firmament, Tiger's Maw, Court of Savantae, Solaris-3\n"
        "- Rover is the protagonist (player character); when the speaker is Rover, write in first person\n"
        "- Maintain consistency with previous translations in this conversation\n\n"
        "TRANSLATION RULES:\n"
        "- The English text is extracted by OCR and may contain recognition errors: split or merged "
        "words, missing/extra letters, or stray characters. Infer the intended meaning from context; "
        "do not translate obvious artifacts literally, and never describe or comment on OCR errors\n"
        "- The capture may be a partial or mid-sentence fragment; translate it as-is without inventing "
        "a continuation\n"
        "- Prioritize natural Vietnamese flow over literal accuracy\n"
        "- Use appropriate Vietnamese honorifics/pronouns based on character gender, age and "
        "relationships; keep each character's pronouns consistent across the session\n"
        "- Maintain character personality and speaking style\n"
        "- Keep game-specific terminology consistent throughout the session\n"
        "- Adapt idioms to Vietnamese equivalents when appropriate\n\n"
        "OUTPUT: Provide only the Vietnamese translation, with no preamble, notes, or explanations."
    ),
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}
