import json
import re
import os
import sys


# Create folder if it doesn't exist
def check_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


# Get the appdata path to the json file
def get_appdata_file_path(file_path):
    # Use %APPDATA% for config storage
    APPDATA_DIR = os.getenv("APPDATA") or os.path.expanduser("~")
    APP_FOLDER = os.path.join(APPDATA_DIR, "GioHuAI")  # Use a subfolder for your app
    os.makedirs(APP_FOLDER, exist_ok=True)  # Ensure folder exists

    return os.path.join(APP_FOLDER, file_path)


# Read json file
def read_json(file_path):
    path = get_appdata_file_path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Standardize dialog format
def standardize_dialog(lines):
    characters = read_json("characters.json")
    cleaned = lines.strip().split('\n')
    print(cleaned)

    if not cleaned:
        return ""

    # If original list had 'F', we use Rover
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


# Build prompt with optional custom instructions
def build_prompt(user_prompt, dialogue):
    config = read_json("config.json")
    custom_prompt = config["custom_prompt"]

    if len(custom_prompt.strip()) > 4:
        return user_prompt + "\nPriotize this rule:\n" + custom_prompt + "\n\nEnglish text:\n" + dialogue
    else:
        return user_prompt + "\n\nOriginal English text:\n" + dialogue
