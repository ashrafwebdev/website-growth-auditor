from __future__ import annotations

from itertools import pairwise

from bs4 import BeautifulSoup

from growthaudit.checks.base import Check
from growthaudit.models import CheckResult, PageContext, Severity


def _soup(page: PageContext) -> BeautifulSoup:
    return BeautifulSoup(page.html, "lxml")


class TitleTagCheck(Check):
    id = "seo.title"
    category = "seo"
    severity = Severity.HIGH
    title = "Title tag"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        tag = soup.find("title")
        text = tag.get_text(strip=True) if tag else ""

        if not text:
            return self._result(
                False,
                "Page has no <title> tag (or it's empty).",
                fix="Add a unique, descriptive <title> between 50-60 characters.",
            )
        if not (10 <= len(text) <= 60):
            return self._result(
                False,
                f"Title is {len(text)} characters — ideal range is ~50-60.",
                fix="Rewrite the title to fall within roughly 50-60 characters.",
                evidence=text,
            )
        return self._result(True, "Title tag present and a reasonable length.", evidence=text)


class MetaDescriptionCheck(Check):
    id = "seo.meta_description"
    category = "seo"
    severity = Severity.MEDIUM
    title = "Meta description"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        tag = soup.find("meta", attrs={"name": "description"})
        content = tag.get("content", "").strip() if tag else ""

        if not content:
            return self._result(
                False,
                "Page has no meta description.",
                fix="Add a <meta name=\"description\"> summarizing the page in ~120-158 characters.",
            )
        if not (50 <= len(content) <= 160):
            return self._result(
                False,
                f"Meta description is {len(content)} characters — ideal range is ~120-158.",
                fix="Rewrite the description to fall within roughly 120-158 characters.",
                evidence=content,
            )
        return self._result(True, "Meta description present and a reasonable length.", evidence=content)


class CanonicalTagCheck(Check):
    id = "seo.canonical"
    category = "seo"
    severity = Severity.MEDIUM
    title = "Canonical tag"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        tag = soup.find("link", rel="canonical")
        href = tag.get("href", "").strip() if tag else ""

        if not href:
            return self._result(
                False,
                "No canonical link tag found.",
                fix='Add <link rel="canonical" href="..."> pointing to the preferred URL.',
            )
        return self._result(True, "Canonical tag present.", evidence=href)


