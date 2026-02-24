"""DOCX to Markdown converter using mammoth."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class DocxConverter(BaseConverter):
    supported_extensions = (".docx",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)

        import mammoth
        from markdownify import markdownify

        with open(path, "rb") as f:
            result = mammoth.convert_to_html(f)

        html = result.value
        md = markdownify(html, heading_style="ATX")
        content = clean_markdown(md)
        return ConversionResult(content=content, title=path.name, source=str(path))
