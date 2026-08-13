# growthaudit

**A free, open-source website auditor.** Scan any URL for SEO, technical, security, and
performance issues — the kind of report that's normally locked behind a SEMrush, Ahrefs, or
GTmetrix Pro subscription.

```
$ growthaudit example.com

╭─────────────── growthaudit report ───────────────╮
│ B  Overall score: 84/100                          │
│ https://example.com/                              │
╰────────────────────────────────────────────────────╯
        Category scores
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ Category    ┃   Score ┃ Grade ┃ Issues ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ Seo         │  92/100 │   A   │      1 │
│ Technical   │  85/100 │   B   │      1 │
│ Security    │  75/100 │   C   │      1 │
│ Performance │ 100/100 │   A   │      0 │
└─────────────┴─────────┴───────┴────────┘
```

## Why this exists

Every serious "site audit" tool worth using sits behind a paywall. Most site owners never see
what's actually wrong with their own website — they just know it "feels slow" or "isn't ranking."
`growthaudit` runs a real audit for free, with clear explanations of what's wrong and how to fix
it, no signup required.

## Install

```bash
pipx install growthaudit   # recommended — isolates the CLI's environment
# or: pip install growthaudit
```

## Usage

```bash
growthaudit https://example.com

# Save a branded HTML report
growthaudit https://example.com --format html --output report.html

# Machine-readable output for scripts/CI
growthaudit https://example.com --format json

# Use as a CI quality gate
growthaudit https://example.com --fail-under 80
```

## What it checks

- **SEO** — title/meta description, canonical tags, Open Graph tags, heading structure, image alt
  text, robots.txt/sitemap.xml, structured data (JSON-LD), html lang, favicon.
- **Technical** — mobile viewport, redirect chains, thin-content heuristic, URL structure.
- **Security** — HTTPS enforcement, SSL certificate validity, security headers (HSTS, CSP,
  X-Frame-Options, etc.), mixed content.
- **Performance** — response time, compression, caching headers. (Core Web Vitals via the Google
  PageSpeed Insights API are planned for a future release.)

### What it doesn't do

This is a technical/on-page/performance auditor, not a backlink checker or rank tracker.
Replicating a tool like Ahrefs' backlink index or keyword-ranking data requires a proprietary,
web-scale crawl that no free, self-hosted tool can realistically provide — so `growthaudit`
doesn't pretend to.

## Contributing

New checks are the easiest way to contribute — each one is a small, self-contained class. See
[`src/growthaudit/checks/base.py`](src/growthaudit/checks/base.py) for the interface and any file
in [`src/growthaudit/checks/`](src/growthaudit/checks/) for examples. PRs welcome.

## Roadmap

- [x] v0.1 — SEO, technical, security, and baseline performance checks; CLI/JSON/HTML reports
- [ ] Accessibility checks (axe-core via Playwright)
- [ ] Core Web Vitals via PageSpeed Insights API
- [ ] Multi-page crawl (`--crawl --max-pages N`) with cross-page checks
- [ ] Hosted web version (no install required)

## About

Built by [ashrafwebdev](https://ashrafwebdev.github.io). If an audit turns up issues you'd rather
not fix yourself, [get in touch](https://ashrafwebdev.github.io/#contact) — that's the whole
reason this is free.

## License

MIT — see [LICENSE](LICENSE).
