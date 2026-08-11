import os
import pypdf

def merge_pdfs(input_file_paths, output_file_path):
    """
    Merge a list of PDF file paths into a single output PDF file.
    :param input_file_paths: List of absolute file paths to input PDFs
    :param output_file_path: Absolute destination path for merged PDF
    :return: (True, output_file_path) on success, or (False, error_message)
    """
    if not input_file_paths or len(input_file_paths) < 2:
        return False, "At least two PDF files are required for merging."

    writer = pypdf.PdfWriter()
    
    try:
        merged_pages = 0
        for path in input_file_paths:
            if not os.path.exists(path):
                return False, f"File not found: {os.path.basename(path)}"
            
            reader = pypdf.PdfReader(path)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return False, f"File '{os.path.basename(path)}' is password protected."
            
            for page in reader.pages:
                writer.add_page(page)
                merged_pages += 1
        
        with open(output_file_path, "wb") as f_out:
            writer.write(f_out)
        
        writer.close()
        return True, f"Successfully merged {len(input_file_paths)} files ({merged_pages} pages)."

    except Exception as e:
        return False, f"Merge failed: {str(e)}"
