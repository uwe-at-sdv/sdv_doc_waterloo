#!/usr/bin/env python3
"""Schema and automatic category-detection tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pytest_common import DIR_SCHEMA, run_waterlint


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"
SCHEMA_PATH = Path(DIR_SCHEMA) / "wtrl-authoring-object-json-0.2.0.schema.json"


def _validate_fixture(name: str):
	"""Run validate-json without --schema to exercise automatic schema selection."""
	return run_waterlint("validate-json", "--in", str(FIXTURE_DIR / name))


def test_authoring_schema_is_a_valid_draft_2020_12_schema() -> None:
	"""Keep schema syntax and self-references valid before testing document fixtures."""
	schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
	Draft202012Validator.check_schema(schema)


def test_authoring_schema_accepts_keyed_table_blocks(tmp_path: Path) -> None:
	"""Schema 0.2 accepts tables only through a free-form text-block position."""
	document = {
		"$schema": "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.2.0.schema.json",
		"$id": "urn:waterlint:wtrl-authoring-object-json:demo.table",
		"__WTRL_CATEGORY__": "wtrl-authoring-object-json",
		"__WTRL_VERSION__": {"schema": "0.2.0"},
		"qualified_name": "demo.table",
		"profile": "module",
		"doc": {
			"Preamble": {"profile": "module", "normative_sections": ["Contract"]},
			"Contract": {"general": ["|Must| provide a table."]},
			"Description": [{"table": {"groups": [{
				"title": ["Result values"],
				"columns": [{"key": "code", "header": "Code"}, {"key": "meaning", "header": "Meaning"}],
				"rows": [{"cells": {"code": "0", "meaning": "success"}}, {"cells": {"code": "1", "meaning": ""}}],
			}]}}],
		},
	}
	path = tmp_path / "table-authoring.json"
	path.write_text(json.dumps(document), encoding="utf-8")
	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 0, result.stderr

	# Contract remains a list of logical text items, not a free-form block sequence.
	document["doc"]["Contract"]["general"] = document["doc"]["Description"]
	path.write_text(json.dumps(document), encoding="utf-8")
	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JSCH-005" in result.stderr, result.stderr


@pytest.mark.parametrize(
	"name",
	[
		"valid_module.json",
		"valid_class.json",
		"valid_function.json",
		"valid_method.json",
		"valid_inherited_method.json",
		"maximal_module.json",
		"maximal_class.json",
		"maximal_function.json",
		"maximal_method.json",
		"maximal_inherited_method.json",
	],
)
def test_authoring_json_valid_profiles_are_auto_detected(name: str) -> None:
	"""Every supported profile must validate through __WTRL_CATEGORY__ without --schema."""
	result = _validate_fixture(name)
	assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
	("name", "rule_id"),
	[
		("invalid_unknown_key.json", "JSCH-005"),
		("invalid_profile_mismatch.json", "JSCH-005"),
		("invalid_physical_line.json", "JSCH-005"),
		("invalid_list_item.json", "JSCH-005"),
		("invalid_definitions_inherit.json", "JSCH-005"),
		("invalid_definition_label.json", "JSCH-005"),
		("invalid_unknown_category.json", "JSCH-003"),
	],
)
def test_authoring_json_invalid_fixtures_are_rejected(name: str, rule_id: str) -> None:
	"""Reject malformed authoring documents before rendering can begin."""
	result = _validate_fixture(name)
	assert result.returncode == 1, result.stderr
	assert rule_id in result.stderr, result.stderr
