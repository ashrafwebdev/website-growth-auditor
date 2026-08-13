from growthaudit.checks.base import Check
from growthaudit.checks.performance import PERFORMANCE_CHECKS
from growthaudit.checks.security import SECURITY_CHECKS
from growthaudit.checks.seo import SEO_CHECKS
from growthaudit.checks.technical import TECHNICAL_CHECKS

ALL_CHECKS: list[Check] = [*SEO_CHECKS, *TECHNICAL_CHECKS, *SECURITY_CHECKS, *PERFORMANCE_CHECKS]

__all__ = ["ALL_CHECKS", "Check"]
