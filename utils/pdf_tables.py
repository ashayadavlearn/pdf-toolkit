import os
import pdfplumber
import pandas as pd

def extract_tables_from_pdf(file_path, page_number=1, output_dir=None):
    """
    Extract tables from specified PDF page using pdfplumber.
    Exports to CSV and XLSX if requested.
    :param page_number: 1-indexed page number
    :return: dict with HTML representation, CSV/XLSX paths, row/col stats
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": "File not found"}

    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            if page_number < 1 or page_number > total_pages:
                return {"success": False, "error": f"Page number {page_number} is out of range (1 - {total_pages})."}

            target_page = pdf.pages[page_number - 1]
            tables = target_page.extract_tables()

            if not tables or len(tables) == 0:
                return {
                    "success": True,
                    "has_tables": False,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "message": f"No tables detected on page {page_number} of this PDF."
                }

            # Process the primary extracted table
            primary_table = tables[0]
            if not primary_table or len(primary_table) == 0:
                return {
                    "success": True,
                    "has_tables": False,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "message": f"No valid tabular data found on page {page_number}."
                }

            # Convert to DataFrame
            # First row as header if available
            headers = primary_table[0]
            data_rows = primary_table[1:] if len(primary_table) > 1 else []

            # Clean nulls
            headers = [str(h or "").strip() for h in headers]
            cleaned_rows = []
            for row in data_rows:
                cleaned_rows.append([str(cell or "").strip() for cell in row])

            if cleaned_rows and len(headers) == len(cleaned_rows[0]):
                df = pd.DataFrame(cleaned_rows, columns=headers)
            else:
                df = pd.DataFrame(primary_table)

            # Generate HTML table representation
            html_table = df.to_html(classes="table table-striped table-hover table-bordered", index=False)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            csv_path = None
            excel_path = None

            if output_dir:
                csv_filename = f"{base_name}_page{page_number}_table.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                df.to_csv(csv_path, index=False)

                excel_filename = f"{base_name}_page{page_number}_table.xlsx"
                excel_path = os.path.join(output_dir, excel_filename)
                df.to_excel(excel_path, index=False, engine='openpyxl')

            return {
                "success": True,
                "has_tables": True,
                "table_count": len(tables),
                "page_number": page_number,
                "total_pages": total_pages,
                "html_table": html_table,
                "rows_count": len(df),
                "cols_count": len(df.columns),
                "csv_path": csv_path,
                "excel_path": excel_path,
                "csv_filename": os.path.basename(csv_path) if csv_path else None,
                "excel_filename": os.path.basename(excel_path) if excel_path else None
            }

    except Exception as e:
        return {"success": False, "error": f"Table extraction error: {str(e)}"}
