"""EPUB to Markdown converter using ebooklib."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class EpubConverter(BaseConverter):
    supported_extensions = (".epub",)

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)

        import ebooklib
        from ebooklib import epub
        from markdownify import markdownify

        book = epub.read_epub(str(path))
        title = book.get_metadata("DC", "title")
        book_title = title[0][0] if title else path.name

        md_parts = [f"# {book_title}\n"]

        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            html = item.get_body_content().decode("utf-8", errors="replace")
            md = markdownify(
                html,
                heading_style="ATX",
                strip=["script", "style"],
            )
            if md.strip():
                md_parts.append(md.strip())

        content = clean_markdown("\n\n---\n\n".join(md_parts))
        return ConversionResult(content=content, title=book_title, source=str(path))
