"""JSON to Markdown converter."""

import json
from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class JsonConverter(BaseConverter):
    supported_extensions = (".json",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        text = path.read_text(encoding="utf-8", errors="replace")

        # Validate and pretty-print
        try:
            data = json.loads(text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            formatted = text

        md = f"# {path.name}\n\n```json\n{formatted}\n```\n"
        content = clean_markdown(md)
        return ConversionResult(content=content, title=path.name, source=str(path))
