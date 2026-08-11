import os
import fitz  # PyMuPDF
import pdfplumber
import pypdf

def extract_digital_text(file_path):
    """
    Extract text from a digital PDF file using pdfplumber / PyMuPDF.
    Returns dict with extracted text, page count, word count, char count.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": "File not found"}

    try:
        pages_text = []
        total_pages = 0

        # Try fitz first for speed and layout retention
        try:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            for page_num in range(total_pages):
                p = doc[page_num]
                txt = p.get_text("text")
                if txt.strip():
                    pages_text.append(f"--- Page {page_num + 1} ---\n" + txt)
            doc.close()
        except Exception:
            # Fallback to pdfplumber
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                for idx, page in enumerate(pdf.pages):
                    txt = page.extract_text() or ""
                    if txt.strip():
                        pages_text.append(f"--- Page {idx + 1} ---\n" + txt)

        full_text = "\n\n".join(pages_text)
        char_count = len(full_text)
        words = full_text.split()
        word_count = len(words)

        if char_count == 0:
            return {
                "success": True,
                "text": "",
                "pages_processed": total_pages,
                "word_count": 0,
                "char_count": 0,
                "is_empty": True,
                "message": "No text detected in this PDF. It may be a scanned document or image-only PDF. Try using the OCR tool!"
            }

        return {
            "success": True,
            "text": full_text,
            "pages_processed": total_pages,
            "word_count": word_count,
            "char_count": char_count,
            "is_empty": False
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to extract text: {str(e)}"}

def save_text_as_pdf(text, output_pdf_path):
    """
    Convert text content into a clean PDF file using fitz.
    """
    try:
        doc = fitz.open()
        page = doc.new_page()
        margin = 50
        rect = fitz.Rect(margin, margin, page.rect.width - margin, page.rect.height - margin)
        
        # Add text with automatic page flow
        font_size = 11
        lines = text.split('\n')
        y = margin
        
        for line in lines:
            if y > page.rect.height - margin:
                page = doc.new_page()
                y = margin
            page.insert_text((margin, y), line[:100], fontsize=font_size)
            y += font_size + 4

        doc.save(output_pdf_path)
        doc.close()
        return True, output_pdf_path
    except Exception as e:
        return False, str(e)
