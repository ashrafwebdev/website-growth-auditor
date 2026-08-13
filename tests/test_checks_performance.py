from growthaudit.checks.performance import CachingHeadersCheck, CompressionCheck, LoadTimeCheck


def test_load_time_flags_slow_response(good_page):
    good_page.elapsed_ms = 3000
    assert not LoadTimeCheck().run(good_page).passed


def test_load_time_passes_fast_response(good_page):
    good_page.elapsed_ms = 200
    assert LoadTimeCheck().run(good_page).passed


def test_compression_fails_without_encoding(good_page):
    assert not CompressionCheck().run(good_page).passed


def test_compression_passes_with_gzip(good_page):
    good_page.headers = {"Content-Encoding": "gzip"}
    assert CompressionCheck().run(good_page).passed


def test_caching_headers_fails_without_cache_control(good_page):
    assert not CachingHeadersCheck().run(good_page).passed


def test_caching_headers_passes_with_cache_control(good_page):
    good_page.headers = {"Cache-Control": "max-age=3600"}
    assert CachingHeadersCheck().run(good_page).passed
