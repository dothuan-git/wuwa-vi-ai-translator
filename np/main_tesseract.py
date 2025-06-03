import mss
import pytesseract
from PIL import Image
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import scrolledtext

# Configure Tesseract path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows example

# Initialize translator
translator = GoogleTranslator(source='auto', target='vi')

# Global variables for region coordinates and interaction state
region = {"top": 100, "left": 100, "width": 1200, "height": 200}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0

# Create main application window
root = tk.Tk()
root.title("Game Text Translator")
root.geometry("400x450")  # Adjusted height for layout

# Configure grid weights to make text areas resize
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create region selector window
selector = tk.Toplevel(root)
selector.title("Screenshot Region")
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)  # Semi-transparent
selector.attributes("-topmost", True)  # Always on top
selector.overrideredirect(True)  # Remove window borders

# Add a canvas to indicate the region
canvas = tk.Canvas(selector, bg="blue", highlightthickness=2, highlightbackground="red")
canvas.pack(fill="both", expand=True)

# Function to translate text
def translate_text_sync():
    text = text_area.get(1.0, tk.END).strip()
    if text and text != "No text detected.":
        translated = translator.translate(text)
    else:
        translated = "Không phát hiện văn bản."
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, translated)

# Function to capture screen and extract text
def capture_text():
    with mss.mss() as sct:
        # Capture screenshot
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        # Extract text using OCR
        text = pytesseract.image_to_string(img)
        
        # Display original text
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")

# Function to capture and translate
def capture_and_translate():
    with mss.mss() as sct:
        # Capture screenshot
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        # Extract text using OCR
        text = pytesseract.image_to_string(img)
        
        # Display original text
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, text if text.strip() else "No text detected.")
        
        # Translate to Vietnamese
        if text and text != "No text detected.":
            translated = translator.translate(text)
        else:
            translated = "Không phát hiện văn bản."
        translated_text_area.delete(1.0, tk.END)
        translated_text_area.insert(tk.END, translated)

# Function to check if mouse is near a corner
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

# Mouse event handlers for dragging and resizing
def start_interaction(event):
    global dragging, resizing, resize_corner, start_x, start_y
    x, y = event.x, event.y
    width, height = region["width"], region["height"]
    
    # Check if mouse is near a corner
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
        
        # Ensure minimum size
        region["width"] = max(region["width"], 50)
        region["height"] = max(region["height"], 50)
    
    # Update selector window geometry
    selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
    start_x = event.x_root
    start_y = event.y_root

# Update region coordinates
def update_region():
    region["left"] = selector.winfo_x()
    region["top"] = selector.winfo_y()
    region["width"] = selector.winfo_width()
    region["height"] = selector.winfo_height()
    print(f"Region updated: {region}")  # For debugging

# Bind mouse events to selector window
canvas.bind("<Button-1>", start_interaction)
canvas.bind("<ButtonRelease-1>", stop_interaction)
canvas.bind("<B1-Motion>", motion_interaction)

# Add buttons for capture, translation, and combined action
capture_button = tk.Button(root, text="Capture Text", command=capture_text)
capture_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
translate_button = tk.Button(root, text="Translate Text", command=translate_text_sync)
translate_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
capture_translate_button = tk.Button(root, text="Capture and Translate", command=capture_and_translate)
capture_translate_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

# Add text area for original text
text_area = scrolledtext.ScrolledText(root, width=40, height=8)
text_area.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Add text area for translated text
translated_text_area = scrolledtext.ScrolledText(root, width=40, height=8)
translated_text_area.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Start the GUI
root.mainloop()