class HeadingStructureCheck(Check):
    id = "seo.heading_structure"
    category = "seo"
    severity = Severity.MEDIUM
    title = "Heading structure"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        h1s = soup.find_all("h1")

        if len(h1s) == 0:
            return self._result(
                False,
                "Page has no <h1>.",
                fix="Add exactly one <h1> describing the page's main topic.",
            )
        if len(h1s) > 1:
            return self._result(
                False,
                f"Page has {len(h1s)} <h1> tags — should have exactly one.",
                fix="Keep a single <h1> and demote the others to <h2>/<h3>.",
            )

        levels = [int(h.name[1]) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        for prev, cur in pairwise(levels):
            if cur - prev > 1:
                return self._result(
                    False,
                    f"Heading level skips from h{prev} to h{cur}.",
                    fix="Don't skip heading levels — descend one level at a time.",
                )
        return self._result(True, "Exactly one <h1> with no skipped heading levels.")


class ImageAltTextCheck(Check):
    id = "seo.image_alt_text"
    category = "seo"
    severity = Severity.MEDIUM
    title = "Image alt text"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        images = soup.find_all("img")
        if not images:
            return self._result(True, "No <img> tags found on the page.")

        missing = [img for img in images if not img.get("alt", "").strip()]
        pct_missing = len(missing) / len(images) * 100

        if missing:
            return self._result(
                False,
                f"{len(missing)}/{len(images)} images ({pct_missing:.0f}%) are missing alt text.",
                fix="Add descriptive alt text to every meaningful image (empty alt=\"\" is fine for decorative images).",
            )
        return self._result(True, f"All {len(images)} images have alt text.")


class OpenGraphCheck(Check):
    id = "seo.open_graph"
    category = "seo"
    severity = Severity.LOW
    title = "Open Graph tags"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        required = {"og:title", "og:description", "og:image"}
        present = {
            tag.get("property")
            for tag in soup.find_all("meta", property=True)
            if tag.get("property") in required
        }
        missing = required - present

        if missing:
            return self._result(
                False,
                f"Missing Open Graph tags: {', '.join(sorted(missing))}.",
                fix="Add the missing og: meta tags so shared links render nicely on social media.",
            )
        return self._result(True, "Core Open Graph tags present.")


class RobotsTxtCheck(Check):
    id = "seo.robots_txt"
    category = "seo"
    severity = Severity.MEDIUM
    title = "robots.txt"

    def run(self, page: PageContext) -> CheckResult:
        if not page.robots_txt:
            return self._result(
                False,
                "No robots.txt found at /robots.txt.",
                fix="Add a robots.txt file, even a permissive one, to guide crawlers.",
            )
        has_sitemap_directive = "sitemap:" in page.robots_txt.lower()
        if not has_sitemap_directive:
            return self._result(
                False,
                "robots.txt exists but doesn't reference a sitemap.",
                fix="Add a `Sitemap: https://yoursite.com/sitemap.xml` line to robots.txt.",
            )
        return self._result(True, "robots.txt present and references a sitemap.")


class SitemapXmlCheck(Check):
    id = "seo.sitemap_xml"
    category = "seo"
    severity = Severity.MEDIUM
    title = "sitemap.xml"

    def run(self, page: PageContext) -> CheckResult:
        if not page.sitemap_xml:
            return self._result(
                False,
                "No sitemap.xml found at /sitemap.xml.",
                fix="Generate and publish a sitemap.xml listing your indexable pages.",
            )
        url_count = page.sitemap_xml.count("<url>") + page.sitemap_xml.count("<sitemap>")
        if url_count == 0:
            return self._result(
                False,
                "sitemap.xml exists but doesn't look like valid XML sitemap content.",
                fix="Regenerate the sitemap using a standard sitemap generator.",
            )
        return self._result(True, f"sitemap.xml present with ~{url_count} entries.")


class StructuredDataCheck(Check):
    id = "seo.structured_data"
    category = "seo"
    severity = Severity.LOW
    title = "Structured data (JSON-LD)"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        scripts = soup.find_all("script", type="application/ld+json")
        if not scripts:
            return self._result(
                False,
                "No JSON-LD structured data found.",
                fix="Add schema.org JSON-LD markup relevant to the page (Organization, Article, Product, etc.).",
            )
        return self._result(True, f"Found {len(scripts)} JSON-LD block(s).")


class HtmlLangCheck(Check):
    id = "seo.html_lang"
    category = "seo"
    severity = Severity.LOW
    title = "HTML lang attribute"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        html_tag = soup.find("html")
        lang = html_tag.get("lang", "").strip() if html_tag else ""

        if not lang:
            return self._result(
                False,
                "No lang attribute on <html>.",
                fix='Add lang="en" (or the appropriate language code) to the <html> tag.',
            )
        return self._result(True, "html lang attribute present.", evidence=lang)


class FaviconCheck(Check):
    id = "seo.favicon"
    category = "seo"
    severity = Severity.LOW
    title = "Favicon"

    def run(self, page: PageContext) -> CheckResult:
        soup = _soup(page)
        icon = soup.find("link", rel=lambda v: v and "icon" in v.lower())
        if not icon:
            return self._result(
                False,
                "No favicon link found.",
                fix='Add <link rel="icon" href="/favicon.ico"> (or an SVG/PNG equivalent).',
            )
        return self._result(True, "Favicon link present.")


SEO_CHECKS: list[Check] = [
    TitleTagCheck(),
    MetaDescriptionCheck(),
    CanonicalTagCheck(),
    HeadingStructureCheck(),
    ImageAltTextCheck(),
    OpenGraphCheck(),
    RobotsTxtCheck(),
    SitemapXmlCheck(),
    StructuredDataCheck(),
    HtmlLangCheck(),
    FaviconCheck(),
]
