from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from growthaudit.models import AuditReport, Severity

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_GRADE_COLORS = {"A": "#22c55e", "B": "#86efac", "C": "#facc15", "D": "#fb923c", "F": "#ef4444"}
_SEVERITY_ORDER = {s: i for i, s in enumerate([Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW])}

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)

DEFAULT_CONTACT_URL = "https://ashrafwebdev.github.io/#contact"


def render_html(
    report: AuditReport,
    branding: bool = True,
    contact_url: str = DEFAULT_CONTACT_URL,
) -> str:
    template = _env.get_template("report.html.jinja")
    issues = sorted(report.all_issues, key=lambda r: _SEVERITY_ORDER[r.severity])
    return template.render(
        report=report,
        issues=issues,
        branding=branding,
        contact_url=contact_url,
        grade_color=_GRADE_COLORS.get(report.overall_grade, "#9ca3af"),
    )
