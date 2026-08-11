import os
import fitz  # PyMuPDF
import pypdf
from utils.pdf_info import format_size

def compress_pdf(input_file_path, output_file_path, level="medium"):
    """
    Compress a PDF file with Low, Medium, or High compression settings.
    Returns dict with file size reduction metrics.
    """
    if not os.path.exists(input_file_path):
        return {"success": False, "error": "Input file not found."}

    original_size = os.path.getsize(input_file_path)

    try:
        # Determine image downsampling and quality params based on compression level
        if level == "low":
            dpi = 200
            jpg_quality = 85
        elif level == "high":
            dpi = 90
            jpg_quality = 40
        else:  # medium (default)
            dpi = 140
            jpg_quality = 65

        doc = fitz.open(input_file_path)

        # PyMuPDF garbage collection, clean metadata, Deflate content streams
        # garbage=4: remove unused objects, compact streams, deduplicate
        doc.save(
            output_file_path,
            garbage=4,
            deflate=True,
            clean=True,
            deflate_images=True,
            deflate_fonts=True
        )
        doc.close()

        # Secondary pass with pypdf to ensure stream compression
        try:
            reader = pypdf.PdfReader(output_file_path)
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)

            temp_compressed = output_file_path + ".tmp"
            with open(temp_compressed, "wb") as f_out:
                writer.write(f_out)
            writer.close()

            # If secondary pass is smaller, adopt it
            if os.path.exists(temp_compressed) and os.path.getsize(temp_compressed) < os.path.getsize(output_file_path):
                os.replace(temp_compressed, output_file_path)
            else:
                if os.path.exists(temp_compressed):
                    os.remove(temp_compressed)
        except Exception:
            pass  # Keep PyMuPDF optimized output

        compressed_size = os.path.getsize(output_file_path)

        # If compressed size ended up larger (e.g. text-only PDF already deflated), keep copy of original
        if compressed_size > original_size:
            with open(input_file_path, "rb") as f_in, open(output_file_path, "wb") as f_out:
                f_out.write(f_in.read())
            compressed_size = original_size

        bytes_saved = original_size - compressed_size
        percentage_reduction = (bytes_saved / original_size * 100) if original_size > 0 else 0

        return {
            "success": True,
            "original_size": format_size(original_size),
            "original_size_bytes": original_size,
            "compressed_size": format_size(compressed_size),
            "compressed_size_bytes": compressed_size,
            "bytes_saved": format_size(bytes_saved),
            "percentage_reduction": round(percentage_reduction, 2),
            "output_path": output_file_path,
            "output_filename": os.path.basename(output_file_path)
        }

    except Exception as e:
        return {"success": False, "error": f"Compression failed: {str(e)}"}
