# 🔑 API Key Setup Guide

To enable high-accuracy OCR and AI-powered translation in **Wuwa AI Vietnamese Translator**, you’ll need to obtain **two API keys**:

- ✅ **Google Vision API Key** — for OCR (text recognition)
- ✅ **Groq API Key** — for GenAI translation

---

## 1. Google Vision API Key (OCR)

This key is **optional** but **recommended** to boost text detection accuracy in-game.

### 🛠️ Steps to get your Google Vision API Key:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project drop-down at the top and select **New Project** (or reuse an existing one).
3. After creating the project, go to **APIs & Services > Library**.
4. In the search bar, type `Vision API` and click **Enable**.
5. Navigate to **APIs & Services > Credentials** in the sidebar.
6. Click **Create Credentials > API Key**.
7. A popup will show your API key — **copy this key** and save it.
8. ✅ **Enable Billing** for your Google Cloud project:
   - The Vision API gives **1,000 free requests/month**.
   - After the free quota, the next 1,000 requests cost approximately **$1.50 USD**.
   - You won’t be charged unless you exceed the free limit.

### 🔽 Paste into the App:

- Launch the app and click the **`Config`** button.
- Paste your API key into the **GOOGLE VISION API_KEY** field.

---

## 2. Groq API Key (LLaMA 3 Translation)

This key is **required** for using the AI translator.

### 🛠️ Steps to get your Groq API Key:

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys).
2. Sign in or create a free Groq account.
3. Click **Create API Key**.
4. Copy the generated key.

### 🔽 Paste into the App:

- Open the app and click the **`Config`** button.
- Paste your key into the **GROQ API KEY** field.

---

## 💾 Final Step: Save Config

After entering both keys:
- Click the **Save** button in the settings window.

---

## 🧩 Troubleshooting

If you encounter issues (e.g. errors in the console window):

- Double-check that your API keys are valid and correctly pasted.
- Ensure your internet connection is active.
- Make sure **Google Cloud Billing is enabled** if using Vision API.

---

Enjoy seamless and high-quality Vietnamese translations with **Wuwa AI Translator** 🇻🇳✨
