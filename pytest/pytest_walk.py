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
#	assert doc["__WTRL_VERSION__"]["schema"] == "0.0.0"
	assert "__WTRL_SUMMARY__" in doc
	assert "__WTRL_OBJECTS__" in doc
	assert len(doc["__WTRL_OBJECTS__"]) > 0
	assert all("reason_detail" in entry for entry in doc["__WTRL_OBJECTS__"])

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


def test_walk_text_show_default_alias(tmp_path: Path) -> None:
	out_txt = tmp_path / "walk_default.txt"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_docitem_coroutine",
		"--no-include-imported",
		"--show", "default,reason_detail",
		"--out", str(out_txt),
	)
	assert res.returncode == 0, res.stderr
	txt = out_txt.read_text(encoding="utf-8")
	assert "qualname" in txt
	assert "kind" in txt
	assert "scope" in txt
	assert "file" in txt
	assert "lineno" in txt
	assert "included" in txt
	assert "reason" in txt
#	assert "reason_detail" in txt


def test_walk_multiple_objects(tmp_path: Path) -> None:
	out_json = tmp_path / "walk_multi.json"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_docitem_coroutine",
		"--obj", "test_scope_mix",
		"--no-include-imported",
		"--sort", "file,lineno",
		"--out-json", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	with out_json.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)
	assert doc["__WTRL_META__"]["objs"] == ["test_docitem_coroutine", "test_scope_mix"]
	assert isinstance(doc["__WTRL_OBJECTS__"], list)
	assert len(doc["__WTRL_OBJECTS__"]) > 0
