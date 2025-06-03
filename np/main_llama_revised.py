import os
import mss
import easyocr
import requests
from PIL import Image, ImageOps
import tkinter as tk
import wordninja

# Initialize EasyOCR
reader = easyocr.Reader(['en', 'ja'])

# Groq API settings
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Global region
region = {"top": 100, "left": 100, "width": 1200, "height": 150}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0
original_text_visible = False

# Main window
root = tk.Tk()
root.title("Wuwa AI Translator")
root.geometry("800x200")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)

# Region selector window
selector = tk.Toplevel(root)
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)
selector.attributes("-topmost", True)
selector.overrideredirect(True)

canvas = tk.Canvas(selector, bg="blue", highlightthickness=2, highlightbackground="red")
canvas.pack(fill="both", expand=True)

# OCR with EasyOCR
def extract_text_from_image(img):
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img = img.crop(img.getbbox())
    img.save("temp_capture.png")
    result = reader.readtext("temp_capture.png", detail=0, paragraph=True)
    raw_text = '\n'.join(result)
    return raw_text

# Translation with LLaMA 3 via Groq
def translate_with_llama3(text):
    if not text.strip():
        return "Không phát hiện văn bản."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional English-to-Vietnamese translator for Wuthering Waves game."},
            {"role": "user", "content": f"Translate the following English text into Vietnamese. Do not translate any proper names enclosed in brackets (e.g., [Tacet Discord], [Madam Magistrate], [Jianxing]). Keep these names exactly as they appear. Return only the Vietnamese translation without any additional explanation. Add punctuation if needed:\n{text}"}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()
        text_response = response.json()["choices"][0]["message"]["content"].strip()
        return text_response
    except Exception as e:
        return f"[LLaMA Error] {str(e)}"

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

# Translate text from original dialog
def translate_original_text():
    text = text_area.get(1.0, tk.END).strip()
    translated = translate_with_llama3(text) if text.strip() else "Không phát hiện văn bản."
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, translated)

# Toggle original text visibility
def toggle_original_text():
    global original_text_visible
    if original_text_visible:
        original_frame.grid_remove()
        show_text_button.config(text="Show\nOriginal")
    else:
        original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        show_text_button.config(text="Hide\nOriginal")
    original_text_visible = not original_text_visible

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

def update_cursor(event):
    corner = is_near_corner(event.x, event.y, region["width"], region["height"])
    if corner == "top-left" or corner == "bottom-right":
        canvas.config(cursor="size_nw_se")
    elif corner == "top-right" or corner == "bottom-left":
        canvas.config(cursor="size_ne_sw")
    else:
        canvas.config(cursor="fleur")  # move icon

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
canvas.bind("<Motion>", update_cursor)

# Button frame
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=1, rowspan=2, sticky="ns", padx=5, pady=5)

# Buttons
tk.Button(
    button_frame,
    text="Translate",
    command=capture_and_translate,
    wraplength=60,
    justify="center"
).grid(row=0, column=0, sticky="ew", padx=5, pady=5)

show_text_button = tk.Button(
    button_frame,
    text="Show\nOriginal",
    command=toggle_original_text,
    wraplength=60,
    justify="center"
)
show_text_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

translate_button = tk.Button(
    button_frame,
    text="Re-translate",
    command=translate_original_text,
    wraplength=60,
    justify="center"
)
translate_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

# Original text frame
original_frame = tk.Frame(root)
original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
original_frame.grid_remove()
text_area = tk.Text(original_frame, width=40, height=8, wrap="word")
text_area.pack(side="top", fill="both", expand=True)

# Translated text area
translated_text_area = tk.Text(root, width=40, height=5, wrap="word")
translated_text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)

# Start GUI
root.mainloop()
