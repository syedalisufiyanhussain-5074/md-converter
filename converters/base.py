from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ConversionResult:
    """Result of a file/URL conversion."""
    content: str
    title: Optional[str] = None
    source: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


class BaseConverter(ABC):
    """Base class for all format converters."""

    supported_extensions: tuple[str, ...] = ()

    @abstractmethod
    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        """Convert the source file or URL to markdown."""
        ...

    def accepts(self, source: str | Path) -> bool:
        """Check if this converter can handle the given source."""
        path = Path(source)
        return path.suffix.lower() in self.supported_extensions
