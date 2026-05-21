"""
Wuthering Waves AI Translator - Main Application
"""

import ctypes
import hashlib
import mss
import threading
from collections import OrderedDict
from PIL import Image
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import ttk
from typing import Dict, List, Optional, Tuple
import logging

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

from settings_window import open_settings_window
from ocr import extract_text
from translators import translate_with_llama
from utils import standardize_dialog, ensure_config, read_json, write_json
from default_params import (
    DEFAULT_CONFIG,
    ROVER_SELF_OPTIONS,
    ROVER_TO_OTHER_OPTIONS,
    OTHER_SELF_OPTIONS,
    OTHER_TO_ROVER_OPTIONS,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Win32 constants for click-through overlay
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020


class AppConstants:
    MAIN_WIDTH_RATIO = 0.55
    MAIN_HEIGHT_RATIO = 0.32
    REGION_WIDTH_RATIO = 0.42
    REGION_HEIGHT_RATIO = 0.12
    MIN_REGION_SIZE = 50
    CORNER_THRESHOLD = 10

    DEFAULT_FONT_FAMILY = "Arial"
    DEFAULT_FONT_SIZE = 16
    BUTTON_FONT = ("Helvetica", 10, "bold")
    PRONOUN_FONT = ("Helvetica", 9, "bold")
    HEADER_FONT = ("Helvetica", 9, "bold")
    SUB_HEADER_FONT = ("Helvetica", 8)

    SELECTOR_BG_COLOR = "#C4E1E6"
    SELECTOR_BORDER_COLOR = "#0065F8"
    BUTTON_BG_COLOR = "#A0DEFF"
    BUTTON_FG_COLOR = "#1D5D9B"
    BUTTON_ACTIVE_BG = "#1363DF"
    BUTTON_ACTIVE_FG = "#DFF6FF"
    SETTINGS_BG_COLOR = "#333446"
    SETTINGS_FG_COLOR = "#F5F5F5"

    ROVER_BAR_BG = "#EAF4FB"      # light blue tint for Rover (player)
    ROVER_BAR_ACCENT = "#1D5D9B"
    OTHER_BAR_BG = "#FBEEE6"      # light warm tint for Other (NPC)
    OTHER_BAR_ACCENT = "#A04000"
    SUB_LABEL_FG = "#555"

    NO_TEXT_DETECTED = "Không phát hiện văn bản."
    UNKNOWN_SPEAKER = "unknown"
    NO_SPEAKER_LABEL = "Đối phương"

    TRANSLATION_CACHE_SIZE = 200
    AUTO_POLL_INTERVAL = 0.7   # seconds
    AUTO_DEBOUNCE_COUNT = 2    # consecutive identical hashes before trigger


def _image_hash(img: Image.Image) -> str:
    """Fast perceptual hash for change detection: 8×8 grayscale bytes."""
    thumb = img.convert("L").resize((8, 8), Image.LANCZOS)
    return hashlib.md5(thumb.tobytes()).hexdigest()


def _set_click_through(hwnd, enable: bool) -> None:
    """Enable or disable Win32 click-through on a window."""
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if enable:
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
    else:
        style &= ~WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


class RegionSelector:
    """Transparent region selection overlay with click-through idle mode."""

    def __init__(self, parent: tk.Tk, region: Dict[str, int]):
        self.parent = parent
        self.region = region
        self.dragging = False
        self.resizing = False
        self.resize_corner: Optional[str] = None
        self.start_x = 0
        self.start_y = 0
        self._edit_mode = True
        self._hwnd: Optional[int] = None

        self._create_selector_window()
        self._bind_events()
        self.parent.after(200, self._apply_click_through)

    def _create_selector_window(self) -> None:
        self.selector = tk.Toplevel(self.parent)
        self.selector.geometry(
            f"{self.region['width']}x{self.region['height']}+"
            f"{self.region['left']}+{self.region['top']}"
        )
        self.selector.attributes("-alpha", 0.35)
        self.selector.attributes("-topmost", True)
        self.selector.overrideredirect(True)

        self.canvas = tk.Canvas(
            self.selector,
            bg=AppConstants.SELECTOR_BG_COLOR,
            highlightthickness=2,
            highlightbackground=AppConstants.SELECTOR_BORDER_COLOR
        )
        self.canvas.pack(fill="both", expand=True)

    def _bind_events(self) -> None:
        self.canvas.bind("<Button-1>", self._start_interaction)
        self.canvas.bind("<ButtonRelease-1>", self._stop_interaction)
        self.canvas.bind("<B1-Motion>", self._motion_interaction)
        self.canvas.bind("<Motion>", self._update_cursor)

    def _apply_click_through(self) -> None:
        try:
            self.selector.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.selector.winfo_id())
            if hwnd == 0:
                hwnd = self.selector.winfo_id()
            self._hwnd = hwnd
            if not self._edit_mode:
                self.selector.attributes("-transparentcolor", AppConstants.SELECTOR_BG_COLOR)
                _set_click_through(hwnd, True)
        except Exception as e:
            logger.warning(f"Click-through setup failed: {e}")

    def toggle_edit_mode(self) -> bool:
        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            try:
                self.selector.attributes("-transparentcolor", "")
            except Exception:
                pass
            if self._hwnd:
                _set_click_through(self._hwnd, False)
            self.selector.attributes("-alpha", 0.35)
        else:
            self.selector.attributes("-alpha", 0.3)
            try:
                self.selector.attributes("-transparentcolor", AppConstants.SELECTOR_BG_COLOR)
            except Exception:
                pass
            if self._hwnd:
                _set_click_through(self._hwnd, True)
        return self._edit_mode

    def _is_near_corner(self, x: int, y: int) -> Optional[str]:
        corners = {
            "top-left": (0, 0),
            "top-right": (self.region["width"], 0),
            "bottom-left": (0, self.region["height"]),
            "bottom-right": (self.region["width"], self.region["height"])
        }
        for corner, (cx, cy) in corners.items():
            if (abs(x - cx) <= AppConstants.CORNER_THRESHOLD and
                    abs(y - cy) <= AppConstants.CORNER_THRESHOLD):
                return corner
        return None

    def _start_interaction(self, event: tk.Event) -> None:
        if not self._edit_mode:
            return
        self.resize_corner = self._is_near_corner(event.x, event.y)
        self.dragging = not self.resize_corner
        self.resizing = bool(self.resize_corner)
        self.start_x = event.x_root
        self.start_y = event.y_root

    def _stop_interaction(self, event: tk.Event) -> None:
        self.dragging = self.resizing = False
        self.resize_corner = None
        self._update_region()

    def _update_cursor(self, event: tk.Event) -> None:
        if not self._edit_mode:
            return
        corner = self._is_near_corner(event.x, event.y)
        if corner in ["top-left", "bottom-right"]:
            self.canvas.config(cursor="size_nw_se")
        elif corner in ["top-right", "bottom-left"]:
            self.canvas.config(cursor="size_ne_sw")
        else:
            self.canvas.config(cursor="fleur")

    def _motion_interaction(self, event: tk.Event) -> None:
        if not self._edit_mode:
            return
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y

        if self.dragging:
            self.region["left"] += dx
            self.region["top"] += dy
        elif self.resizing and self.resize_corner:
            self._handle_resize(dx, dy)

        self._update_selector_geometry()
        self.start_x = event.x_root
        self.start_y = event.y_root

    def _handle_resize(self, dx: int, dy: int) -> None:
        if self.resize_corner == "top-left":
            self.region["left"] += dx
            self.region["top"] += dy
            self.region["width"] -= dx
            self.region["height"] -= dy
        elif self.resize_corner == "top-right":
            self.region["top"] += dy
            self.region["width"] += dx
            self.region["height"] -= dy
        elif self.resize_corner == "bottom-left":
            self.region["left"] += dx
            self.region["width"] -= dx
            self.region["height"] += dy
        elif self.resize_corner == "bottom-right":
            self.region["width"] += dx
            self.region["height"] += dy

        self.region["width"] = max(self.region["width"], AppConstants.MIN_REGION_SIZE)
        self.region["height"] = max(self.region["height"], AppConstants.MIN_REGION_SIZE)

    def _update_selector_geometry(self) -> None:
        self.selector.geometry(
            f"{self.region['width']}x{self.region['height']}+"
            f"{self.region['left']}+{self.region['top']}"
        )

    def _update_region(self) -> None:
        self.region["left"] = self.selector.winfo_x()
        self.region["top"] = self.selector.winfo_y()
        self.region["width"] = self.selector.winfo_width()
        self.region["height"] = self.selector.winfo_height()


