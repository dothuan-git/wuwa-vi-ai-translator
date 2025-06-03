import mss
from PIL import Image
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import ttk

from settings_window import open_settings_window

from ocr import *
from translators import *
from utils import *


# ============================= GLOBAL PARAMS =============================
# Global region (this region is used to define the area of the screen to capture for translation.)
region = {"top": 100, "left": 100, "width": 800, "height": 150}
dragging = False
resizing = False
resize_corner = None
start_x = 0
start_y = 0
original_text_visible = False

# Full log history
full_log = []
# History window state
log_window = None
log_text_area = None

# Main window (app window)
root = tk.Tk()
root.title("Gió Hú AI Translator")
root.geometry("950x250")
root.attributes("-topmost", True)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)

# Region selector window (transparent window for selecting the capture area)
selector = tk.Toplevel(root)
selector.geometry(f"{region['width']}x{region['height']}+{region['left']}+{region['top']}")
selector.attributes("-alpha", 0.3)
selector.attributes("-topmost", True)
selector.overrideredirect(True)

canvas = tk.Canvas(selector, bg="#C4E1E6", highlightthickness=2, highlightbackground="#0065F8")
canvas.pack(fill="both", expand=True)

# Customer style
default_font = tkFont.Font(family="Arial", size=16)  # Change size as desired
# Custom style for buttons
style = ttk.Style()
style.theme_use("default")  # Ensure the theme supports custom styling

style.configure(
    "Translate.TButton",
    font=("Helvetica", 10, "bold"),
    background="#A0DEFF",      # Normal background
    foreground="#1D5D9B",      # Normal text
    padding=4,
    borderwidth=2,
    relief="flat"
)

style.map(
    "Translate.TButton",
    background=[
        ("active", "#1363DF"),   # Hover/active background
        ("pressed", "#90D7DC")
    ],
    foreground=[
        ("active", "#DFF6FF")
    ]
)


# ============================= FUNCTIONS CALL =============================
# Capture and translate
def capture_and_translate():
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        if use_google_ocr_var.get():
            text = extract_text_with_google_ocr(img)
        else:
            text = extract_text_from_image(img)

        if text.strip():
            speaker, dialogue = standardize_dialog(text)
            dialog = f"{speaker}: {dialogue.strip()}"
            full_log.append(dialog)

            # Update log window if it's open
            if log_window and log_text_area:
                log_text_area.config(state="normal")
                log_text_area.insert(tk.END, f"\n\n{dialog.strip()}")
                log_text_area.config(state="disabled")
                log_text_area.see(tk.END)

        translated = translate_with_llama3(dialogue, speaker) if dialogue.strip() else "Không phát hiện văn bản."
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, dialog if dialog.strip() else "No text detected.", "center")
        translated_text_area.delete(1.0, tk.END)
        translated_text_area.insert(tk.END, translated, "center")


# Translate text from original dialog
def translate_original_text():
    dialog = text_area.get(1.0, tk.END).strip()
    speaker = dialog.split(":")[0]
    dialogue = dialog.split(":")[1].strip()

    translated = translate_with_llama3(dialogue, speaker) if dialogue.strip() else "Không phát hiện văn bản."
    translated_text_area.delete(1.0, tk.END)
    translated_text_area.insert(tk.END, translated, "center")

# Toggle log window visibility
def toggle_log_window():
    global log_window, log_text_area

    if log_window and log_window.winfo_exists():
        log_window.destroy()
        log_window = None
        log_text_area = None
        log_button.config(text="Show Log")
    else:
        log_window = tk.Toplevel(root)
        log_window.title("Log History")
        log_window.geometry("500x400")

        log_text_area = tk.Text(log_window, wrap="word", font=default_font)
        log_text_area.pack(fill="both", expand=True, padx=5, pady=5)
        log_text_area.insert("1.0", "\n\n".join(full_log))
        log_text_area.config(state="disabled")

        log_button.config(text="Hide Log")

        def on_close():
            global log_window, log_text_area
            log_window.destroy()
            log_window = None
            log_text_area = None
            log_button.config(text="Show Log")

        log_window.protocol("WM_DELETE_WINDOW", on_close)


def export_log_to_file():
    if not full_log:
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Log file", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(full_log))


# Toggle original text visibility
def toggle_original_text():
    global original_text_visible
    if original_text_visible:
        original_frame.grid_remove()
        show_text_button.config(text="Show Raw")
    else:
        original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        show_text_button.config(text="Hide Raw")
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


# ============================= LAYOUT AND FEATURES SETUP =============================
# Bind events for region interaction
canvas.bind("<Button-1>", start_interaction)
canvas.bind("<ButtonRelease-1>", stop_interaction)
canvas.bind("<B1-Motion>", motion_interaction)
canvas.bind("<Motion>", update_cursor)

# Button frame
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=1, rowspan=3, sticky="ns", padx=5, pady=5)


# Buttons
ttk.Button(
    button_frame,
    text="Translate $",
    command=capture_and_translate,
    style="Translate.TButton"
).grid(row=0, column=0, sticky="ew", padx=2, pady=2)

translate_button = ttk.Button(
    button_frame,
    text="Re-translate",
    command=translate_original_text,
    style="Translate.TButton"
)
translate_button.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

show_text_button = ttk.Button(
    button_frame,
    text="Show Raw",
    command=toggle_original_text,
    style="Translate.TButton"
)
show_text_button.grid(row=2, column=0, sticky="ew", padx=2, pady=2)

use_google_ocr_var = tk.BooleanVar()
google_ocr_checkbox = tk.Checkbutton(
    button_frame,
    text="Use Google OCR",
    variable=use_google_ocr_var
)
google_ocr_checkbox.grid(row=3, column=0, sticky="w", padx=2, pady=2)

log_button = ttk.Button(
    button_frame,
    text="Show Log",
    command=toggle_log_window,
    style="Translate.TButton"
)
log_button.grid(row=4, column=0, sticky="ew", padx=2, pady=2)

ttk.Button(
    button_frame,
    text="Export Log",
    command=export_log_to_file,
    style="Translate.TButton"
).grid(row=5, column=0, sticky="ew", padx=2, pady=2)


# Add settings button at bottom right
settings_btn = tk.Button(root, text="Config", font=("Helvetica", 10), relief="flat", bg="#333446", fg="#F5F5F5",
                         command=lambda: open_settings_window(root))
settings_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")


# Original text area
original_frame = tk.Frame(root)
original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
original_frame.grid_remove()
text_area = tk.Text(
    original_frame, 
    width=40, height=3, 
    wrap="word", 
    font=default_font,
    padx=10,
    pady=10,
    spacing1=4,   # Space above lines
    spacing3=4    # Space below lines
)
text_area.pack(side="top", fill="both", expand=True)
text_area.tag_configure("center", justify="center")

# Translated text area
translated_text_area = tk.Text(
    root, 
    width=40, height=5, 
    wrap="word", 
    font=default_font,
    padx=30,
    pady=10,
    # spacing1=10,   # Space above lines
    spacing2=8,    # line spacing between wrapped lines in a paragraph
    spacing3=15    # Space below lines
)
translated_text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
translated_text_area.tag_configure("center", justify="center")


# Start GUI
root.mainloop()
