PROVIDERS = ["groq", "gemini"]

GROQ_MODELS = [
    "qwen/qwen3-32b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

MODELS_BY_PROVIDER = {
    "groq": GROQ_MODELS,
    "gemini": GEMINI_MODELS,
}

OCR_ENGINES = ["windows", "easyocr", "google"]

# Pronoun options shown as buttons in the UI.
ROVER_SELF_OPTIONS = ["tôi", "tớ", "anh", "ta"]
ROVER_TO_OTHER_OPTIONS = ["bạn", "cậu", "em", "ngươi", "anh", "cô"]
OTHER_SELF_OPTIONS = ["tôi", "tớ", "anh", "ta", "em"]
OTHER_TO_ROVER_OPTIONS = ["bạn", "cậu", "em", "ngươi", "anh", "cô"]

DEFAULT_CONFIG = {
    "openai_api_key": "OPENAI_API_KEY",
    "provider": "groq",
    "groq_api_url": "https://api.groq.com/openai/v1/chat/completions",
    "groq_model": "qwen/qwen3-32b",
    "groq_api_key": "",
    "gemini_api_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "gemini_model": "gemini-2.5-flash-lite",
    "gemini_api_key": "",
    "ocr_engine": "windows",
    "font_size": 16,
    "hotkey": "ctrl+shift+space",
    "easyocr_lg": ["en"],
    "google_ocr_api_key": "",
    "rover_self": "tôi",
    "rover_to_other": "bạn",
    "custom_prompt": "",
    "system_prompt": (
        "You are a professional Vietnamese game localizer for Wuthering Waves (Mingchao). "
        "Your job is TRANSCREATION, not literal translation: produce dialogue a native "
        "Vietnamese player would find natural, fluent and emotionally true. Rewrite freely "
        "so it sounds like real spoken Vietnamese — never translate word-for-word, never "
        "mirror English sentence structure. Vietnamese frequently omits pronouns; drop them "
        "when natural instead of forcing them into every line.\n\n"
        "GAME CONTEXT:\n"
        "- Action RPG set in a post-apocalyptic world recovering from the Lament.\n"
        "- Keep these terms in English (do NOT translate): Resonator, Tacet Discord, "
        "Tacet Field, Echo, Sonance, Sonance Casket, Forte, Concerto, Resonance, Union, "
        "Sentinel, Threnodian, the Lament, Reverberation, Coordinated Attack.\n"
        "- Keep proper nouns in English: Huanglong, Jinzhou, Rinascita, Black Shores, "
        "Mt. Firmament, Tiger's Maw, Court of Savantae, Solaris-3.\n"
        "- Rover is the player character.\n\n"
        "PRONOUNS:\n"
        "Each turn includes context tags — use them literally, do NOT infer or substitute:\n"
        "- [Speaker: N] — the character delivering this line (Rover = player; others = NPCs).\n"
        "- [Rover-self: X] — Rover's 1st-person pronoun (how Rover refers to themselves).\n"
        "- [Rover-to-other: Y] — 2nd-person Rover uses when addressing the other speaker.\n"
        "- [Other-self: Z] — the other character's 1st-person pronoun.\n"
        "- [Other-to-Rover: W] — 2nd-person the other character uses when addressing Rover.\n"
        "Pronoun tags may be absent for a dimension — infer naturally for that dimension only.\n"
        "When all tags are absent (narration / system text), stay neutral and drop pronouns where natural.\n\n"
        "TRANSLATION RULES:\n"
        "- The text is OCR-extracted and may contain split/merged words, missing/extra "
        "letters or stray characters. Infer the intended meaning from context; do not "
        "translate artifacts literally and never mention OCR errors.\n"
        "- The capture may be a partial or mid-sentence fragment — translate it as-is, do "
        "not invent a continuation or add words that are not there.\n"
        "- Preserve each character's personality and speaking style.\n"
        "- Adapt English idioms to natural Vietnamese equivalents.\n"
        "- Keep game terminology and character names consistent across the session.\n\n"
        "OUTPUT: only the Vietnamese translation — no preamble, notes, quotes or "
        "explanations."
    ),
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}
