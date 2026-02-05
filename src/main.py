"""
Wuthering Waves AI Translator - Main Application

A professional GUI application for real-time screen capture and translation
using OCR and AI translation services.

Author: Wuthering Waves AI Translator Team
Version: 2.0.0
"""

import mss
from PIL import Image
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Dict, List, Optional, Tuple, Any
import logging

from settings_window import open_settings_window
from ocr import extract_text_with_google_ocr, extract_text_from_image
from translators import translate_with_llama
from utils import standardize_dialog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AppConstants:
    """Application constants and configuration."""
    
    # Window dimensions and properties
    MAIN_WINDOW_SIZE = "950x250"
    LOG_WINDOW_SIZE = "600x400"
    
    # Default region settings
    DEFAULT_REGION = {"top": 100, "left": 100, "width": 800, "height": 150}
    MIN_REGION_SIZE = 50
    CORNER_THRESHOLD = 10
    
    # UI styling
    DEFAULT_FONT_FAMILY = "Arial"
    DEFAULT_FONT_SIZE = 16
    BUTTON_FONT = ("Helvetica", 10, "bold")
    
    # Colors
    SELECTOR_BG_COLOR = "#C4E1E6"
    SELECTOR_BORDER_COLOR = "#0065F8"
    BUTTON_BG_COLOR = "#A0DEFF"
    BUTTON_FG_COLOR = "#1D5D9B"
    BUTTON_ACTIVE_BG = "#1363DF"
    BUTTON_ACTIVE_FG = "#DFF6FF"
    SETTINGS_BG_COLOR = "#333446"
    SETTINGS_FG_COLOR = "#F5F5F5"
    
    # Messages
    NO_TEXT_DETECTED = "Không phát hiện văn bản."
    UNKNOWN_SPEAKER = "unknown"


class RegionSelector:
    """Handles the transparent region selection overlay."""
    
    def __init__(self, parent: tk.Tk, region: Dict[str, int]):
        self.parent = parent
        self.region = region
        self.dragging = False
        self.resizing = False
        self.resize_corner: Optional[str] = None
        self.start_x = 0
        self.start_y = 0
        
        self._create_selector_window()
        self._bind_events()
    
    def _create_selector_window(self) -> None:
        """Create the transparent selector window."""
        self.selector = tk.Toplevel(self.parent)
        self.selector.geometry(
            f"{self.region['width']}x{self.region['height']}+"
            f"{self.region['left']}+{self.region['top']}"
        )
        self.selector.attributes("-alpha", 0.3)
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
        """Bind mouse events for region interaction."""
        self.canvas.bind("<Button-1>", self._start_interaction)
        self.canvas.bind("<ButtonRelease-1>", self._stop_interaction)
        self.canvas.bind("<B1-Motion>", self._motion_interaction)
        self.canvas.bind("<Motion>", self._update_cursor)
    
    def _is_near_corner(self, x: int, y: int) -> Optional[str]:
        """Check if mouse position is near a corner for resizing."""
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
        """Start dragging or resizing interaction."""
        self.resize_corner = self._is_near_corner(event.x, event.y)
        self.dragging = not self.resize_corner
        self.resizing = bool(self.resize_corner)
        self.start_x = event.x_root
        self.start_y = event.y_root
    
    def _stop_interaction(self, event: tk.Event) -> None:
        """Stop dragging or resizing interaction."""
        self.dragging = self.resizing = False
        self.resize_corner = None
        self._update_region()
    
    def _update_cursor(self, event: tk.Event) -> None:
        """Update cursor based on mouse position."""
        corner = self._is_near_corner(event.x, event.y)
        if corner in ["top-left", "bottom-right"]:
            self.canvas.config(cursor="size_nw_se")
        elif corner in ["top-right", "bottom-left"]:
            self.canvas.config(cursor="size_ne_sw")
        else:
            self.canvas.config(cursor="fleur")
    
    def _motion_interaction(self, event: tk.Event) -> None:
        """Handle mouse motion for dragging or resizing."""
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
        """Handle resizing based on the corner being dragged."""
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
        
        # Ensure minimum size
        self.region["width"] = max(self.region["width"], AppConstants.MIN_REGION_SIZE)
        self.region["height"] = max(self.region["height"], AppConstants.MIN_REGION_SIZE)
    
    def _update_selector_geometry(self) -> None:
        """Update the selector window geometry."""
        self.selector.geometry(
            f"{self.region['width']}x{self.region['height']}+"
            f"{self.region['left']}+{self.region['top']}"
        )
    
    def _update_region(self) -> None:
        """Update region coordinates from selector window."""
        self.region["left"] = self.selector.winfo_x()
        self.region["top"] = self.selector.winfo_y()
        self.region["width"] = self.selector.winfo_width()
        self.region["height"] = self.selector.winfo_height()
        logger.info(f"Region updated: {self.region}")


