import io
import base64
import numpy as np
import requests
from PIL import Image, ImageOps, ImageEnhance

from utils import read_json
from default_params import DEFAULT_CONFIG

# Lazy EasyOCR reader — only instantiated on first use
_easyocr_reader = None


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        _easyocr_reader = easyocr.Reader(DEFAULT_CONFIG["easyocr_lg"])
    return _easyocr_reader


def _preprocess(pil_img):
    img = ImageOps.grayscale(pil_img)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img


def extract_text_with_windows_ocr(pil_img):
    """OCR via Windows.Media.OCR — free, offline, no torch dependency."""
    import winocr
    result = winocr.recognize_pil_sync(_preprocess(pil_img), "en")
    return result.text if result else ""


def extract_text_from_image(pil_img):
    """OCR via EasyOCR (offline, requires torch). Lazy-loaded on first use."""
    img = _preprocess(pil_img)
    arr = np.array(img)
    reader = _get_easyocr_reader()
    result = reader.readtext(arr, detail=0, paragraph=True)
    return '\n'.join(result)


def extract_text_with_google_ocr(pil_img):
    """OCR via Google Vision API (requires API key)."""
    api_key = read_json("config.json").get("google_ocr_api_key", "")

    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    payload = {
        "requests": [{
            "image": {"content": image_base64},
            "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            "imageContext": {"languageHints": ["en"]}
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        annotations = response.json()["responses"][0]
        return annotations.get("textAnnotations", [{}])[0].get("description", "").strip()
    except Exception as e:
        return f"[Google OCR Error] {str(e)}"


def extract_text(pil_img, engine="windows"):
    """Dispatch to the configured OCR engine."""
    if engine == "google":
        return extract_text_with_google_ocr(pil_img)
    elif engine == "easyocr":
        return extract_text_from_image(pil_img)
    else:
        return extract_text_with_windows_ocr(pil_img)
