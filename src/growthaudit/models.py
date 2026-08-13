from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["seo", "technical", "security", "performance", "accessibility"]


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


SEVERITY_WEIGHT: dict[Severity, int] = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
}


class PageContext(BaseModel):
    """Everything a Check needs to inspect a fetched page."""

    url: str
    status_code: int
    headers: dict[str, str]
    html: str
    elapsed_ms: float
    redirect_chain: list[str] = Field(default_factory=list)
    robots_txt: str | None = None
    sitemap_xml: str | None = None

    model_config = {"arbitrary_types_allowed": True}


class CheckResult(BaseModel):
    check_id: str
    category: Category
    passed: bool
    severity: Severity
    title: str
    message: str
    fix: str | None = None
    evidence: str | None = None


class CategoryScore(BaseModel):
    category: Category
    score: int
    grade: str
    results: list[CheckResult]


class AuditReport(BaseModel):
    url: str
    scanned_at: str
    overall_score: int
    overall_grade: str
    categories: list[CategoryScore]

    @property
    def all_issues(self) -> list[CheckResult]:
        return [r for cat in self.categories for r in cat.results if not r.passed]
