# Wuwa AI Vietnamese Translator

**Wuwa AI Vietnamese Translator** is a non-profit, fan-made application designed to translate dialogue and narration from the game *Wuthering Waves* from English to Vietnamese. By combining OCR (Optical Character Recognition) and cutting-edge generative AI, this tool delivers accurate and natural-sounding translations, enhancing your immersive game experience.


## 🎮 Features

1. **Capture and Translate**: Instantly capture on-screen English text and translate it using AI.
2. **Re-translate**: Refine translations (dont consume your Google OCR quota).
3. **Manual Input Support**: View or manually modify the captured English text before translating.
4. **OCR Engines**:
    - EasyOCR (default, offline, 100% free - slower, a bit less accuracy).
    - Google Vision OCR (online, higher accuracy, requires API key - read carefully the note below if you would like to use this engine).
5. **History Log**: Show/hide log history.
6. **Export Log**: Export the history log as a `.txt` file. (this file can be used by ChatGPT to summary the story).
7. **Vietnamese Pronoun Customization (Beta)**: Adjusts pronouns when characters speak to Rover.
8. **Custom Prompt**: Fine-tune AI behavior with your own instructions.
![guidance](https://github.com/user-attachments/assets/d7c0ddee-6a53-4ddd-b496-07e226da6379)


## 🧩 Requirements

- Windows OS 
- Stable Internet Connection
- [Groq API Key](https://console.groq.com/keys) — for AI translation (**Free**)
- [Google Cloud Vision API Key](https://cloud.google.com/vision/docs/setup):
   - Need credit/debit card to enable 
   - Optional, for better OCR accuracy (**Read the note below carefully to stay free**)

### 📌 Notes on Google Vision API:

- Google offers **3 months free** for new users (with generous credits).
- After that, you get **1,000 free OCR requests/month**.
- Beyond that, the cost is about **$1.50 USD per 1,000 additional requests**.
- You will not be charged unless you exceed the free limit.
- **Usage tip**: Based on experience, the free 1,000 requests/month are usually sufficient for following story quests.
- Need more? You can sign in with another Google account to get another API key and access an additional free 1,000 requests/month.

> Tip: To avoid unnecessary usage, use the **Re-translate** button instead of re-capturing if you’re just adjusting translations.


## 🛠️ How to Use

1. **Download & Install**
   - Get the latest release from the [Releases Page](https://github.com/dothuan-git/wuwa-vi-ai-translator/releases).
   - Right-click on `GioHuAI_Setup.exe` and select **"Run as administrator"**.
   - Choose to create a desktop shortcut for easier access.

2. **Initial Setup (Important)**
   - Launch the app.
   - Click the `Config` button in the bottom-right corner of the main window.
   - Fill in:
     - Your **Google Vision OCR API key** (optional but recommended for better accuracy).
     - Your **Groq API key** (required, for AI translation).
     - Custom prompt if desired.
     - Rover's name and gender (for pronoun adjustment).

   > See [this guide](https://github.com/dothuan-git/wuwa-vi-ai-translator/blob/main/doc/api-setup-guide-en.md) for API key setup instructions.

3. **Start Translating**
   - Position the blue semi-transparent canvas over the English text in the game.
   - Click **"Translate $"** to capture and translate.
   - Use **"Re-translate"** for refining results.
  
Demo video: https://youtu.be/XW4ggE_lIik

