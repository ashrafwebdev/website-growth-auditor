from __future__ import annotations

from growthaudit.models import AuditReport


def render_json(report: AuditReport) -> str:
    return report.model_dump_json(indent=2)
