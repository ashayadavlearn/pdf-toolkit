import os
import pypdf
from utils.pdf_extract import parse_page_selection

def delete_pdf_pages(input_file_path, output_file_path, page_selection_str):
    """
    Delete specified pages from PDF document.
    Prevents deleting all pages.
    """
    if not os.path.exists(input_file_path):
        return False, "Input file not found."

    try:
        reader = pypdf.PdfReader(input_file_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            return False, "PDF contains 0 pages."

        delete_indices = set(parse_page_selection(page_selection_str, total_pages))

        if not delete_indices:
            return False, f"Invalid page numbers to delete. Total pages: {total_pages}"

        if len(delete_indices) >= total_pages:
            return False, "Cannot delete all pages from the PDF. At least 1 page must remain."

        writer = pypdf.PdfWriter()
        kept_count = 0

        for i in range(total_pages):
            if i not in delete_indices:
                writer.add_page(reader.pages[i])
                kept_count += 1

        with open(output_file_path, "wb") as f_out:
            writer.write(f_out)
        
        writer.close()
        return True, f"Successfully deleted {len(delete_indices)} page(s). Remaining pages: {kept_count}."

    except Exception as e:
        return False, f"Delete operation failed: {str(e)}"
