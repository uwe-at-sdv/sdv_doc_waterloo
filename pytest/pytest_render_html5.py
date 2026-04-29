#!/usr/bin/env python3
"""Pytest suite for waterlint subcommand render-html5."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import ROOT, run_waterlint, DIR_DOC, DIR_EXAMPLES, DIR_EXAMPLES_JSON, PATH_EXAMPLES_JSON


def test_render_html5_lists_in_freeform_smoketest(tmp_path: Path) -> None:
	"""Render a freeform-list showcase and verify that HTML output is produced."""
	out_json = tmp_path / "pytest_lists_in_freeform.wtrl.core.rfc-2119.json"
	out_html = tmp_path / "pytest_lists_in_freeform.html"

	render_json = run_waterlint(
		"render-json",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"pytest_lists_in_freeform",
		"--out",
		str(out_json),
	)
	assert render_json.returncode == 0, f"render-json failed: {render_json.stderr}"
	assert out_json.exists(), "render-json did not produce output file"

	render_html = run_waterlint(
		"render-html5",
		"--in",
		str(out_json),
		"--out",
		str(out_html),
	)
	assert render_html.returncode == 0, f"render-html5 failed: {render_html.stderr}"
	assert out_html.exists(), "render-html5 did not produce output file"

	html = out_html.read_text(encoding="utf-8")
	assert "pytest_lists_in_freeform" in html
	assert "Item b.a.1" in html


def test_render_html5_single_in_to_out(tmp_path: Path) -> None:
	"""A single JSON input is rendered to a single requested output file."""
	out_file = tmp_path / "single.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), f"expected file not found: {out_file}"
	txt = out_file.read_text(encoding="utf-8")
	assert "<!doctype html>" in txt.lower()
	assert "wtrl-search" in txt


def test_render_html5_multi_in_to_out_dir_generates_default_name(tmp_path: Path) -> None:
	"""Multiple JSON inputs rendered via --out-dir get the documented default name."""
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_decorator.wtrl.core.rfc-2119.json",
		"--out-dir",
		str(tmp_path),
	)
	assert res.returncode == 0, res.stderr
	out_file = tmp_path / "waterloo-docs.core.rfc-2119.html"
	assert out_file.exists(), f"expected file not found: {out_file}"


def test_render_html5_fails_on_flavour_mismatch(tmp_path: Path) -> None:
	"""Merging inputs with different flavours must fail."""
	src = PATH_EXAMPLES_JSON / "test_docitem_method_property.wtrl.core.rfc-2119.json"
	bad = tmp_path / "bad_flavour.json"
	doc = json.loads(src.read_text(encoding="utf-8"))
	doc["__WTRL_META__"]["flavour"] = "raw"
	bad.write_text(json.dumps(doc), encoding="utf-8")
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--in",
		str(bad),
		"--out",
		str(tmp_path / "x.html"),
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}"
	assert "flavour mismatch" in res.stderr, res.stderr


def test_render_html5_embeds_extra_css_from_file(tmp_path: Path) -> None:
	"""A user-provided primary CSS file is embedded instead of the built-in stylesheet."""
	out_file = tmp_path / "with_css.html"
	css_file = tmp_path / "extra.css"
	css_file.write_text(".wtrl-app { outline: 3px solid red; }\n", encoding="utf-8")
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--css",
		str(css_file),
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), f"expected file not found: {out_file}"
	txt = out_file.read_text(encoding="utf-8")
	assert ".wtrl-app { outline: 3px solid red; }" in txt
	assert ".wtrl-side { border-right:1px solid #ddd;" not in txt
	assert ".wtrl-code" in txt


def test_render_html5_invalid_pygments_theme_falls_back(tmp_path: Path) -> None:
	"""An unknown Pygments theme falls back to a working default theme."""
	out_file = tmp_path / "fallback_theme.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--pygments-theme",
		"theme_that_does_not_exist",
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	txt = out_file.read_text(encoding="utf-8")
	assert ".wtrl-code" in txt


def test_render_html5_accepts_custom_header_fragment(tmp_path: Path) -> None:
	"""A valid custom header fragment is embedded into the generated HTML."""
	out_file = tmp_path / "custom_header.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--header-html",
		DIR_DOC + "/input-html/test_header_minimal.html",
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), "expected html output file was not created"
	txt = out_file.read_text(encoding="utf-8")
	assert 'id="wtrl-header"' in txt
	assert 'id="wtrl-title"' in txt


def test_render_html5_rejects_header_fragment_without_title(tmp_path: Path) -> None:
	"""A custom header fragment without #wtrl-title fails with RHTM-008."""
	bad_header = tmp_path / "bad_header.html"
	bad_header.write_text(
		"<div id=\"wtrl-header\"><p id=\"wtrl-sub\">No title here</p></div>\n",
		encoding="utf-8",
	)
	out_file = tmp_path / "bad.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--header-html",
		str(bad_header),
		"--out",
		str(out_file),
	)
	assert res.returncode == 1, res.stderr
	assert "RHTM-008" in res.stderr, res.stderr
	assert not out_file.exists(), "html output should not be created on invalid header fragment"


def test_render_html5_additional_css_keeps_default_css(tmp_path: Path) -> None:
	"""--additional-css appends to the default CSS instead of replacing it."""
	extra_css = tmp_path / "extra.css"
	extra_css.write_text(".wtrl-title { letter-spacing: 0.2em; }\n", encoding="utf-8")
	out_file = tmp_path / "with_additional_css.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--additional-css",
		str(extra_css),
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	txt = out_file.read_text(encoding="utf-8")
	assert ".wtrl-title { letter-spacing: 0.2em; }" in txt
	assert ".wtrl-side {" in txt


def test_render_html5_css_and_additional_css_are_combined(tmp_path: Path) -> None:
	"""--css and --additional-css may be used together in defined order."""
	primary_css = tmp_path / "primary.css"
	extra_css = tmp_path / "extra.css"
	primary_css.write_text(".wtrl-title { color: teal; }\n", encoding="utf-8")
	extra_css.write_text(".wtrl-title { letter-spacing: 0.2em; }\n", encoding="utf-8")
	out_file = tmp_path / "with_primary_and_extra_css.html"
	res = run_waterlint(
		"render-html5",
		"--in",
		DIR_EXAMPLES_JSON + "/test_docitem_method_property.wtrl.core.rfc-2119.json",
		"--css",
		str(primary_css),
		"--additional-css",
		str(extra_css),
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	txt = out_file.read_text(encoding="utf-8")
	assert ".wtrl-title { color: teal; }" in txt
	assert ".wtrl-title { letter-spacing: 0.2em; }" in txt
	assert ".wtrl-side {" not in txt
