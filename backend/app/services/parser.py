from pathlib import Path
from typing import BinaryIO

import pdfplumber
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _extract_txt(file: BinaryIO) -> str:
    return file.read().decode("utf-8")


def _extract_pdf(file: BinaryIO) -> str:
    text_parts: list[str] = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def _extract_docx(file: BinaryIO) -> str:
    document = Document(file)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(paragraphs)


def extract_text(file) -> str:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    try:
        if extension == ".txt":
            return _extract_txt(file.file)
        if extension == ".pdf":
            return _extract_pdf(file.file)
        if extension == ".docx":
            return _extract_docx(file.file)
    except UnicodeDecodeError as exc:
        raise ValueError("TXT file must be UTF-8 encoded") from exc
    except Exception as exc:
        raise ValueError(f"Could not parse file: {exc}") from exc

    raise ValueError("Unsupported file type")
