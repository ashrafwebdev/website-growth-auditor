from __future__ import annotations

from abc import ABC, abstractmethod

from growthaudit.models import Category, CheckResult, PageContext, Severity


class Check(ABC):
    """Base class for a single audit check.

    Subclasses implement `run` and return a CheckResult describing whether
    the page passed. Keeping each check as its own small class makes it easy
    for contributors to add new checks without touching existing ones.
    """

    id: str
    category: Category
    severity: Severity
    title: str

    def applies_to(self, page: PageContext) -> bool:
        return True

    @abstractmethod
    def run(self, page: PageContext) -> CheckResult: ...

    def _result(
        self,
        passed: bool,
        message: str,
        fix: str | None = None,
        evidence: str | None = None,
    ) -> CheckResult:
        return CheckResult(
            check_id=self.id,
            category=self.category,
            passed=passed,
            severity=self.severity,
            title=self.title,
            message=message,
            fix=fix,
            evidence=evidence,
        )
