"""Small, dependency-free search and reading tools.

The agent works with either user-provided URLs or DuckDuckGo's lightweight HTML
endpoint. If network access is unavailable, it still produces a transparent
brief that says evidence is missing instead of inventing sources.
"""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Iterable


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title += text
        elif len(text) > 35:
            self.parts.append(text)


def normalize_text(text: str, max_chars: int = 2400) -> str:
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def extract_urls(raw_urls: Iterable[str]) -> list[str]:
    urls = []
    for raw_url in raw_urls:
        candidate = raw_url.strip()
        if candidate.startswith(("http://", "https://")):
            urls.append(candidate)
    return urls


def search_web(query: str, max_results: int = 5) -> list[dict[str, str]]:
    encoded = urllib.parse.urlencode({"q": query})
    url = f"https://duckduckgo.com/html/?{encoded}"
    request = urllib.request.Request(url, headers={"User-Agent": "local-research-agent/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            page = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return []

    results: list[dict[str, str]] = []
    pattern = re.compile(r'class="result__a" href="([^"]+)".*?>(.*?)</a>', re.DOTALL)
    for href, title_html in pattern.findall(page):
        title = re.sub("<.*?>", "", title_html)
        title = normalize_text(title, max_chars=180)
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(href)).query)
        target = parsed.get("uddg", [html.unescape(href)])[0]
        if target.startswith("http") and title:
            results.append({"title": title, "url": target, "snippet": ""})
        if len(results) >= max_results:
            break
    return results


def read_url(url: str, max_chars: int = 2400) -> dict[str, str] | None:
    request = urllib.request.Request(url, headers={"User-Agent": "local-research-agent/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                return None
            page = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

    parser = TextExtractor()
    parser.feed(page)
    title = normalize_text(parser.title or url, max_chars=180)
    text = normalize_text(" ".join(parser.parts), max_chars=max_chars)
    if not text:
        return None
    return {"title": title, "url": url, "text": text}
