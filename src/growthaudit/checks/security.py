from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from growthaudit.checks.base import Check
from growthaudit.models import CheckResult, PageContext, Severity

SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "content-security-policy": "Content-Security-Policy",
    "referrer-policy": "Referrer-Policy",
}


def _lower_headers(page: PageContext) -> dict[str, str]:
    return {k.lower(): v for k, v in page.headers.items()}


class HttpsEnforcementCheck(Check):
    id = "security.https"
    category = "security"
    severity = Severity.CRITICAL
    title = "HTTPS enforcement"

    def run(self, page: PageContext) -> CheckResult:
        scheme = urlparse(page.url).scheme
        if scheme != "https":
            return self._result(
                False,
                "Final page URL is not served over HTTPS.",
                fix="Serve the site over HTTPS and redirect all HTTP traffic to HTTPS.",
            )
        return self._result(True, "Site is served over HTTPS.")


class SslCertificateCheck(Check):
    id = "security.ssl_certificate"
    category = "security"
    severity = Severity.CRITICAL
    title = "SSL certificate validity"

    def applies_to(self, page: PageContext) -> bool:
        return urlparse(page.url).scheme == "https"

    def run(self, page: PageContext) -> CheckResult:
        host = urlparse(page.url).hostname
        if not host:
            return self._result(False, "Could not determine hostname to check certificate.")

        try:
            ctx = ssl.create_default_context()
            with (
                socket.create_connection((host, 443), timeout=10) as sock,
                ctx.wrap_socket(sock, server_hostname=host) as ssock,
            ):
                cert = ssock.getpeercert()
        except (ssl.SSLError, OSError) as exc:
            return self._result(
                False,
                f"Could not verify SSL certificate: {exc}.",
                fix="Ensure a valid, trusted TLS certificate is installed and not expired.",
            )

        not_after = cert.get("notAfter")
        if not not_after:
            return self._result(True, "SSL certificate present (expiry unknown).")

        expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days_left = (expires - datetime.now(timezone.utc)).days

        if days_left < 0:
            return self._result(False, "SSL certificate has expired.", fix="Renew the TLS certificate immediately.")
        if days_left < 14:
            return self._result(
                False,
                f"SSL certificate expires in {days_left} day(s).",
                fix="Renew the TLS certificate soon.",
            )
        return self._result(True, f"SSL certificate valid for {days_left} more day(s).")


class SecurityHeadersCheck(Check):
    id = "security.headers"
    category = "security"
    severity = Severity.MEDIUM
    title = "Security headers"

    def run(self, page: PageContext) -> CheckResult:
        headers = _lower_headers(page)
        missing = [label for key, label in SECURITY_HEADERS.items() if key not in headers]

        if missing:
            return self._result(
                False,
                f"Missing recommended security headers: {', '.join(missing)}.",
                fix="Add the missing headers at your server/CDN/reverse-proxy level.",
            )
        return self._result(True, "All recommended security headers are present.")


class MixedContentCheck(Check):
    id = "security.mixed_content"
    category = "security"
    severity = Severity.HIGH
    title = "Mixed content"

    def applies_to(self, page: PageContext) -> bool:
        return urlparse(page.url).scheme == "https"

    def run(self, page: PageContext) -> CheckResult:
        soup = BeautifulSoup(page.html, "lxml")
        offenders = []
        for tag, attr in (("img", "src"), ("script", "src"), ("link", "href")):
            for el in soup.find_all(tag):
                value = el.get(attr, "")
                if value.startswith("http://"):
                    offenders.append(value)

        if offenders:
            return self._result(
                False,
                f"Found {len(offenders)} resource(s) loaded over plain HTTP on an HTTPS page.",
                fix="Update those resource URLs to HTTPS (or protocol-relative).",
                evidence=offenders[0],
            )
        return self._result(True, "No mixed-content resources found.")


SECURITY_CHECKS: list[Check] = [
    HttpsEnforcementCheck(),
    SslCertificateCheck(),
    SecurityHeadersCheck(),
    MixedContentCheck(),
]
