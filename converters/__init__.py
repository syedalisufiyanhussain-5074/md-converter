"""Converter registry with lazy imports."""

from pathlib import Path
from typing import Optional

from .base import BaseConverter

# Registry: extension -> (module_path, class_name)
_CONVERTER_MAP: dict[str, tuple[str, str]] = {
    # Simple formats
    ".csv": ("converters.csv_conv", "CsvConverter"),
    ".json": ("converters.json_conv", "JsonConverter"),
    ".xml": ("converters.xml_conv", "XmlConverter"),
    ".html": ("converters.html", "HtmlConverter"),
    ".htm": ("converters.html", "HtmlConverter"),
    # Documents
    ".pdf": ("converters.pdf", "PdfConverter"),
    ".docx": ("converters.docx", "DocxConverter"),
    ".pptx": ("converters.pptx", "PptxConverter"),
    ".xlsx": ("converters.xlsx", "XlsxConverter"),
    ".xls": ("converters.xlsx", "XlsxConverter"),
    # Images
    ".png": ("converters.image", "ImageConverter"),
    ".jpg": ("converters.image", "ImageConverter"),
    ".jpeg": ("converters.image", "ImageConverter"),
    ".bmp": ("converters.image", "ImageConverter"),
    ".tiff": ("converters.image", "ImageConverter"),
    ".tif": ("converters.image", "ImageConverter"),
    ".webp": ("converters.image", "ImageConverter"),
    ".gif": ("converters.image", "ImageConverter"),
    # EPUB
    ".epub": ("converters.epub", "EpubConverter"),
    # Audio
    ".mp3": ("converters.audio", "AudioConverter"),
    ".wav": ("converters.audio", "AudioConverter"),
    ".m4a": ("converters.audio", "AudioConverter"),
    ".ogg": ("converters.audio", "AudioConverter"),
    ".flac": ("converters.audio", "AudioConverter"),
    ".wma": ("converters.audio", "AudioConverter"),
    ".aac": ("converters.audio", "AudioConverter"),
}

_WEB_CONVERTER = ("converters.web", "WebConverter")


def _load_converter(module_path: str, class_name: str) -> Optional[BaseConverter]:
    """Lazily import and instantiate a converter. Returns None if deps missing."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls()
    except (ImportError, AttributeError):
        return None


def get_converter(
    *,
    extension: Optional[str] = None,
    filepath: Optional[str] = None,
    url: bool = False,
) -> Optional[BaseConverter]:
    """Get the appropriate converter for a file extension or URL.

    Args:
        extension: File extension (e.g. ".pdf")
        filepath: File path (used for MIME-type fallback)
        url: If True, return the web scraper converter

    Returns:
        A converter instance, or None if no converter available.
    """
    if url:
        return _load_converter(*_WEB_CONVERTER)

    if extension:
        ext = extension.lower()
        entry = _CONVERTER_MAP.get(ext)
        if entry:
            return _load_converter(*entry)

    # Fallback: try MIME-type detection
    if filepath:
        from utils.mime_detect import detect_extension
        detected_ext = detect_extension(filepath)
        if detected_ext:
            entry = _CONVERTER_MAP.get(detected_ext)
            if entry:
                return _load_converter(*entry)

    return None


def get_supported_formats() -> dict[str, bool]:
    """Return a dict of extension -> is_available for all known formats."""
    result = {}
    checked = set()

    for ext, (module_path, class_name) in _CONVERTER_MAP.items():
        key = (module_path, class_name)
        if key not in checked:
            checked.add(key)
            converter = _load_converter(module_path, class_name)
            available = converter is not None
            # Mark all extensions for this converter
            for e, (m, c) in _CONVERTER_MAP.items():
                if (m, c) == key:
                    result[e] = available
        elif ext not in result:
            # Already checked this module, just copy the result
            for e, v in result.items():
                if _CONVERTER_MAP.get(e) == (module_path, class_name):
                    result[ext] = v
                    break

    return result
