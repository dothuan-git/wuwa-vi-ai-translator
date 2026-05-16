import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from utils import get_appdata_file_path, write_json, read_json
from default_params import GROQ_MODELS, OCR_ENGINES, DEFAULT_CONFIG


CONFIG_PATH = get_appdata_file_path("config.json")

WINDOW_BG = "#F0F0F0"
LABEL_BG = "#F0F0F0"
LABEL_FG = "#333446"


def _make_style(window):
    style = ttk.Style(window)
    style.theme_use('clam')
    style.configure(
        "Translate.TButton",
        font=("Helvetica", 10, "bold"),
        background="#A0DEFF",
        foreground="#1D5D9B",
        padding=6,
        borderwidth=2
    )
    style.map(
        "Translate.TButton",
        background=[("active", "#1363DF"), ("pressed", "#90D7DC")],
        foreground=[("active", "#DFF6FF")]
    )


def _toggle_show(entry, btn):
    if entry.cget("show") == "":
        entry.config(show="*")
        btn.config(text="👁")
    else:
        entry.config(show="")
        btn.config(text="🙈")


def open_settings_window(master, on_hotkey_change=None):
    window = tk.Toplevel(master)
    window.title("Settings")
    window.attributes('-topmost', True)
    window.configure(bg=WINDOW_BG)

    screen_w = master.winfo_screenwidth()
    screen_h = master.winfo_screenheight()
    settings_w = max(380, int(screen_w * 0.22))
    settings_h = max(400, int(screen_h * 0.48))
    master.update_idletasks()
    x = master.winfo_rootx() + master.winfo_width() - settings_w
    y = master.winfo_rooty() + (master.winfo_height() - settings_h) // 2
    window.geometry(f"{settings_w}x{settings_h}+{x}+{y}")
    window.minsize(380, 400)

    _make_style(window)

    config = read_json("config.json")

    google_ocr_var = tk.StringVar(value=config.get("google_ocr_api_key", ""))
    groq_api_var = tk.StringVar(value=config.get("groq_api_key", ""))
    groq_model_var = tk.StringVar(value=config.get("groq_model", DEFAULT_CONFIG["groq_model"]))
    ocr_engine_var = tk.StringVar(value=config.get("ocr_engine", DEFAULT_CONFIG["ocr_engine"]))
    hotkey_var = tk.StringVar(value=config.get("hotkey", DEFAULT_CONFIG["hotkey"]))
    custom_prompt = config.get("custom_prompt", "")

    frm = tk.Frame(window, bg=WINDOW_BG)
    frm.pack(fill='both', expand=True, padx=10, pady=10)
    frm.columnconfigure(0, weight=1)

    row = 0

    # OCR engine
    tk.Label(frm, text="OCR Engine:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    engine_combo = ttk.Combobox(frm, textvariable=ocr_engine_var, values=OCR_ENGINES, state="readonly")
    engine_combo.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    row += 1

    # Google Vision API key (only relevant when engine = google)
    tk.Label(frm, text="Google Vision API Key:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    google_row_frame = tk.Frame(frm, bg=WINDOW_BG)
    google_row_frame.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    google_row_frame.columnconfigure(0, weight=1)
    google_ocr_entry = tk.Entry(google_row_frame, textvariable=google_ocr_var, bg="#e8f0fe", fg="#222B38", show="*")
    google_ocr_entry.grid(row=0, column=0, sticky='ew')
    tk.Button(google_row_frame, text="👁", width=3,
              command=lambda: _toggle_show(google_ocr_entry, google_show_btn)).grid(row=0, column=1, padx=(4, 0))
    google_show_btn = google_row_frame.winfo_children()[-1]
    row += 1

    # Groq API key
    tk.Label(frm, text="Groq API Key*:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    groq_row_frame = tk.Frame(frm, bg=WINDOW_BG)
    groq_row_frame.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    groq_row_frame.columnconfigure(0, weight=1)
    groq_api_entry = tk.Entry(groq_row_frame, textvariable=groq_api_var, bg="#e8f0fe", fg="#222B38", show="*")
    groq_api_entry.grid(row=0, column=0, sticky='ew')
    tk.Button(groq_row_frame, text="👁", width=3,
              command=lambda: _toggle_show(groq_api_entry, groq_show_btn)).grid(row=0, column=1, padx=(4, 0))
    groq_show_btn = groq_row_frame.winfo_children()[-1]
    row += 1

    # Model
    tk.Label(frm, text="Model:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    model_combo = ttk.Combobox(frm, textvariable=groq_model_var, values=GROQ_MODELS, state="readonly")
    model_combo.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    row += 1

    # Hotkey
    tk.Label(frm, text="Hotkey (e.g. ctrl+shift+space):", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    hotkey_entry = tk.Entry(frm, textvariable=hotkey_var, bg="#e8f0fe", fg="#222B38")
    hotkey_entry.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    row += 1

    # Custom prompt
    tk.Label(frm, text="Custom Prompt:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w', pady=(8, 0))
    row += 1
    custom_prompt_txt = tk.Text(frm, height=5, wrap="word")
    custom_prompt_txt.grid(row=row, column=0, sticky='nsew', pady=(0, 8))
    frm.rowconfigure(row, weight=1)
    custom_prompt_txt.insert('1.0', custom_prompt)
    row += 1

    def save_settings():
        new_hotkey = hotkey_var.get().strip()
        config["google_ocr_api_key"] = google_ocr_var.get().strip()
        config["groq_api_key"] = groq_api_var.get().strip()
        config["groq_model"] = groq_model_var.get()
        config["ocr_engine"] = ocr_engine_var.get()
        config["hotkey"] = new_hotkey
        config["custom_prompt"] = custom_prompt_txt.get("1.0", "end-1c").strip()
        write_json("config.json", config)

        if on_hotkey_change:
            on_hotkey_change(new_hotkey)

        messagebox.showinfo("Success", "Settings saved!")
        window.destroy()

    btn_frm = tk.Frame(window, bg=WINDOW_BG)
    btn_frm.pack(fill='x', side='bottom', pady=(0, 8), padx=10)
    ttk.Button(btn_frm, text="Save", command=save_settings, style="Translate.TButton").pack(side='right')

    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
