from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse

import httpx

from growthaudit.models import PageContext

USER_AGENT = "growthaudit/0.1 (+https://github.com/ashrafwebdev/website-growth-auditor)"


def fetch_page(url: str, timeout: float = 15.0) -> PageContext:
    """Fetch a single URL and everything a Check needs to inspect it."""
    if not urlparse(url).scheme:
        url = f"https://{url}"

    start = time.perf_counter()
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        response = client.get(url)
        elapsed_ms = (time.perf_counter() - start) * 1000

        redirect_chain = [str(r.headers.get("location", r.url)) for r in response.history]

        robots_txt = _fetch_optional(client, urljoin(str(response.url), "/robots.txt"))
        sitemap_xml = _fetch_optional(client, urljoin(str(response.url), "/sitemap.xml"))

    return PageContext(
        url=str(response.url),
        status_code=response.status_code,
        headers=dict(response.headers),
        html=response.text,
        elapsed_ms=elapsed_ms,
        redirect_chain=redirect_chain,
        robots_txt=robots_txt,
        sitemap_xml=sitemap_xml,
    )


def _fetch_optional(client: httpx.Client, url: str) -> str | None:
    try:
        response = client.get(url)
        if response.status_code == 200:
            return response.text
    except httpx.HTTPError:
        pass
    return None
