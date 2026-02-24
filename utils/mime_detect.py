"""File type detection using the filetype library."""

from pathlib import Path
from typing import Optional

# MIME type -> extension mapping
_MIME_TO_EXT: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/epub+zip": ".epub",
    "text/csv": ".csv",
    "text/html": ".html",
    "text/xml": ".xml",
    "application/xml": ".xml",
    "application/json": ".json",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "audio/x-m4a": ".m4a",
    "audio/mp4": ".m4a",
}


def detect_extension(filepath: str | Path) -> Optional[str]:
    """Detect file type and return the corresponding extension.

    Returns None if the file type cannot be determined.
    """
    try:
        import filetype
        kind = filetype.guess(str(filepath))
        if kind:
            return _MIME_TO_EXT.get(kind.mime)
    except ImportError:
        pass

    return None
