import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from utils import get_appdata_file_path


CHARACTERS_PATH = get_appdata_file_path("characters.json")
CONFIG_PATH = get_appdata_file_path("config.json")


# Helper function for show/hide key entries
def toggle_entry_show(entry, var, btn):
    if entry.cget("show") == "":
        entry.config(show="*")
        btn.config(text="👁")
    else:
        entry.config(show="")
        btn.config(text="🙈")


# Open settings window function
def open_settings_window(master):
    # --- Custom Colors and Styles ---
    WINDOW_BG = "#F0F0F0"
    LABEL_BG = "#F0F0F0"
    LABEL_FG = "#333446"

    # --- Create Toplevel window ---
    window = tk.Toplevel(master)
    window.title("Settings")
    window.geometry("400x450")
    window.minsize(350, 300)
    window.attributes('-topmost', True)
    window.configure(bg=WINDOW_BG)

    # Place at right side, vertically centered, overlay main window
    master.update_idletasks()
    x = master.winfo_rootx() + master.winfo_width() - 400
    y = master.winfo_rooty() + (master.winfo_height() - 450) // 2
    window.geometry(f"+{x}+{y}")

    # --- Styles for ttk Button ---
    style = ttk.Style(window)
    style.theme_use('clam')  # Ensures colors work on all platforms
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
        background=[
            ("active", "#1363DF"),
            ("pressed", "#90D7DC")
        ],
        foreground=[
            ("active", "#DFF6FF")
        ]
    )

    # --- Variables ---
    rover_name_var = tk.StringVar()
    rover_gender_var = tk.StringVar(value="male")
    google_ocr_var = tk.StringVar()
    groq_api_var = tk.StringVar()
    vi_pronoun_var = tk.BooleanVar()

    # --- Load existing values ---
    chars = {}
    if os.path.exists(CHARACTERS_PATH):
        with open(CHARACTERS_PATH, "r", encoding="utf-8") as f:
            chars = json.load(f)
        if "Rover" in chars:
            rover_gender_var.set(chars["Rover"].get("gender", "unknown"))
    config = {}
    custom_prompt = ""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        google_ocr_var.set(config.get("google_ocr_api_key", ""))
        groq_api_var.set(config.get("groq_api_key", ""))
        custom_prompt = config.get("custom_prompt", "")
        vi_pronoun_var.set(config.get("vi_pronoun", False))

    # --- Main Frame Layout ---
    frm = tk.Frame(window, bg=WINDOW_BG)
    frm.pack(fill='both', expand=True, padx=10, pady=10)
    frm.columnconfigure(0, weight=1)

    tk.Label(frm, text="Rover Name:", bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=0, sticky='w')
    tk.Entry(frm, textvariable=rover_name_var).grid(row=1, column=0, sticky='ew', pady=(0,8))

    tk.Label(frm, text="Gender:", bg=LABEL_BG, fg=LABEL_FG).grid(row=2, column=0, sticky='w')
    ttk.Combobox(frm, textvariable=rover_gender_var, values=["male", "female", "unknown"], state="readonly").grid(row=3, column=0, sticky='ew', pady=(0,8))

    # --- GOOGLE OCR API Key ---
    tk.Label(frm, text="Google Vision API KEY:", bg=LABEL_BG, fg=LABEL_FG).grid(row=4, column=0, sticky='w')
    google_ocr_entry = tk.Entry(frm, textvariable=google_ocr_var, bg="#e8f0fe", fg="#222B38", show="*")
    google_ocr_entry.grid(row=5, column=0, sticky='ew', pady=(0,8))
    # show_google_btn = tk.Button(frm, text="👁", width=2,
    #                             command=lambda: toggle_entry_show(google_ocr_entry, google_ocr_var, show_google_btn))
    # show_google_btn.grid(row=5, column=1, sticky='w', padx=(4,0))

    # --- GROQ API Key ---
    tk.Label(frm, text="Groq API KEY*:", bg=LABEL_BG, fg=LABEL_FG).grid(row=6, column=0, sticky='w')
    groq_api_entry = tk.Entry(frm, textvariable=groq_api_var, bg="#e8f0fe", fg="#222B38", show="*")
    groq_api_entry.grid(row=7, column=0, sticky='ew', pady=(0,8))
    # show_groq_btn = tk.Button(frm, text="👁", width=2,
    #                         command=lambda: toggle_entry_show(groq_api_entry, groq_api_var, show_groq_btn))
    # show_groq_btn.grid(row=7, column=1, sticky='w', padx=(4,0))

    tk.Checkbutton(frm, text="Vietnamese pronoun (beta)", variable=vi_pronoun_var).grid(row=8, column=0, sticky="w", pady=(8, 0))

    tk.Label(frm, text="Custom Prompt:").grid(row=9, column=0, sticky='w', pady=(8,0))
    
    # --- Scalable custom_prompt box ---
    custom_prompt_txt = tk.Text(frm, height=6, wrap="word")
    custom_prompt_txt.grid(row=10, column=0, sticky='nsew', pady=(0,8))
    frm.rowconfigure(10, weight=1)
    custom_prompt_txt.insert('1.0', custom_prompt)

    def save_settings():
        rover_name = rover_name_var.get().strip()
        rover_gender = rover_gender_var.get().strip()
        google_key = google_ocr_var.get().strip()
        groq_key = groq_api_var.get().strip()
        vi_pronoun = vi_pronoun_var.get()
        custom_prompt_val = custom_prompt_txt.get("1.0", "end-1c").strip()

        # --- Save to characters.json ---
        chars["Rover"] = {"gender": rover_gender}
        if rover_name:
            if rover_name in chars:
                chars[rover_name]["gender"] = rover_gender
            else:
                chars[rover_name] = {"gender": rover_gender}
        # Create file if not exists
        with open(CHARACTERS_PATH, "w", encoding="utf-8") as f:
            json.dump(chars, f, indent=2, ensure_ascii=False)

        # --- Save to config.json ---
        config["google_ocr_api_key"] = google_key
        config["groq_api_key"] = groq_key
        config["vi_pronoun"] = vi_pronoun
        config["custom_prompt"] = custom_prompt_val
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        messagebox.showinfo("Success", "Settings saved!")
        window.destroy()

    # --- Save Button Frame at Bottom ---
    btn_frm = tk.Frame(window, bg=WINDOW_BG)
    btn_frm.pack(fill='x', side='bottom', pady=(0,8), padx=10)
    save_btn = ttk.Button(btn_frm, text="Save", command=save_settings, style="Translate.TButton")
    save_btn.pack(side='right')

    # --- Resizable Layout ---
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

# Example of usage from your main.py:
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    settings_btn = tk.Button(root, text="⚙️", font=("Arial", 16), bg="#A0DEFF", fg="#1D5D9B",
                             activebackground="#1363DF", activeforeground="#DFF6FF",
                             command=lambda: open_settings_window(root))
    settings_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
    root.mainloop()
