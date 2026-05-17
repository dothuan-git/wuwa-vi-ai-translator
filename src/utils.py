import json
import re
import os
import sys


def check_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def get_appdata_file_path(file_path):
    APPDATA_DIR = os.getenv("APPDATA") or os.path.expanduser("~")
    APP_FOLDER = os.path.join(APPDATA_DIR, "GioHuAI")
    os.makedirs(APP_FOLDER, exist_ok=True)
    return os.path.join(APP_FOLDER, file_path)


def read_json(file_path):
    path = get_appdata_file_path(file_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path, data):
    path = get_appdata_file_path(file_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def ensure_config():
    """Write default config.json and characters.json on first run."""
    from default_params import DEFAULT_CONFIG

    config_path = get_appdata_file_path("config.json")
    if not os.path.exists(config_path):
        write_json("config.json", DEFAULT_CONFIG)

    chars_path = get_appdata_file_path("characters.json")
    if not os.path.exists(chars_path):
        write_json("characters.json", {})


UNKNOWN_SPEAKER = "unknown"


def _normalize(text):
    """Join OCR line-wraps into a single clean block."""
    return re.sub(r'\s+', ' ', text).strip()


def _looks_like_speaker(line):
    """Heuristic: a Wuthering Waves speaker label is a short name with no
    sentence/clause punctuation. Reject sentences so narration is never
    mistaken for a speaker (which would drop the first line of dialogue)."""
    s = line.strip()
    if not s:
        return False
    if s == "???":  # in-game label for an unrevealed speaker
        return True
    if len(s) > 30 or len(s.split()) > 4:
        return False
    return not re.search(r'[.!?,:;"]', s)


def standardize_dialog(lines):
    """Return (speaker, dialogue, original) where dialogue is always the
    normalized text sent to the model. speaker is UNKNOWN_SPEAKER when no
    speaker label is present (narration / system text)."""
    parts = [p.strip() for p in lines.strip().split('\n') if p.strip()]
    if not parts:
        return UNKNOWN_SPEAKER, "", ""

    # "F" is the in-game interact prompt shown when Rover speaks.
    if any(p == 'F' for p in parts):
        dialogue = _normalize(' '.join(p for p in parts if p != 'F'))
        return "Rover", dialogue, dialogue

    if len(parts) >= 2 and _looks_like_speaker(parts[0]):
        speaker = parts[0]
        dialogue = _normalize(' '.join(parts[1:]))
    else:
        speaker = UNKNOWN_SPEAKER
        dialogue = _normalize(' '.join(parts))

    return speaker, dialogue, dialogue


def _compose_request(user_prompt, dialogue, speaker, custom_prompt=""):
    prompt = user_prompt
    if speaker and speaker != UNKNOWN_SPEAKER:
        prompt += f"\n[Speaker: {speaker}]"
    if custom_prompt and len(custom_prompt.strip()) > 4:
        prompt += "\nPrioritize this rule:\n" + custom_prompt
    prompt += "\n\nEnglish text:\n" + dialogue
    return prompt


def build_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER):
    """Live-turn user message: includes the user's custom rule."""
    custom_prompt = read_json("config.json").get("custom_prompt", "")
    return _compose_request(user_prompt, dialogue, speaker, custom_prompt)


def build_history_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER):
    """History user message: same structure as the live turn (so few-shot
    examples match the real query) but without repeating the custom rule."""
    return _compose_request(user_prompt, dialogue, speaker)


def build_glossary(max_entries=40):
    """Build a character/term glossary block from characters.json so the
    model keeps names and pronouns consistent. Returns "" when empty so it
    is a no-op until the user populates the file."""
    try:
        characters = read_json("characters.json")
    except Exception:
        return ""
    if not isinstance(characters, dict) or not characters:
        return ""

    entries = []
    for name, value in list(characters.items())[:max_entries]:
        if isinstance(value, dict):
            note = ", ".join(f"{k}: {v}" for k, v in value.items() if v)
        else:
            note = str(value).strip()
        entries.append(f"- {name}: {note}" if note else f"- {name}")

    return (
        "CHARACTER GLOSSARY (translate these names/terms consistently; "
        "use the given Vietnamese pronouns where provided):\n"
        + "\n".join(entries)
    )
