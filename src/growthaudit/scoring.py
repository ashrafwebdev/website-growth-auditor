from __future__ import annotations

from datetime import datetime, timezone

from growthaudit.models import (
    SEVERITY_WEIGHT,
    AuditReport,
    Category,
    CategoryScore,
    CheckResult,
)

CATEGORY_ORDER: list[Category] = ["seo", "technical", "security", "performance", "accessibility"]


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def score_category(results: list[CheckResult]) -> int:
    score = 100
    for result in results:
        if not result.passed:
            score -= SEVERITY_WEIGHT[result.severity]
    return max(score, 0)


def build_report(url: str, results: list[CheckResult]) -> AuditReport:
    categories: list[CategoryScore] = []
    for category in CATEGORY_ORDER:
        cat_results = [r for r in results if r.category == category]
        if not cat_results:
            continue
        score = score_category(cat_results)
        categories.append(
            CategoryScore(
                category=category,
                score=score,
                grade=grade_for_score(score),
                results=cat_results,
            )
        )

    overall_score = round(sum(c.score for c in categories) / len(categories)) if categories else 0

    return AuditReport(
        url=url,
        scanned_at=datetime.now(timezone.utc).isoformat(),
        overall_score=overall_score,
        overall_grade=grade_for_score(overall_score),
        categories=categories,
    )
