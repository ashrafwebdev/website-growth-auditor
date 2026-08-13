from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from growthaudit.models import AuditReport, Severity

GRADE_COLORS = {"A": "green", "B": "green", "C": "yellow", "D": "orange3", "F": "red"}
SEVERITY_COLORS = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "dim",
}
SEVERITY_ORDER = {s: i for i, s in enumerate([Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW])}


def render_report(report: AuditReport, console: Console | None = None) -> None:
    console = console or Console()

    grade_color = GRADE_COLORS.get(report.overall_grade, "white")
    console.print(
        Panel(
            f"[bold {grade_color}]{report.overall_grade}[/]  "
            f"Overall score: [bold]{report.overall_score}/100[/]\n"
            f"[dim]{report.url}[/]",
            title="growthaudit report",
        )
    )

    table = Table(title="Category scores")
    table.add_column("Category")
    table.add_column("Score", justify="right")
    table.add_column("Grade", justify="center")
    table.add_column("Issues", justify="right")
    for cat in report.categories:
        color = GRADE_COLORS.get(cat.grade, "white")
        issue_count = sum(1 for r in cat.results if not r.passed)
        table.add_row(
            cat.category.title(),
            f"{cat.score}/100",
            f"[{color}]{cat.grade}[/]",
            str(issue_count),
        )
    console.print(table)

    issues = sorted(report.all_issues, key=lambda r: SEVERITY_ORDER[r.severity])
    if not issues:
        console.print("\n[bold green]No issues found — nice work![/]")
        return

    console.print(f"\n[bold]{len(issues)} issue(s) found[/] (sorted by severity):\n")
    for issue in issues:
        color = SEVERITY_COLORS[issue.severity]
        console.print(f"[{color}]● [{issue.severity.value.upper()}][/] {issue.title}: {issue.message}")
        if issue.fix:
            console.print(f"  [dim]Fix: {issue.fix}[/]")
