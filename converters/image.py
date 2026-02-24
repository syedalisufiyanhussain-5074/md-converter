"""Image to Markdown converter using pytesseract OCR."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class ImageConverter(BaseConverter):
    supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".gif")

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        lang = kwargs.get("lang", "eng")

        import pytesseract
        from PIL import Image

        img = Image.open(path)

        # Convert to RGB if needed (handles RGBA, palette, etc.)
        if img.mode not in ("L", "RGB"):
            img = img.convert("RGB")

        text = pytesseract.image_to_string(img, lang=lang)

        if not text.strip():
            md = f"# {path.name}\n\n*No text detected in image.*\n"
        else:
            md = f"# {path.name}\n\n{text.strip()}\n"

        content = clean_markdown(md)
        return ConversionResult(content=content, title=path.name, source=str(path))
