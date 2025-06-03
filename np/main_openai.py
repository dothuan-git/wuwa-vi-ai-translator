import os
import io
import base64
import mss
import tkinter as tk
from PIL import Image, ImageOps
from tkinter import scrolledtext
import openai

# Set up OpenAI client (new SDK structure)
client = openai.OpenAI(api_key="OPENAI_API_KEY")


# Global region for screen capture
region = {"top": 100, "left": 100, "width": 1200, "height": 150}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0

# GUI Window
root = tk.Tk()
root.title("Game Text Translator (OpenAI SDK)")
root.geometry("400x450")
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Region Selector
selector = tk.Toplevel(root)
selector.title("Screenshot Region")
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)
selector.attributes("-topmost", True)
selector.overrideredirect(True)

canvas = tk.Canvas(selector, bg="blue", highlightthickness=2, highlightbackground="red")
canvas.pack(fill="both", expand=True)

# OCR + Translation using GPT-4 Vision
def extract_text_and_translate_with_openai(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the subtitle text from this image and translate it into Vietnamese. Format output:\nEnglish: ...\nVietnamese: ..."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"

# Capture text only
def capture_text():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        result = extract_text_and_translate_with_openai(img)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, result if result.strip() else "No text detected.")

# Placeholder (already translated)
def translate_text_sync():
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, "Translation is already included above.")

# Capture and translate
def capture_and_translate():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        result = extract_text_and_translate_with_openai(img)
        text_area.delete(1.0, tk.END)
        translated_text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, result if result.strip() else "No text detected.")
        translated_text_area.insert(tk.END, result if result.strip() else "Không phát hiện văn bản.")

# Interaction logic
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
    x, y = event.x, event.y
    width, height = region["width"], region["height"]
    resize_corner = is_near_corner(x, y, width, height)
    if resize_corner:
        resizing = True
        dragging = False
    else:
        dragging = True
        resizing = False
    start_x = event.x_root
    start_y = event.y_root

def stop_interaction(event):
    global dragging, resizing, resize_corner
    dragging = False
    resizing = False
    resize_corner = None
    update_region()

def motion_interaction(event):
    global start_x, start_y
    dx = event.x_root - start_x
    dy = event.y_root - start_y
    width, height = region["width"], region["height"]

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
capture_button = tk.Button(root, text="Capture Text", command=capture_text)
capture_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
translate_button = tk.Button(root, text="Translate Text", command=translate_text_sync)
translate_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
capture_translate_button = tk.Button(root, text="Capture and Translate", command=capture_and_translate)
capture_translate_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

# Text Display
text_area = scrolledtext.ScrolledText(root, width=40, height=8)
text_area.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
# translated_text_area = scrolledtext.ScrolledText(root, width=40, height=8)
# translated_text_area.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

root.mainloop()
