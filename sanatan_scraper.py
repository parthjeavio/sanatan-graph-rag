import json
import re
from dataclasses import dataclass
from html import unescape
from typing import Iterable, Optional
from urllib.parse import quote, unquote, urlparse
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class Document:
    source_url: str
    title: str
    text: str


class MythologyScraper:
    """Scrapes mythology text from Wikipedia, sacred-texts pages, and generic sites."""

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def scrape(self, urls: Iterable[str]) -> list[Document]:
        documents: list[Document] = []
        for url in urls:
            try:
                text, title = self._extract_text(url)
            except (URLError, OSError, ValueError):
                continue
            if text:
                documents.append(Document(source_url=url, title=title, text=text))
        return documents

    def _extract_text(self, url: str) -> tuple[Optional[str], str]:
        if "wikipedia.org/wiki/" in url:
            page_title = self._title_from_wikipedia_url(url)
            if page_title:
                api_result = self._fetch_wikipedia_article_text_via_api(page_title)
                if api_result:
                    return api_result[1], api_result[0]

        html = self._fetch_url(url)
        if not html:
            return None, url

        title = self._extract_title(html) or url
        text = self._extract_paragraph_text(html)
        if not text:
            return None, title
        return text, title

    def _fetch_url(self, url: str) -> str:
        request = Request(url, headers=self.headers)
        with urlopen(request, timeout=self.timeout) as response:
            return response.read().decode("utf-8", errors="ignore")

    def _extract_title(self, html: str) -> Optional[str]:
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        return unescape(match.group(1)).strip() if match else None

    def _extract_paragraph_text(self, html: str) -> Optional[str]:
        html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
        html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)

        blocks = re.findall(r"<(p|li)[^>]*>(.*?)</\1>", html, flags=re.I | re.S)
        cleaned: list[str] = []
        for _, block in blocks:
            text = re.sub(r"<[^>]+>", " ", block)
            text = unescape(re.sub(r"\s+", " ", text)).strip()
            if len(text) >= 50:
                cleaned.append(text)

        if not cleaned:
            return None
        return "\n".join(cleaned)

    def _title_from_wikipedia_url(self, url: str) -> Optional[str]:
        path = urlparse(url).path
        if "/wiki/" not in path:
            return None
        slug = path.split("/wiki/", 1)[1].strip("/")
        if not slug:
            return None
        return unquote(slug).replace("_", " ")

    def _fetch_wikipedia_article_text_via_api(self, title: str) -> Optional[tuple[str, str]]:
        encoded_title = quote(title)
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2"
            f"&prop=extracts&explaintext=1&titles={encoded_title}"
        )
        payload = self._fetch_url(url)
        data = json.loads(payload)
        pages = data.get("query", {}).get("pages", [])
        if not pages:
            return None

        page = pages[0]
        extract = page.get("extract", "").strip()
        if not extract:
            return None
        return page.get("title", title), extract
