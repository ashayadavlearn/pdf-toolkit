import os
import pypdf
from utils.pdf_extract import parse_page_selection

def rotate_pdf(input_file_path, output_file_path, angle=90, scope="all", page_selection_str=""):
    """
    Rotate PDF pages clockwise by specified angle (90, 180, 270).
    :param scope: "all" or "selected"
    :param page_selection_str: string like "1,3,5" or "2-7" if scope == "selected"
    """
    if not os.path.exists(input_file_path):
        return False, "Input PDF file not found."

    if angle not in [90, 180, 270]:
        return False, "Invalid rotation angle. Must be 90, 180, or 270 degrees."

    try:
        reader = pypdf.PdfReader(input_file_path)
        writer = pypdf.PdfWriter()
        total_pages = len(reader.pages)

        if total_pages == 0:
            return False, "PDF contains 0 pages."

        target_indices = set()
        if scope == "all":
            target_indices = set(range(total_pages))
        else:
            selected = parse_page_selection(page_selection_str, total_pages)
            if not selected:
                return False, f"Invalid page range specified. Total pages: {total_pages}"
            target_indices = set(selected)

        rotated_count = 0
        for i in range(total_pages):
            page = reader.pages[i]
            if i in target_indices:
                page.rotate(angle)
                rotated_count += 1
            writer.add_page(page)

        with open(output_file_path, "wb") as f_out:
            writer.write(f_out)
        
        writer.close()
        return True, f"Successfully rotated {rotated_count} page(s) by {angle}°."

    except Exception as e:
        return False, f"Rotation failed: {str(e)}"
