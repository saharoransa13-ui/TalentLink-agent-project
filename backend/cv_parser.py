from pathlib import Path
import io
import re
import pdfplumber
from docx import Document

MAX_FILE_BYTES = 10 * 1024 * 1024

# The skill analysis only understands English CVs.
ARABIC_LETTERS = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")
MAX_ARABIC_SHARE = 0.30  # an English CV may still contain an Arabic name or address


class CVUploadError(ValueError):
    """A problem with the uploaded CV. `code` lets the website show the message in its own language."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class NotEnglishCVError(CVUploadError):
    """Raised when the CV text is mostly not English."""

    def __init__(self, message: str):
        super().__init__("cv_not_english", message)


def ensure_english(text: str) -> None:
    arabic = len(ARABIC_LETTERS.findall(text))
    latin = len(LATIN_LETTERS.findall(text))
    if latin == 0 or arabic / (arabic + latin) > MAX_ARABIC_SHARE:
        raise NotEnglishCVError("The CV must be written in English. Please upload an English version of your CV.")

def extract_text(filename: str, content: bytes) -> str:
    if len(content) > MAX_FILE_BYTES:
        raise CVUploadError("file_too_large", "File is too large. Maximum supported size is 10 MB.")
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            raise CVUploadError("pdf_unreadable", "This PDF could not be read. It may be damaged or not a real PDF file.")
    elif suffix == ".docx":
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            for table in doc.tables:
                text += "\n" + "\n".join(" ".join(cell.text for cell in row.cells) for row in table.rows)
        except Exception:
            raise CVUploadError("docx_unreadable", "This Word file could not be read. It may be damaged or not a real .docx file.")
    elif suffix in {".txt", ".md"}:
        text = content.decode("utf-8", errors="replace")
    else:
        raise CVUploadError("bad_file_type", "Unsupported file type. Upload PDF, DOCX, or TXT.")
    text = text.strip()
    if not text:
        raise CVUploadError("no_text", "No text could be extracted. If this is a scanned PDF, OCR is not included in this MVP.")
    ensure_english(text)
    return text
