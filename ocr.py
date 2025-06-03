
import io
import json
import base64
import easyocr
import requests
from PIL import Image, ImageOps, ImageEnhance

from utils import check_create_folder


# ============================= GLOBAL PARAMS =============================
with open("config.json", "r", encoding='utf-8') as f:
    config = json.load(f)

# Initialize EasyOCR
reader = easyocr.Reader(config["easyocr_lg"])

# Google OCR API settings
GOOGLE_OCR_API_KEY = config["google_ocr_api_key"]
# =========================================================================


# OCR with EasyOCR
def extract_text_from_image(pil_img):
    img = ImageOps.grayscale(pil_img)
    # Light contrast and brightness boost
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Brightness(img).enhance(1.1)

    # 2x upscale using LANCZOS (best for sharp edges)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    check_create_folder("asset_tmp")
    img.save("asset_tmp\\temp_capture.png")

    # OCR
    result = reader.readtext("asset_tmp\\temp_capture.png", detail=0, paragraph=True)
    raw_text = '\n'.join(result)
    return raw_text


def extract_text_with_google_ocr(img):
    try:
        # Convert image to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_OCR_API_KEY}"
        payload = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        annotations = response.json()["responses"][0]
        raw_text = annotations.get("textAnnotations", [{}])[0].get("description", "").strip()
        return raw_text
    except Exception as e:
        return f"[Google OCR Error] {str(e)}"