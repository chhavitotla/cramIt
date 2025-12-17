# modules/pdf_parser.py

from typing import List, Dict
import fitz  # PyMuPDF


class PDFParser:
    """
    Robust PDF parser that extracts page-level text
    with rich metadata for high-quality RAG pipelines.
    """

    def __init__(self):
        pass

    def parse(self, pdf_bytes: bytes, source_name: str) -> List[Dict]:
        """
        Parses a PDF file into page-level text blocks.

        Returns:
        [
            {
                "page_id": int,
                "text": str,
                "metadata": {
                    "source": str,
                    "page_number": int
                }
            }
        ]
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []

        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            text = page.get_text("text").strip()

            if not text:
                continue  # skip empty pages safely

            pages.append({
                "page_id": page_index,
                "text": text,
                "metadata": {
                    "source": source_name,
                    "page": page_index + 1
                }
            })

        doc.close()
        return pages
