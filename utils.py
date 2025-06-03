import json
import re


with open('characters.json', 'r', encoding='utf-8') as f:
        characters = json.load(f)


# Standardize dialog format
def standardize_dialog(lines):
    cleaned = lines.strip().split('\n')
    print(cleaned)

    if not cleaned:
        return ""

    # If original list had 'F', we use Rover
    speaker = "Rover" if 'F' in cleaned else cleaned[0]

    # If speaker is Rover, get 1st line only
    if speaker == "Rover":
        remove_F = [line for line in cleaned if line.strip() != 'F']
        full_text = ' '.join(remove_F)
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        dialogue = re.sub(r'([.?!])\s+', r'\1\n', full_text)
    elif speaker in characters:
        dialogue = " ".join(cleaned[1:]) if len(cleaned) > 1 else ""
    else:
        dialogue = lines

    return speaker, dialogue


# Get character gender
def get_gender(characters, name):
    return characters.get(name, {}).get("gender", "unknown")


# Build prompt with pronouns based on speaker and listener
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
            f"\n\nCharacter context:\n"
            f"- Speaker: {speaker_name} (gender: unknown)\n"
            f"- Listener: {listener_name} (gender: {listener_gender})\n"
            f"- Infer speaker gender from their name, then apply appropriate Vietnamese pronouns based on gender of speaker and listener."
        )
    else:
        i_pronoun = pronouns[speaker_gender]["I"]
        you_pronoun = pronouns[speaker_gender][f"you_to_{listener_gender}"]

        gender_hint = (
            f"\n\nCharacter context:\n"
            f"- Speaker: {speaker_name} (gender: {speaker_gender})\n"
            f"- Listener: {listener_name} (gender: {listener_gender})\n"
            f"- Translate first-person \"I\" as \"{i_pronoun}\" and second-person \"you\" as \"{you_pronoun}\" in Vietnamese."
        )

    # Final prompt
    if len(custom_prompt.strip()) > 4:
        return user_prompt + gender_hint + "\n" + custom_prompt + "\n\nEnglish text:\n" + dialogue
    else:
        return user_prompt + gender_hint + "\n\nEnglish text:\n" + dialogue
