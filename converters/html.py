"""HTML to Markdown converter for local files."""

from pathlib import Path

from markdownify import markdownify

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class HtmlConverter(BaseConverter):
    supported_extensions = (".html", ".htm")

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        html = path.read_text(encoding="utf-8", errors="replace")

        md = markdownify(
            html,
            heading_style="ATX",
            strip=["script", "style", "nav", "footer", "header"],
        )

        content = clean_markdown(md)
        return ConversionResult(content=content, title=path.name, source=str(path))