class TranslatorApp:
    """Main application class for the AI Translator."""
    
    def __init__(self):
        self.region = AppConstants.DEFAULT_REGION.copy()
        self.full_log: List[str] = []
        self.log_window: Optional[tk.Toplevel] = None
        self.log_text_area: Optional[tk.Text] = None
        self.original_text_visible = False
        
        self._setup_main_window()
        self._setup_styles()
        self._create_region_selector()
        self._create_ui_components()
        
        logger.info("Translator application initialized successfully")
    
    def _setup_main_window(self) -> None:
        """Initialize the main application window."""
        self.root = tk.Tk()
        self.root.title("Gió Hú AI Translator")
        self.root.geometry(AppConstants.MAIN_WINDOW_SIZE)
        self.root.attributes("-topmost", True)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        
        # Set up default font
        self.default_font = tkFont.Font(
            family=AppConstants.DEFAULT_FONT_FAMILY,
            size=AppConstants.DEFAULT_FONT_SIZE
        )
    
    def _setup_styles(self) -> None:
        """Configure custom styles for UI components."""
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
            background=[
                ("active", AppConstants.BUTTON_ACTIVE_BG),
                ("pressed", "#90D7DC")
            ],
            foreground=[("active", AppConstants.BUTTON_ACTIVE_FG)]
        )
    
    def _create_region_selector(self) -> None:
        """Create the region selector overlay."""
        self.region_selector = RegionSelector(self.root, self.region)
    
    def _create_ui_components(self) -> None:
        """Create all UI components."""
        self._create_button_frame()
        self._create_text_areas()
        self._create_settings_button()
    
    def _create_button_frame(self) -> None:
        """Create the button frame and all control buttons."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=0, column=1, rowspan=3, sticky="ns", padx=5, pady=5)
        
        # Main translate button
        ttk.Button(
            self.button_frame,
            text="Translate $",
            command=self.capture_and_translate,
            style="Translate.TButton"
        ).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        
        # Re-translate button
        ttk.Button(
            self.button_frame,
            text="Re-translate",
            command=self.translate_original_text,
            style="Translate.TButton"
        ).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        
        # Show/Hide raw text button
        self.show_text_button = ttk.Button(
            self.button_frame,
            text="Show Raw",
            command=self.toggle_original_text,
            style="Translate.TButton"
        )
        self.show_text_button.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        
        # Google OCR checkbox
        self.use_google_ocr_var = tk.BooleanVar()
        tk.Checkbutton(
            self.button_frame,
            text="Use Google OCR",
            variable=self.use_google_ocr_var
        ).grid(row=3, column=0, sticky="w", padx=2, pady=2)
        
        # Log window button
        self.log_button = ttk.Button(
            self.button_frame,
            text="Show Log",
            command=self.toggle_log_window,
            style="Translate.TButton"
        )
        self.log_button.grid(row=4, column=0, sticky="ew", padx=2, pady=2)
        
        # Export log button
        ttk.Button(
            self.button_frame,
            text="Export Log",
            command=self.export_log_to_file,
            style="Translate.TButton"
        ).grid(row=5, column=0, sticky="ew", padx=2, pady=2)
    
    def _create_text_areas(self) -> None:
        """Create text areas for original and translated text."""
        # Original text frame (initially hidden)
        self.original_frame = tk.Frame(self.root)
        self.original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.original_frame.grid_remove()
        
        self.text_area = tk.Text(
            self.original_frame,
            width=40, height=3,
            wrap="word",
            font=self.default_font,
            padx=10, pady=10,
            spacing1=4, spacing3=4
        )
        self.text_area.pack(side="top", fill="both", expand=True)
        self.text_area.tag_configure("center", justify="center")
        
        # Translated text area
        self.translated_text_area = tk.Text(
            self.root,
            width=40, height=5,
            wrap="word",
            font=self.default_font,
            padx=30, pady=10,
            spacing2=3, spacing3=10
        )
        self.translated_text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        self.translated_text_area.tag_configure("center", justify="center")
    
    def _create_settings_button(self) -> None:
        """Create the settings button."""
        self.settings_btn = tk.Button(
            self.root,
            text="Config",
            font=("Helvetica", 10),
            relief="flat",
            bg=AppConstants.SETTINGS_BG_COLOR,
            fg=AppConstants.SETTINGS_FG_COLOR,
            command=lambda: open_settings_window(self.root)
        )
        self.settings_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
    
    def capture_and_translate(self) -> None:
        """Capture screen region and translate the extracted text."""
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(self.region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
                # Extract text using selected OCR method
                if self.use_google_ocr_var.get():
                    text = extract_text_with_google_ocr(img)
                else:
                    text = extract_text_from_image(img)
                
                # Process extracted text
                if text.strip():
                    _, dialog, text = standardize_dialog(text)
                else:
                    dialog = AppConstants.NO_TEXT_DETECTED
                
                # Translate the dialog
                translated = (translate_with_llama(dialog)
                            if dialog.strip() else AppConstants.NO_TEXT_DETECTED)
                
                # Update log and UI
                self._update_log(translated)
                self._update_text_areas(dialog, translated)
                
                logger.info("Translation completed successfully")
                
        except Exception as e:
            error_msg = f"Error during capture and translation: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Translation Error", error_msg)
    
    def translate_original_text(self) -> None:
        """Re-translate the text currently in the original text area."""
        try:
            dialog = self.text_area.get(1.0, tk.END).strip()
            if not dialog:
                return
            
            translated = translate_with_llama(dialog)
            
            self.translated_text_area.delete(1.0, tk.END)
            self.translated_text_area.insert(tk.END, translated, "center")
            
            logger.info("Re-translation completed successfully")
            
        except Exception as e:
            error_msg = f"Error during re-translation: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Re-translation Error", error_msg)
    
    def toggle_original_text(self) -> None:
        """Toggle visibility of the original text area."""
        if self.original_text_visible:
            self.original_frame.grid_remove()
            self.show_text_button.config(text="Show Raw")
        else:
            self.original_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
            self.show_text_button.config(text="Hide Raw")
        
        self.original_text_visible = not self.original_text_visible
    
    def toggle_log_window(self) -> None:
        """Toggle the log history window."""
        if self.log_window and self.log_window.winfo_exists():
            self._close_log_window()
        else:
            self._open_log_window()
    
    def _open_log_window(self) -> None:
        """Open the log history window."""
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Log History")
        self.log_window.geometry(AppConstants.LOG_WINDOW_SIZE)
        
        self.log_text_area = tk.Text(
            self.log_window,
            wrap="word",
            font=self.default_font
        )
        self.log_text_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text_area.insert("1.0", "\n\n".join(self.full_log))
        self.log_text_area.config(state="disabled")
        
        self.log_button.config(text="Hide Log")
        self.log_window.protocol("WM_DELETE_WINDOW", self._close_log_window)
    
    def _close_log_window(self) -> None:
        """Close the log history window."""
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
            self.log_text_area = None
            self.log_button.config(text="Show Log")
    
    def export_log_to_file(self) -> None:
        """Export the translation log to a text file."""
        if not self.full_log:
            messagebox.showinfo("Export Log", "No log entries to export.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(self.full_log))
                
                messagebox.showinfo("Export Log", f"Log exported successfully to {file_path}")
                logger.info(f"Log exported to {file_path}")
                
        except Exception as e:
            error_msg = f"Error exporting log: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def _update_log(self, translated_text: str) -> None:
        """Update the full log with new translated text."""
        self.full_log.append(translated_text)
        
        # Update log window if it's open
        if self.log_window and self.log_text_area:
            self.log_text_area.config(state="normal")
            self.log_text_area.insert(tk.END, f"{translated_text.strip()}\n\n")
            self.log_text_area.config(state="disabled")
            self.log_text_area.see(tk.END)
    
    def _update_text_areas(self, original_text: str, translated_text: str) -> None:
        """Update both original and translated text areas."""
        # Update original text area
        self.text_area.delete(1.0, tk.END)
        display_text = original_text if original_text.strip() else "No text detected."
        self.text_area.insert(tk.END, display_text, "center")
        
        # Update translated text area
        self.translated_text_area.delete(1.0, tk.END)
        self.translated_text_area.insert(tk.END, translated_text, "center")
    
    def run(self) -> None:
        """Start the application main loop."""
        try:
            logger.info("Starting application main loop")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            raise


def main() -> None:
    """Main entry point of the application."""
    try:
        app = TranslatorApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()
