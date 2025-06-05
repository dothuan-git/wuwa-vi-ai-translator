import json
import re
import os
import sys

# Ensure the script is run from the correct directory
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
    print(f"Reading JSON file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Standardize dialog format
def standardize_dialog(lines):
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


# Get character gender
def get_gender(characters, name):
    return characters.get(name, {}).get("gender", "unknown")


# Build prompt with pronouns based on speaker and listener
characters = read_json("characters.json")
def build_prompt_with_pronouns(user_prompt, custom_prompt, dialogue, speaker_name):
    # Setup names
    listener_name = "Rover"
    listener_gender = get_gender(characters, listener_name)
    speaker_gender = get_gender(characters, speaker_name)

    # Define pronouns
    pronouns = {
        "male": {"I": "anh", "you_to_male": "cậu", "you_to_female": "em"},
        "female": {"I": "em", "you_to_male": "anh", "you_to_female": "em"},
        "unknown": {"I": "tôi", "you": "bạn"}
    }

    # Add pronoun instruction only if speaker gender is known
    if speaker_name == "Rover":
        gender_hint = ""
    elif speaker_gender == "unknown":
        gender_hint = (
            f"\nCharacter context:\n"
            f"- Speaker: {speaker_name} (gender: unknown)\n"
            f"- Listener: {listener_name} (gender: {listener_gender})\n"
            f"- Infer speaker gender from their name, then apply appropriate Vietnamese pronouns based on gender of speaker and listener."
        )
    else:
        i_pronoun = pronouns[speaker_gender]["I"]
        you_pronoun = pronouns[speaker_gender][f"you_to_{listener_gender}"]

        gender_hint = (
            f"\nCharacter context:\n"
            f"- Speaker: {speaker_name} (gender: {speaker_gender})\n"
            f"- Listener: {listener_name} (gender: {listener_gender})\n"
            f"- Translate first-person \"I\" as \"{i_pronoun}\" and second-person \"you\" as \"{you_pronoun}\" in Vietnamese."
        )

    # Final prompt
    if len(custom_prompt.strip()) > 4:
        return user_prompt + gender_hint + "\n" + custom_prompt + "\n\nEnglish text:\n" + dialogue
    else:
        return user_prompt + gender_hint + "\n\nEnglish text:\n" + dialogue
