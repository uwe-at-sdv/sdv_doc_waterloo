#!/usr/bin/env python3
"""Pytests for waterlint subcommand validate-json."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import ROOT, run_waterlint, DIR_EXAMPLES, PATH_EXAMPLES, DIR_EXAMPLES_JSON, PATH_EXAMPLES_JSON


def _run_waterlint_validate_json(path: str, schema: str | None = None):
	"""Run ``waterlint validate-json`` for a JSON file under project root."""
	args: list[str] = ["validate-json", "--in", path]
	if schema:
		args.extend(["--schema", schema])
	return run_waterlint(*args)


def test_validate_json_selftest() -> None:
	"""Render module JSON and validate against the schema."""
	tmp_json = "/tmp/sdv_doc_docitem.wtrl.json"

	render = run_waterlint(
		"render-json",
		"--obj",
		"sdv_doc_docitem",
		"--out",
		tmp_json,
	)
	assert render.returncode == 0, f"render-json failed: {render.stderr}"

	result = _run_waterlint_validate_json(
		tmp_json,
		"schema/wtrl-json-0.0.5.schema.json",
	)
	assert result.returncode == 0, f"validate-json failed: {result.stderr}"


def test_validate_json_bad_not_even() -> None:
	result = _run_waterlint_validate_json(DIR_EXAMPLES_JSON + "/bad_not_even.json")
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert "JSCH-004" in result.stderr, result.stderr


def test_validate_json_bad_missing_version() -> None:
	result = _run_waterlint_validate_json(DIR_EXAMPLES_JSON + "/bad_missing_version.json")
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert "JSCH-003" in result.stderr, result.stderr


def test_validate_json_bad_missing_legend() -> None:
	result = _run_waterlint_validate_json(DIR_EXAMPLES_JSON + "/bad_missing_legend.json")
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert "JSCH-005" in result.stderr, result.stderr


def test_validate_json_draft_examples_ok() -> None:
	result = _run_waterlint_validate_json(
		DIR_EXAMPLES_JSON + "/mymod.wtrl.core.rfc-2119.json",
		"schema/wtrl-json-0.0.6.schema.json",
	)
	assert result.returncode == 0, f"expected exit code 0, got {result.returncode}"


def test_validate_json_draft_examples_missing_pointer() -> None:
	src = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	tmp = PATH_EXAMPLES_JSON / "_tmp_bad_examples_missing_pointer.json"
	doc = json.loads(src.read_text(encoding="utf-8"))
	obj_qid = "mymod.X"
	doc["__WTRL_OBJECTS__"][obj_qid]["examples"] = ["/__WTRL_EXAMPLES__/does_not_exist"]
	tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
	try:
		result = _run_waterlint_validate_json(str(tmp), "schema/wtrl-json-0.0.6.schema.json")
		assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
		assert "JSCH-006" in result.stderr, result.stderr
	finally:
		if tmp.exists():
			tmp.unlink()


def test_validate_json_draft_examples_unknown_referenced_by() -> None:
	src = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	tmp = PATH_EXAMPLES_JSON / "_tmp_bad_examples_unknown_refby.json"
	doc = json.loads(src.read_text(encoding="utf-8"))
	ex_key = next(iter(doc["__WTRL_EXAMPLES__"].keys()))
	doc["__WTRL_EXAMPLES__"][ex_key]["referenced_by"] = ["mymod.DoesNotExist"]
	tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
	try:
		result = _run_waterlint_validate_json(str(tmp), "schema/wtrl-json-0.0.6.schema.json")
		assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
		assert "JSCH-007" in result.stderr, result.stderr
	finally:
		if tmp.exists():
			tmp.unlink()


def test_validate_json_draft_examples_missing_back_reference() -> None:
	src = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	tmp = PATH_EXAMPLES_JSON / "_tmp_bad_examples_missing_backref.json"
	doc = json.loads(src.read_text(encoding="utf-8"))
	ex_key = next(iter(doc["__WTRL_EXAMPLES__"].keys()))
	doc["__WTRL_EXAMPLES__"][ex_key]["referenced_by"] = []
	tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
	try:
		result = _run_waterlint_validate_json(str(tmp), "schema/wtrl-json-0.0.6.schema.json")
		assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
		assert "JSCH-008" in result.stderr, result.stderr
	finally:
		if tmp.exists():
			tmp.unlink()


def test_validate_json_draft_examples_missing_forward_reference() -> None:
	src = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	tmp = PATH_EXAMPLES_JSON / "_tmp_bad_examples_missing_forwardref.json"
	doc = json.loads(src.read_text(encoding="utf-8"))
	obj_qid = "mymod.X"
	doc["__WTRL_OBJECTS__"][obj_qid]["examples"] = []
	tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
	try:
		result = _run_waterlint_validate_json(str(tmp), "schema/wtrl-json-0.0.6.schema.json")
		assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
		assert "JSCH-009" in result.stderr, result.stderr
	finally:
		if tmp.exists():
			tmp.unlink()

