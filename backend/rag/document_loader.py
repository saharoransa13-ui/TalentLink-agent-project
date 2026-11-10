from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@dataclass(frozen=True)
class LoadedDocument:
    text: str
    source: str
    file_type: str


def load_document(path: str | Path) -> LoadedDocument:
    """Extract text from a supported local document."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if suffix == ".pdf":
        import pdfplumber

        with pdfplumber.open(str(file_path)) as pdf:
            text = "\n\n".join((page.extract_text() or "") for page in pdf.pages)
    elif suffix == ".docx":
        from docx import Document

        doc = Document(str(file_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        table_rows = [
            " | ".join(cell.text.strip() for cell in row.cells)
            for table in doc.tables
            for row in table.rows
            if any(cell.text.strip() for cell in row.cells)
        ]
        text = "\n".join(paragraphs + table_rows)
    else:
        text = file_path.read_text(encoding="utf-8", errors="replace")

    text = text.strip()
    if not text:
        raise ValueError(f"No extractable text found in '{file_path.name}'.")

    return LoadedDocument(
        text=text,
        source=file_path.name,
        file_type=suffix.lstrip("."),
    )


def discover_documents(directory: str | Path) -> Iterable[Path]:
    """Yield supported files recursively, in a stable order."""
    base = Path(directory)
    if not base.exists():
        raise FileNotFoundError(f"Knowledge-base directory does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"Expected a directory: {base}")
    yield from sorted(
        (p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS),
        key=lambda p: str(p).lower(),
    )
