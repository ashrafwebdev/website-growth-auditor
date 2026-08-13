from growthaudit.checks import ALL_CHECKS
from growthaudit.checks.security import SslCertificateCheck
from growthaudit.models import Severity
from growthaudit.scoring import build_report, grade_for_score, score_category

# Exclude checks that make real network calls — unit tests should stay offline.
OFFLINE_CHECKS = [c for c in ALL_CHECKS if not isinstance(c, SslCertificateCheck)]


def test_grade_boundaries():
    assert grade_for_score(100) == "A"
    assert grade_for_score(90) == "A"
    assert grade_for_score(89) == "B"
    assert grade_for_score(65) == "D"
    assert grade_for_score(10) == "F"


def test_score_category_deducts_by_severity():
    from growthaudit.models import CheckResult

    results = [
        CheckResult(
            check_id="x",
            category="seo",
            passed=False,
            severity=Severity.CRITICAL,
            title="X",
            message="broken",
        )
    ]
    assert score_category(results) == 75


def test_build_report_on_good_page_scores_well(good_page):
    results = [check.run(good_page) for check in OFFLINE_CHECKS if check.applies_to(good_page)]
    report = build_report(good_page.url, results)
    assert report.overall_score >= 70
    assert report.overall_grade in ("A", "B", "C")


def test_build_report_on_bad_page_scores_poorly(bad_page):
    results = [check.run(bad_page) for check in OFFLINE_CHECKS if check.applies_to(bad_page)]
    report = build_report(bad_page.url, results)
    assert len(report.all_issues) > 0
    assert report.overall_score < 100
