from pathlib import Path
from pypdf import PdfReader
import docx

def read_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def read_docx(path: str) -> str:
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)

def load_srs(path: str) -> str:
    p = path.lower()
    if p.endswith(".txt"):
        return read_txt(path)
    if p.endswith(".pdf"):
        return read_pdf(path)
    if p.endswith(".docx"):
        return read_docx(path)
    raise ValueError("Unsupported format. Use .txt, .pdf, or .docx")