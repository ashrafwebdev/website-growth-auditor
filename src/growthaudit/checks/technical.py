from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from growthaudit.checks.base import Check
from growthaudit.models import CheckResult, PageContext, Severity

WORDS_PER_PAGE_MINIMUM = 150


class MobileViewportCheck(Check):
    id = "technical.viewport"
    category = "technical"
    severity = Severity.HIGH
    title = "Mobile viewport"

    def run(self, page: PageContext) -> CheckResult:
        soup = BeautifulSoup(page.html, "lxml")
        tag = soup.find("meta", attrs={"name": "viewport"})
        if not tag:
            return self._result(
                False,
                "No viewport meta tag found.",
                fix='Add <meta name="viewport" content="width=device-width, initial-scale=1"> for mobile rendering.',
            )
        content = tag.get("content", "")
        if "width=device-width" not in content.replace(" ", ""):
            return self._result(
                False,
                "Viewport meta tag exists but doesn't set width=device-width.",
                fix='Use content="width=device-width, initial-scale=1".',
                evidence=content,
            )
        return self._result(True, "Viewport meta tag correctly configured.")


class RedirectChainCheck(Check):
    id = "technical.redirect_chain"
    category = "technical"
    severity = Severity.LOW
    title = "Redirect chain length"

    def run(self, page: PageContext) -> CheckResult:
        hops = len(page.redirect_chain)
        if hops > 2:
            return self._result(
                False,
                f"URL redirects {hops} times before reaching the final page.",
                fix="Point links directly at the final URL to avoid extra redirect hops.",
                evidence=" -> ".join(page.redirect_chain),
            )
        return self._result(True, f"Redirect chain is short ({hops} hop(s)).")


class ThinContentCheck(Check):
    id = "technical.thin_content"
    category = "technical"
    severity = Severity.LOW
    title = "Content length"

    def run(self, page: PageContext) -> CheckResult:
        soup = BeautifulSoup(page.html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())

        if word_count < WORDS_PER_PAGE_MINIMUM:
            return self._result(
                False,
                f"Page has only ~{word_count} words of visible text.",
                fix="Thin pages tend to rank poorly — consider adding more substantive content.",
            )
        return self._result(True, f"Page has ~{word_count} words of visible text.")


class UrlStructureCheck(Check):
    id = "technical.url_structure"
    category = "technical"
    severity = Severity.LOW
    title = "URL structure"

    def run(self, page: PageContext) -> CheckResult:
        parsed = urlparse(page.url)
        issues = []
        if len(page.url) > 100:
            issues.append(f"URL is {len(page.url)} characters (long URLs are harder to share)")
        if parsed.query:
            issues.append("URL contains query parameters")
        if "_" in parsed.path:
            issues.append("URL path uses underscores instead of hyphens")

        if issues:
            return self._result(
                False,
                "; ".join(issues) + ".",
                fix="Prefer short, hyphenated, query-free URLs where possible.",
            )
        return self._result(True, "URL structure looks clean.")


TECHNICAL_CHECKS: list[Check] = [
    MobileViewportCheck(),
    RedirectChainCheck(),
    ThinContentCheck(),
    UrlStructureCheck(),
]
