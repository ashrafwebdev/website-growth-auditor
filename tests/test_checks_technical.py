from growthaudit.checks.technical import (
    MobileViewportCheck,
    RedirectChainCheck,
    ThinContentCheck,
    UrlStructureCheck,
)


def test_viewport_passes_and_fails(good_page, bad_page):
    assert MobileViewportCheck().run(good_page).passed
    assert not MobileViewportCheck().run(bad_page).passed


def test_thin_content_flags_short_page(bad_page):
    assert not ThinContentCheck().run(bad_page).passed


def test_thin_content_passes_on_good_page(good_page):
    assert ThinContentCheck().run(good_page).passed


def test_redirect_chain_flags_long_chains(good_page):
    good_page.redirect_chain = ["a", "b", "c", "d"]
    assert not RedirectChainCheck().run(good_page).passed


def test_redirect_chain_passes_with_no_redirects(good_page):
    assert RedirectChainCheck().run(good_page).passed


def test_url_structure_flags_query_params(good_page):
    good_page.url = "https://example.com/page?utm_source=x"
    assert not UrlStructureCheck().run(good_page).passed


def test_url_structure_passes_clean_url(good_page):
    assert UrlStructureCheck().run(good_page).passed
