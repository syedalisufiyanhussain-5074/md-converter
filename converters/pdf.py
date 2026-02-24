"""PDF to Markdown converter using pymupdf4llm with OCR fallback."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class PdfConverter(BaseConverter):
    supported_extensions = (".pdf",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        password = kwargs.get("password")

        import pymupdf4llm

        md_text = pymupdf4llm.to_markdown(str(path), show_progress=False)

        # If pymupdf4llm returned very little text, it might be a scanned PDF
        if len(md_text.strip()) < 50:
            ocr_text = self._try_ocr(path)
            if ocr_text and len(ocr_text.strip()) > len(md_text.strip()):
                md_text = f"# {path.name}\n\n{ocr_text}"

        content = clean_markdown(md_text)
        return ConversionResult(content=content, title=path.name, source=str(path))

    def _try_ocr(self, path: Path) -> str | None:
        """Attempt OCR on a scanned PDF by converting pages to images."""
        try:
            import fitz  # pymupdf
            import pytesseract
            from PIL import Image
            import io

            doc = fitz.open(str(path))
            pages_text = []

            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img)
                if text.strip():
                    pages_text.append(f"## Page {i + 1}\n\n{text.strip()}")

            doc.close()
            return "\n\n".join(pages_text) if pages_text else None
        except ImportError:
            return None
