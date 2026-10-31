
import json
from pathlib import Path

import fitz
import pytesseract

from PIL import Image


# Project paths
BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "storage" / "extracted"

# Windows Tesseract executable
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# OCR configuration
OCR_DPI = 300
MIN_NATIVE_TEXT_LENGTH = 50


def extract_text_with_ocr(page):
    """
    Render a PDF page as an image and extract text using Tesseract.
    """

    pix = page.get_pixmap(
        dpi=OCR_DPI,
        colorspace=fitz.csRGB,
        alpha=False
    )

    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return text.strip()


def extract_session_pdfs(session_id: str):

    session_dir = UPLOAD_DIR / session_id

    if not session_dir.exists():
        raise FileNotFoundError("Upload session not found")

    pdf_files = list(session_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("No PDF files found in this session")

    # Load original document metadata
    metadata_path = session_dir / "metadata.json"
    document_metadata = {}

    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as file:
            document_metadata = json.load(file)

    output_session_dir = OUTPUT_DIR / session_id
    output_session_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for pdf_path in pdf_files:

        file_metadata = document_metadata.get(pdf_path.name, {})

        original_filename = file_metadata.get(
            "original_filename",
            pdf_path.name
        )

        document_id = file_metadata.get("document_id")

        output_path = output_session_dir / f"{pdf_path.stem}.jsonl"

        total_chars = 0
        empty_pages = 0
        ocr_pages = 0
        native_pages = 0

        with fitz.open(pdf_path) as pdf:

            total_pages = len(pdf)

            with open(output_path, "w", encoding="utf-8") as output_file:

                for page_index, page in enumerate(pdf):

                    # First attempt: native PDF text extraction
                    text = page.get_text("text").strip()

                    extraction_method = "native"

                    # Fallback: OCR for pages with insufficient native text
                    if len(text) < MIN_NATIVE_TEXT_LENGTH:

                        ocr_text = extract_text_with_ocr(page)

                        if ocr_text:
                            text = ocr_text
                            extraction_method = "ocr"

                    if extraction_method == "ocr":
                        ocr_pages += 1
                    else:
                        native_pages += 1

                    if not text:
                        empty_pages += 1

                    total_chars += len(text)

                    record = {
                        "filename": original_filename,
                        "stored_filename": pdf_path.name,
                        "document_id": document_id,
                        "page_number": page_index + 1,
                        "extraction_method": extraction_method,
                        "text": text,
                    }

                    output_file.write(
                        json.dumps(record, ensure_ascii=False) + "\n"
                    )

        results.append({
            "filename": original_filename,
            "stored_filename": pdf_path.name,
            "document_id": document_id,
            "total_pages": total_pages,
            "total_characters": total_chars,
            "native_pages": native_pages,
            "ocr_pages": ocr_pages,
            "empty_pages": empty_pages,
            "output_file": str(output_path),
        })

    return results
