import os
from typing import List, Dict, Any
from pypdf import PdfReader
from docx import Document as DocxDocument

class DocumentLoader:
    """Handles extraction of text from various file formats."""

    @staticmethod
    def load_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Extracts text from PDF page by page."""
        documents = []
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    "content": text,
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "page": i + 1,
                        "type": "pdf"
                    }
                })
        return documents

    @staticmethod
    def load_docx(file_path: str) -> List[Dict[str, Any]]:
        """Extracts text from DOCX files."""
        doc = DocxDocument(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        return [{
            "content": "\n".join(full_text),
            "metadata": {
                "source": os.path.basename(file_path),
                "type": "docx"
            }
        }]

    @staticmethod
    def load_txt(file_path: str) -> List[Dict[str, Any]]:
        """Extracts text from plain text or markdown files."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return [{
            "content": content,
            "metadata": {
                "source": os.path.basename(file_path),
                "type": "text"
            }
        }]

    def load_any(self, file_path: str) -> List[Dict[str, Any]]:
        """Entry point to load a file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.load_pdf(file_path)
        elif ext == ".docx":
            return self.load_docx(file_path)
        elif ext in [".txt", ".md"]:
            return self.load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

# Example Usage (for testing)
if __name__ == "__main__":
    loader = DocumentLoader()
    # print(loader.load_any("path/to/your/test.pdf"))
