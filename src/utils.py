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


def standardize_dialog(lines):
    characters = read_json("characters.json")
    cleaned = lines.strip().split('\n')

    if not cleaned:
        return "", "", ""

    if 'F' in cleaned:
        speaker = "Rover"
        remove_F = [line for line in cleaned if line.strip() != 'F']
        lines = "\n".join(remove_F).strip()
        full_text = ' '.join(remove_F)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        dialogue = re.sub(r'([.?!)])\s+', r'\1\n', full_text)
    else:
        speaker = cleaned[0]
        dialogue = "\n".join(cleaned[1:]) if len(cleaned) > 1 else ""
        dialogue = re.sub(r'\s+', ' ', dialogue).strip()

    if speaker in characters:
        dialog = f"{speaker}\n {dialogue.strip()}"
    else:
        dialog = lines.strip()

    return speaker, dialog, lines


def build_prompt(user_prompt, dialogue, speaker="unknown"):
    config = read_json("config.json")
    custom_prompt = config.get("custom_prompt", "")

    prompt = user_prompt
    if speaker and speaker != "unknown":
        prompt += f"\n[Speaker: {speaker}]"
    if len(custom_prompt.strip()) > 4:
        prompt += "\nPriotize this rule:\n" + custom_prompt
    prompt += "\n\nEnglish text:\n" + dialogue
    return prompt
