#!/usr/bin/env python3
"""Dependency-free structural audit for the static Altayskiy Uezd website."""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".github", "node_modules", "venv", ".venv", "dist", "build"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_depth = 0
        self.title = ""
        self.description = False
        self.h1_count = 0
        self.images = 0
        self.images_without_alt = 0
        self.canonical = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title_depth += 1
        elif tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = bool(attrs.get("content", "").strip())
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img":
            self.images += 1
            if "alt" not in attrs:
                self.images_without_alt += 1
        elif tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = bool(attrs.get("href", "").strip())

    def handle_endtag(self, tag):
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data):
        if self.title_depth:
            self.title += data.strip()


def main() -> int:
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            parser = PageParser()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            rel = path.relative_to(ROOT).as_posix()
            issues = []
            if not parser.title.strip():
                issues.append("missing-title")
            if not parser.description:
                issues.append("missing-meta-description")
            if parser.h1_count == 0:
                issues.append("missing-h1")
            elif parser.h1_count > 1:
                issues.append("multiple-h1")
            if parser.images_without_alt:
                issues.append(f"images-without-alt:{parser.images_without_alt}")
            pages.append({
                "path": rel,
                "title_present": bool(parser.title.strip()),
                "meta_description_present": parser.description,
                "h1_count": parser.h1_count,
                "images": parser.images,
                "images_without_alt": parser.images_without_alt,
                "canonical_present": parser.canonical,
                "issues": issues,
            })
        except OSError as exc:
            pages.append({"path": str(path), "issues": [f"read-error:{exc}"]})

    summary = {
        "pages_scanned": len(pages),
        "pages_with_issues": sum(bool(p["issues"]) for p in pages),
        "issues_total": sum(len(p["issues"]) for p in pages),
        "pages": pages,
    }
    out = ROOT / "site-audit-report.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "pages"}, ensure_ascii=False, indent=2))
    for page in pages:
        if page["issues"]:
            print(f"- {page['path']}: {', '.join(page['issues'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
