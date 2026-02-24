"""Web page to Markdown converter using trafilatura + Playwright fallback."""

from .base import BaseConverter, ConversionResult
from utils.markdown_clean import clean_markdown


class WebConverter(BaseConverter):
    supported_extensions = ()  # Handles URLs, not file extensions
    is_url_converter = True

    def convert(self, source: str, **kwargs) -> ConversionResult:
        url = str(source)

        # Attempt 1: trafilatura (fast, no browser needed)
        result = self._try_trafilatura(url)
        if result and len(result.content.strip()) > 10:
            return result

        # Attempt 2: Playwright (renders JavaScript)
        playwright_result = self._try_playwright(url)
        if playwright_result:
            return playwright_result

        # Attempt 3: Direct HTTP + markdownify fallback
        fallback = self._try_direct_fetch(url)
        if fallback:
            return fallback

        raise RuntimeError(
            f"Could not extract content from {url}. "
            "The page may be empty, require authentication, or block scrapers."
        )

    def _try_trafilatura(self, url: str) -> ConversionResult | None:
        try:
            import trafilatura

            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None

            text = trafilatura.extract(
                downloaded,
                output_format="markdown",
                include_tables=True,
                include_links=True,
                include_images=False,
            )
            if text:
                title = trafilatura.extract(downloaded, output_format="txt", only_with_metadata=True)
                content = clean_markdown(text)
                return ConversionResult(content=content, title=None, source=url)
        except Exception:
            pass
        return None

    def _try_playwright(self, url: str) -> ConversionResult | None:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=60000)
                html = page.content()
                title = page.title()
                browser.close()

            # Try trafilatura on the rendered HTML
            try:
                import trafilatura
                text = trafilatura.extract(
                    html,
                    output_format="markdown",
                    include_tables=True,
                    include_links=True,
                )
                if text and len(text.strip()) > 50:
                    content = clean_markdown(text)
                    return ConversionResult(content=content, title=title, source=url)
            except Exception:
                pass

            # Final fallback: markdownify on raw HTML
            from markdownify import markdownify
            md = markdownify(
                html,
                heading_style="ATX",
                strip=["script", "style", "nav", "footer", "header", "aside"],
            )
            content = clean_markdown(md)
            return ConversionResult(content=content, title=title, source=url)

        except Exception:
            return None

    def _try_direct_fetch(self, url: str) -> ConversionResult | None:
        """Fallback: fetch HTML directly and convert with markdownify."""
        try:
            from urllib.request import urlopen, Request
            from markdownify import markdownify

            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=60) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            md = markdownify(
                html,
                heading_style="ATX",
                strip=["script", "style", "nav", "footer", "header", "aside"],
            )
            if md.strip():
                content = clean_markdown(md)
                return ConversionResult(content=content, title=None, source=url)
        except Exception:
            pass
        return None
