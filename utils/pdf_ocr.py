import os
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def is_tesseract_available():
    """Check if Tesseract-OCR is installed and accessible."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        # Common Windows path check if default PATH doesn't have it
        win_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(win_default):
            pytesseract.pytesseract.tesseract_cmd = win_default
            try:
                pytesseract.get_tesseract_version()
                return True
            except Exception:
                return False
        return False

def extract_ocr_text(file_path):
    """
    Perform OCR on scanned PDF pages.
    Returns dict with OCR extracted text, stats, or detailed error message.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": "File not found"}

    if not is_tesseract_available():
        return {
            "success": False,
            "tesseract_missing": True,
            "error": "Tesseract OCR engine is not installed or not in PATH. Please install Tesseract-OCR to enable scanned PDF text recognition."
        }

    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        ocr_text_pages = []

        for page_num in range(total_pages):
            page = doc[page_num]
            # Render page to high-res image (200 DPI matrix)
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))

            # Execute Tesseract OCR
            text = pytesseract.image_to_string(img)
            if text.strip():
                ocr_text_pages.append(f"--- Page {page_num + 1} (OCR) ---\n" + text.strip())

        doc.close()

        full_text = "\n\n".join(ocr_text_pages)
        char_count = len(full_text)
        words = full_text.split()
        word_count = len(words)

        return {
            "success": True,
            "text": full_text if full_text else "No text could be recognized by OCR.",
            "pages_processed": total_pages,
            "word_count": word_count,
            "char_count": char_count,
            "tesseract_missing": False
        }

    except Exception as e:
        return {"success": False, "error": f"OCR processing error: {str(e)}"}
