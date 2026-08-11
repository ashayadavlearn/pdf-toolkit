import os
import uuid
from datetime import datetime
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, send_from_directory, jsonify
)
from werkzeug.utils import secure_filename

# Local configurations and database
import config
from database import log_operation, get_history, clear_history, get_stats

# PDF Processing Utility imports
from utils.pdf_info import get_pdf_info
from utils.pdf_merge import merge_pdfs
from utils.pdf_split import split_pdf
from utils.pdf_extract import extract_pages
from utils.pdf_text import extract_digital_text, save_text_as_pdf
from utils.pdf_ocr import extract_ocr_text
from utils.pdf_tables import extract_tables_from_pdf
from utils.pdf_compress import compress_pdf
from utils.pdf_rotate import rotate_pdf
from utils.pdf_delete import delete_pdf_pages

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = str(config.UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(config.OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename, prefix=""):
    safe_name = secure_filename(original_filename)
    name_stem = Path(safe_name).stem
    ext = Path(safe_name).suffix or ".pdf"
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix_str = f"{prefix}_" if prefix else ""
    return f"{prefix_str}{name_stem}_{timestamp}_{unique_id}{ext}"

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def index():
    stats = get_stats()
    recent_history = get_history(limit=5)
    return render_template('index.html', stats=stats, recent_history=recent_history)

@app.route('/api/pdf-info', methods=['POST'])
def api_pdf_info():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Empty filename"})

    temp_filename = generate_unique_filename(file.filename, prefix="temp")
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    
    try:
        file.save(temp_path)
        info = get_pdf_info(temp_path)
        return jsonify({"success": True, "info": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.route('/merge', methods=['GET', 'POST'])
def merge_pdf_route():
    if request.method == 'POST':
        files = request.files.getlist('files')
        valid_files = [f for f in files if f and f.filename and allowed_file(f.filename)]

        if len(valid_files) < 2:
            flash("Please upload at least 2 valid PDF files to merge.", "error")
            return redirect(url_for('merge_pdf_route'))

        saved_input_paths = []
        original_filenames = []

        try:
            for file in valid_files:
                filename = generate_unique_filename(file.filename, prefix="in_merge")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_input_paths.append(filepath)
                original_filenames.append(file.filename)

            output_filename = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.pdf"
            output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            success, message = merge_pdfs(saved_input_paths, output_filepath)

            if success:
                log_operation(
                    operation_type="Merge PDF",
                    input_filename=", ".join(original_filenames),
                    output_filename=output_filename,
                    status="Success",
                    details=f"Merged {len(valid_files)} PDF documents"
                )
                flash("PDFs merged successfully!", "success")
                return render_template(
                    'result.html',
                    title="PDFs Merged Successfully!",
                    message=f"Combined {len(valid_files)} PDF files into one output document.",
                    filename=output_filename,
                    return_url=url_for('merge_pdf_route')
                )
            else:
                log_operation(
                    operation_type="Merge PDF",
                    input_filename=", ".join(original_filenames),
                    output_filename="-",
                    status="Failed",
                    details=message
                )
                flash(f"Merge error: {message}", "error")
                return redirect(url_for('merge_pdf_route'))

        except Exception as e:
            flash(f"Unexpected error during merge: {str(e)}", "error")
            return redirect(url_for('merge_pdf_route'))
        finally:
            for p in saved_input_paths:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
def split_pdf_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in upload request.", "error")
            return redirect(url_for('split_pdf_route'))

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid .pdf file.", "error")
            return redirect(url_for('split_pdf_route'))

        split_mode = request.form.get('split_mode', 'all')
        range_str = request.form.get('range_str', '').strip()

        input_filename = generate_unique_filename(file.filename, prefix="in_split")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        try:
            success, output_path, is_zip, message = split_pdf(
                input_file_path=input_path,
                output_dir=app.config['OUTPUT_FOLDER'],
                split_mode=split_mode,
                range_str=range_str
            )

            if success:
                out_name = os.path.basename(output_path)
                log_operation(
                    operation_type="Split PDF",
                    input_filename=file.filename,
                    output_filename=out_name,
                    status="Success",
                    details=message
                )
                flash("PDF split successfully!", "success")
                return render_template(
                    'result.html',
                    title="PDF Split Successfully!",
                    message=message,
                    filename=out_name,
                    return_url=url_for('split_pdf_route')
                )
            else:
                log_operation("Split PDF", file.filename, "-", "Failed", message)
                flash(f"Split error: {message}", "error")
                return redirect(url_for('split_pdf_route'))

        except Exception as e:
            flash(f"Error splitting PDF: {str(e)}", "error")
            return redirect(url_for('split_pdf_route'))
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('split.html')

@app.route('/extract', methods=['GET', 'POST'])
def extract_pages_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No PDF file provided.", "error")
            return redirect(url_for('extract_pages_route'))

        file = request.files['file']
        page_selection = request.form.get('page_selection', '').strip()

        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid .pdf file.", "error")
            return redirect(url_for('extract_pages_route'))

        if not page_selection:
            flash("Please enter page numbers to extract.", "error")
            return redirect(url_for('extract_pages_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_extract")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        output_filename = generate_unique_filename(file.filename, prefix="extracted")
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        try:
            success, message = extract_pages(input_path, output_path, page_selection)

            if success:
                log_operation(
                    operation_type="Extract Pages",
                    input_filename=file.filename,
                    output_filename=output_filename,
                    status="Success",
                    details=f"Extracted range '{page_selection}'"
                )
                flash("Selected pages extracted successfully!", "success")
                return render_template(
                    'result.html',
                    title="Pages Extracted Successfully!",
                    message=message,
                    filename=output_filename,
                    return_url=url_for('extract_pages_route')
                )
            else:
                log_operation("Extract Pages", file.filename, "-", "Failed", message)
                flash(message, "error")
                return redirect(url_for('extract_pages_route'))

        except Exception as e:
            flash(f"Page extraction failed: {str(e)}", "error")
            return redirect(url_for('extract_pages_route'))
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('extract.html')

@app.route('/text', methods=['GET', 'POST'])
def extract_text_route():
    text_result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded.", "error")
            return redirect(url_for('extract_text_route'))

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid PDF document.", "error")
            return redirect(url_for('extract_text_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_text")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        try:
            res = extract_digital_text(input_path)
            if res.get("success"):
                txt_filename = f"{Path(file.filename).stem}_text.txt"
                txt_path = os.path.join(app.config['OUTPUT_FOLDER'], txt_filename)
                with open(txt_path, "w", encoding="utf-8") as f_out:
                    f_out.write(res["text"])

                res["download_txt"] = txt_filename

                log_operation(
                    operation_type="Extract Text",
                    input_filename=file.filename,
                    output_filename=txt_filename,
                    status="Success",
                    details=f"Extracted {res['word_count']} words from {res['pages_processed']} pages"
                )
                text_result = res
            else:
                log_operation("Extract Text", file.filename, "-", "Failed", res.get("error"))
                flash(res.get("error", "Failed to extract text."), "error")

        except Exception as e:
            flash(f"Error during text extraction: {str(e)}", "error")
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('text.html', text_result=text_result)

@app.route('/ocr', methods=['GET', 'POST'])
def ocr_pdf_route():
    ocr_result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded.", "error")
            return redirect(url_for('ocr_pdf_route'))

        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            flash("Please select a valid PDF file.", "error")
            return redirect(url_for('ocr_pdf_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_ocr")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        try:
            res = extract_ocr_text(input_path)
            if res.get("success"):
                txt_filename = f"{Path(file.filename).stem}_ocr.txt"
                txt_path = os.path.join(app.config['OUTPUT_FOLDER'], txt_filename)
                with open(txt_path, "w", encoding="utf-8") as f_out:
                    f_out.write(res["text"])

                res["download_txt"] = txt_filename
                log_operation(
                    operation_type="OCR PDF",
                    input_filename=file.filename,
                    output_filename=txt_filename,
                    status="Success",
                    details=f"OCR recognized {res['word_count']} words"
                )
                ocr_result = res
            else:
                log_operation("OCR PDF", file.filename, "-", "Failed" if not res.get("tesseract_missing") else "Missing Tesseract Engine", res.get("error"))
                ocr_result = res

        except Exception as e:
            flash(f"OCR Exception: {str(e)}", "error")
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('ocr.html', ocr_result=ocr_result)

@app.route('/tables', methods=['GET', 'POST'])
def extract_tables_route():
    table_result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded.", "error")
            return redirect(url_for('extract_tables_route'))

        file = request.files['file']
        page_num = request.form.get('page_number', '1')
        try:
            page_num = int(page_num)
        except ValueError:
            page_num = 1

        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid PDF.", "error")
            return redirect(url_for('extract_tables_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_table")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        try:
            res = extract_tables_from_pdf(
                file_path=input_path,
                page_number=page_num,
                output_dir=app.config['OUTPUT_FOLDER']
            )

            if res.get("success"):
                out_name = res.get("excel_filename") or res.get("csv_filename") or "table_export"
                log_operation(
                    operation_type="Extract Tables",
                    input_filename=file.filename,
                    output_filename=out_name if res.get("has_tables") else "-",
                    status="Success" if res.get("has_tables") else "No Tables Found",
                    details=f"Extracted page {page_num} table ({res.get('rows_count', 0)} rows)" if res.get("has_tables") else "No table found on page"
                )
                table_result = res
            else:
                flash(res.get("error", "Error extracting table."), "error")

        except Exception as e:
            flash(f"Table processing error: {str(e)}", "error")
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('tables.html', table_result=table_result)

@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file selected.", "error")
            return redirect(url_for('compress_pdf_route'))

        file = request.files['file']
        level = request.form.get('level', 'medium')

        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid PDF.", "error")
            return redirect(url_for('compress_pdf_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_comp")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        output_filename = generate_unique_filename(file.filename, prefix=f"compressed_{level}")
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        try:
            res = compress_pdf(input_path, output_path, level=level)

            if res.get("success"):
                log_operation(
                    operation_type="Compress PDF",
                    input_filename=file.filename,
                    output_filename=output_filename,
                    status="Success",
                    details=f"Reduced size from {res['original_size']} to {res['compressed_size']} ({res['percentage_reduction']}% saved)"
                )
                flash("PDF compressed successfully!", "success")
                return render_template(
                    'result.html',
                    title="PDF Compressed Successfully!",
                    message=f"File size reduced from {res['original_size']} down to {res['compressed_size']} (Saved {res['bytes_saved']} - {res['percentage_reduction']}% reduction).",
                    filename=output_filename,
                    result=res,
                    return_url=url_for('compress_pdf_route')
                )
            else:
                flash(res.get("error", "Compression failed."), "error")
                return redirect(url_for('compress_pdf_route'))

        except Exception as e:
            flash(f"Compression error: {str(e)}", "error")
            return redirect(url_for('compress_pdf_route'))
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('compress.html')

@app.route('/rotate', methods=['GET', 'POST'])
def rotate_pdf_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No PDF file provided.", "error")
            return redirect(url_for('rotate_pdf_route'))

        file = request.files['file']
        angle = request.form.get('angle', '90')
        scope = request.form.get('scope', 'all')
        page_selection = request.form.get('page_selection', '').strip()

        try:
            angle = int(angle)
        except ValueError:
            angle = 90

        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid PDF.", "error")
            return redirect(url_for('rotate_pdf_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_rot")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        output_filename = generate_unique_filename(file.filename, prefix=f"rotated_{angle}")
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        try:
            success, message = rotate_pdf(
                input_file_path=input_path,
                output_file_path=output_path,
                angle=angle,
                scope=scope,
                page_selection_str=page_selection
            )

            if success:
                log_operation(
                    operation_type="Rotate PDF",
                    input_filename=file.filename,
                    output_filename=output_filename,
                    status="Success",
                    details=message
                )
                flash("PDF pages rotated successfully!", "success")
                return render_template(
                    'result.html',
                    title="PDF Rotated Successfully!",
                    message=message,
                    filename=output_filename,
                    return_url=url_for('rotate_pdf_route')
                )
            else:
                flash(message, "error")
                return redirect(url_for('rotate_pdf_route'))

        except Exception as e:
            flash(f"Rotation error: {str(e)}", "error")
            return redirect(url_for('rotate_pdf_route'))
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('rotate.html')

@app.route('/delete-pages', methods=['GET', 'POST'])
def delete_pages_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded.", "error")
            return redirect(url_for('delete_pages_route'))

        file = request.files['file']
        page_selection = request.form.get('page_selection', '').strip()

        if file.filename == '' or not allowed_file(file.filename):
            flash("Please upload a valid PDF.", "error")
            return redirect(url_for('delete_pages_route'))

        if not page_selection:
            flash("Please specify page numbers to delete.", "error")
            return redirect(url_for('delete_pages_route'))

        input_filename = generate_unique_filename(file.filename, prefix="in_del")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        output_filename = generate_unique_filename(file.filename, prefix="deleted_pages")
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        try:
            success, message = delete_pdf_pages(input_path, output_path, page_selection)

            if success:
                log_operation(
                    operation_type="Delete Pages",
                    input_filename=file.filename,
                    output_filename=output_filename,
                    status="Success",
                    details=message
                )
                flash("Pages deleted successfully!", "success")
                return render_template(
                    'result.html',
                    title="Pages Deleted Successfully!",
                    message=message,
                    filename=output_filename,
                    return_url=url_for('delete_pages_route')
                )
            else:
                flash(message, "error")
                return redirect(url_for('delete_pages_route'))

        except Exception as e:
            flash(f"Error deleting pages: {str(e)}", "error")
            return redirect(url_for('delete_pages_route'))
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass

    return render_template('delete_pages.html')

@app.route('/history')
def history_route():
    history_records = get_history(limit=100)
    return render_template('history.html', history=history_records)

@app.route('/clear-history', methods=['POST'])
def clear_history_route():
    if clear_history():
        flash("Operation history records cleared.", "info")
    else:
        flash("Failed to clear operation history.", "error")
    return redirect(url_for('history_route'))

@app.route('/about')
def about_route():
    return render_template('about.html')

@app.route('/download/<filename>')
def download_file(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(app.config['OUTPUT_FOLDER'], safe_name, as_attachment=True)

# Main Application Entrypoint
if __name__ == '__main__':
    print("Starting PDF Toolkit Flask Web Server...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='127.0.0.1', port=5000, debug=True)
