"""CSV to Markdown converter."""

import csv
import io
from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class CsvConverter(BaseConverter):
    supported_extensions = (".csv",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        text = path.read_text(encoding="utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            return ConversionResult(
                content=f"# {path.name}\n\n*This file is empty.*\n",
                title=path.name,
                source=str(path),
            )

        md_lines = [f"# {path.name}\n"]

        # Header row
        header = rows[0]
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join("---" for _ in header) + " |")

        # Data rows
        for row in rows[1:]:
            # Pad row to match header length
            padded = row + [""] * (len(header) - len(row))
            md_lines.append("| " + " | ".join(padded[:len(header)]) + " |")

        content = clean_markdown("\n".join(md_lines))
        return ConversionResult(content=content, title=path.name, source=str(path))
