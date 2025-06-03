import os
import cv2
import numpy as np
import mss
import easyocr
import requests
from PIL import Image, ImageOps, ImageEnhance
import tkinter as tk
from tkinter import scrolledtext
import wordninja
import pytesseract

# Initialize EasyOCR
reader = easyocr.Reader(['en', 'ja'])

# Groq API settings
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Global region
region = {"top": 100, "left": 100, "width": 950, "height": 150}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0

# Main window
root = tk.Tk()
root.title("Game Translator (LLaMA 3 + Groq)")
root.geometry("400x450")
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Region selector window
selector = tk.Toplevel(root)
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)
selector.attributes("-topmost", True)
selector.overrideredirect(True)

canvas = tk.Canvas(selector, bg="blue", highlightthickness=2, highlightbackground="red")
canvas.pack(fill="both", expand=True)

# OCR with EasyOCR
def extract_text_from_image(pil_img):
    img = ImageOps.grayscale(pil_img)
    # Light contrast and brightness boost
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.1)

    # 2x upscale using LANCZOS (best for sharp edges)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img.save("temp_capture.png")

    # OCR
    result = reader.readtext("temp_capture.png", detail=0, paragraph=True)
    raw_text = '\n'.join(result)
    spaced_text = '\n'.join([' '.join(wordninja.split(line)) for line in raw_text.split('\n')])
    return spaced_text

# Translation with LLaMA 3 via Groq
def translate_with_llama3(text):
    if not text.strip():
        return "Không phát hiện văn bản."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",  # or llama3-8b-8192 if you prefer
        "messages": [
            {"role": "system", "content": "You are a professional English-to-Vietnamese translator for Wuthering Waves game."},
            {"role": "user", "content": f"Translate the following English text into Vietnamese. Do not translate proper names, character names and capital name (e.g., people, places, organizations). Return only the Vietnamese translation without additional explanation or formatting:\n{text}"}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        text_response = response.json()["choices"][0]["message"]["content"].strip()
        return text_response
    except Exception as e:
        return f"[LLaMA Error] {str(e)}"

# Capture only
def capture_text():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text = extract_text_from_image(img)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")

# Translate only
def translate_text_sync():
    text = text_area.get(1.0, tk.END).strip()
    translated = translate_with_llama3(text) if text else "Không phát hiện văn bản."
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, translated)

# Capture and translate
def capture_and_translate():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text = extract_text_from_image(img)
        translated = translate_with_llama3(text) if text.strip() else "Không phát hiện văn bản."
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")
        translated_text_area.delete(1.0, tk.END)
        translated_text_area.insert(tk.END, translated)

# Region interaction logic
def is_near_corner(x, y, width, height, threshold=10):
    corners = {
        "top-left": (0, 0),
        "top-right": (width, 0),
        "bottom-left": (0, height),
        "bottom-right": (width, height)
    }
    for corner, (cx, cy) in corners.items():
        if abs(x - cx) <= threshold and abs(y - cy) <= threshold:
            return corner
    return None

def start_interaction(event):
    global dragging, resizing, resize_corner, start_x, start_y
    resize_corner = is_near_corner(event.x, event.y, region["width"], region["height"])
    dragging = not resize_corner
    resizing = bool(resize_corner)
    start_x = event.x_root
    start_y = event.y_root

def stop_interaction(event):
    global dragging, resizing, resize_corner
    dragging = resizing = False
    resize_corner = None
    update_region()

def motion_interaction(event):
    global start_x, start_y
    dx = event.x_root - start_x
    dy = event.y_root - start_y

    if dragging:
        region["left"] += dx
        region["top"] += dy
    elif resizing and resize_corner:
        if resize_corner == "top-left":
            region["left"] += dx
            region["top"] += dy
            region["width"] -= dx
            region["height"] -= dy
        elif resize_corner == "top-right":
            region["top"] += dy
            region["width"] += dx
            region["height"] -= dy
        elif resize_corner == "bottom-left":
            region["left"] += dx
            region["width"] -= dx
            region["height"] += dy
        elif resize_corner == "bottom-right":
            region["width"] += dx
            region["height"] += dy
        region["width"] = max(region["width"], 50)
        region["height"] = max(region["height"], 50)

    selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
    start_x = event.x_root
    start_y = event.y_root

def update_region():
    region["left"] = selector.winfo_x()
    region["top"] = selector.winfo_y()
    region["width"] = selector.winfo_width()
    region["height"] = selector.winfo_height()
    print(f"Region updated: {region}")

canvas.bind("<Button-1>", start_interaction)
canvas.bind("<ButtonRelease-1>", stop_interaction)
canvas.bind("<B1-Motion>", motion_interaction)

# Buttons
tk.Button(root, text="Capture Text", command=capture_text).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
tk.Button(root, text="Translate Text", command=translate_text_sync).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
tk.Button(root, text="Capture and Translate", command=capture_and_translate).grid(row=0, column=2, sticky="ew", padx=5, pady=5)

# Text boxes
text_area = scrolledtext.ScrolledText(root, width=40, height=8)
text_area.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
translated_text_area = scrolledtext.ScrolledText(root, width=40, height=8)
translated_text_area.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Start GUI
root.mainloop()
