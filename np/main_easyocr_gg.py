import mss
import easyocr
from PIL import Image, ImageOps
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import scrolledtext
import wordninja

# Initialize OCR and translator
reader = easyocr.Reader(['en', 'ja'])  # Add other languages if needed
translator = GoogleTranslator(source='auto', target='vi')

# Global variables for region coordinates and interaction state
region = {"top": 100, "left": 100, "width": 1200, "height": 150}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0

# Create main application window
root = tk.Tk()
root.title("Game Text Translator")
root.geometry("400x450")

# Configure grid weights to make text areas resize
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create region selector window
selector = tk.Toplevel(root)
selector.title("Screenshot Region")
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)
selector.attributes("-topmost", True)
selector.overrideredirect(True)

# Add a canvas to indicate the region
canvas = tk.Canvas(selector, bg="blue", highlightthickness=2, highlightbackground="red")
canvas.pack(fill="both", expand=True)

# OCR function using EasyOCR
def extract_text_from_image(img):
    # Preprocessing
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img = img.crop(img.getbbox())

    img.save("temp_capture.png")

    # OCR
    result = reader.readtext("temp_capture.png", detail=0, paragraph=True)
    raw_text = '\n'.join(result)

    # Word segmentation
    spaced_text = '\n'.join([' '.join(wordninja.split(line)) for line in raw_text.split('\n')])

    return spaced_text

# Capture screen and extract text
def capture_text():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text = extract_text_from_image(img)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")

# Translate current text
def translate_text_sync():
    text = text_area.get(1.0, tk.END).strip()
    if text and text != "No text detected.":
        translated = translator.translate(text)
    else:
        translated = "Không phát hiện văn bản."
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, translated)

# Capture and translate at once
def capture_and_translate():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text = extract_text_from_image(img)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")
        translated = translator.translate(text) if text.strip() else "Không phát hiện văn bản."
        translated_text_area.delete(1.0, tk.END)
        translated_text_area.insert(tk.END, translated)

# Check if mouse is near a corner for resizing
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

# Mouse interaction handlers
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

# Bind mouse events
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

# Text display areas
text_area = scrolledtext.ScrolledText(root, width=40, height=8)
text_area.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

translated_text_area = scrolledtext.ScrolledText(root, width=40, height=8)
translated_text_area.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Start GUI
root.mainloop()
