#!/usr/bin/env python3
"""Validate a canonical Markdown / generated HTML pair and write review JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


class ArtifactParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[int, str]] = []
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.meta: dict[str, str] = {}
        self.formula_depth = 0
        self.formula_em_count = 0
        self.formula_text: list[str] = []
        self._heading_level: int | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[values["name"] or ""] = values["content"] or ""
        if tag in {"h1", "h2", "h3", "h4"}:
            self._heading_level = int(tag[1])
            self._heading_text = []
        classes = set((values.get("class") or "").split())
        if "formula" in classes:
            self.formula_depth += 1
        if tag == "em" and self.formula_depth:
            self.formula_em_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4"} and self._heading_level:
            self.headings.append((self._heading_level, "".join(self._heading_text).strip()))
            self._heading_level = None
            self._heading_text = []
        if tag == "div" and self.formula_depth:
            self.formula_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._heading_level:
            self._heading_text.append(data)
        if self.formula_depth:
            self.formula_text.append(data)


def check(name: str, ok: bool, evidence: str) -> dict[str, str]:
    return {"name": name, "status": "PASS" if ok else "FAIL", "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("html", type=Path)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--visual-status", choices=["PASS", "PENDING"], default="PENDING")
    parser.add_argument("--visual-evidence", default="尚未执行浏览器桌面/窄屏视觉 QA")
    parser.add_argument("--required-sections", default="")
    parser.add_argument("--question-prefix", default="")
    parser.add_argument("--question-count", type=int, default=0)
    args = parser.parse_args()

    source = args.source.resolve()
    artifact = args.html.resolve()
    source_text = source.read_text(encoding="utf-8")
    html_text = artifact.read_text(encoding="utf-8")
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    parsed = ArtifactParser()
    parsed.feed(html_text)

    h1_count = sum(level == 1 for level, _ in parsed.headings)
    hierarchy_ok = all(curr <= prev + 1 for (prev, _), (curr, _) in zip(parsed.headings, parsed.headings[1:]))
    anchor_failures = sorted({href[1:] for href in parsed.hrefs if href.startswith("#") and href[1:] not in parsed.ids})
    local_failures: list[str] = []
    for href in parsed.hrefs:
        parsed_url = urlparse(href)
        if parsed_url.scheme or href.startswith(('#', 'mailto:', 'data:')):
            continue
        path_part = href.split("#", 1)[0]
        if path_part and not (artifact.parent / path_part).resolve().exists():
            local_failures.append(href)

    formula_text = "\n".join(parsed.formula_text)
    required_style = all(
        marker in html_text
        for marker in [
            "#fdfcf7", "#f4f1ea", "#1a1a1a", "#1a4a8c", "#b8390e",
            'grid-template-columns: 260px minmax(0, 1fr)', "position: sticky",
            "@media (max-width: 900px)", "Source Serif Pro", "atom-one-light",
        ]
    )
    overflow_ok = all(marker in html_text for marker in ["pre, .formula, .table-wrap", "overflow-x: auto", "table-wrap"])
    mathjax_ok = all(
        marker in html_text
        for marker in ["mathjax@3", "inlineMath", "displayMath", "skipHtmlTags", "'pre'", "'code'"]
    )
    sha_ok = parsed.meta.get("source-sha256") == source_sha and source_sha in html_text
    source_subscripts = sorted(set(re.findall(r"_\{[^{}\n]+\}", source_text)))
    missing_subscripts = [item for item in source_subscripts if item not in html_text]
    required_sections = [item.strip() for item in args.required_sections.split(",") if item.strip()]
    missing_sections = [item for item in required_sections if item not in parsed.ids]
    question_ids: list[str] = []
    question_counts: dict[str, int] = {}
    if args.question_prefix:
        question_ids = re.findall(rf"\b{re.escape(args.question_prefix)}\d{{2}}\b", source_text)
        question_counts = {qid: question_ids.count(qid) for qid in sorted(set(question_ids))}
    diagnostic_ok = (
        not args.question_prefix
        or (
            len(question_counts) == args.question_count
            and all(count >= 2 for count in question_counts.values())
        )
    )

    checks = [
        check("source_sha", sha_ok, f"expected={source_sha}; embedded={parsed.meta.get('source-sha256', 'missing')}"),
        check("single_h1", h1_count == 1, f"h1_count={h1_count}"),
        check("heading_hierarchy", hierarchy_ok, f"headings={parsed.headings}"),
        check("academic_template", required_style, "palette/serif/1280-grid/260-sticky/900-breakpoint markers"),
        check("mathjax_config", mathjax_ok, "MathJax 3 delimiters and skipHtmlTags markers"),
        check("formula_em_zero", parsed.formula_em_count == 0, f"formula_em_count={parsed.formula_em_count}"),
        check("latex_subscript_literal", not missing_subscripts, f"source={source_subscripts}; missing={missing_subscripts}"),
        check("internal_overflow", overflow_ok, "table/code/formula internal overflow CSS markers"),
        check("anchors", not anchor_failures, f"unresolved={anchor_failures}"),
        check("local_links", not local_failures, f"unresolved={sorted(set(local_failures))}"),
    ]
    if required_sections:
        checks.append(check("required_sections", not missing_sections, f"required={required_sections}; missing={missing_sections}"))
    if args.question_prefix:
        checks.append(
            check(
                "diagnostic_question_coverage",
                diagnostic_ok,
                f"prefix={args.question_prefix}; expected={args.question_count}; counts={question_counts}",
            )
        )
    checks.append({"name": "browser_visual_qa", "status": args.visual_status, "evidence": args.visual_evidence})
    failed = [item for item in checks if item["status"] == "FAIL"]
    pending = [item for item in checks if item["status"] == "PENDING"]
    verdict = "FAIL" if failed else ("WARN" if pending else "PASS")
    open_items = [item["name"] for item in failed + pending]

    try:
        artifact_rel = artifact.relative_to(ROOT).as_posix()
    except ValueError:
        artifact_rel = artifact.as_posix()
    review = {
        "artifact": artifact_rel,
        "canonical_source": source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else source.as_posix(),
        "source_revision": source_sha,
        "verdict": verdict,
        "checks": checks,
        "open_items": open_items,
        "next": (
            "进入 M00 导航与诊断模块"
            if verdict == "PASS"
            else ("完成浏览器视觉 QA 后重新审查" if not failed else "修复失败项并重新审查")
        ),
    }
    args.review.parent.mkdir(parents=True, exist_ok=True)
    args.review.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
