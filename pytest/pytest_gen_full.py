#!/usr/bin/env python3
"""Pytests for waterlint subcommand gen-full."""

from __future__ import annotations

from pathlib import Path

import json
import pytest

from pytest_common import run_waterlint, DIR_EXAMPLES

OBJECTS = [
	("empty_objects", "module"),
	("empty_objects.EmptyClass", "class"),
	("empty_objects.empty_function", "function"),
	("empty_objects.X.empty_method", "method"),
]

INDENTS = ["tab", "spc4"]


def _strip_triple_quotes(text: str) -> str:
	lines = text.splitlines()
	if lines and lines[0].strip() == 'r"""':
		lines = lines[1:]
	if lines and lines[-1].strip() == '"""':
		lines = lines[:-1]
	return "\n".join(lines).rstrip() + "\n"


def _validate_generated_docstring(tmp_path: Path, generated_literal: str) -> None:
	doc_for_validate = _strip_triple_quotes(generated_literal)
	in_file = tmp_path / "generated_docstring.txt"
	in_file.write_text(doc_for_validate, encoding="utf-8")
	res = run_waterlint("validate", "--in", str(in_file))
	assert res.returncode == 0, (
		f"waterlint validate --in failed\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}\n"
		f"doc:\n{doc_for_validate}"
	)


@pytest.mark.parametrize("obj,profile", OBJECTS)
@pytest.mark.parametrize("indent", INDENTS)
def test_gen_full_raw_to_file_validates(
	tmp_path: Path,
	obj: str,
	profile: str,
	indent: str,
) -> None:
	out_file = tmp_path / f"test_full_{obj.replace('.', '_')}_{indent}.py"
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		obj,
		"--format",
		"raw",
		"--indent",
		indent,
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert res.stdout == ""
	assert out_file.exists()
	generated = out_file.read_text(encoding="utf-8")
	assert generated.startswith('r"""')
	assert f"{profile}" in generated
	_validate_generated_docstring(tmp_path, generated)


def test_gen_full_raw_stdout_smoke() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"empty_objects.empty_function",
		"--format",
		"raw",
		"--indent",
		"spc4",
	)
	assert res.returncode == 0, res.stderr
	assert res.stdout.startswith('r"""')
	assert "Raises:" in res.stdout
	assert "|Must| return |None|." in res.stdout


def test_gen_full_recursive_json_traverses_expected_objects() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"empty_objects",
		"--recursive",
		"--format",
		"json",
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert doc["mode"] == "full"
	assert doc["recursive"] is True
	assert doc["missing_only"] is False
	assert doc["count"] == 9
	qids = {entry["qualified_identifier"] for entry in doc["objects"]}
	assert "empty_objects" in qids
	assert "empty_objects.EmptyClass" in qids
	assert "empty_objects.empty_function" in qids
	assert "empty_objects.X" in qids
	assert "empty_objects.X.EmptySubclass" in qids
	assert "empty_objects.X.Y" in qids
	assert "empty_objects.X.Y.method_in_subclass" in qids
	assert "empty_objects.X.empty_method" in qids
	assert "empty_objects.X.f" in qids
	assert "empty_objects.X.Y.method_in_subclass.non_documentable_function" not in qids
	assert "empty_objects.X.Y.NonDocumentabelClass" not in qids


def test_gen_full_recursive_missing_only_filters_existing_docstrings() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"empty_objects",
		"--recursive",
		"--missing-only",
		"--format",
		"json",
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert doc["mode"] == "full"
	assert doc["recursive"] is True
	assert doc["missing_only"] is True
	assert doc["count"] == 7
	qids = {entry["qualified_identifier"] for entry in doc["objects"]}
	assert "empty_objects.X.Y" not in qids
	assert "empty_objects.X.f" not in qids
	assert "empty_objects" in qids
	assert "empty_objects.EmptyClass" in qids
	assert "empty_objects.empty_function" in qids
	assert "empty_objects.X" in qids
	assert "empty_objects.X.EmptySubclass" in qids
	assert "empty_objects.X.Y.method_in_subclass" in qids
	assert "empty_objects.X.empty_method" in qids


def test_gen_full_recursive_defaults_to_json() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"pytest_no_docstring",
		"--recursive",
		"--missing-only",
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert doc["mode"] == "full"
	assert doc["recursive"] is True
	assert doc["missing_only"] is True
	assert isinstance(doc.get("objects"), list)
	qids = {entry["qualified_identifier"] for entry in doc["objects"]}
	assert "pytest_no_docstring" in qids
	assert "pytest_no_docstring.X" in qids
	assert "pytest_no_docstring.X.m" in qids
	assert "pytest_no_docstring.f" in qids


def test_gen_full_recursive_multi_obj_deduplicates_targets() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"pytest_good_render_json_A",
		"--obj",
		"pytest_good_render_json_A.A",
		"--recursive",
		"--format",
		"json",
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	qids = [entry["qualified_identifier"] for entry in doc["objects"]]
	assert qids.count("pytest_good_render_json_A.A") == 1, qids


def test_gen_full_format_raw_requires_exactly_one_target() -> None:
	res = run_waterlint(
		"gen-full",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_function_minimal.spam",
		"--obj",
		"test_docitem_function_full.test",
		"--format",
		"raw",
	)
	assert res.returncode == 2, res.stderr
	assert "TOOL-008" in res.stderr, res.stderr
	assert "--format raw requires exactly one target object" in res.stderr
