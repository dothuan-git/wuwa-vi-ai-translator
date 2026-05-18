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
    """Write default config.json on first run; seed/update characters.json.

    - Missing file: write DEFAULT_CHARACTERS.
    - Empty dict: write DEFAULT_CHARACTERS.
    - Non-empty dict: merge — add any DEFAULT_CHARACTERS keys not already
      present (never overwrites user-customised entries, so custom pronouns
      and deletions are respected for existing keys).
    - Corrupt file: leave it for the user to fix.
    """
    from default_params import DEFAULT_CONFIG, DEFAULT_CHARACTERS

    config_path = get_appdata_file_path("config.json")
    if not os.path.exists(config_path):
        write_json("config.json", DEFAULT_CONFIG)

    chars_path = get_appdata_file_path("characters.json")
    if not os.path.exists(chars_path):
        write_json("characters.json", DEFAULT_CHARACTERS)
        return

    try:
        existing = read_json("characters.json")
    except Exception:
        return  # corrupt — leave it for the user to fix

    if not isinstance(existing, dict):
        return

    if not existing:
        write_json("characters.json", DEFAULT_CHARACTERS)
    else:
        new_entries = {k: v for k, v in DEFAULT_CHARACTERS.items()
                       if k not in existing}
        if new_entries:
            existing.update(new_entries)
            write_json("characters.json", existing)


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


def _get_known_names():
    """Return the set of character names from characters.json.
    Called once per capture; the file is small so no caching needed."""
    try:
        chars = read_json("characters.json")
        return set(chars.keys()) if isinstance(chars, dict) else set()
    except Exception:
        return set()


def standardize_dialog(lines):
    """Return (speaker, dialogue, original) where dialogue is always the
    normalized text sent to the model. speaker is UNKNOWN_SPEAKER when no
    speaker label is present (narration / system text).

    Speaker detection priority:
      1. 'F' marker → Rover (interact prompt).
      2. First line is an exact known character name → speaker confirmed.
      3. Heuristic (_looks_like_speaker) → catches unnamed NPCs.
      4. No speaker found → UNKNOWN_SPEAKER (narration / system text).
    """
    parts = [p.strip() for p in lines.strip().split('\n') if p.strip()]
    if not parts:
        return UNKNOWN_SPEAKER, "", ""

    # "F" is the in-game interact prompt shown when Rover speaks.
    if any(p == 'F' for p in parts):
        dialogue = _normalize(' '.join(p for p in parts if p != 'F'))
        return "Rover", dialogue, dialogue

    if len(parts) >= 2:
        candidate = parts[0]
        known_names = _get_known_names()
        is_speaker = (candidate in known_names) or _looks_like_speaker(candidate)
        if is_speaker:
            return candidate, _normalize(' '.join(parts[1:])), _normalize(' '.join(parts[1:]))

    return UNKNOWN_SPEAKER, _normalize(' '.join(parts)), _normalize(' '.join(parts))


def _compose_request(user_prompt, dialogue, speaker, addressee=UNKNOWN_SPEAKER,
                     custom_prompt=""):
    prompt = user_prompt
    if speaker and speaker != UNKNOWN_SPEAKER:
        prompt += f"\n[Speaker: {speaker}]"
        # Addressee only makes sense relative to a known speaker.
        if addressee and addressee != UNKNOWN_SPEAKER and addressee != speaker:
            prompt += f"\n[Addressee: {addressee}]"
    if custom_prompt and len(custom_prompt.strip()) > 4:
        prompt += "\nPrioritize this rule:\n" + custom_prompt
    prompt += "\n\nEnglish text:\n" + dialogue
    return prompt


def build_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER,
                 addressee=UNKNOWN_SPEAKER):
    """Live-turn user message: includes the user's custom rule."""
    custom_prompt = read_json("config.json").get("custom_prompt", "")
    return _compose_request(user_prompt, dialogue, speaker, addressee,
                            custom_prompt)


def build_history_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER,
                         addressee=UNKNOWN_SPEAKER):
    """History user message: same structure as the live turn (so few-shot
    examples match the real query) but without repeating the custom rule."""
    return _compose_request(user_prompt, dialogue, speaker, addressee)


_ROVER_PRONOUN_PAIRS = {
    "tôi": "xưng 'tôi', gọi người kia là 'bạn'; cặp tôi–bạn (trung tính, lịch sự)",
    "tớ": "xưng 'tớ', gọi người kia là 'cậu'; cặp tớ–cậu (trẻ trung, thân mật)",
    "anh": "xưng 'anh', gọi người kia là 'em'; cặp anh–em (Rover vai anh/đàn anh)",
    "ta": "xưng 'ta', gọi người kia là 'ngươi'; cặp ta–ngươi (cổ kính, thù địch)",
}
_ROVER_GENDER_VI = {"male": "nam", "female": "nữ"}


def build_glossary(filter_names=None, max_entries=60):
    """Build a character/term glossary block for the given participants.

    filter_names: set of speaker/addressee names seen in the current turn +
    history. Only entries whose key is in filter_names are included. Pass
    None to include all (legacy behaviour). Returns "" when no entries match
    so the section is omitted entirely from the prompt.
    """
    try:
        characters = read_json("characters.json")
    except Exception:
        return ""
    if not isinstance(characters, dict) or not characters:
        return ""

    # Override Rover's pronoun note from config so it always reflects the
    # player's chosen pronoun, even if characters.json has a stale value.
    if "Rover" in characters and isinstance(characters["Rover"], dict):
        cfg = read_json("config.json")
        rover_gender = cfg.get("rover_gender", "male")
        rover_pronoun = cfg.get("rover_pronoun", "tôi")
        rover_entry = dict(characters["Rover"])
        rover_entry["gender"] = _ROVER_GENDER_VI.get(rover_gender, "nam")
        rover_entry["pronoun"] = _ROVER_PRONOUN_PAIRS.get(rover_pronoun, _ROVER_PRONOUN_PAIRS["tôi"])
        characters = dict(characters)
        characters["Rover"] = rover_entry

    if filter_names is not None:
        characters = {k: v for k, v in characters.items() if k in filter_names}

    if not characters:
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
