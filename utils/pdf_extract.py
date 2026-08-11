import os
import pypdf

def parse_page_selection(page_input, total_pages):
    """
    Parse strings like "1,3,5", "2-7", "1,4-6,10" into a sorted list of unique 0-indexed page numbers.
    """
    selected_pages = set()
    parts = [p.strip() for p in page_input.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            sub = part.split("-")
            if len(sub) == 2 and sub[0].isdigit() and sub[1].isdigit():
                start, end = int(sub[0]), int(sub[1])
                for page in range(start, end + 1):
                    if 1 <= page <= total_pages:
                        selected_pages.add(page - 1)
        elif part.isdigit():
            page = int(part)
            if 1 <= page <= total_pages:
                selected_pages.add(page - 1)

    return sorted(list(selected_pages))

def extract_pages(input_file_path, output_file_path, page_selection_str):
    """
    Extract specific pages from PDF into a new PDF.
    :param page_selection_str: string like "1,3,5" or "2-7"
    """
    if not os.path.exists(input_file_path):
        return False, "Input PDF file not found."

    try:
        reader = pypdf.PdfReader(input_file_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            return False, "PDF file contains 0 pages."

        page_indices = parse_page_selection(page_selection_str, total_pages)

        if not page_indices:
            return False, f"Invalid page selection. Please enter numbers between 1 and {total_pages} (e.g., '1,3,5' or '2-5')."

        writer = pypdf.PdfWriter()
        for idx in page_indices:
            writer.add_page(reader.pages[idx])

        with open(output_file_path, "wb") as f_out:
            writer.write(f_out)
        
        writer.close()
        return True, f"Successfully extracted {len(page_indices)} page(s) into a new PDF."

    except Exception as e:
        return False, f"Page extraction failed: {str(e)}"
