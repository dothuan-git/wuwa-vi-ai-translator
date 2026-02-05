# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fan-made Windows desktop app that translates *Wuthering Waves* game dialogue (English → Vietnamese) using OCR + AI translation. Built with Python/Tkinter. Uses Groq API for translation, with EasyOCR (offline) or Google Vision API (optional) for text recognition.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py

# Check GPU/CUDA support for EasyOCR
python check_cuda.py
```

No test suite or linter is configured. The project uses Inno Setup (`setup.iss`) for building the Windows installer.

## Architecture

```
src/main.py           → Entry point. TranslatorApp (Tkinter GUI) + RegionSelector (transparent overlay)
src/ocr.py            → OCR engines: EasyOCR (offline) and Google Vision API
src/translators.py    → AI translation via Groq API (OpenAI-compatible endpoint)
src/utils.py          → Dialog parsing (speaker extraction), prompt building
src/settings_window.py → Config UI for API keys, custom prompts
src/default_params.py  → Default config values (API URLs, system/user prompts)
```

**Data flow**: Screen capture (mss) → image preprocessing (PIL/OpenCV) → OCR → dialog standardization → Groq API translation → display

**Config storage**: JSON files in `%APPDATA%/GioHuAI/` (`config.json` for API keys/prompts, `characters.json` for character name lookup in dialog standardization).

## Key Design Details

- **RegionSelector**: Transparent Tkinter overlay (30% alpha) that users drag over game text. Supports corner-based resizing with 10px detection threshold, minimum 50x50px.
- **Dialog standardization** (`utils.py`): Extracts speaker name from first line, handles "F" marker (represents Rover/player character), normalizes multi-line text.
- **Translation**: Groq API with temperature 0.3. System prompt is RPG localization-focused. Supports user-customizable prompts.
- **Windows-only**: Uses `mss` for screen capture, `%APPDATA%` for config. No cross-platform support.
