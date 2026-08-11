import os
import zipfile
import pypdf

def parse_range_string(range_str, total_pages):
    """
    Parse a range string like "1-5, 6-10" into list of (start, end) tuples (1-indexed).
    """
    ranges = []
    parts = [p.strip() for p in range_str.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            sub = part.split("-")
            if len(sub) == 2 and sub[0].isdigit() and sub[1].isdigit():
                start, end = int(sub[0]), int(sub[1])
                start = max(1, min(start, total_pages))
                end = max(1, min(end, total_pages))
                if start <= end:
                    ranges.append((start, end))
        elif part.isdigit():
            val = int(part)
            if 1 <= val <= total_pages:
                ranges.append((val, val))
    return ranges

def split_pdf(input_file_path, output_dir, split_mode="all", range_str=""):
    """
    Split PDF into separate files or ranges.
    If multiple files generated, create a ZIP file.
    :param split_mode: "all" or "range"
    :param range_str: range string like "1-5, 6-10"
    :return: (success, output_filepath, is_zip, message)
    """
    if not os.path.exists(input_file_path):
        return False, None, False, "Input PDF file does not exist."

    try:
        reader = pypdf.PdfReader(input_file_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            return False, None, False, "PDF file has no pages."

        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        generated_files = []

        if split_mode == "all":
            for idx in range(total_pages):
                writer = pypdf.PdfWriter()
                writer.add_page(reader.pages[idx])
                out_filename = f"{base_name}_page_{idx+1}.pdf"
                out_path = os.path.join(output_dir, out_filename)
                with open(out_path, "wb") as f_out:
                    writer.write(f_out)
                writer.close()
                generated_files.append(out_path)
        elif split_mode == "range":
            ranges = parse_range_string(range_str, total_pages)
            if not ranges:
                return False, None, False, f"Invalid page ranges specified. Total pages in PDF: {total_pages}"

            for idx, (start, end) in enumerate(ranges):
                writer = pypdf.PdfWriter()
                for p in range(start - 1, end):
                    writer.add_page(reader.pages[p])
                out_filename = f"{base_name}_range_{start}_to_{end}.pdf"
                out_path = os.path.join(output_dir, out_filename)
                with open(out_path, "wb") as f_out:
                    writer.write(f_out)
                writer.close()
                generated_files.append(out_path)
        else:
            return False, None, False, "Invalid split mode."

        if not generated_files:
            return False, None, False, "No output files were generated."

        if len(generated_files) == 1:
            return True, generated_files[0], False, "PDF split successfully."

        # Multiple files -> package into ZIP
        zip_filename = f"{base_name}_split_files.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in generated_files:
                zipf.write(f, os.path.basename(f))
                # Clean up individual file if zipped
                try:
                    os.remove(f)
                except Exception:
                    pass

        return True, zip_path, True, f"PDF split into {len(generated_files)} files (packaged into ZIP)."

    except Exception as e:
        return False, None, False, f"Split operation failed: {str(e)}"
