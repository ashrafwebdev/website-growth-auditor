from __future__ import annotations

from pathlib import Path

import pytest

from growthaudit.models import PageContext

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def make_page(
    html_fixture: str,
    url: str = "https://example.com/",
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    elapsed_ms: float = 200.0,
    redirect_chain: list[str] | None = None,
    robots_txt: str | None = "User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml\n",
    sitemap_xml: str | None = "<urlset><url><loc>https://example.com/</loc></url></urlset>",
) -> PageContext:
    return PageContext(
        url=url,
        status_code=status_code,
        headers=headers or {},
        html=load_fixture(html_fixture),
        elapsed_ms=elapsed_ms,
        redirect_chain=redirect_chain or [],
        robots_txt=robots_txt,
        sitemap_xml=sitemap_xml,
    )


@pytest.fixture
def good_page() -> PageContext:
    return make_page("good_page.html")


@pytest.fixture
def bad_page() -> PageContext:
    return make_page("bad_page.html", robots_txt=None, sitemap_xml=None)
