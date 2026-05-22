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
OTHER_TO_LISTENER_OPTIONS = ["bạn", "cậu", "em", "ngươi", "anh", "cô"]

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
    "custom_prompt_rover": "",
    "custom_prompt_npc": "",
    "user_prompt": "Translate this Wuthering Waves dialog to Vietnamese.",
}


# ── System prompt pieces ──────────────────────────────────────────────────────
# The system prompt is assembled per turn so the PRONOUNS section is specialized
# to whoever is speaking (Rover, NPC, or narration). HEAD and TAIL are shared.

SYSTEM_PROMPT_HEAD = (
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
)

PRONOUNS_BLOCK_ROVER = (
    "PRONOUNS — this turn is spoken by Rover (the player character).\n"
    "Each turn provides only the tags relevant to the current speaker. "
    "Apply them literally to THIS line; do NOT infer or substitute.\n"
    "- [Speaker: Rover] — confirms Rover is speaking.\n"
    "- [Rover-self: X] — use X as Rover's 1st-person pronoun in this line.\n"
    "- [Rover-to-N: Y] — use Y when Rover addresses the named character N.\n"
    "Any tag may be absent — infer naturally for that dimension only.\n\n"
)

PRONOUNS_BLOCK_NPC = (
    "PRONOUNS — this turn is spoken by an NPC.\n"
    "Each turn provides only the tags relevant to the current speaker. "
    "Apply them literally to THIS line; do NOT infer or substitute.\n"
    "- [Speaker: N] — the NPC delivering this line.\n"
    "- [N-self: Z] — use Z as N's 1st-person pronoun in this line.\n"
    "- [N-to-Rover: W] — use W when N addresses Rover.\n"
    "Any tag may be absent — infer naturally for that dimension only.\n\n"
)

PRONOUNS_BLOCK_NARRATION = (
    "PRONOUNS — this turn has no identified speaker (narration or system text).\n"
    "Stay neutral; drop pronouns where natural in Vietnamese.\n\n"
)

SYSTEM_PROMPT_TAIL = (
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
)


def build_system_prompt(speaker):
    """Assemble the system prompt with a PRONOUNS section specialized to the speaker."""
    if speaker == "Rover":
        block = PRONOUNS_BLOCK_ROVER
    elif speaker and speaker != "unknown":
        block = PRONOUNS_BLOCK_NPC
    else:
        block = PRONOUNS_BLOCK_NARRATION
    return SYSTEM_PROMPT_HEAD + block + SYSTEM_PROMPT_TAIL
