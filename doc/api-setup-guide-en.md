# 🔑 API Key Setup Guide

To enable high-accuracy OCR and AI-powered translation in **Wuwa AI Vietnamese Translator**, you’ll need to obtain **two API keys**:

- ✅ **Groq API Key** — for GenAI translation
- ✅ **Google Vision API Key** — for OCR (text recognition)


## 1. Groq API Key (LLaMA 3 Translation)

This key is **required** for using the AI translator.

### 🛠️ Steps to get your Groq API Key:

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys).
![image](https://github.com/user-attachments/assets/124cf025-2c83-4fbc-932e-77469a505714)

3. Sign in or create a free Groq account.
![image](https://github.com/user-attachments/assets/c8b4c76a-2298-4270-a7de-6e958338d8fd)

5. Click **Create API Key**. Can name anything you want.
![image](https://github.com/user-attachments/assets/3b0bba33-9831-4675-a0ff-00e7a5b02a9e)

7. Copy the generated key.
![image](https://github.com/user-attachments/assets/45d720f5-048f-40c0-955a-bd69957f506f)



## 2. Google Vision API Key (OCR) - skip if you dont want to use

This key is **optional** but **recommended** to boost text detection accuracy in-game.
- Video guide: https://youtu.be/zF27tW5bEMY


### 🛠️ Steps to get your Google Vision API Key:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/). Login via your gmail.
![image](https://github.com/user-attachments/assets/90594469-021f-4b49-9766-5c489adcb10f)

3. Click the project drop-down at the top and select **New Project** - Can use any name (or reuse an existing one).
![image](https://github.com/user-attachments/assets/f1297e3e-a411-4f41-bc25-5bdfbca9f6b6)
![image](https://github.com/user-attachments/assets/50467b25-a41f-4615-b769-7e336a9f18b0)
![image](https://github.com/user-attachments/assets/c74eedd6-d691-41a0-9abb-399fbbce0c9d)
![image](https://github.com/user-attachments/assets/df9f4764-3c2d-4ae1-87e7-34c0442e9d3a)
![image](https://github.com/user-attachments/assets/61a4504e-96a7-4653-99da-6fc76f1b784e)


5. After creating the project, go to **APIs & Services**.
![image](https://github.com/user-attachments/assets/f99bc319-c4d0-475b-a74a-6ef8bebf7ca3)

7. In the search bar, type `Vision API` and click **Enable**.
![image](https://github.com/user-attachments/assets/3f83bef4-26f9-42c5-879e-0eb31815bb6c)
![image](https://github.com/user-attachments/assets/b3b24785-a282-4306-b80b-60404e4e468b)
![image](https://github.com/user-attachments/assets/4fb14019-c8f8-4452-9987-ae21c89fc9fb)
![image](https://github.com/user-attachments/assets/c32840d6-64f3-4059-994f-d8eb22096e34)

9. Navigate to **APIs & Services > Credentials** in the sidebar.
![image](https://github.com/user-attachments/assets/a1410936-1ad7-43a3-848f-4b50100f4c55)

11. Click **Create Credentials > API Key**.
![image](https://github.com/user-attachments/assets/19469fc9-c0aa-47d4-9dee-8b2931cd34e7)

13. A popup will show your API key — **copy this key** and save it.
![image](https://github.com/user-attachments/assets/194659ec-5232-4ad7-9f6f-6a993f5736e6)

15. ✅ **Enable Billing** for your Google Cloud project:
   - The Vision API gives **1,000 free requests/month**.
   - After the free quota, the next 1,000 requests cost approximately **$1.50 USD**.
   - You won’t be charged unless you exceed the free limit.
![image](https://github.com/user-attachments/assets/ba5fca06-e6ab-4361-83a2-d2863bcd7418)
![image](https://github.com/user-attachments/assets/53062a00-50c5-434c-8f0f-d603300dc15e)
![image](https://github.com/user-attachments/assets/594ea830-8afe-4b33-9acf-03f2424ad9d0)

### 🔽 Paste into the App:

- Launch the app and click the **`Config`** button.
- Paste your API key into the **GOOGLE VISION API_KEY** field.


## 💾 Final Step: Save Config

After entering both keys:
- Click the **Save** button in the settings window.


## 🧩 Troubleshooting

If you encounter issues (e.g. errors in the console window):

- Double-check that your API keys are valid and correctly pasted.
- Ensure your internet connection is active.
- Make sure **Google Cloud Billing is enabled** if using Vision API.


Enjoy seamless and high-quality Vietnamese translations with **Wuwa AI Translator** 🇻🇳✨