class TranslatorApp:
    def __init__(self):
        self.region: Dict[str, int] = {}
        self.translation_history: List[Tuple[str, str, str]] = []
        self._job_in_flight = False
        self._last_speaker = AppConstants.UNKNOWN_SPEAKER
        self.current_other_speaker: Optional[str] = None

        # Current pronoun selections (updated by button clicks)
        cfg = read_json("config.json")
        self._rover_self: Optional[str] = cfg.get("rover_self") or None
        self._rover_to_other: Optional[str] = cfg.get("rover_to_other") or None
        self._other_self: Optional[str] = "tôi"
        self._other_to_rover: Optional[str] = "bạn"

        # LRU translation cache
        self._cache: OrderedDict[str, str] = OrderedDict()

        # Auto-detect state
        self._auto_stop = threading.Event()
        self._auto_thread: Optional[threading.Thread] = None
        self._auto_active = False

        # Hotkey
        self._hotkey_registered: Optional[str] = None

        self._setup_main_window()
        self._setup_styles()
        self._create_region_selector()
        self._create_ui_components()
        self.root.update_idletasks()

        self._register_hotkey(read_json("config.json").get("hotkey", DEFAULT_CONFIG["hotkey"]))
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        logger.info("Translator application initialized")

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_main_window(self) -> None:
        self.root = tk.Tk()
        self.root.title("Gió Hú AI Translator")
        self.root.attributes("-topmost", True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        cfg = read_json("config.json")

        saved_geo = cfg.get("window_geometry")
        if saved_geo:
            self.root.geometry(saved_geo)
        else:
            win_w = int(screen_w * AppConstants.MAIN_WIDTH_RATIO)
            win_h = int(screen_h * AppConstants.MAIN_HEIGHT_RATIO)
            win_x = (screen_w - win_w) // 2
            win_y = screen_h - win_h - 60
            self.root.geometry(f"{win_w}x{win_h}+{win_x}+{win_y}")

        saved_region = cfg.get("region")
        if isinstance(saved_region, dict) and all(
            k in saved_region for k in ("top", "left", "width", "height")
        ):
            self.region = dict(saved_region)
        else:
            self.region = {
                "top": int(screen_h * 0.45),
                "left": (screen_w - int(screen_w * AppConstants.REGION_WIDTH_RATIO)) // 2,
                "width": int(screen_w * AppConstants.REGION_WIDTH_RATIO),
                "height": int(screen_h * AppConstants.REGION_HEIGHT_RATIO),
            }

        # row 0: top button row (Re-translate+Auto | [text] | Translate+Lock Region)
        # row 1: main content (Rover bar | translated text | other bar), weight=1
        # row 2: original text toggle
        # row 3: status bar
        # uniform="bars" keeps cols 0 and 2 at the same width.
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=0, uniform="bars")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0, uniform="bars")
        self.root.grid_propagate(False)

        font_size = cfg.get("font_size", AppConstants.DEFAULT_FONT_SIZE)
        self.default_font = tkFont.Font(
            family=AppConstants.DEFAULT_FONT_FAMILY,
            size=font_size
        )

    def _setup_styles(self) -> None:
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "Translate.TButton",
            font=AppConstants.BUTTON_FONT,
            background=AppConstants.BUTTON_BG_COLOR,
            foreground=AppConstants.BUTTON_FG_COLOR,
            padding=4,
            borderwidth=2,
            relief="flat"
        )
        self.style.map(
            "Translate.TButton",
            background=[("active", AppConstants.BUTTON_ACTIVE_BG), ("pressed", "#90D7DC")],
            foreground=[("active", AppConstants.BUTTON_ACTIVE_FG)]
        )

        # Rover (left bar) — cool blue palette
        self.style.configure(
            "RoverPronoun.TButton",
            font=AppConstants.PRONOUN_FONT,
            background="#D6E9F5",
            foreground="#1D5D9B",
            padding=(2, 1),
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "RoverPronoun.TButton",
            background=[("active", "#B4D4EB"), ("pressed", "#A0C8E2")],
            foreground=[("active", "#0E3A66")],
        )
        self.style.configure(
            "RoverPronounActive.TButton",
            font=AppConstants.PRONOUN_FONT,
            background="#1D5D9B",
            foreground="#FFFFFF",
            padding=(2, 1),
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "RoverPronounActive.TButton",
            background=[("active", "#164773"), ("pressed", "#0E3A66")],
            foreground=[("active", "#FFFFFF")],
        )

        # Other (right bar) — warm amber palette
        self.style.configure(
            "OtherPronoun.TButton",
            font=AppConstants.PRONOUN_FONT,
            background="#F7D7BC",
            foreground="#6B2800",
            padding=(2, 1),
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "OtherPronoun.TButton",
            background=[("active", "#F0B988"), ("pressed", "#E89F60")],
            foreground=[("active", "#3D1500")],
        )
        self.style.configure(
            "OtherPronounActive.TButton",
            font=AppConstants.PRONOUN_FONT,
            background="#C75B16",
            foreground="#FFFFFF",
            padding=(2, 1),
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "OtherPronounActive.TButton",
            background=[("active", "#A04000"), ("pressed", "#7A3000")],
            foreground=[("active", "#FFFFFF")],
        )

    def _create_region_selector(self) -> None:
        self.region_selector = RegionSelector(self.root, self.region)

    # ── UI components ─────────────────────────────────────────────────────────

    def _create_ui_components(self) -> None:
        self._create_top_buttons()
        self._create_rover_pronoun_bar()
        self._create_right_panel()
        self._create_text_areas()
        self._create_status_bar()
        self._create_settings_button()

    def _create_top_buttons(self) -> None:
        """Row 0 button strip: Re-translate+Auto (col 0), Translate+Lock Region (col 2)."""
        left = tk.Frame(self.root)
        left.grid(row=0, column=0, sticky="ew", padx=(4, 0), pady=(5, 2))
        left.grid_columnconfigure(0, weight=1, uniform="ltop")
        left.grid_columnconfigure(1, weight=1, uniform="ltop")

        self.retranslate_btn = ttk.Button(
            left, text="Re-translate",
            command=self.translate_original_text, style="Translate.TButton"
        )
        self.retranslate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 1))

        self.auto_btn = ttk.Button(
            left, text="Auto: Off",
            command=self.toggle_auto_detect, style="Translate.TButton"
        )
        self.auto_btn.grid(row=0, column=1, sticky="ew", padx=(1, 0))

        right = tk.Frame(self.root)
        right.grid(row=0, column=2, sticky="ew", padx=5, pady=(5, 2))
        right.grid_columnconfigure(0, weight=1, uniform="rtop")
        right.grid_columnconfigure(1, weight=1, uniform="rtop")

        self.translate_btn = ttk.Button(
            right, text="Translate",
            command=self._trigger_translate, style="Translate.TButton"
        )
        self.translate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 1))

        self.edit_region_btn = ttk.Button(
            right, text="Lock Region",
            command=self.toggle_edit_region, style="Translate.TButton"
        )
        self.edit_region_btn.grid(row=0, column=1, sticky="ew", padx=(1, 0))

    def _create_right_panel(self) -> None:
        """Column 2, row 1+: other-pronoun bar."""
        self.right_panel = tk.Frame(self.root)
        self.right_panel.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=5, pady=5)
        self._create_other_pronoun_bar()

    def _make_pronoun_column(self, parent, options, active, on_click, col, style_pair, start_row=0):
        """Build a single-select column of pronoun buttons in `parent` at grid column `col`.
        style_pair is (base_style, active_style). Returns {option: button}."""
        btns = {}
        for i, opt in enumerate(options):
            btn = ttk.Button(
                parent,
                text=opt,
                style=style_pair[0],
                command=lambda o=opt: on_click(o),
                width=6,
            )
            btn.grid(row=start_row + i, column=col, sticky="ew", padx=1, pady=1)
            btns[opt] = btn
        self._refresh_pronoun_column(btns, active, style_pair)
        return btns

    def _refresh_pronoun_column(self, btns: dict, active: str, style_pair) -> None:
        base, active_style = style_pair
        for opt, btn in btns.items():
            btn.configure(style=active_style if opt == active else base)

    def _create_rover_pronoun_bar(self) -> None:
        """Column 0: two sub-columns — Rover self-pronoun and Rover→other pronoun."""
        self._rover_style_pair = ("RoverPronoun.TButton", "RoverPronounActive.TButton")

        self.rover_pronoun_frame = tk.Frame(
            self.root,
            bg=AppConstants.ROVER_BAR_BG,
            highlightthickness=1,
            highlightbackground="#B4D4EB",
        )
        self.rover_pronoun_frame.grid(row=1, column=0, rowspan=2, sticky="nsew",
                                      padx=(4, 0), pady=5)
        self.rover_pronoun_frame.grid_columnconfigure(0, weight=1, uniform="rover")
        self.rover_pronoun_frame.grid_columnconfigure(1, weight=1, uniform="rover")

        tk.Label(
            self.rover_pronoun_frame, text="Rover",
            bg=AppConstants.ROVER_BAR_BG, fg=AppConstants.ROVER_BAR_ACCENT,
            font=AppConstants.HEADER_FONT,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(3, 1))

        tk.Label(
            self.rover_pronoun_frame, text="xưng",
            bg=AppConstants.ROVER_BAR_BG, fg=AppConstants.SUB_LABEL_FG,
            font=AppConstants.SUB_HEADER_FONT,
        ).grid(row=1, column=0, sticky="ew", padx=1)
        tk.Label(
            self.rover_pronoun_frame, text="gọi",
            bg=AppConstants.ROVER_BAR_BG, fg=AppConstants.SUB_LABEL_FG,
            font=AppConstants.SUB_HEADER_FONT,
        ).grid(row=1, column=1, sticky="ew", padx=1)

        self._rover_self_btns = self._make_pronoun_column(
            self.rover_pronoun_frame,
            ROVER_SELF_OPTIONS,
            self._rover_self,
            self._on_rover_self_click,
            col=0,
            style_pair=self._rover_style_pair,
            start_row=2,
        )
        self._rover_to_other_btns = self._make_pronoun_column(
            self.rover_pronoun_frame,
            ROVER_TO_OTHER_OPTIONS,
            self._rover_to_other,
            self._on_rover_to_other_click,
            col=1,
            style_pair=self._rover_style_pair,
            start_row=2,
        )

    def _create_other_pronoun_bar(self) -> None:
        """Below the action buttons in right_panel: two sub-columns for the
        other speaker's pronouns."""
        self._other_style_pair = ("OtherPronoun.TButton", "OtherPronounActive.TButton")

        self.other_pronoun_frame = tk.Frame(
            self.right_panel,
            bg=AppConstants.OTHER_BAR_BG,
            highlightthickness=1,
            highlightbackground="#F0B988",
        )
        self.other_pronoun_frame.pack(side="top", fill="x")
        self.other_pronoun_frame.grid_columnconfigure(0, weight=1, uniform="other")
        self.other_pronoun_frame.grid_columnconfigure(1, weight=1, uniform="other")

        self._other_header_var = tk.StringVar(value=AppConstants.NO_SPEAKER_LABEL)
        tk.Label(
            self.other_pronoun_frame, textvariable=self._other_header_var,
            bg=AppConstants.OTHER_BAR_BG, fg=AppConstants.OTHER_BAR_ACCENT,
            font=AppConstants.HEADER_FONT,
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(3, 1))

        tk.Label(
            self.other_pronoun_frame, text="xưng",
            bg=AppConstants.OTHER_BAR_BG, fg=AppConstants.SUB_LABEL_FG,
            font=AppConstants.SUB_HEADER_FONT,
        ).grid(row=1, column=0, sticky="ew", padx=1)
        tk.Label(
            self.other_pronoun_frame, text="gọi",
            bg=AppConstants.OTHER_BAR_BG, fg=AppConstants.SUB_LABEL_FG,
            font=AppConstants.SUB_HEADER_FONT,
        ).grid(row=1, column=1, sticky="ew", padx=1)

        self._other_self_btns = self._make_pronoun_column(
            self.other_pronoun_frame,
            OTHER_SELF_OPTIONS,
            self._other_self,
            self._on_other_self_click,
            col=0,
            style_pair=self._other_style_pair,
            start_row=2,
        )
        self._other_to_rover_btns = self._make_pronoun_column(
            self.other_pronoun_frame,
            OTHER_TO_ROVER_OPTIONS,
            self._other_to_rover,
            self._on_other_to_rover_click,
            col=1,
            style_pair=self._other_style_pair,
            start_row=2,
        )

    def _create_text_areas(self) -> None:
        self.original_frame = tk.Frame(self.root)
        self.original_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        self.original_frame.grid_remove()

        self.text_area = tk.Text(
            self.original_frame,
            wrap="word",
            font=self.default_font,
            padx=10, pady=10,
            spacing1=4, spacing3=4
        )
        self.text_area.pack(side="top", fill="both", expand=True)
        self.text_area.tag_configure("center", justify="center")

        self.translated_text_area = tk.Text(
            self.root,
            wrap="word",
            font=self.default_font,
            padx=30, pady=10,
            spacing2=3, spacing3=10
        )
        self.translated_text_area.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=2)
        self.translated_text_area.tag_configure("center", justify="center")

    def _create_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            fg="#555",
            anchor="w",
            padx=6
        )
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="ew")

    def _create_settings_button(self) -> None:
        self.settings_btn = tk.Button(
            self.root,
            text="Config",
            font=("Helvetica", 10),
            relief="flat",
            bg=AppConstants.SETTINGS_BG_COLOR,
            fg=AppConstants.SETTINGS_FG_COLOR,
            command=lambda: open_settings_window(
                self.root,
                on_hotkey_change=self._register_hotkey,
                on_font_change=self._apply_font_size,
                on_close=self._restore_styles,
            )
        )
        self.settings_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    # ── Pronoun button handlers ───────────────────────────────────────────────

    def _on_rover_self_click(self, pronoun: str) -> None:
        self._rover_self = None if self._rover_self == pronoun else pronoun
        self._refresh_pronoun_column(self._rover_self_btns, self._rover_self, self._rover_style_pair)
        cfg = read_json("config.json")
        cfg["rover_self"] = self._rover_self or ""
        write_json("config.json", cfg)

    def _on_rover_to_other_click(self, pronoun: str) -> None:
        self._rover_to_other = None if self._rover_to_other == pronoun else pronoun
        self._refresh_pronoun_column(self._rover_to_other_btns, self._rover_to_other, self._rover_style_pair)
        cfg = read_json("config.json")
        cfg["rover_to_other"] = self._rover_to_other or ""
        write_json("config.json", cfg)

    def _on_other_self_click(self, pronoun: str) -> None:
        self._other_self = None if self._other_self == pronoun else pronoun
        self._refresh_pronoun_column(self._other_self_btns, self._other_self, self._other_style_pair)

    def _on_other_to_rover_click(self, pronoun: str) -> None:
        self._other_to_rover = None if self._other_to_rover == pronoun else pronoun
        self._refresh_pronoun_column(self._other_to_rover_btns, self._other_to_rover, self._other_style_pair)

    def _update_other_bar(self, speaker: str) -> None:
        """Update the right bar header when speaker changes; keep current pronoun selections."""
        self.current_other_speaker = speaker
        self._other_header_var.set(speaker or AppConstants.NO_SPEAKER_LABEL)

    def _get_current_pronouns(self, speaker: str) -> Optional[dict]:
        """Build the pronouns dict to pass to the translator. Returns None for narration."""
        if not speaker or speaker == AppConstants.UNKNOWN_SPEAKER:
            return None
        pronouns = {
            "rover_self": self._rover_self,
            "rover_to_other": self._rover_to_other,
        }
        if speaker != "Rover":
            pronouns["other_self"] = self._other_self
            pronouns["other_to_rover"] = self._other_to_rover
        return pronouns

    # ── Hotkey ────────────────────────────────────────────────────────────────

    def _register_hotkey(self, hotkey: str) -> None:
        try:
            import keyboard
            if self._hotkey_registered:
                try:
                    keyboard.remove_hotkey(self._hotkey_registered)
                except Exception:
                    pass
            if hotkey:
                keyboard.add_hotkey(hotkey, lambda: self.root.after(0, self._trigger_translate))
                self._hotkey_registered = hotkey
                logger.info(f"Hotkey registered: {hotkey}")
        except Exception as e:
            logger.warning(f"Could not register hotkey '{hotkey}': {e}")

    # ── Auto-detect ───────────────────────────────────────────────────────────

    def toggle_auto_detect(self) -> None:
        if self._auto_active:
            self._stop_auto_detect()
        else:
            self._start_auto_detect()

    def _start_auto_detect(self) -> None:
        self._auto_stop.clear()
        self._auto_active = True
        self.auto_btn.config(text="Auto: On")
        self._auto_thread = threading.Thread(target=self._auto_poll_loop, daemon=True)
        self._auto_thread.start()
        self._set_status("Auto-detect: watching…")

    def _stop_auto_detect(self) -> None:
        self._auto_stop.set()
        self._auto_active = False
        self.auto_btn.config(text="Auto: Off")
        self._set_status("Ready")

    def _auto_poll_loop(self) -> None:
        last_hash = ""
        stable_count = 0

        while not self._auto_stop.is_set():
            try:
                with mss.mss() as sct:
                    shot = sct.grab(self.region)
                    img = Image.frombytes("RGB", shot.size, shot.rgb)
                h = _image_hash(img)

                if h == last_hash:
                    stable_count = 0
                else:
                    stable_count += 1
                    last_hash = h
                    if stable_count >= AppConstants.AUTO_DEBOUNCE_COUNT:
                        stable_count = 0
                        self.root.after(0, self._trigger_translate)
            except Exception:
                pass

            self._auto_stop.wait(AppConstants.AUTO_POLL_INTERVAL)

    # ── Edit region toggle ────────────────────────────────────────────────────

    def toggle_edit_region(self) -> None:
        editing = self.region_selector.toggle_edit_mode()
        self.edit_region_btn.config(text="Lock Region" if editing else "Edit Region")

    # ── Translation pipeline ──────────────────────────────────────────────────

    def _trigger_translate(self) -> None:
        if self._job_in_flight:
            return
        self._job_in_flight = True
        self._set_buttons_enabled(False)
        self._set_status("Capturing…")
        threading.Thread(target=self._translate_worker, daemon=True).start()

    def _translate_worker(self) -> None:
        try:
            engine = read_json("config.json").get("ocr_engine", DEFAULT_CONFIG["ocr_engine"])

            if engine == "easyocr":
                self.root.after(0, lambda: self._set_status("Loading OCR model…"))

            with mss.mss() as sct:
                screenshot = sct.grab(self.region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            self.root.after(0, lambda: self._set_status("Running OCR…"))
            text = extract_text(img, engine)

            if text.strip():
                speaker, dialog, raw = standardize_dialog(text)
            else:
                speaker = AppConstants.UNKNOWN_SPEAKER
                dialog = ""
                raw = ""

            # Update other-speaker bar on main thread when speaker changes
            if (speaker != AppConstants.UNKNOWN_SPEAKER
                    and speaker != "Rover"
                    and speaker != self.current_other_speaker):
                self.root.after(0, lambda s=speaker: self._update_other_bar(s))

            if not dialog.strip():
                self.root.after(0, lambda: self._finish_translate(
                    raw, AppConstants.NO_TEXT_DETECTED, speaker
                ))
                return

            # Cache check
            cache_key = dialog.strip()
            if cache_key in self._cache:
                translated = self._cache[cache_key]
                self._cache.move_to_end(cache_key)
                self.root.after(0, lambda: self._finish_translate(raw, translated, speaker))
                return

            self.root.after(0, lambda: self._set_status("Translating…"))
            recent_history = self.translation_history[-5:]
            pronouns = self._get_current_pronouns(speaker)

            def on_chunk(partial: str) -> None:
                self.root.after(0, lambda p=partial: self._update_translated_display(p))

            translated = translate_with_llama(
                dialog, speaker, recent_history, on_chunk=on_chunk, pronouns=pronouns
            )

            # Update cache
            self._cache[cache_key] = translated
            if len(self._cache) > AppConstants.TRANSLATION_CACHE_SIZE:
                self._cache.popitem(last=False)

            self.root.after(0, lambda: self._finish_translate(raw, translated, speaker))

        except Exception as e:
            msg = f"Error: {str(e)}"
            logger.error(msg)
            self.root.after(0, lambda: self._on_translate_error(msg))

    def _update_translated_display(self, text: str) -> None:
        self.translated_text_area.delete(1.0, tk.END)
        self.translated_text_area.insert(tk.END, text, "center")

    def _finish_translate(self, raw: str, translated: str, speaker: str) -> None:
        self._last_speaker = speaker
        self.translation_history.append((speaker, raw, translated))
        self.translation_history = self.translation_history[-10:]

        self._update_text_areas(raw, translated)
        self._set_status("Ready")
        self._set_buttons_enabled(True)
        self._job_in_flight = False

    def _on_translate_error(self, msg: str) -> None:
        self._set_status(f"Error — {msg[:60]}")
        self._set_buttons_enabled(True)
        self._job_in_flight = False
        messagebox.showerror("Translation Error", msg)

    def translate_original_text(self) -> None:
        dialog = self.text_area.get(1.0, tk.END).strip()
        if not dialog or self._job_in_flight:
            return
        self._job_in_flight = True
        self._set_buttons_enabled(False)
        self._set_status("Re-translating…")

        def worker():
            try:
                recent_history = self.translation_history[-5:]
                pronouns = self._get_current_pronouns(self._last_speaker)

                def on_chunk(partial: str) -> None:
                    self.root.after(0, lambda p=partial: self._update_translated_display(p))

                translated = translate_with_llama(
                    dialog, self._last_speaker, recent_history,
                    on_chunk=on_chunk, pronouns=pronouns
                )
                self.root.after(0, lambda: self._finish_translate(dialog, translated, self._last_speaker))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda: self._on_translate_error(msg))

        threading.Thread(target=worker, daemon=True).start()

    # ── UI helpers ────────────────────────────────────────────────────────────

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.translate_btn.config(state=state)
        self.retranslate_btn.config(state=state)

    def _apply_font_size(self, size) -> None:
        self.default_font.configure(size=int(size))

    def _restore_styles(self) -> None:
        """Re-apply custom ttk styles after the settings window resets the theme."""
        self._setup_styles()
        self._refresh_pronoun_column(self._rover_self_btns, self._rover_self, self._rover_style_pair)
        self._refresh_pronoun_column(self._rover_to_other_btns, self._rover_to_other, self._rover_style_pair)
        self._refresh_pronoun_column(self._other_self_btns, self._other_self, self._other_style_pair)
        self._refresh_pronoun_column(self._other_to_rover_btns, self._other_to_rover, self._other_style_pair)

    def _update_text_areas(self, original_text: str, translated_text: str) -> None:
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, original_text or "No text detected.", "center")

        self.translated_text_area.delete(1.0, tk.END)
        self.translated_text_area.insert(tk.END, translated_text, "center")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _persist_layout(self) -> None:
        try:
            cfg = read_json("config.json")
            cfg["window_geometry"] = self.root.winfo_geometry()
            cfg["region"] = {
                "top": int(self.region["top"]),
                "left": int(self.region["left"]),
                "width": int(self.region["width"]),
                "height": int(self.region["height"]),
            }
            write_json("config.json", cfg)
        except Exception as e:
            logger.warning(f"Failed to persist layout: {e}")

    def _on_close(self) -> None:
        self._stop_auto_detect()
        self._persist_layout()
        try:
            import keyboard
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ensure_config()
    try:
        app = TranslatorApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        messagebox.showerror("Application Error", f"Failed to start: {str(e)}")


if __name__ == "__main__":
    main()
