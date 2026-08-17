from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document


def extract_text(file_path: Path) -> str:
    """
    Extract text from a supported document.
    """

    extension = file_path.suffix.lower()

    if extension == ".txt":
        return extract_txt(file_path)

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    raise ValueError(f"Unsupported file type: {extension}")


def extract_txt(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


def extract_docx(file_path: Path) -> str:
    document = Document(file_path)

    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )
