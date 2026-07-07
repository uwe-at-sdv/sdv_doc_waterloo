#!/usr/bin/env python3
"""Pytest suite for waterlint subcommand gen-example-template-json."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import run_waterlint


def test_gen_example_template_json_stdout_default() -> None:
	"""Default invocation writes a valid template JSON to stdout."""
	res = run_waterlint("gen-example-template-json")
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert "wtrl-example-refs-json-" in doc["$schema"] and doc["$schema"].endswith(".schema.json")
	assert "urn:none:local:wtrl-example-refs-json:" in doc["$id"]
	assert doc["__WTRL_EXAMPLE_REFS__"] == {
		"my_module.my_function": ["path/to/example1.py", "path/to/example2.py"],
	}


def test_gen_example_template_json_with_custom_id_segments() -> None:
	"""$id segments can be set via --org-or-project and --domain."""
	res = run_waterlint(
		"gen-example-template-json",
		"--org-or-project",
		"sdv",
		"--domain",
		"waterloo",
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert ":wtrl-example-refs-json:" in doc["$id"]


def test_gen_example_template_json_out_file(tmp_path: Path) -> None:
	"""--out writes template JSON to file."""
	out_file = tmp_path / "examples.template.json"
	res = run_waterlint(
		"gen-example-template-json",
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), "expected output file was not created"
	doc = json.loads(out_file.read_text(encoding="utf-8"))
	assert isinstance(doc, dict)
	assert doc["__WTRL_EXAMPLE_REFS__"] == {
		"my_module.my_function": ["path/to/example1.py", "path/to/example2.py"],
	}
