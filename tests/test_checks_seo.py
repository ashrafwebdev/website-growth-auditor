from growthaudit.checks.seo import (
    CanonicalTagCheck,
    FaviconCheck,
    HeadingStructureCheck,
    ImageAltTextCheck,
    MetaDescriptionCheck,
    OpenGraphCheck,
    RobotsTxtCheck,
    SitemapXmlCheck,
    StructuredDataCheck,
    TitleTagCheck,
)


def test_title_tag_passes_on_good_page(good_page):
    assert TitleTagCheck().run(good_page).passed


def test_title_tag_fails_when_missing(bad_page):
    assert not TitleTagCheck().run(bad_page).passed


def test_meta_description_fails_when_missing(bad_page):
    result = MetaDescriptionCheck().run(bad_page)
    assert not result.passed


def test_meta_description_passes_on_good_page(good_page):
    assert MetaDescriptionCheck().run(good_page).passed


def test_canonical_passes_and_fails(good_page, bad_page):
    assert CanonicalTagCheck().run(good_page).passed
    assert not CanonicalTagCheck().run(bad_page).passed


def test_heading_structure_flags_multiple_h1(bad_page):
    result = HeadingStructureCheck().run(bad_page)
    assert not result.passed
    assert "h1" in result.message.lower()


def test_heading_structure_passes_on_good_page(good_page):
    assert HeadingStructureCheck().run(good_page).passed


def test_image_alt_text_flags_missing_alt(bad_page):
    result = ImageAltTextCheck().run(bad_page)
    assert not result.passed


def test_image_alt_text_passes_on_good_page(good_page):
    assert ImageAltTextCheck().run(good_page).passed


def test_open_graph_passes_and_fails(good_page, bad_page):
    assert OpenGraphCheck().run(good_page).passed
    assert not OpenGraphCheck().run(bad_page).passed


def test_robots_txt_passes_and_fails(good_page, bad_page):
    assert RobotsTxtCheck().run(good_page).passed
    assert not RobotsTxtCheck().run(bad_page).passed


def test_sitemap_passes_and_fails(good_page, bad_page):
    assert SitemapXmlCheck().run(good_page).passed
    assert not SitemapXmlCheck().run(bad_page).passed


def test_structured_data_passes_and_fails(good_page, bad_page):
    assert StructuredDataCheck().run(good_page).passed
    assert not StructuredDataCheck().run(bad_page).passed


def test_favicon_passes_and_fails(good_page, bad_page):
    assert FaviconCheck().run(good_page).passed
    assert not FaviconCheck().run(bad_page).passed
