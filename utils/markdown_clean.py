"""Post-processing to normalize and clean markdown output."""

import re


def clean_markdown(text: str) -> str:
    """Normalize and clean markdown for LLM consumption."""
    text = _strip_css_blocks(text)
    text = _strip_html_tags(text)
    text = _collapse_blank_lines(text)
    text = _ensure_heading_spacing(text)
    text = _strip_html_comments(text)
    text = _strip_trailing_whitespace(text)
    return text.strip() + "\n"


def _collapse_blank_lines(text: str) -> str:
    """Collapse 3+ consecutive blank lines down to 2."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _ensure_heading_spacing(text: str) -> str:
    """Ensure blank line before headings (except at start of text)."""
    return re.sub(r"([^\n])\n(#{1,6} )", r"\1\n\n\2", text)


def _strip_html_comments(text: str) -> str:
    """Remove HTML comments."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _strip_css_blocks(text: str) -> str:
    """Remove inline CSS that leaks into markdown output, preserving fenced code blocks."""
    # Split on fenced code blocks to avoid modifying their content
    parts = re.split(r"(```[\s\S]*?```)", text)
    for i, part in enumerate(parts):
        if not part.startswith("```"):
            # Only strip CSS outside of code blocks
            # Match CSS-like patterns: selector { property: value; }
            parts[i] = re.sub(
                r"[a-zA-Z0-9\s,.:>#\-_*\[\]=~^|]+\{[^}]*[:;][^}]*\}",
                "", part
            )
    return "".join(parts)


def _strip_html_tags(text: str) -> str:
    """Remove leftover HTML tags, preserving fenced code blocks."""
    parts = re.split(r"(```[\s\S]*?```)", text)
    for i, part in enumerate(parts):
        if not part.startswith("```"):
            parts[i] = re.sub(r"<[^>]+>", "", part)
    return "".join(parts)


def _strip_trailing_whitespace(text: str) -> str:
    """Remove trailing whitespace from each line."""
    return "\n".join(line.rstrip() for line in text.split("\n"))
