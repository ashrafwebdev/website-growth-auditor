from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from growthaudit.checks import ALL_CHECKS
from growthaudit.fetch import fetch_page
from growthaudit.report.cli_renderer import render_report
from growthaudit.report.html_renderer import render_html
from growthaudit.report.json_renderer import render_json
from growthaudit.scoring import build_report

app = typer.Typer(
    name="growthaudit",
    help="Free, open-source website auditor for SEO, performance, security, and technical health.",
)
console = Console()


@app.command()
def scan(
    url: str = typer.Argument(..., help="URL to audit, e.g. https://example.com"),
    format: str = typer.Option("cli", "--format", "-f", help="Output format: cli, json, or html."),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write the report to this file instead of stdout."
    ),
    no_branding: bool = typer.Option(False, "--no-branding", help="Omit the branding footer in HTML reports."),
    fail_under: int | None = typer.Option(
        None, "--fail-under", help="Exit with a non-zero status if the overall score is below this value."
    ),
) -> None:
    """Audit a single URL and print or save a report."""
    with console.status(f"Scanning {url}..."):
        page = fetch_page(url)
        results = [check.run(page) for check in ALL_CHECKS if check.applies_to(page)]
        report = build_report(page.url, results)

    if format == "json":
        text = render_json(report)
        _emit(text, output)
    elif format == "html":
        text = render_html(report, branding=not no_branding)
        _emit(text, output)
    elif format == "cli":
        render_report(report, console=console)
    else:
        raise typer.BadParameter(f"Unknown format: {format!r} (expected cli, json, or html)")

    if fail_under is not None and report.overall_score < fail_under:
        console.print(
            f"\n[bold red]Score {report.overall_score} is below --fail-under threshold {fail_under}.[/]"
        )
        raise typer.Exit(code=1)


def _emit(text: str, output: Path | None) -> None:
    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"[green]Wrote report to {output}[/]")
    else:
        console.print(text)


if __name__ == "__main__":
    app()
