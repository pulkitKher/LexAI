import fitz  # PyMuPDF
import pdfplumber
import easyocr
import os
from PIL import Image
import tempfile

# Initialize EasyOCR reader once (heavy, so we do it at module level)
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Try pdfplumber first (best for digital PDFs)
    Fall back to PyMuPDF
    Fall back to EasyOCR if scanned/image-based
    """
    text = ""

    # Method 1: pdfplumber (best for text-based PDFs)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    # If we got decent text, return it
    if len(text.strip()) > 100:
        return clean_text(text)

    # Method 2: PyMuPDF fallback
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
    except Exception as e:
        print(f"PyMuPDF failed: {e}")

    if len(text.strip()) > 100:
        return clean_text(text)

    # Method 3: EasyOCR for scanned documents
    print("Falling back to OCR...")
    text = extract_text_via_ocr(file_path)

    return clean_text(text)


def extract_text_from_image(file_path: str) -> str:
    """Extract text from image files using EasyOCR"""
    try:
        results = reader.readtext(file_path, detail=0)
        return clean_text(" ".join(results))
    except Exception as e:
        raise ValueError(f"OCR failed on image: {e}")


def extract_text_via_ocr(pdf_path: str) -> str:
    """Convert PDF pages to images then OCR each page"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to image at 2x resolution for better OCR
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
                pix.save(tmp_path)

            # OCR the image
            results = reader.readtext(tmp_path, detail=0)
            text += " ".join(results) + "\n"

            # Cleanup
            os.unlink(tmp_path)

        doc.close()
    except Exception as e:
        raise ValueError(f"OCR extraction failed: {e}")

    return text


def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # Remove empty lines
    cleaned = "\n".join(lines)

    # Remove excessive spaces
    import re
    cleaned = re.sub(r' +', ' ', cleaned)

    return cleaned.strip()


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def extract_text(file_path: str, filename: str) -> str:
    """Main entry point — auto-detects file type"""
    ext = get_file_extension(filename)

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"]:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Upload PDF or image.")