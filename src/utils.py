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
    """Write default config.json on first run; initialise/migrate characters.json.

    characters.json new schema: {speaker_name: {self_pronoun, addressee_pronoun}}
    Old schema (entries with 'gender' or 'role' fields) is backed up and replaced
    with an empty dict so the new system starts fresh.
    """
    from default_params import DEFAULT_CONFIG

    config_path = get_appdata_file_path("config.json")
    if not os.path.exists(config_path):
        write_json("config.json", DEFAULT_CONFIG)
    else:
        # Migrate old rover_pronoun → rover_self if present
        try:
            cfg = read_json("config.json")
            if "rover_pronoun" in cfg and "rover_self" not in cfg:
                cfg["rover_self"] = cfg.pop("rover_pronoun")
                write_json("config.json", cfg)
        except Exception:
            pass

    chars_path = get_appdata_file_path("characters.json")
    if not os.path.exists(chars_path):
        write_json("characters.json", {})
        return

    try:
        existing = read_json("characters.json")
    except Exception:
        return  # corrupt — leave it for the user to fix

    if not isinstance(existing, dict):
        return

    # Detect old schema (any entry has 'gender' or 'role')
    is_old_schema = any(
        isinstance(v, dict) and ("gender" in v or "role" in v)
        for v in existing.values()
    )
    if is_old_schema:
        bak_path = get_appdata_file_path("characters.json.bak")
        with open(get_appdata_file_path("characters.json"), "r", encoding="utf-8") as f:
            bak_content = f.read()
        with open(bak_path, "w", encoding="utf-8") as f:
            f.write(bak_content)
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


def _get_known_names():
    """Return the set of character names from characters.json."""
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


def _compose_request(user_prompt, dialogue, speaker, pronouns=None, custom_prompt=""):
    prompt = user_prompt
    if pronouns and speaker and speaker != UNKNOWN_SPEAKER:
        parts = []
        if pronouns.get("rover_self"):
            parts.append(f"[Rover-self: {pronouns['rover_self']}]")
        if pronouns.get("rover_to_other"):
            parts.append(f"[Rover-to-other: {pronouns['rover_to_other']}]")
        if speaker != "Rover":
            if pronouns.get("other_self"):
                parts.append(f"[Other-self: {pronouns['other_self']}]")
            if pronouns.get("other_to_rover"):
                parts.append(f"[Other-to-Rover: {pronouns['other_to_rover']}]")
        if parts:
            prompt += "\n" + " ".join(parts)
    if custom_prompt and len(custom_prompt.strip()) > 4:
        prompt += "\nPrioritize this rule:\n" + custom_prompt
    prompt += "\n\nEnglish text:\n" + dialogue
    return prompt


def build_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER, pronouns=None):
    """Live-turn user message: includes the user's custom rule."""
    custom_prompt = read_json("config.json").get("custom_prompt", "")
    return _compose_request(user_prompt, dialogue, speaker, pronouns, custom_prompt)


def build_history_prompt(user_prompt, dialogue, speaker=UNKNOWN_SPEAKER, pronouns=None):
    """History user message: same structure as the live turn but without the custom rule."""
    return _compose_request(user_prompt, dialogue, speaker, pronouns)
