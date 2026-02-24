"""XML to Markdown converter."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class XmlConverter(BaseConverter):
    supported_extensions = (".xml",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        text = path.read_text(encoding="utf-8", errors="replace")

        # Pretty-print if possible
        try:
            from defusedxml.minidom import parseString
            dom = parseString(text)
            formatted = dom.toprettyxml(indent="  ")
            # Remove the XML declaration line that toprettyxml adds
            lines = formatted.split("\n")
            if lines and lines[0].startswith("<?xml"):
                formatted = "\n".join(lines[1:])
        except Exception:
            formatted = text

        md = f"# {path.name}\n\n```xml\n{formatted.strip()}\n```\n"
        content = clean_markdown(md)
        return ConversionResult(content=content, title=path.name, source=str(path))
