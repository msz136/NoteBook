#!/usr/bin/env python3
"""Deterministic smoke and failure-path tests for the academic renderer."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from render_academic import DEFAULT_CSS, render_markdown


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "templates" / "render_fixture.md"
VALIDATOR = ROOT / "tools" / "validate_artifact.py"


class RenderPipelineTest(unittest.TestCase):
    def test_render_is_deterministic_and_math_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fixture.html"
            first_sha = render_markdown(FIXTURE, out, DEFAULT_CSS)
            first = out.read_bytes()
            second_sha = render_markdown(FIXTURE, out, DEFAULT_CSS)
            second = out.read_bytes()
            self.assertEqual(first_sha, second_sha)
            self.assertEqual(first, second)
            text = second.decode("utf-8")
            self.assertIn(f'<meta name="source-sha256" content="{first_sha}">', text)
            self.assertIn("_{b,h,j}", text)
            self.assertNotIn('<div class="formula" data-math-kind="display"><em>', text)
            self.assertIn("$not_math$", text)

    def test_validator_rejects_stale_generated_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            source = temp / "fixture.md"
            html = temp / "fixture.html"
            review = temp / "fixture.review.json"
            source.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            render_markdown(source, html, DEFAULT_CSS)
            source.write_text(source.read_text(encoding="utf-8") + "\n<!-- changed -->\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(source), str(html), "--review", str(review)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(review.read_text(encoding="utf-8"))
            self.assertEqual(payload["verdict"], "FAIL")
            sha_check = next(item for item in payload["checks"] if item["name"] == "source_sha")
            self.assertEqual(sha_check["status"], "FAIL")
            expected = hashlib.sha256(source.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            self.assertIn(expected, sha_check["evidence"])

    def test_local_svg_is_inlined_into_single_file_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            source = temp / "asset.md"
            asset = temp / "plot.svg"
            output = temp / "asset.html"
            asset.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="2" height="2"/></svg>', encoding="utf-8")
            source.write_text("# Asset fixture\n\n![plot](plot.svg)\n", encoding="utf-8")
            render_markdown(source, output, DEFAULT_CSS)
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("data:image/svg+xml;base64,", rendered)
            self.assertIn('data-source-path="plot.svg"', rendered)


if __name__ == "__main__":
    unittest.main()
