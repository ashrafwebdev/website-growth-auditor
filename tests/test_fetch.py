import httpx
import respx

from growthaudit.fetch import fetch_page


@respx.mock
def test_fetch_page_adds_scheme_and_reads_html():
    respx.get("https://example.com/").mock(
        return_value=httpx.Response(200, html="<html><title>Hi</title></html>")
    )
    respx.get("https://example.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://example.com/sitemap.xml").mock(return_value=httpx.Response(404))

    page = fetch_page("example.com")

    assert page.url.rstrip("/") == "https://example.com"
    assert page.status_code == 200
    assert "<title>Hi</title>" in page.html
    assert page.robots_txt is None
    assert page.sitemap_xml is None
