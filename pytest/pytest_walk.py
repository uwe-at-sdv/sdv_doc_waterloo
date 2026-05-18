#!/usr/bin/env python3
"""Pytests for waterlint subcommand walk."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import run_waterlint, DIR_EXAMPLES


def test_walk_json_and_schema_inference(tmp_path: Path) -> None:
	out_json = tmp_path / "walk.json"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_docitem_coroutine",
		"--no-include-imported",
		"--out-json", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	assert out_json.exists()
	with out_json.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)
	assert isinstance(doc, dict)
	assert doc["__WTRL_VERSION__"]["schema"] == "0.0.0"
	assert "__WTRL_SUMMARY__" in doc
	assert "__WTRL_OBJECTS__" in doc
	assert len(doc["__WTRL_OBJECTS__"]) > 0

	val = run_waterlint("validate-json", "--in", str(out_json))
	assert val.returncode == 0, val.stderr


def test_walk_text_show_subset(tmp_path: Path) -> None:
	out_txt = tmp_path / "walk.txt"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_docitem_coroutine",
		"--no-include-imported",
		"--out", str(out_txt),
	)
	assert res.returncode == 0, res.stderr
	assert out_txt.exists()
	txt = out_txt.read_text(encoding="utf-8")
	assert "BASEDIR:" in txt
	assert "{BASEDIR}/" in txt
	assert "qualname" in txt
	assert "kind" in txt
	assert "scope" in txt
	assert "lineno" in txt
	assert "included" in txt
	assert "reason" in txt
