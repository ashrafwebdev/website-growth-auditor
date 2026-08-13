from __future__ import annotations

from growthaudit.checks.base import Check
from growthaudit.models import CheckResult, PageContext, Severity

# PageSpeed Insights / Core Web Vitals integration is planned for a later
# release. v1 ships with baseline checks that need no external API or key.


class LoadTimeCheck(Check):
    id = "performance.load_time"
    category = "performance"
    severity = Severity.HIGH
    title = "Response time"

    def run(self, page: PageContext) -> CheckResult:
        ms = page.elapsed_ms
        if ms > 1500:
            return self._result(
                False,
                f"Page took {ms:.0f}ms to respond — slower than the ~1500ms rule of thumb.",
                fix="Investigate server response time: caching, database queries, or CDN placement.",
            )
        return self._result(True, f"Page responded in {ms:.0f}ms.")


class CompressionCheck(Check):
    id = "performance.compression"
    category = "performance"
    severity = Severity.MEDIUM
    title = "Response compression"

    def run(self, page: PageContext) -> CheckResult:
        headers = {k.lower(): v for k, v in page.headers.items()}
        encoding = headers.get("content-encoding", "")
        if encoding not in ("gzip", "br", "deflate"):
            return self._result(
                False,
                "Response is not compressed (no gzip/brotli Content-Encoding).",
                fix="Enable gzip or brotli compression at your server/CDN.",
            )
        return self._result(True, f"Response is compressed ({encoding}).")


class CachingHeadersCheck(Check):
    id = "performance.caching"
    category = "performance"
    severity = Severity.LOW
    title = "Caching headers"

    def run(self, page: PageContext) -> CheckResult:
        headers = {k.lower(): v for k, v in page.headers.items()}
        if "cache-control" not in headers:
            return self._result(
                False,
                "No Cache-Control header set.",
                fix="Set an appropriate Cache-Control header to let browsers/CDNs cache responses.",
            )
        return self._result(True, "Cache-Control header present.", evidence=headers["cache-control"])


PERFORMANCE_CHECKS: list[Check] = [
    LoadTimeCheck(),
    CompressionCheck(),
    CachingHeadersCheck(),
]
