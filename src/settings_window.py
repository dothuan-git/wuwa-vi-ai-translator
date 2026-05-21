import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from utils import get_appdata_file_path, write_json, read_json
from default_params import (
    PROVIDERS,
    MODELS_BY_PROVIDER,
    OCR_ENGINES,
    DEFAULT_CONFIG,
)


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


def open_settings_window(master, on_hotkey_change=None, on_font_change=None, on_close=None):
    window = tk.Toplevel(master)
    window.title("Settings")
    window.attributes('-topmost', True)
    window.configure(bg=WINDOW_BG)

    _make_style(window)

    config = read_json("config.json")

    google_ocr_var = tk.StringVar(value=config.get("google_ocr_api_key", ""))
    provider_var = tk.StringVar(value=config.get("provider", DEFAULT_CONFIG["provider"]))
    groq_api_var = tk.StringVar(value=config.get("groq_api_key", ""))
    gemini_api_var = tk.StringVar(value=config.get("gemini_api_key", ""))
    _init_provider = provider_var.get()
    model_var = tk.StringVar(
        value=config.get(f"{_init_provider}_model", DEFAULT_CONFIG["groq_model"])
    )
    ocr_engine_var = tk.StringVar(value=config.get("ocr_engine", DEFAULT_CONFIG["ocr_engine"]))
    hotkey_var = tk.StringVar(value=config.get("hotkey", DEFAULT_CONFIG["hotkey"]))
    font_size_var = tk.IntVar(value=config.get("font_size", DEFAULT_CONFIG["font_size"]))
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

    # Provider
    tk.Label(frm, text="Provider:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    provider_combo = ttk.Combobox(frm, textvariable=provider_var, values=PROVIDERS, state="readonly")
    provider_combo.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    row += 1

    # Groq API key
    tk.Label(frm, text="Groq API Key:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
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

    # Gemini API key
    tk.Label(frm, text="Gemini API Key:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    gemini_row_frame = tk.Frame(frm, bg=WINDOW_BG)
    gemini_row_frame.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    gemini_row_frame.columnconfigure(0, weight=1)
    gemini_api_entry = tk.Entry(gemini_row_frame, textvariable=gemini_api_var, bg="#e8f0fe", fg="#222B38", show="*")
    gemini_api_entry.grid(row=0, column=0, sticky='ew')
    tk.Button(gemini_row_frame, text="👁", width=3,
              command=lambda: _toggle_show(gemini_api_entry, gemini_show_btn)).grid(row=0, column=1, padx=(4, 0))
    gemini_show_btn = gemini_row_frame.winfo_children()[-1]
    row += 1

    # Model
    tk.Label(frm, text="Model:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    model_combo = ttk.Combobox(frm, textvariable=model_var, state="readonly")
    model_combo.grid(row=row, column=0, sticky='ew', pady=(0, 2))
    row += 1
    tk.Label(
        frm,
        text="Tip: stronger models give better Vietnamese (e.g. Gemini 2.5 Flash).",
        bg=LABEL_BG, fg="#7A7A8C", font=("Helvetica", 8),
        wraplength=320, justify="left",
    ).grid(row=row, column=0, sticky='w', pady=(0, 8))
    row += 1

    def on_provider_change(*_):
        p = provider_var.get()
        models = MODELS_BY_PROVIDER.get(p, [])
        model_combo["values"] = models
        saved = config.get(f"{p}_model", DEFAULT_CONFIG[f"{p}_model"])
        model_var.set(saved if saved in models else (models[0] if models else ""))

    provider_combo.bind("<<ComboboxSelected>>", on_provider_change)
    on_provider_change()

    # Hotkey
    tk.Label(frm, text="Hotkey (e.g. ctrl+shift+space):", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    hotkey_entry = tk.Entry(frm, textvariable=hotkey_var, bg="#e8f0fe", fg="#222B38")
    hotkey_entry.grid(row=row, column=0, sticky='ew', pady=(0, 8))
    row += 1

    # Font size
    tk.Label(frm, text="Font Size:", bg=LABEL_BG, fg=LABEL_FG).grid(row=row, column=0, sticky='w')
    row += 1
    ttk.Spinbox(frm, from_=8, to=40, increment=2, textvariable=font_size_var,
                state="readonly").grid(row=row, column=0, sticky='w', pady=(0, 8))
    row += 1

    def save_settings():
        new_hotkey = hotkey_var.get().strip()
        provider = provider_var.get()
        config["google_ocr_api_key"] = google_ocr_var.get().strip()
        config["provider"] = provider
        config["groq_api_key"] = groq_api_var.get().strip()
        config["gemini_api_key"] = gemini_api_var.get().strip()
        config[f"{provider}_model"] = model_var.get()
        config["ocr_engine"] = ocr_engine_var.get()
        config["hotkey"] = new_hotkey
        config["font_size"] = font_size_var.get()
        config["settings_geometry"] = window.winfo_geometry()
        write_json("config.json", config)

        if on_hotkey_change:
            on_hotkey_change(new_hotkey)
        if on_font_change:
            on_font_change(font_size_var.get())

        messagebox.showinfo("Success", "Settings saved!")
        window.destroy()
        if on_close:
            on_close()

    btn_frm = tk.Frame(window, bg=WINDOW_BG)
    btn_frm.pack(fill='x', side='bottom', pady=(0, 8), padx=10)
    ttk.Button(btn_frm, text="Save", command=save_settings, style="Translate.TButton").pack(side='right')

    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    # Size the modal to fit its components (or restore the remembered size)
    window.update_idletasks()
    req_w = max(360, window.winfo_reqwidth())
    req_h = window.winfo_reqheight()
    window.minsize(req_w, req_h)

    saved_geo = config.get("settings_geometry")
    if saved_geo:
        window.geometry(saved_geo)
    else:
        master.update_idletasks()
        x = master.winfo_rootx() + master.winfo_width() - req_w
        y = master.winfo_rooty() + (master.winfo_height() - req_h) // 2
        window.geometry(f"{req_w}x{req_h}+{x}+{y}")

    def _on_window_close():
        try:
            c = read_json("config.json")
            c["settings_geometry"] = window.winfo_geometry()
            write_json("config.json", c)
        except Exception:
            pass
        window.destroy()
        if on_close:
            on_close()

    window.protocol("WM_DELETE_WINDOW", _on_window_close)
