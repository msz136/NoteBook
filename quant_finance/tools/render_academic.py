#!/usr/bin/env python3
"""Render canonical Markdown into an ARIS academic HTML artifact."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import mimetypes
import re
from pathlib import Path

import yaml
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSS = ROOT / "templates" / "aris_academic_v1.css"
NAVIGATION_PATH = ROOT / "navigation.json"
HEADING_ID_RE = re.compile(r"\s*\{#([A-Za-z][A-Za-z0-9_-]*)\}\s*$")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("YAML front matter 未闭合")
    meta = yaml.safe_load(text[4:end]) or {}
    if not isinstance(meta, dict):
        raise ValueError("YAML front matter 必须是映射")
    return {str(k): str(v) for k, v in meta.items()}, text[end + 5 :]


def split_fenced_segments(text: str) -> list[tuple[bool, str]]:
    segments: list[tuple[bool, str]] = []
    normal: list[str] = []
    fenced: list[str] = []
    fence_char = ""
    fence_len = 0
    in_fence = False
    for line in text.splitlines(keepends=True):
        match = FENCE_RE.match(line)
        if not in_fence and match:
            if normal:
                segments.append((False, "".join(normal)))
                normal = []
            in_fence = True
            marker = match.group(1)
            fence_char, fence_len = marker[0], len(marker)
            fenced.append(line)
        elif in_fence:
            fenced.append(line)
            stripped = line.lstrip()
            if stripped.startswith(fence_char * fence_len) and not stripped.startswith(fence_char * (fence_len + 1)):
                segments.append((True, "".join(fenced)))
                fenced = []
                in_fence = False
        else:
            normal.append(line)
    if fenced:
        segments.append((True, "".join(fenced)))
    if normal:
        segments.append((False, "".join(normal)))
    return segments


def protect_math(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}
    counter = 0

    def token(kind: str, latex: str) -> str:
        nonlocal counter
        key = f"qf-math-{kind}-{counter}"
        counter += 1
        escaped = html.escape(latex, quote=False)
        if kind == "block":
            replacements[key] = f'<div class="formula" data-math-kind="display">\\[{escaped}\\]</div>'
            return f'\n<div data-math-placeholder="{key}"></div>\n'
        replacements[key] = f'<span class="math-inline" data-math-kind="inline">\\({escaped}\\)</span>'
        return f'<span data-math-placeholder="{key}"></span>'

    def process(segment: str) -> str:
        out: list[str] = []
        i = 0
        length = len(segment)
        while i < length:
            if segment[i] == "`":
                run = 1
                while i + run < length and segment[i + run] == "`":
                    run += 1
                marker = "`" * run
                end = segment.find(marker, i + run)
                if end >= 0:
                    out.append(segment[i : end + run])
                    i = end + run
                    continue
            if segment.startswith("$$", i):
                end = segment.find("$$", i + 2)
                if end >= 0:
                    out.append(token("block", segment[i + 2 : end].strip()))
                    i = end + 2
                    continue
            if segment.startswith("\\[", i):
                end = segment.find("\\]", i + 2)
                if end >= 0:
                    out.append(token("block", segment[i + 2 : end].strip()))
                    i = end + 2
                    continue
            if segment.startswith("\\(", i):
                end = segment.find("\\)", i + 2)
                if end >= 0:
                    out.append(token("inline", segment[i + 2 : end]))
                    i = end + 2
                    continue
            if segment[i] == "$" and (i == 0 or segment[i - 1] != "\\"):
                end = segment.find("$", i + 1)
                if end > i + 1 and "\n" not in segment[i + 1 : end]:
                    content = segment[i + 1 : end]
                    if not content.startswith(" ") and not content.endswith(" "):
                        out.append(token("inline", content))
                        i = end + 1
                        continue
            out.append(segment[i])
            i += 1
        return "".join(out)

    protected = "".join(part if fenced else process(part) for fenced, part in split_fenced_segments(text))
    return protected, replacements


def slugify(value: str) -> str:
    value = HEADING_ID_RE.sub("", value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE).strip("-")
    return value or "section"


def inline_local_assets(body_html: str, source_dir: Path) -> str:
    """Inline local image assets so rendered reports remain single-file artifacts."""
    image_re = re.compile(r'<img\s+([^>]*?)src="([^"]+)"([^>]*)>', flags=re.I)

    def replace(match: re.Match[str]) -> str:
        before, src, after = match.groups()
        if re.match(r"^(?:[a-z]+:|//|#)", src, flags=re.I):
            return match.group(0)
        asset = (source_dir / src).resolve()
        if not asset.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
        payload = base64.b64encode(asset.read_bytes()).decode("ascii")
        return f'<img {before}src="data:{mime};base64,{payload}" data-source-path="{html.escape(src, quote=True)}"{after}>'

    return image_re.sub(replace, body_html)


def next_chapter_link(source: Path, output: Path) -> tuple[str, str] | None:
    """Return a relative next-report link from the repository navigation manifest."""
    if not NAVIGATION_PATH.is_file():
        return None
    navigation = __import__("json").loads(NAVIGATION_PATH.read_text(encoding="utf-8"))
    entries = navigation.get("reports", [])
    try:
        source_rel = source.relative_to(ROOT).as_posix()
    except ValueError:
        # Fixture/temp renders outside the repository have no navigation entry.
        return None
    for index, entry in enumerate(entries):
        if entry.get("source") != source_rel:
            continue
        next_entry = entries[(index + 1) % len(entries)] if entries else None
        if not next_entry:
            return None
        next_html = ROOT / next_entry["html"]
        relative = __import__("os").path.relpath(next_html, output.parent).replace("\\", "/")
        return relative, str(next_entry.get("title", Path(next_entry["html"]).stem))
    return None


def render_markdown(source: Path, output: Path, css_path: Path) -> str:
    source_text = source.read_text(encoding="utf-8")
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    meta, body = parse_front_matter(source_text)
    protected, math_replacements = protect_math(body)

    md = MarkdownIt("commonmark", {"html": True, "linkify": True}).enable("table")
    tokens = md.parse(protected)
    headings: list[tuple[int, str, str]] = []
    seen_ids: dict[str, int] = {}
    h1_title = ""
    remove_indexes: set[int] = set()

    for index, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        level = int(tok.tag[1])
        inline = tokens[index + 1]
        raw_title = inline.content.strip()
        explicit = HEADING_ID_RE.search(raw_title)
        clean_title = HEADING_ID_RE.sub("", raw_title).strip()
        base_id = explicit.group(1) if explicit else slugify(clean_title)
        seen_ids[base_id] = seen_ids.get(base_id, 0) + 1
        heading_id = base_id if seen_ids[base_id] == 1 else f"{base_id}-{seen_ids[base_id]}"
        tok.attrSet("id", heading_id)
        if clean_title != raw_title:
            inline.content = clean_title
            parsed = md.parseInline(clean_title)
            inline.children = parsed[0].children if parsed else []
        if level == 1:
            if h1_title:
                raise ValueError("Markdown 必须且只能包含一个 H1")
            h1_title = clean_title
            remove_indexes.update({index, index + 1, index + 2})
        else:
            headings.append((level, clean_title, heading_id))

    if not h1_title:
        raise ValueError("Markdown 必须包含一个 H1")
    filtered_tokens = [tok for i, tok in enumerate(tokens) if i not in remove_indexes]
    body_html = md.renderer.render(filtered_tokens, md.options, {})
    for key, value in math_replacements.items():
        body_html = body_html.replace(f'<div data-math-placeholder="{key}"></div>', value)
        body_html = body_html.replace(f'<span data-math-placeholder="{key}"></span>', value)
    body_html = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', body_html, flags=re.S)
    body_html = inline_local_assets(body_html, source.parent)

    title = meta.get("title", h1_title)
    subtitle = meta.get("subtitle", "计量金融与量化资料库")
    topic = meta.get("topic", "Quant Finance")
    date = meta.get("date", "未标注")
    cutoff = meta.get("evidence_cutoff", date)
    toc_items = "\n".join(
        f'<li class="depth-{level}"><a href="#{html.escape(hid)}">{html.escape(text)}</a></li>'
        for level, text, hid in headings
        if 2 <= level <= 4
    )
    css = css_path.read_text(encoding="utf-8")
    next_link = next_chapter_link(source, output)
    next_html = ""
    if next_link:
        next_href, next_title = next_link
        next_html = f'''        <nav class="next-chapter" aria-label="下一章节">
          <span class="next-chapter-label">下一章节</span>
          <a rel="next" href="{html.escape(next_href, quote=True)}">{html.escape(next_title)} →</a>
        </nav>
'''
    document = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="generator" content="quant_finance ARIS render-html (academic, v1)">
  <meta name="source-file" content="{html.escape(source.name)}">
  <meta name="source-sha256" content="{source_sha}">
  <title>{html.escape(title)}</title>
  <script>
    window.MathJax = {{
      tex: {{inlineMath: [['\\\\(', '\\\\)'], ['$', '$']], displayMath: [['\\\\[', '\\\\]'], ['$$', '$$']]}},
      options: {{skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']}}
    }};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
{css}
    .next-chapter {{ margin: 2.5rem 0 1rem; padding: 1rem 1.2rem; border: 1px solid #b9c9df; border-left: 4px solid #1a4a8c; background: #f4f1ea; display: flex; gap: .75rem; align-items: baseline; justify-content: space-between; }}
    .next-chapter-label {{ color: #1a4a8c; font-weight: 700; white-space: nowrap; }}
    .next-chapter a {{ color: #1a4a8c; font-weight: 700; text-decoration: none; }}
    .next-chapter a:hover, .next-chapter a:focus {{ color: #b8390e; text-decoration: underline; }}
    @media (max-width: 900px) {{ .next-chapter {{ display: block; }} .next-chapter-label {{ display: block; margin-bottom: .35rem; }} }}
  </style>
</head>
<body id="top">
  <div class="page-shell">
    <nav class="toc" aria-label="目录">
      <p class="toc-title">Contents</p>
      <ol>
{toc_items}
      </ol>
    </nav>
    <main>
      <article>
        <header>
          <p class="eyebrow">{html.escape(topic)}</p>
          <p class="subtitle">{html.escape(subtitle)}</p>
          <h1>{html.escape(h1_title)}</h1>
          <p class="meta">发布日期：{html.escape(date)} · 证据截止：{html.escape(cutoff)} · 源文件 SHA-256：<code>{source_sha}</code></p>
        </header>
{body_html}
{next_html}
        <a class="back-to-top" href="#top">返回页首 ↑</a>
      </article>
    </main>
  </div>
</body>
</html>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8", newline="\n")
    return source_sha


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--css", type=Path, default=DEFAULT_CSS)
    args = parser.parse_args()
    source = args.source.resolve()
    output = (args.output or source.with_suffix(".html")).resolve()
    sha = render_markdown(source, output, args.css.resolve())
    print(f"rendered={output}")
    print(f"source_sha256={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
