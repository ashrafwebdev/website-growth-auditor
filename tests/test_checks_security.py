import socket

from growthaudit.checks.security import (
    HttpsEnforcementCheck,
    MixedContentCheck,
    SecurityHeadersCheck,
    SslCertificateCheck,
)


def test_https_enforcement_passes_on_https(good_page):
    assert HttpsEnforcementCheck().run(good_page).passed


def test_https_enforcement_fails_on_http(good_page):
    good_page.url = "http://example.com/"
    assert not HttpsEnforcementCheck().run(good_page).passed


def test_security_headers_fails_when_missing(good_page):
    assert not SecurityHeadersCheck().run(good_page).passed


def test_security_headers_passes_when_present(good_page):
    good_page.headers = {
        "Strict-Transport-Security": "max-age=63072000",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "no-referrer",
    }
    assert SecurityHeadersCheck().run(good_page).passed


def test_mixed_content_flags_http_resources(bad_page):
    assert not MixedContentCheck().run(bad_page).passed


def test_mixed_content_passes_on_good_page(good_page):
    assert MixedContentCheck().run(good_page).passed


def test_ssl_certificate_check_handles_connection_failure(good_page, monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr(socket, "create_connection", _raise)
    result = SslCertificateCheck().run(good_page)
    assert not result.passed
