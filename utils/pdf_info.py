import os
import fitz  # PyMuPDF
import pypdf

def get_pdf_info(file_path):
    """Extract metadata and info from a PDF file."""
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    file_size_bytes = os.path.getsize(file_path)
    formatted_size = format_size(file_size_bytes)
    
    info = {
        "filename": os.path.basename(file_path),
        "file_size": formatted_size,
        "file_size_bytes": file_size_bytes,
        "page_count": 0,
        "title": "Unknown",
        "author": "Unknown",
        "producer": "Unknown",
        "creation_date": "Unknown",
        "mod_date": "Unknown",
        "pdf_version": "Unknown",
        "is_encrypted": False,
        "has_text": False
    }

    try:
        # Try PyMuPDF fitz first for detailed info
        doc = fitz.open(file_path)
        info["page_count"] = len(doc)
        info["is_encrypted"] = doc.is_encrypted

        metadata = doc.metadata or {}
        if metadata.get("title"):
            info["title"] = metadata["title"]
        if metadata.get("author"):
            info["author"] = metadata["author"]
        if metadata.get("producer"):
            info["producer"] = metadata["producer"]
        if metadata.get("creationDate"):
            info["creation_date"] = metadata["creationDate"]
        if metadata.get("modDate"):
            info["mod_date"] = metadata["modDate"]
        if metadata.get("format"):
            info["pdf_version"] = metadata["format"]

        # Quick check if document has text content across pages
        text_count = 0
        for i in range(min(5, len(doc))):
            text_count += len(doc[i].get_text().strip())
        info["has_text"] = text_count > 20
        doc.close()

    except Exception:
        # Fallback to pypdf
        try:
            reader = pypdf.PdfReader(file_path)
            info["page_count"] = len(reader.pages)
            if reader.metadata:
                info["title"] = reader.metadata.title or "Unknown"
                info["author"] = reader.metadata.author or "Unknown"
                info["producer"] = reader.metadata.producer or "Unknown"
        except Exception as e:
            info["error"] = f"Could not parse PDF info: {str(e)}"

    return info

def format_size(size_bytes):
    """Format bytes into readable string KB/MB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
