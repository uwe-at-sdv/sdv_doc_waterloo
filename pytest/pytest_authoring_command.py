#!/usr/bin/env python3
"""End-to-end command-line tests for Waterloo Authoring JSON rendering."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import run_waterlint


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"


def test_render_docstring_reads_file_and_writes_raw_docstring() -> None:
	"""The command renders document data to stdout and keeps diagnostics on stderr."""
	result = run_waterlint(
		"render-docstring",
		"--in", str(FIXTURE_DIR / "valid_method.json"),
	)
	assert result.returncode == 0, result.stderr
	assert result.stdout.startswith("Preamble:\n")
	assert "Contract:\n" in result.stdout
	assert "rendering docstring" not in result.stdout
	assert "rendering docstring" in result.stderr


def test_render_docstring_defaults_to_stdin() -> None:
	"""Omitting --in must be equivalent to explicitly selecting @STDIN."""
	input_text = (FIXTURE_DIR / "valid_method.json").read_text(encoding="utf-8")
	implicit = run_waterlint("render-docstring", input_text=input_text)
	explicit = run_waterlint("render-docstring", "--in", "@STDIN", input_text=input_text)
	assert implicit.returncode == 0, implicit.stderr
	assert explicit.returncode == 0, explicit.stderr
	assert implicit.stdout == explicit.stdout
	assert implicit.stdout.startswith("Preamble:\n")
	assert "[@STDIN] rendering docstring" in implicit.stderr


def test_render_docstring_reports_schema_valid_semantic_error(tmp_path: Path) -> None:
	"""Source-independent contradictions are diagnosed as JIDO-001 before output."""
	document = json.loads((FIXTURE_DIR / "valid_method.json").read_text(encoding="utf-8"))
	document["doc"]["Preamble"]["normative_sections"].append("Contract")
	path = tmp_path / "duplicate-normative.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("render-docstring", "--in", str(path))
	assert result.returncode == 1
	assert "JIDO-001" in result.stderr
	assert "listed more than once" in result.stderr
	assert result.stdout == ""
