from PyPDF2 import PdfReader

def read_file(processor: str, file_path: str) -> str:
    if processor.lower() == "pypdf2":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    else:
        raise ValueError(f"Unknown processor: {processor}")
