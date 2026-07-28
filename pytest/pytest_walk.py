#!/usr/bin/env python3
"""Pytests for waterlint subcommand walk."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from pytest_common import ROOT, WATERLINT, run_waterlint, DIR_EXAMPLES, DIR_DOC_EXAMPLES


def _walk_qualnames(path: Path) -> list[str]:
	with path.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)
	return [entry["qualname"] for entry in doc["__WTRL_OBJECTS__"]]


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


def test_walk_include_qid_prefix_uses_synthetic_package_tree(tmp_path: Path) -> None:
	out_json = tmp_path / "walk_A_B0_C1.json"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_DOC_EXAMPLES,
		"--obj", "A",
		"--include-qid-prefix", "A.B0.C1",
		"--out-json", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	assert _walk_qualnames(out_json) == [
		"A",
		"A.B0.C1",
		"A.B0.C1.mod_D0",
		"A.B0.C1.mod_D1",
	]


def test_walk_include_qid_prefix_is_segment_aware(tmp_path: Path) -> None:
	out_json = tmp_path / "walk_A_segment_aware.json"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_DOC_EXAMPLES,
		"--obj", "A",
		"--include-qid-prefix", "A.B0.C1.mod_D",
		"--out-json", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	assert _walk_qualnames(out_json) == ["A"]


def test_walk_reports_invalid_basedir(tmp_path: Path) -> None:
	env = os.environ.copy()
	env["PYTHONPATH"] = os.pathsep.join([str(ROOT / "src"), env.get("PYTHONPATH", "")])
	res = subprocess.run(
		[
			*WATERLINT,
			"walk",
			"--basedir",
			"src/sdv/doc/waterloo",
			"--obj",
			"mcp.wtrl_tools.get_root",
			"--out",
			str(tmp_path / "walk.txt"),
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		env=env,
		cwd=ROOT.parent,
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-001" in res.stderr, res.stderr
	assert "basedir is not a directory" in res.stderr, res.stderr
