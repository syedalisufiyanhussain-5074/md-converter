"""Audio to Markdown converter using faster-whisper."""

from pathlib import Path

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class AudioConverter(BaseConverter):
    supported_extensions = (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac")

    def convert(self, source: str | Path, **kwargs) -> ConversionResult:
        path = Path(source)
        model_size = kwargs.get("whisper_model", "base")
        timestamps = kwargs.get("timestamps", False)

        from faster_whisper import WhisperModel

        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(path))

        lines = [f"# Transcription: {path.name}\n"]
        lines.append(f"*Language: {info.language} (probability: {info.language_probability:.1%})*\n")

        for segment in segments:
            if timestamps:
                start = self._format_time(segment.start)
                end = self._format_time(segment.end)
                lines.append(f"**[{start} - {end}]**")
            lines.append(segment.text.strip())
            lines.append("")

        content = clean_markdown("\n".join(lines))
        return ConversionResult(
            content=content,
            title=path.name,
            source=str(path),
            metadata={"language": info.language, "duration": info.duration},
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as HH:MM:SS."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
