# PDF Toolkit – PDF Merger, Splitter & Text Extractor

> **A complete, production-quality Python Flask Web Application for local PDF operations.**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📌 Project Description

**PDF Toolkit** is a full-stack web application designed for students, researchers, and professionals. It provides a suite of local PDF processing utilities directly inside a web browser without sending confidential documents to third-party cloud services or paid APIs.

This project is built specifically to demonstrate core **Python Software Engineering, Web Development (Flask), Data Processing, OCR, and SQLite Database Integration** for college projects and technical viva examinations.

---

## ✨ Features & Utilities

1. 🔀 **Merge PDF**: Combine multiple PDF documents into a single PDF with custom reordering.
2. ✂️ **Split PDF**: Split a multi-page PDF into single-page documents or custom ranges (packaged in `.zip`).
3. 📑 **Extract Pages**: Extract specific pages or page ranges (e.g. `1,3,5` or `2-7`) into a new PDF.
4. 📄 **Extract Text**: Extract selectable digital PDF text with character & word counts. Download as `.txt`.
5. 👁️ **OCR PDF**: Optical Character Recognition for scanned PDFs using Tesseract OCR engine + PIL.
6. 📊 **Extract Tables**: Detect tabular data using `pdfplumber` and export to `.csv` and Excel `.xlsx`.
7. 🗜️ **Compress PDF**: Multi-level compression (Low, Medium, High) with exact bytes saved & percentage reduction metrics.
8. 🔄 **Rotate PDF**: Rotate all or selected pages clockwise by 90°, 180°, or 270°.
9. 🗑️ **Delete Pages**: Remove unwanted pages safely (validates that at least 1 page remains).
10. 📊 **Operation History**: Automatic SQLite database tracking of processed files, timestamps, and execution status.
11. 🛡️ **Built-in Security**: Input file extension validation (`.pdf`), secure filename handling, file size limit enforcement, and automatic temporary file cleanup.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.9+, Flask 3.0
* **PDF Processing**: `pypdf`, `pdfplumber`, `PyMuPDF` (`fitz`)
* **OCR & Imaging**: `pytesseract`, `Pillow` (PIL)
* **Data & Export**: `pandas`, `openpyxl`
* **Database**: SQLite 3
* **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS, Fetch API), Jinja2
* **Styling**: Bootstrap 5.3 (CDN), Font Awesome 6 (CDN), Google Fonts (Inter)

---

## 📁 Project Directory Structure

```text
pdf_toolkit/
│
├── app.py                  # Main Flask application & routes
├── config.py               # Paths, security limits & directory auto-creation
├── database.py             # SQLite helper methods & schema initialization
├── requirements.txt        # Python dependency manifest
├── README.md               # Project documentation
├── .gitignore              # Git ignore patterns
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom modern CSS design system
│   └── js/
│       └── script.js       # Drag-and-drop, dynamic metadata preview, clipboard
│
├── templates/
│   ├── base.html           # Main layout template (navbar, flash alerts, footer)
│   ├── index.html          # Main dashboard & stat counters
│   ├── merge.html          # Multi-file merge view
│   ├── split.html          # Split PDF view
│   ├── extract.html        # Extract pages view
│   ├── text.html           # Text extraction view
│   ├── ocr.html            # Scanned OCR view
│   ├── tables.html         # Table extraction view
│   ├── compress.html       # Compression view
│   ├── rotate.html         # Page rotation view
│   ├── delete_pages.html   # Delete pages view
│   ├── history.html        # Database history view
│   ├── result.html         # Universal success result view
│   └── about.html          # Project architecture & Viva guide
│
├── uploads/                # Temporary file uploads (auto-created)
├── outputs/                # Processed output files (auto-created)
└── data/                   # SQLite database directory (auto-created)
    └── toolkit.db
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- **Python 3.9+** installed on your system.

### 2. Clone / Copy Workspace
Open terminal or PowerShell in the project directory:
```bash
cd "pdf toolkit"
```

### 3. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Required Packages
```bash
pip install -r requirements.txt
```

---

## 🔍 Installing Tesseract OCR (Optional for Scanned PDFs)

The application handles missing Tesseract gracefully with helpful warning alerts. To enable OCR for scanned PDFs:

### Windows:
1. Download installer from: [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer and install to default location: `C:\Program Files\Tesseract-OCR\`
3. Or via PowerShell / Command Prompt:
   ```cmd
   winget install UB-Mannheim.TesseractOCR
   ```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

## ▶️ Running the Application

Start the Flask development server:
```bash
python app.py
```

Output in terminal:
```text
Starting PDF Toolkit Flask Web Server...
Open http://127.0.0.1:5000 in your browser.
 * Running on http://127.0.0.1:5000
```

Open **`http://127.0.0.1:5000`** in your browser to access the PDF Toolkit dashboard!

---

## 🎓 College Project Viva Explanation Points

When presenting this project to external examiners or professors:

1. **Architecture**: Explain the modular separation between `app.py` (Controller/Routes), `database.py` (Model/Data), `utils/` (Business Logic), and `templates/` (View/UI).
2. **Library Comparison**:
   - `pypdf`: Used for page stream manipulation, page rotation, page deletion, and merging.
   - `pdfplumber`: Used for text layout analysis and structured table border detection.
   - `PyMuPDF` (`fitz`): Used for high-speed page rendering into images for OCR and PDF file compression.
3. **Database Logging**: Mention that every operation logs input/output filenames, execution status ("Success"/"Failed"), and timestamps into SQLite database `operations` table.
4. **Security Controls**: Mention `secure_filename()` preventing path injection attacks and strict file extension verification (`.pdf`).

---

## 📄 License
This project is open-source and free to use for academic and educational purposes.
